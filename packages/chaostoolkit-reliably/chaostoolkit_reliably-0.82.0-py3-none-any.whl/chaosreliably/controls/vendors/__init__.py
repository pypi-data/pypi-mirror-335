import logging

from chaosreliably.controls.vendors.honeycomb import HoneycombVendorHandler
from chaosreliably.controls.vendors.otel import OTELVendorHandler

__all__ = ["apply_vendors", "register_vendors", "unregister_vendors"]
logger = logging.getLogger("chaostoolkit")
VENDORS = []


def register_vendors() -> None:
    if OTELVendorHandler.is_on():
        VENDORS.append(OTELVendorHandler())

    if HoneycombVendorHandler.is_on():
        VENDORS.append(HoneycombVendorHandler())  # type: ignore


def unregister_vendors() -> None:
    VENDORS.clear()


def apply_vendors(method: str, **kwargs) -> None:  # type: ignore
    logger.debug(f"Apply '{method}' on vendors")
    for v in VENDORS:
        logger.debug(f"Processing vendor {v.__class__.__name__}")
        if method == "started":
            try:
                v.started(**kwargs)
            except Exception:
                logger.debug(
                    "failed to apply 'started' method on vendor "
                    f"class {v.__class__.__name__}",
                    exc_info=True,
                )
        elif method == "finished":
            try:
                v.finished(**kwargs)
            except Exception:
                logger.debug(
                    "failed to apply 'finished' method on vendor "
                    f"class {v.__class__.__name__}",
                    exc_info=True,
                )
