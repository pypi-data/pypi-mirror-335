from typing import Any, Dict, List, Optional

__all__ = ["has_error_budget_left"]


def has_error_budget_left(
    name: str, value: Optional[List[Dict[str, Any]]] = None
) -> bool:
    """
    Validate there is enough error budget left from compute_slo returned
    value
    """
    if not value:
        return False

    for item in value:
        if item.get("name") == name:
            return float(item["error_budget_burn_rate"]) < 1.0

    return False
