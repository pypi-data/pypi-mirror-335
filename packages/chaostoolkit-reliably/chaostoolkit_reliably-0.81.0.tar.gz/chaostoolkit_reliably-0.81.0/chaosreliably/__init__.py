import io
import logging
import os
import threading
from contextlib import contextmanager
from datetime import timedelta
from typing import Any, Dict, Generator, Iterator, List

import httpx
from chaoslib.discovery.discover import (
    discover_actions,
    discover_activities,
    discover_probes,
    initialize_discovery_result,
)
from chaoslib.types import (
    Configuration,
    DiscoveredActivities,
    Discovery,
    Secrets,
)

try:
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

    HAS_HTTPX_OLTP = True
except ImportError:
    HAS_HTTPX_OLTP = False

from .__version__ import __version__

__all__ = [
    "get_session",
    "discover",
    "parse_duration",
    "attach_log_stream_handler",
]
RELIABLY_HOST = "app.reliably.com"
STREAM_LOG = io.StringIO()

logger = logging.getLogger("chaostoolkit")
shared_state_lock = threading.Lock()
shared_state = {}  # type: ignore


@contextmanager
def get_session(
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> Generator[httpx.Client, None, None]:
    c = configuration or {}
    verify_tls = c.get(
        "reliably_verify_tls",
        os.getenv("RELIABLY_VERIFY_TLS", "true").lower() in ("true", "1", "t"),
    )
    with_http2 = True if verify_tls else False
    use_http = c.get(
        "reliably_use_http",
        os.getenv("RELIABLY_USE_HTTP", "false").lower() in ("true", "1", "t"),
    )
    scheme = "http" if use_http else "https"
    auth_info = get_auth_info(configuration, secrets)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(auth_info["token"]),
    }

    with httpx.Client(
        verify=verify_tls, http2=with_http2, timeout=30
    ) as client:
        # do not pollute users traces
        if HAS_HTTPX_OLTP:
            try:
                if client._is_instrumented_by_opentelemetry:  # type: ignore
                    HTTPXClientInstrumentor.uninstrument_client(client)
            except AttributeError:
                pass

        client.headers = httpx.Headers(headers)
        client.base_url = httpx.URL(
            f"{scheme}://{auth_info['host']}/api/v1/organization"
        )
        yield client


def discover(discover_system: bool = True) -> Discovery:
    """
    Discover Reliably capabilities from this extension.
    """
    logger.info("Discovering capabilities from chaostoolkit-reliably")

    discovery = initialize_discovery_result(
        "chaostoolkit-reliably", __version__, "reliably"
    )
    discovery["activities"].extend(load_exported_activities())

    return discovery


@contextmanager
def attach_log_stream_handler(
    ctk_logger: logging.Logger, fmt: logging.Formatter
) -> Iterator[None]:
    run_handler = logging.StreamHandler(stream=STREAM_LOG)
    run_handler.setLevel(logging.DEBUG)
    run_handler.setFormatter(fmt)

    ctk_logger.addHandler(run_handler)

    yield

    ctk_logger.removeHandler(run_handler)
    run_handler.flush()
    run_handler.close()


###############################################################################
# Private functions
###############################################################################
def get_auth_info(
    configuration: Configuration = None, secrets: Secrets = None
) -> Dict[str, str]:
    reliably_host = None
    reliably_token = None

    reliably_host = secrets.get(
        "host", os.getenv("RELIABLY_HOST", RELIABLY_HOST)
    )

    reliably_token = secrets.get(
        "token", os.getenv("RELIABLY_TOKEN", reliably_token)
    )

    return {"host": reliably_host, "token": reliably_token}


def load_exported_activities() -> List[DiscoveredActivities]:
    """
    Extract metadata from actions, probes and tolerances
    exposed by this extension.
    """
    activities = []
    activities.extend(
        discover_activities(
            "chaosreliably.activities.http.tolerances", "tolerance"
        )
    )
    activities.extend(discover_probes("chaosreliably.activities.http.probes"))
    activities.extend(
        discover_activities(
            "chaosreliably.activities.tls.tolerances", "tolerance"
        )
    )
    activities.extend(discover_probes("chaosreliably.activities.tls.probes"))
    activities.extend(
        discover_activities(
            "chaosreliably.activities.gh.tolerances", "tolerance"
        )
    )
    activities.extend(discover_actions("chaosreliably.activities.gh.actions"))
    activities.extend(discover_probes("chaosreliably.activities.gh.probes"))
    activities.extend(discover_probes("chaosreliably.activities.load.probes"))
    activities.extend(discover_actions("chaosreliably.activities.load.actions"))
    activities.extend(discover_probes("chaosreliably.activities.slo.probes"))
    activities.extend(
        discover_activities(
            "chaosreliably.activities.slo.tolerances", "tolerance"
        )
    )
    activities.extend(
        discover_probes("chaosreliably.activities.safeguard.probes")
    )
    activities.extend(discover_probes("chaosreliably.activities.dns.probes"))
    activities.extend(
        discover_activities(
            "chaosreliably.activities.dns.tolerances", "tolerance"
        )
    )

    return activities


def parse_duration(duration: str) -> timedelta:
    value = int(duration[:-1])
    unit = duration[-1]

    if unit == "s":
        return timedelta(seconds=value)
    elif unit == "m":
        return timedelta(minutes=value)
    elif unit == "d":
        return timedelta(days=value)
    elif unit == "w":
        return timedelta(weeks=value)

    return timedelta(weeks=1)


def get_shared_state() -> Dict[str, Any]:
    with shared_state_lock:
        s = shared_state.copy()
        shared_state.clear()
        return s


def update_shared_state(state: Dict[str, Any]) -> None:
    with shared_state_lock:
        shared_state.clear()
        shared_state.update(state)
