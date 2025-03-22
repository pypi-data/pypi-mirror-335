import json
import logging
import os
import os.path
import pkgutil
import shutil
import subprocess  # nosec
import tempfile
from typing import Any, Dict, Optional, cast
from urllib.parse import urlparse

from chaoslib import decode_bytes
from chaoslib.exceptions import ActivityFailed, InvalidActivity
from chaoslib.types import Configuration, Secrets

from chaosreliably.activities.load import store_results

try:
    from opentelemetry.context import get_current
    from opentelemetry.propagate import inject

    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False

__all__ = ["inject_gradual_traffic_into_endpoint", "run_load_test"]
logger = logging.getLogger("chaostoolkit")


def inject_gradual_traffic_into_endpoint(
    endpoint: str,
    step_duration: int = 5,
    step_additional_vu: int = 1,
    vu_per_second_rate: int = 1,
    test_duration: int = 30,
    results_json_filepath: Optional[str] = None,
    enable_opentracing: bool = False,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Load traffic into the given `endpoint`. Uses an approach that creates an
    incremental load into the endpoint rather than swarming it. The point of
    this action is to ensure your endpoint is active while you perform another
    action. This you means you likely want to run this action in the
    `background`.

    You may set a bearer token if your application uses one to authenticate.
    Pass `test_bearer_token` as a secret key in the `secrets` payload.

    This action return a dictionary payload of the load test results.
    """
    u = urlparse(endpoint)
    if not u.scheme or not u.netloc:
        raise InvalidActivity("endpoint must be a proper url")

    script = pkgutil.get_data(
        "chaosreliably", "activities/load/scripts/step_load_test.py"
    )
    if not script:
        raise ActivityFailed("failed to locate load-test script")

    locust_path = shutil.which("locust")
    if not locust_path:
        raise ActivityFailed("missing load test dependency")

    env = {
        "RELIABLY_LOCUST_ENDPOINT": endpoint,
        "RELIABLY_LOCUST_STEP_TIME": str(step_duration),
        "RELIABLY_LOCUST_STEP_LOAD": str(step_additional_vu),
        "RELIABLY_LOCUST_SPAWN_RATE": str(vu_per_second_rate),
        "RELIABLY_LOCUST_TIME_LIMIT": str(test_duration),
    }

    secrets = secrets or {}
    test_bearer_token = secrets.get("test_bearer_token")
    if test_bearer_token:
        env["RELIABLY_LOCUST_ENDPOINT_TOKEN"] = test_bearer_token

    if enable_opentracing and HAS_OTEL:
        c = configuration
        env["RELIABLY_LOCUST_ENABLE_OLTP"] = "true"
        env["OTEL_VENDOR"] = (
            c.get("otel_vendor", os.getenv("OTEL_VENDOR")) or ""
        )
        env["CHAOSTOOLKIT_OTEL_GCP_SA"] = (
            c.get(
                "otel_gcp_service_account",
                os.getenv("CHAOSTOOLKIT_OTEL_GCP_SA"),
            )
            or ""
        )
        env["CHAOSTOOLKIT_OTEL_GCP_PROJECT_ID"] = (
            c.get(
                "otel_gcp_project_id",
                os.getenv("CHAOSTOOLKIT_OTEL_GCP_PROJECT_ID"),
            )
            or ""
        )
        env["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = (
            os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT") or ""
        )
        env["OTEL_EXPORTER_OTLP_TRACES_HEADERS"] = (
            os.getenv("OTEL_EXPORTER_OTLP_TRACES_HEADERS") or ""
        )

        trace_context = {}  # type: ignore
        inject(trace_context, get_current())
        env["OTEL_RELIABLY_CONTEXT"] = json.dumps(trace_context)

    results = {}

    with tempfile.TemporaryDirectory() as d:
        locustfile_path = os.path.join(d, "locustfile.py")
        with open(locustfile_path, mode="wb") as f:
            f.write(script)

        cmd = [
            locust_path,
            "--host",
            "localhost:8089",
            "--locustfile",
            locustfile_path,
            "--json",
            "--headless",
            "--loglevel",
            "INFO",
            "--exit-code-on-error",
            "0",
        ]
        try:
            p = subprocess.run(  # nosec
                cmd,
                timeout=test_duration + 60,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                shell=False,
                cwd=d,
            )
            os.remove(locustfile_path)
        except KeyboardInterrupt:
            logger.debug(
                "Caught SIGINT signal while running locust. Ignoring it."
            )
        except subprocess.TimeoutExpired:
            raise ActivityFailed("load test took too long to complete")
        else:
            stdout = decode_bytes(p.stdout)
            stderr = decode_bytes(p.stderr)

            logger.debug(f"locust exit code: {p.returncode}")
            logger.debug(f"locust stderr: {stderr}")

            if results_json_filepath:
                with open(results_json_filepath, "w") as f:
                    f.write(stdout)

            try:
                results = json.loads(stdout)
            except json.decoder.JSONDecodeError:
                logger.error("failed to parse locust results")

    return cast(Dict[str, Any], results)


def run_load_test(
    url: str,
    duration: int = 30,
    qps: int = 5,
    connect_to: str = "",
    insecure: bool = False,
    host: str = "None",
    method: str = "GET",
    headers: str = "",
    body: str = "",
    content_type: str = "",
    test_name: str = "load test",
) -> Dict[str, Any]:
    """
    Run a load test against the given URL.

    This action uses [oha](https://github.com/hatoo/oha) rather than Locust.
    It produces a different set of results. Please make sure to have it
    installed in your `PATH`.

    Set the `test_name` so you can use one of the probe against this action
    to retrieve its results.

    Use the following parameters to adjust the default:

    * `connect_to` pass a column seperated list of addresses `host:port`
       to connect to instead of the DNS values for the domain
    * `insecure` set to False to communicate with a non-secure TLS server
    * `host` set a different `HOST` header
    * `method` the HTTP method to use
    * `headers` a comma-separated list of headers "foo: bar,other: thing"
    * `body` the content of the request to send if any
    * `content_type` the content-type of the request to send if any

    """
    oha_path = shutil.which("oha")
    if not oha_path:
        raise ActivityFailed("missing load test dependency")

    results = {}  # Dict[str, Any]

    cmd = [
        oha_path,
        "--json",
        "--disable-color",
        "--no-tui",
        "--stats-success-breakdown",
        "--latency-correction",
        "-z",
        f"{duration}s",
        "-q",
        f"{qps}",
    ]

    proxy = os.environ.get("OHA_HTTPS_PROXY", os.environ.get("OHA_HTTP_PROXY"))
    if proxy:
        logger.debug(f"Using proxy {proxy} on requests from oha")
        cmd.extend(["-x", proxy])

    if connect_to:
        cmd.extend(["--connect-to", connect_to])

    if insecure:
        cmd.extend(
            [
                "--insecure",
            ]
        )

    if host:
        cmd.extend(["--host", host])

    if method:
        cmd.extend(["--method", method])

    if headers:
        for pair in headers.split(","):
            cmd.extend(["-H", pair])

    if body:
        cmd.extend(["--body", body])
    if content_type:
        cmd.extend(["-T", content_type])

    cmd.append(url)

    env = {}  # type: Dict[str, str]
    try:
        logger.debug(f"Running command {cmd}")
        p = subprocess.run(  # nosec
            cmd,
            timeout=duration + 60,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            shell=False,
        )
    except KeyboardInterrupt:
        logger.debug(
            "Caught SIGINT signal while running load test. Ignoring it."
        )
    except subprocess.TimeoutExpired:
        raise ActivityFailed("load test took too long to complete")
    else:
        stdout = decode_bytes(p.stdout)
        stderr = decode_bytes(p.stderr)

        logger.debug(f"oha exit code: {p.returncode}")
        logger.debug(f"oha stderr: {stderr}")

        try:
            results = cast(Dict[str, Any], json.loads(stdout))
        except json.decoder.JSONDecodeError:
            logger.error("failed to parse oha results")
            raise ActivityFailed("failed to parse oha results")

    if test_name:
        store_results(test_name, results)

    return results
