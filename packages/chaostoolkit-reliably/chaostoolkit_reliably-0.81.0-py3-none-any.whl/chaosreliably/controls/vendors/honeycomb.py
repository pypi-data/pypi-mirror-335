import logging
import os
from typing import Any, Dict, Optional, cast

import httpx
from chaoslib.types import Configuration, Experiment, Journal, Secrets

__all__ = ["HoneycombVendorHandler"]
logger = logging.getLogger("chaostoolkit")


class HoneycombVendorHandler:
    @staticmethod
    def is_on() -> bool:
        return os.getenv("HONEYCOMB_API_KEY") is not None

    def started(
        self,
        experiment: Experiment,
        plan_id: Optional[str],
        execution_id: str,
        execution_url: str,
        configuration: Configuration,
        secrets: Secrets,
    ) -> None:
        self.experiment_marker = set_marker(
            message=experiment["title"],
            dataset_slug="__all__",
            url=execution_url,
            configuration=configuration,
            secrets=secrets,
        )

    def finished(
        self, journal: Journal, configuration: Configuration, secrets: Secrets
    ) -> None:
        if not self.experiment_marker:
            return None

        try:
            set_marker(
                message=self.experiment_marker["message"],
                url=self.experiment_marker["url"],
                marker_type=self.experiment_marker["type"],
                start_time=self.experiment_marker["start_time"],
                end_time=int(
                    self.experiment_marker["start_time"] + journal["duration"]
                ),
                marker_id=self.experiment_marker["id"],
            )
        finally:
            self.experiment_marker = None


###############################################################################
# Private
###############################################################################
def get_api_key(secrets: Secrets) -> Optional[str]:
    secrets = secrets or {}
    key = secrets.get("api_key", os.getenv("HONEYCOMB_API_KEY"))

    if not key:
        return None

    return cast(str, key)


def set_marker(
    message: str,
    marker_type: str = "reliably-plan",
    dataset_slug: str = "__all__",
    url: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    marker_id: Optional[str] = None,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> Optional[Dict[str, Any]]:
    api_key = get_api_key(secrets)
    if not api_key:
        return None

    h = httpx.Headers(
        {
            "X-Honeycomb-Team": api_key,
            "Accept": "application/json",
        }
    )

    with httpx.Client(
        http2=True, headers=h, base_url="https://api.honeycomb.io"
    ) as c:
        marker_url = f"/1/markers/{dataset_slug}"
        if marker_id:
            payload = {
                "message": message,
                "type": marker_type,
                "url": url,
                "start_time": start_time,
                "end_time": end_time,
            }
            logger.debug(f"Updating Honeycomb marker {marker_id}")
            marker_url = f"{marker_url}/{marker_id}"
            r = c.put(marker_url, json=payload)
        else:
            logger.debug("Setting Honeycomb marker")
            payload = {"message": message, "type": marker_type, "url": url}
            r = c.post(marker_url, json=payload)

        if r.status_code > 399:
            logger.debug(
                f"failed to create/update Honeycomb marker: {r.json()}"
            )
            return None

        marker = cast(Dict[str, Any], r.json())

        logger.debug(f"Honeycomb marker {marker['id']} set")

        return marker
