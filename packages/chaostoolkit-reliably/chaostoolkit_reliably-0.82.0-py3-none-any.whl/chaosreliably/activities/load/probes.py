import json
import os.path
from typing import Optional, cast

from chaosreliably.activities.load import get_results

__all__ = [
    "load_test_result_field_should_be",
    "load_test_result_field_should_be_less_than",
    "load_test_result_field_should_be_greater_than",
    "verify_latency_percentile_from_load_test",
]


def load_test_result_field_should_be(
    result_filepath: str,
    field: str,
    expect: int,
    result_item_name: Optional[str] = None,
    pass_if_file_is_missing: bool = True,
) -> bool:
    """
    Reads a load test result and compares the field's value to the expected
    given value.

    If the load test runs against many endpoint, specify which one must be
    validated by setting the `result_item_name` to match the `name` field.

    Can only be used with the result from inject_gradual_traffic_into_endpoint
    """
    if not os.path.exists(result_filepath):
        return pass_if_file_is_missing

    with open(result_filepath) as f:
        data = json.load(f)

    if result_item_name:
        for item in data:
            if result_item_name == item["name"]:
                return cast(bool, item[field] == expect)
    else:
        return cast(bool, data[0][field] == int(expect))

    return False


def load_test_result_field_should_be_less_than(
    result_filepath: str,
    field: str,
    expect: int,
    result_item_name: Optional[str] = None,
    pass_if_file_is_missing: bool = True,
) -> bool:
    """
    Reads a load test result and compares the field's value to less than the
    expected given value.

    If the load test runs against many endpoint, specify which one must be
    validated by setting the `result_item_name` to match the `name` field.

    Can only be used with the result from inject_gradual_traffic_into_endpoint
    """
    if not os.path.exists(result_filepath):
        return pass_if_file_is_missing

    with open(result_filepath) as f:
        data = json.load(f)

    if result_item_name:
        for item in data:
            if result_item_name == item["name"]:
                return cast(bool, item[field] < expect)
    else:
        return cast(bool, data[0][field] < int(expect))

    return False


def load_test_result_field_should_be_greater_than(
    result_filepath: str,
    field: str,
    expect: int,
    result_item_name: Optional[str] = None,
    pass_if_file_is_missing: bool = True,
) -> bool:
    """
    Reads a load test result and compares the field's value to greater than the
    expected given value.

    If the load test runs against many endpoint, specify which one must be
    validated by setting the `result_item_name` to match the `name` field.

    Can only be used with the result from inject_gradual_traffic_into_endpoint
    """
    if not os.path.exists(result_filepath):
        return pass_if_file_is_missing

    with open(result_filepath) as f:
        data = json.load(f)

    if result_item_name:
        for item in data:
            if result_item_name == item["name"]:
                return cast(bool, item[field] > expect)
    else:
        return cast(bool, data[0][field] > int(expect))

    return False


def verify_latency_percentile_from_load_test(
    lower_than: float, percentile: str = "p99", test_name: str = "load test"
) -> bool:
    """
    Verify that the percentile of a load test result, generated with the
    `run_load_test` action, is lower than the expected value.
    """
    results = get_results("test_name")
    if not results:
        return False

    p = results.get("latencyPercentilesSuccessful", {}).get(percentile)
    if not p:
        return False

    return cast(float, p) <= lower_than
