import json
import logging
import math
import os
from typing import Any, Optional

from locust import HttpUser, LoadTestShape, TaskSet, between, task


def is_oltp_enabled() -> bool:
    if HAS_OLTP:
        enable_oltp = os.getenv("RELIABLY_LOCUST_ENABLE_OLTP") or ""
        logging.info(f"OLTP flag: '{enable_oltp}'")

        if enable_oltp.lower() in (
            "1",
            "t",
            "true",
        ):
            logging.info("OLTP tracing enabled from Locust file")
            return True

    logging.info("OLTP tracing disabled from Locust file")
    return False


try:
    # these will be available when `chaostoolkit-opentracing` is also
    # installed
    from chaostracing import oltp
    from opentelemetry import baggage, context
    from opentelemetry.propagate import extract

    logging.info("OLTP dependencies from locust file were imported")

    HAS_OLTP = True

    if is_oltp_enabled():
        logging.info("Configuring OLTP tracer and instrumentations")
        oltp.configure_traces(configuration={})
        oltp.configure_instrumentations(trace_request=True, trace_urllib3=True)

        current_context = extract(
            json.loads(os.getenv("OTEL_RELIABLY_CONTEXT") or "{}")
        )


except ImportError:
    logging.info("Failed to load OLTP dependencies from locust file")
    HAS_OLTP = False


class UserTasks(TaskSet):
    @task
    def get_root(self) -> None:
        endpoint = os.getenv("RELIABLY_LOCUST_ENDPOINT")
        headers = {}

        bearer_token = os.getenv("RELIABLY_LOCUST_ENDPOINT_TOKEN", "").strip()
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        self.client.get(endpoint, headers=headers)


class WebsiteUser(HttpUser):
    wait_time = between(1, 10)
    tasks = [UserTasks]

    def on_start(self) -> None:
        if is_oltp_enabled():
            ctx = baggage.set_baggage(
                "synthetic_request", "true", current_context
            )
            context.attach(ctx)


class StepLoadShape(LoadTestShape):
    step_time = int(os.getenv("RELIABLY_LOCUST_STEP_TIME", 1))
    step_load = int(os.getenv("RELIABLY_LOCUST_STEP_LOAD", 1))
    spawn_rate = int(os.getenv("RELIABLY_LOCUST_SPAWN_RATE", 1))
    time_limit = int(os.getenv("RELIABLY_LOCUST_TIME_LIMIT", 5))

    def tick(self) -> Optional[Any]:
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        current_step = math.floor(run_time / self.step_time) + 1
        return (current_step * self.step_load, self.spawn_rate)
