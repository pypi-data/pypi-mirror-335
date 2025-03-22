import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, cast

from chaoslib.types import Configuration, Experiment, Secrets
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from chaosreliably.controls.capture import get_control_by_name

__all__ = ["start_capturing", "stop_capturing"]
logger = logging.getLogger("chaostoolkit")


def start_capturing(
    experiment: Experiment, configuration: Configuration, secrets: Secrets
) -> None:
    pass


def stop_capturing(
    start: datetime,
    end: datetime,
    experiment: Experiment,
    configuration: Configuration,
    secrets: Secrets,
) -> Optional[Dict[str, Any]]:
    ctrl = get_control_by_name(experiment, "reliably-integration-slack")
    if not ctrl:
        logger.debug("No slack integration configured, nothing to capture")
        return None

    args = ctrl["provider"].get("arguments", {})

    channel = args.get("channel", os.getenv("SLACK_CHANNEL"))
    limit = args.get("limit", 300)
    past = int((end - start).total_seconds() / 60) + 1
    include_metadata = True

    context = {"channels": [], "users": {}}  # type: ignore

    client = get_client(secrets)

    logger.debug(
        f"Trying to capture the last {past}mn of the Slack channel {channel}"
    )

    channel_id = get_channel_id(client, channel)
    if not channel_id:
        logger.debug("Missing channel to initiate slack capture")
        return context

    oldest = datetime.now().astimezone(tz=timezone.utc) - timedelta(
        minutes=past
    )

    get_channel_history(
        client,
        context,
        channel,
        channel_id,
        oldest,
        limit,
        past,
        include_metadata,
    )

    c = configuration or {}
    capture_channel_pattern = c.get("reliably_capture_slack_channel_pattern")
    if capture_channel_pattern:
        for c in list_channels(client, capture_channel_pattern):
            get_channel_history(
                client,
                context,
                c["name"],
                c["id"],
                oldest,
                limit,
                past,
                include_metadata,
                remove_ctk_thread=False,
            )

    return context


###############################################################################
# Private functions
###############################################################################
def get_client(secrets: Secrets) -> WebClient:
    secrets = secrets or {}
    slack_token = secrets.get("slack", {}).get(
        "token", os.getenv("SLACK_BOT_TOKEN")
    )
    client = WebClient(token=slack_token)
    return client


def get_channel_id(client: WebClient, channel: str) -> Optional[str]:
    channel = channel.lstrip("#").strip()

    cursor = None
    while True:
        result = client.conversations_list(exclude_archived=True, cursor=cursor)

        for c in result["channels"]:
            if c["name"] == channel:
                return cast(str, c["id"])

        cursor = result.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    return None


def get_channel_history(
    client: WebClient,
    context: Dict[str, Any],
    channel: str,
    channel_id: str,
    oldest: datetime,
    limit: int = 100,
    past: int = 15,
    include_metadata: bool = False,
    remove_ctk_thread: bool = True,
) -> None:
    """
    Fetches the history of a channel up to a certain limit of messages or
    for the past minutes.

    By default no more than 100 messages in the last 15 minutes.
    """
    messages = []
    ts = oldest.timestamp()

    try:
        logger.debug(f"Capture Slack messages from {channel}")

        logger.debug(
            f"Fetching the last {limit} messages for the past {past}mn "
            f"[{oldest}] from channel {channel} [{channel_id}]"
        )
        result = client.conversations_history(
            channel=channel_id,
            inclusive=True,
            limit=limit,
            include_metadata=include_metadata,
            oldest=str(ts),
        )
        messages.extend(result["messages"])

        while (result["ok"] is True) and (result["has_more"] is True):
            cursor = result["response_metadata"]["next_cursor"]
            result = client.conversations_history(
                channel=channel_id,
                cursor=cursor,
                inclusive=True,
                limit=limit,
                include_metadata=include_metadata,
                oldest=str(ts),
            )

            messages.extend(result["messages"])

    except SlackApiError as e:
        logger.error(f"Failed to retrieve Slack channel history: {e}")

    # collect user information
    threads = {}
    users = context["users"]
    for m in messages:
        thread_ts = m.get("thread_ts")
        if thread_ts:
            threads[thread_ts] = get_thread_history(
                client,
                channel_id,
                thread_ts,
                limit,
                include_metadata,
            )

        if m.get("bot_id") is not None:
            continue

        user_id = m.get("user")
        if not user_id:
            continue

        if user_id not in users:
            users[user_id] = get_user_info(client, user_id)

    if remove_ctk_thread:
        remove_bot_threads(threads)

    context["channels"].append(
        {
            "id": channel_id,
            "name": channel,
            "conversation": messages,
            "threads": threads,
        }
    )


def get_user_info(client: WebClient, user_id: str) -> Dict[str, str]:
    result = client.users_info(
        user=user_id,
    )

    u = result["user"]

    return {
        "id": u["id"],
        "name": u["name"],
        "real_name": u["real_name"],
        "display_name": u["profile"]["display_name_normalized"],
        "image": u["profile"]["image_24"],
    }


def get_thread_history(
    client: WebClient,
    channel_id: str,
    thread_ts: float,
    limit: int = 100,
    include_metadata: bool = False,
) -> List[Dict[str, Any]]:
    messages = []
    try:
        result = client.conversations_replies(
            channel=channel_id,
            ts=str(thread_ts),
            inclusive=True,
            limit=100,
            include_metadata=include_metadata,
        )
        messages.extend(result["messages"])

        while (result["ok"] is True) and (result["has_more"] is True):
            cursor = result["response_metadata"]["next_cursor"]
            result = client.conversations_replies(
                channel=channel_id,
                ts=str(thread_ts),
                cursor=cursor,
                inclusive=True,
                limit=limit,
                include_metadata=include_metadata,
            )

            messages.extend(result["messages"])

    except SlackApiError as e:
        logger.error(f"Failed to retrieve Slack thread history: {e}")

    return messages


def remove_bot_threads(threads: Dict[str, Any]) -> None:
    for ts, entry in threads.items():
        for t in entry:
            # flaky heuristic
            bot_id = t.get("bot_id")
            t_type = t.get("type")
            t_text = t.get("text", "")
            if (
                bot_id
                and t_type == "message"
                and t_text.startswith("Experiment is ")
            ):
                threads.pop(ts, None)
                return None

    return None


def list_channels(client: WebClient, pattern: str) -> List[Dict[str, str]]:
    p = re.compile(pattern.lstrip("#"))

    channels = []
    try:
        cursor = None
        while True:
            result = client.conversations_list(
                exclude_archived=True,
                types="public_channel",
                cursor=cursor,
            )
            channels.extend(
                [
                    {"name": c["name"], "id": c["id"]}
                    for c in result["channels"]
                    if p.match(c["name"])
                ]
            )

            cursor = result["response_metadata"]["next_cursor"]
            if not cursor:
                break

    except SlackApiError as e:
        logger.error(f"Failed to list Slack channels: {e}")

    return channels
