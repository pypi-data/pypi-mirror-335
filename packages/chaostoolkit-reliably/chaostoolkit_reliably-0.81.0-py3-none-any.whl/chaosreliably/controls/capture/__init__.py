import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, cast

from chaoslib.control import get_global_controls
from chaoslib.types import Configuration, Experiment, Journal, Secrets

logger = logging.getLogger("chaostoolkit")


def get_control_by_name(
    experiment: Experiment,
    name: str,
) -> Optional[Dict[str, Any]]:
    ctrls = get_global_controls()

    for ctrl in ctrls:
        if ctrl["name"] == name:
            return cast(Dict[str, Any], ctrl)

    ctrls = experiment.get("controls")
    if not ctrls:
        return None

    for ctrl in ctrls:
        if ctrl["name"] == name:
            return cast(Dict[str, Any], ctrl)

    return None


def start_capturing(
    experiment: Experiment, configuration: Configuration, secrets: Secrets
) -> None:
    from chaosreliably.controls.capture import slack

    try:
        slack.start_capturing(experiment, configuration, secrets)
    except Exception:
        logger.debug("Failed to start capturing slack messages", exc_info=True)


def stop_capturing(
    journal: Journal, configuration: Configuration, secrets: Secrets
) -> Optional[Dict[str, Any]]:
    from chaosreliably.controls.capture import slack

    slack_cap = None

    experiment = journal["experiment"]
    start = datetime.fromisoformat(journal["start"]).replace(
        tzinfo=timezone.utc
    )
    end = datetime.fromisoformat(journal["end"]).replace(tzinfo=timezone.utc)

    try:
        slack_cap = slack.stop_capturing(
            start, end, experiment, configuration, secrets
        )
    except Exception:
        logger.debug("Failed to stop capturing slack messages", exc_info=True)

    captures = {"slack": slack_cap}

    return captures
