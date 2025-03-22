import json
import os
import re
from typing import Any, Dict, List, cast

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Configuration, Secrets
from slo_generator.compute import compute

__all__ = ["compute_slo"]


def compute_slo(
    slo: Dict[str, Any],
    config: Dict[str, Any],
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> List[Dict[str, Any]]:
    """
    Computes the given SLO and return a list of outcomes for each error budget
    policies in the `config`.

    This is a wrapper around https://github.com/google/slo-generator so all
    of its documentation applies for the definition of the `slo` and
    `config` objects. The former contains the the SLO description while the
    latter describes where to source SLIs from and the error budget policies.

    The most notable difference is that we disable any exporters so there
    is no need to define them in your objects.
    """
    s_config = replace_vars(slo)
    g_config = replace_vars(config)

    # prevent any export
    g_config.pop("default_exporters", None)
    g_config.pop("exporters", None)

    return cast(
        List[Dict[str, Any]],
        compute(
            s_config,
            g_config,
            client=None,
            do_export=False,
        ),
    )


###############################################################################
# Private function
###############################################################################


# drawn from slo-generator to prevent: json -> dict -> yaml -> dict
def replace_vars(
    config: Dict[str, Any], ctx: os._Environ = os.environ  # type: ignore
) -> Dict[str, Any]:
    content = json.dumps(config)

    pattern = re.compile(r".*?\${(\w+)}.*?")
    match = pattern.findall(content)

    if match:
        full_value = content
        for var in match:
            try:
                full_value = full_value.replace(f"${{{var}}}", ctx[var])
            except KeyError:
                raise ActivityFailed(
                    f'Environment variable "{var}" should be set.',
                )

        content = full_value

    return cast(Dict[str, Any], json.loads(content))
