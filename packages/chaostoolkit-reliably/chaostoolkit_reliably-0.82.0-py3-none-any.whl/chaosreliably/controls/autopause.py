import logging
import os
import secrets
from typing import Any, Dict, Union

from chaoslib.types import Activity, Configuration, Experiment, Secrets

from chaosreliably.types import AutoPause

__all__ = ["configure_control"]
logger = logging.getLogger("chaostoolkit")


def configure_control(
    experiment: Experiment,
    autopause: AutoPause,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    logger.debug("Configure Reliably's autopause control")

    amend_experiment_for_autopauses(experiment, autopause)


###############################################################################
# Private functions
###############################################################################
def amend_experiment_for_autopauses(
    experiment: Experiment, autopause: AutoPause
) -> None:
    method = experiment.get("method")
    if method and "method" in autopause:
        p = autopause["method"]
        if is_enabled(p.get("actions", {}).get("enabled")):
            pause_duration = get_duration(
                p.get("actions", {}).get("pause_duration", 0)
            )

            activities = method[:]
            for index, activity in enumerate(activities):
                index = method.index(activity)
                if activity["type"] == "action":
                    method.insert(index + 1, make_pause(pause_duration))

        if is_enabled(p.get("probes", {}).get("enabled")):
            pause_duration = get_duration(
                p.get("probes", {}).get("pause_duration", 0)
            )

            activities = method[:]
            for index, activity in enumerate(activities):
                index = method.index(activity)
                if activity["type"] == "probe":
                    method.insert(index + 1, make_pause(pause_duration))

    ssh_probes = experiment.get("steady-state-hypothesis", {}).get("probes")
    if ssh_probes and "steady-state-hypothesis" in autopause:
        p = autopause["steady-state-hypothesis"]
        if is_enabled(p["enabled"]):
            pause_duration = get_duration(p.get("pause_duration", 0))

            activities = ssh_probes[:]
            for index, activity in enumerate(activities):
                index = ssh_probes.index(activity)
                ssh_probes.insert(index + 1, make_pause(pause_duration))

    rollbacks = experiment.get("rollbacks")
    if rollbacks and "rollbacks" in autopause:
        p = autopause["rollbacks"]
        if is_enabled(p["enabled"]):
            pause_duration = get_duration(p.get("pause_duration", 0))

            activities = rollbacks[:]
            for index, activity in enumerate(activities):
                index = rollbacks.index(activity)
                rollbacks.insert(index + 1, make_pause(pause_duration))


def make_pause(pause_duration: float = 0) -> Activity:
    return {
        "type": "action",
        "name": f"reliably-autopause-{secrets.token_hex(4)}",
        "provider": {
            "type": "python",
            "module": "chaosreliably.activities.pauses",
            "func": "pause_execution",
            "arguments": {"duration": pause_duration},
        },
    }


def is_enabled(value: Union[bool, Dict[str, str]]) -> bool:
    if not value:
        return False

    if isinstance(value, bool):
        return value

    if value.get("type") == "env":
        if os.getenv(value["key"], value.get("default", "")) not in (
            "",
            "f",
            "false",
            "0",
            "False",
        ):
            return True

        return False

    return False


def get_duration(value: Union[float, int, Dict[str, str]]) -> float:
    if not value:
        return 0.0

    if isinstance(value, (float, int)):
        return float(value)

    if value.get("type") == "env":
        return float(os.getenv(value["key"], value.get("default", "0"))) or 0.0

    return 0.0
