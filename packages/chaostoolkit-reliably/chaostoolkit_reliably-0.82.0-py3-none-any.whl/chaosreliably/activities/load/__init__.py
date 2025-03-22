import threading
from typing import Any, Dict

lock = threading.Lock()
RESULTS = {}


def store_results(name: str, results: Dict[str, Any]) -> None:
    with lock:
        RESULTS[name] = results


def get_results(name: str) -> Dict[str, Any]:
    with lock:
        return RESULTS.get("name", {})
