from typing import List, Sequence

import dns.message
import dns.resolver
from chaoslib.exceptions import ActivityFailed

__all__ = ["resolve_name"]


def resolve_name(
    domain: str,
    nameservers: Sequence[str] = ("8.8.8.8",),
    resolve_type: str = "A",
) -> List[str]:
    """
    Resolve a domain for a specific type from the given nameservers.
    """
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = list(nameservers)

    try:
        answer = resolver.resolve(domain, resolve_type)
    except dns.resolver.NoAnswer:
        raise ActivityFailed(
            f"no DNS answer for type '{resolve_type}' on domain '{domain}' "
            f"from nameservers {nameservers}"
        )

    return [rr.to_text() for rr in answer]
