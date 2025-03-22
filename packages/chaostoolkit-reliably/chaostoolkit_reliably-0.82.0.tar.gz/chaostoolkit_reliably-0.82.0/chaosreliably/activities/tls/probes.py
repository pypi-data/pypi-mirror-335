import socket
import ssl
from typing import Any, Dict, List, Optional

from chaoslib.exceptions import ActivityFailed
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from chaosreliably.activities.tls import tolerances

__all__ = ["get_certificate_info", "verify_certificate"]


# copied mostly from this awesome piece
# https://github.com/dspruell/tls-probe/blob/main/tls_probe.py
def get_certificate_info(host: str, port: int = 443) -> Dict[str, Any]:
    """
    Extract certificate information from the remote connection.
    """
    context = ssl.create_default_context()
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True

    with socket.create_connection((host, port)) as sock:
        conn_info = dict(  # type: ignore
            conn={}, cert={"fingerprints": {}, "extensions": {}}
        )
        with context.wrap_socket(sock, server_hostname=host) as secsock:
            cert = secsock.getpeercert(binary_form=True)
            if not cert:
                raise ActivityFailed(
                    f"endpoint {host}:{port} has no certificate"
                )

            cert_data = x509.load_der_x509_certificate(cert, default_backend())

            conn_info["conn"].update(
                {
                    "version": secsock.version(),  # type: ignore
                    "remote_addr": ":".join(  # type: ignore
                        [str(_) for _ in secsock.getpeername()]
                    ),
                }
            )

            sig_hash = cert_data.signature_hash_algorithm.name  # type: ignore
            conn_info["cert"].update(
                {
                    "issuer": cert_data.issuer.rfc4514_string(),  # type: ignore
                    "subject": cert_data.subject.rfc4514_string(),  # type: ignore
                    "serial": str(cert_data.serial_number),  # type: ignore
                    "version": cert_data.version.name,  # type: ignore
                    "signature_hash": sig_hash,  # type: ignore
                    "not_valid_before": cert_data.not_valid_before.isoformat(),  # type: ignore
                    "not_valid_after": cert_data.not_valid_after.isoformat(),  # type: ignore
                }
            )

            conn_info["cert"]["fingerprints"].update(
                {
                    "md5": cert_data.fingerprint(hashes.MD5()).hex(),  # nosec
                    "sha1": cert_data.fingerprint(hashes.SHA1()).hex(),  # nosec
                    "sha256": cert_data.fingerprint(hashes.SHA256()).hex(),
                }
            )

            for ext in cert_data.extensions:
                if ext.oid._name in ("subjectAltName",):
                    names = []  # type: ignore
                    conn_info["cert"]["extensions"].update(
                        {
                            ext.oid._name: names,
                        }
                    )
                    for g in ext.value._general_names:
                        names.append(g.value)

        return conn_info


def verify_certificate(
    host: str,
    port: int = 443,
    expire_after: str = "7d",
    alt_names: Optional[List[str]] = None,
) -> bool:
    """
    Performs a range of checks on the certificate of the remote endpoint:

    * that we are beyond a certain duration of the certificate expiricy date
    * that the certificate exports the right alternative names

    If any of these values is not set (the default), the according
    check is not performed. This doesn't apply to the expiration date which
    is always checked.
    """
    info = get_certificate_info(host, port)

    if tolerances.expire_in_more_than(expire_after, info) is False:
        return False

    if alt_names not in ("", [""], None):
        if (
            tolerances.has_subject_alt_names(alt_names, True, info)  # type: ignore
            is False
        ):
            return False

    return True
