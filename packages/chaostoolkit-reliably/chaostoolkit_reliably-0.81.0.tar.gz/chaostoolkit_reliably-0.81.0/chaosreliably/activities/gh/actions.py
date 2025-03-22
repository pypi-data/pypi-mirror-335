import logging
import random
import re
from typing import Any, Dict, Optional, cast

import httpx
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Configuration, Secrets

from chaosreliably.activities.gh import get_gh_token, get_period

__all__ = ["cancel_workflow_run"]
logger = logging.getLogger("chaostoolkit")


def cancel_workflow_run(
    repo: str,
    at_random: bool = False,
    commit_message_pattern: Optional[str] = None,
    actor: Optional[str] = None,
    branch: str = "main",
    event: str = "push",
    status: str = "in_progress",
    window: str = "5d",
    workflow_id: Optional[str] = None,
    workflow_run_id: Optional[str] = None,
    exclude_pull_requests: bool = False,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Cancels a GitHub Workflow run.

    The target run is chosen from the list of workflow runs matching the
    given parameters.

    To refine the choice, you can set `commit_message_pattern` which is a
    regex matching the commit message that triggered the event.

    If you set `at_random`, a run will be picked from the matching list
    randomly. otherwise, the first match will be used.

    You may also filter down by `workflow_id` to ensure only runs of a specific
    workflow are considered.

    Finally, if you know the `workflow_run_id` you may directly target it.

    See the parameters meaning and values at:
    https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#list-workflow-runs-for-a-repository
    """
    gh_token = get_gh_token(secrets)
    start, _ = get_period(window)
    api_url = f"https://api.github.com/repos/{repo}/actions/runs"

    if not workflow_run_id:
        params = {
            "branch": branch,
            "event": event,
            "created": ">" + start.strftime("%Y-%m-%d"),
            "exclude_pull_requests": exclude_pull_requests,
            "page": 1,
        }

        # until they fix https://github.com/orgs/community/discussions/53266
        # if status:
        #    params["status"] = status

        if actor:
            params["actor"] = actor

        logger.debug(f"Searching for a potential run to cancel with: {params}")

        r = httpx.get(
            api_url,
            headers={
                "accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Authorization": f"Bearer {gh_token}",
            },
            params=params,  # type: ignore
        )

        if r.status_code > 399:
            logger.debug(f"failed to list runs for repo '{repo}': {r.json()}")
            raise ActivityFailed(f"failed to retrieve PR for repo '{repo}'")

        result = r.json()
        runs = result.get("workflow_runs", [])

        # until GH fixes https://github.com/orgs/community/discussions/53266
        runs = list(filter(lambda r: r["status"] == status, runs))

        count = len(runs)

        logger.debug(f"Found {count} GitHub workflow runs matching your query")

        if count == 0:
            raise ActivityFailed(
                "Failed to locate a GitHub Worlflow run matching your query"
            )

        target = None

        if workflow_id:
            runs = list(filter(lambda r: r["workflow_id"] == workflow_id, runs))
            index = 0
            if at_random:
                index = random.randint(0, count - 1)  # nosec
            target = runs[index]
        else:
            if commit_message_pattern is not None:
                pattern = re.compile(commit_message_pattern)

                for run in runs:
                    m = run["head_commit"]["message"]
                    if pattern:
                        if pattern.match(m) is not None:
                            target = run
                            break
            else:
                index = 0
                if at_random:
                    index = random.randint(0, count - 1)  # nosec
                target = runs[index]

        if not target:
            raise ActivityFailed(
                "Failed to locate a GitHub Worlflow run matching your filters"
            )

        run_id = target["id"]
    else:
        run_id = workflow_run_id

    api_url = f"{api_url}/{run_id}/cancel"

    r = httpx.post(
        api_url,
        headers={
            "accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Bearer {gh_token}",
        },
    )

    if r.status_code > 399:
        logger.debug(f"failed to cancel run {run_id} in '{repo}': {r.json()}")
        raise ActivityFailed(f"failed to cancel run {run_id} in '{repo}'")

    logger.debug(f"Cancelled workflow run {run_id}")

    return cast(Dict[str, Any], target)
