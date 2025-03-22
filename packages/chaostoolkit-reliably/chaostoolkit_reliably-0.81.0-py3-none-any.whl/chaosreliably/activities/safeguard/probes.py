import logging
from typing import Optional

import httpx
from chaoslib.types import Configuration, Secrets

__all__ = ["call_endpoint"]
logger = logging.getLogger("chaostoolkit")


def call_endpoint(
    url: str,
    auth: Optional[str] = None,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> bool:
    headers = {}
    if auth:
        headers["Authorization"] = auth

    r = httpx.get(url, headers=headers)
    if r.status_code != 200:
        logger.critical("Safeguard endpoint returned a non 200 response")
        return False

    result = r.json()
    if not result.get("ok"):
        logger.critical(
            f"Safeguard endpoint returned with an error: {result['error']}"
        )
        return False

    return True
