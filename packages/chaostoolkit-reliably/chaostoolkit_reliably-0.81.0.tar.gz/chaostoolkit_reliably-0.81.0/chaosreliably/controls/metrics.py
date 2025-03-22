import logging
import threading
import time
from copy import deepcopy
from datetime import datetime, timezone
from typing import List, Optional

from chaoslib.activity import run_activity
from chaoslib.exceptions import ActivityFailed
from chaoslib.hypothesis import within_tolerance
from chaoslib.run import EventHandlerRegistry, RunEventHandler
from chaoslib.types import (
    Configuration,
    Experiment,
    Journal,
    Probe,
    Schedule,
    Secrets,
    Settings,
)

from chaosreliably.controls import find_extension_by_name, global_lock

__all__ = ["configure_control"]
logger = logging.getLogger("chaostoolkit")


class MetricsHandler(RunEventHandler):  # type: ignore
    def __init__(
        self,
        probes: List[Probe],
        frequency: int = 30,
        recovery_timeout: int = 600,
        continue_until_recovered_or_timedout: bool = False,
    ) -> None:
        RunEventHandler.__init__(self)

        self.probes = probes
        self.frequency = frequency
        self.recovery_timeout = recovery_timeout
        self.block_execution = continue_until_recovered_or_timedout

        self.should_exit = threading.Event()
        self._t = None

    def running(
        self,
        experiment: Experiment,
        journal: Journal,
        configuration: Configuration,
        secrets: Secrets,
        schedule: Schedule,
        settings: Settings,
    ) -> None:
        logger.debug("Starting metrics measurement in background")
        self._t = threading.Thread(  # type: ignore
            None,
            compute_metrics,
            kwargs=dict(
                state=journal,
                should_exit=self.should_exit,
                probes=self.probes,
                frequency=self.frequency,
                recovery_timeout=self.recovery_timeout,
                block_execution=self.block_execution,
                configuration=configuration,
                secrets=secrets,
            ),
            daemon=True,
        )
        self._t.start()  # type: ignore

    def finish(self, journal: Journal) -> None:
        if self._t is not None and self._t.is_alive():
            try:
                global_lock.acquire()
                self.should_exit.set()
                logger.debug("Waiting for metrics measurement to complete")
                self._t.join(timeout=self.frequency + 2)
            finally:
                global_lock.release()
                self._t = None


def configure_control(
    event_registry: EventHandlerRegistry,
    probes: Optional[List[Probe]] = None,
    frequency: int = 30,
    recovery_timeout: int = 600,
    block_execution: bool = False,
    configuration: Configuration = None,
    secrets: Secrets = None,
    settings: Settings = None,
    experiment: Experiment = None,
) -> None:
    if not probes:
        probes = experiment.get("steady-state-hypothesis", {}).get("probes", [])
        probes = deepcopy(probes)

    event_registry.register(
        MetricsHandler(
            probes, frequency, recovery_timeout, block_execution  # type: ignore
        )
    )


###############################################################################
# Private functions
###############################################################################
def compute_metrics(
    state: Journal,
    should_exit: threading.Event,
    probes: List[Probe],
    frequency: int = 30,
    recovery_timeout: int = 600,
    block_execution: bool = False,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> None:
    experiment = state["experiment"]
    extension = find_extension_by_name(experiment, "dora")
    if not extension:
        logger.debug("Failed to find the dora extension block")
        return

    detection_time = None
    recovery_time = None
    went_over_timeout = None

    execution_terminated = False

    try:
        while True:
            all_fine_this_iteration = True
            for probe in probes:
                if should_exit.is_set():
                    if not block_execution:
                        logger.debug("Execution is complete, let's leave")
                        return
                    elif not execution_terminated:
                        execution_terminated = True
                        logger.debug(
                            "Execution is complete, but checking system for "
                            f"up to to {recovery_timeout}s"
                        )

                try:
                    result = run_activity(probe, configuration, secrets)
                except ActivityFailed:
                    all_fine_this_iteration = False
                    if detection_time is None:
                        logger.debug("System state changed and is not healthy")
                        detection_time = get_utc_now()
                except Exception:
                    logger.debug(
                        f"Metrics probe '{probe['name']}' failed", exc_info=True
                    )
                else:
                    tolerance = probe.get("tolerance")
                    checked = within_tolerance(
                        tolerance,
                        result,
                        configuration=configuration,
                        secrets=secrets,
                    )
                    if not checked:
                        all_fine_this_iteration = False
                        if detection_time is None:
                            logger.debug(
                                "System state changed and is not healthy"
                            )
                            detection_time = get_utc_now()

            if all_fine_this_iteration and detection_time is not None:
                recovery_time = get_utc_now()
                logger.debug("System state changed and is healthy again")
                break

            od = get_outage_duration(detection_time, get_utc_now())
            if od and od > recovery_timeout:
                logger.info(
                    "System took longer than expected to come back to health"
                )
                went_over_timeout = True
                break

            time.sleep(frequency)
    finally:
        duration = get_outage_duration(detection_time, recovery_time)
        if (
            duration is not None
            and (detection_time and recovery_time)
            and duration < recovery_timeout
        ):
            went_over_timeout = False

        detection = detection_time.isoformat() if detection_time else None
        recovery = recovery_time.isoformat() if recovery_time else None

        extension["metrics"] = {
            "detection_time": detection,
            "recovery_time": recovery,
            "outage_duration": duration,
            "went_over_timeout": went_over_timeout,
            "timeout": recovery_timeout,
        }


def get_utc_now() -> datetime:
    return datetime.now().astimezone(tz=timezone.utc)


def get_outage_duration(
    start: Optional[datetime], end: Optional[datetime]
) -> Optional[float]:
    if not start or not end:
        return None

    return (end - start).total_seconds()
