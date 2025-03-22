from typing import Any, Optional

from chaoslib.run import EventHandlerRegistry
from chaoslib.types import Configuration, Experiment, Secrets

from . import initialize, register, run_all

__all__ = ["configure_control"]


def configure_control(
    event_registry: EventHandlerRegistry,
    url: str,
    auth: Optional[str] = None,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    initialize(event_registry)
    register(url=url, auth=auth)


def before_experiment_control(
    context: Experiment,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    run_all(context, configuration, secrets)
