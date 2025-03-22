import logging
import threading

logger = logging.getLogger("chaostoolkit")

__all__ = ["pause_execution"]

CURRENT_PAUSE = threading.Event()


def pause_execution(
    duration: int = 0,
    username: str = "",
    user_id: str = "",
) -> None:
    """
    Pause the execution of the experiment until the resume state has been
    received.
    """
    m = "Pausing activity"
    if duration:
        m = f"{m} for {duration}s or"
    m = f"{m} until the execution is resumed"
    logger.info(m)

    if CURRENT_PAUSE.wait(duration or None) is False:
        logger.info("Resuming execution...")


###############################################################################
# Private functions
###############################################################################
def reset() -> None:
    global CURRENT_PAUSE
    CURRENT_PAUSE.set()
    CURRENT_PAUSE.clear()
