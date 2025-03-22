import logging
import warnings

logger = logging.getLogger("chaostoolkit")


# from slo-egenerator
def reroute_slo_generator_logging() -> None:
    slo_gen_logger = logging.getLogger("slo_generator")
    slo_gen_logger.setLevel(logging.DEBUG)
    slo_gen_logger.propagate = False

    gcp_logger = logging.getLogger("googleapiclient")
    gcp_logger.setLevel(logging.ERROR)
    gcp_logger.propagate = False

    # not ideal here but it's the only way to route these messages to
    # chaostoolkit logger
    for h in logger.handlers:
        slo_gen_logger.addHandler(h)
        gcp_logger.addHandler(h)

    # Ignore Cloud SDK warning when using a user instead of service account
    try:
        # pylint: disable=import-outside-toplevel
        from google.auth._default import (
            _CLOUD_SDK_CREDENTIALS_WARNING,
        )

        warnings.filterwarnings(
            "ignore", message=_CLOUD_SDK_CREDENTIALS_WARNING
        )
    except ImportError:
        pass


reroute_slo_generator_logging()
