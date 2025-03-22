from typing import List

__all__ = [
    "dns_response_must_be_equal",
    "dns_response_is_superset",
]


def dns_response_must_be_equal(
    expect: List[str], value: List[str] = None  # type: ignore
) -> bool:
    """
    Validates the response from the DNS `resolve_name` probe is exactly
    equal to the given set.
    """
    return sorted(expect) == sorted(value or [])


def dns_response_is_superset(
    expect: List[str], value: List[str] = None  # type: ignore
) -> bool:
    """
    Validates the response from the DNS `resolve_name` probe is a superset
    of the given set of values.
    """
    return set(value or []).issuperset(expect)
