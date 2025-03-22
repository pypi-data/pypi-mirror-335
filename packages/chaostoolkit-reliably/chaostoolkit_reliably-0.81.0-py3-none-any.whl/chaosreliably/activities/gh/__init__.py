import os
from datetime import datetime
from typing import Tuple, cast

from chaoslib.exceptions import InvalidActivity
from chaoslib.types import Secrets

from chaosreliably import parse_duration


def get_gh_token(secrets: Secrets) -> str:
    secrets = secrets or {}
    gh_token = secrets.get("github", {}).get("token")
    gh_token = os.getenv("GITHUB_TOKEN", gh_token)

    if not gh_token:
        raise InvalidActivity(
            "GitHub activity requires a github token as a secret or via the "
            "GITHUB_TOKEN environment variable"
        )

    return cast(str, gh_token)


def get_period(window: str) -> Tuple[datetime, datetime]:
    duration = parse_duration(window)
    today = datetime.today()
    start_period = today - duration

    return (start_period, today)
