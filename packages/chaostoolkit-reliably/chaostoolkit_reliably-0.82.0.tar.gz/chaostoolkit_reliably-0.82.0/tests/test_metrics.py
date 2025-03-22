import time
from pathlib import Path
from tempfile import TemporaryDirectory

from chaoslib.run import EventHandlerRegistry
from chaosreliably.controls import find_extension_by_name
from chaosreliably.controls.metrics import configure_control


def test_compute_metrics(respx_mock):
    registry = EventHandlerRegistry()

    secrets = {}

    probes = [
        {
            "name": "lookup-file",
            "type": "probe",
            "tolerance": True,
            "provider": {
                "type": "python",
                "module": "os.path",
                "func": "exists",
                "arguments": {
                    "path": "${filename}"
                }
            }
        }
    ]

    experiment = {
        "title": "n/a",
        "description": "n/a",
        "steady-state-hypothesis": {
            "title": "n/a",
            "probes": probes
        },
        "method": []
    }

    journal = {
        "experiment": {
            "extensions": [
                {
                    "name": "dora"
                }
            ]
        }
    }

    with TemporaryDirectory() as d:
        p = Path(d) / "my.txt"
        p.touch()

        configuration = {
            "filename": p
        }

        configure_control(
            registry, None, 1, 10, True, configuration, secrets, {}, experiment
        )

        registry.running(experiment, journal, configuration, secrets, None, None)

        time.sleep(2)

        p.unlink()

        time.sleep(2)


        registry.finish(journal)

        p.touch()

        time.sleep(2)

        x = find_extension_by_name(journal["experiment"], "dora")
        m = x["metrics"]

        assert m["detection_time"] is not None
        assert m["recovery_time"] is not None
        assert m["outage_duration"] > 4.0
        assert m["went_over_timeout"] is False
        assert m["timeout"] == 10


def test_compute_metrics_with_timeout(respx_mock):
    registry = EventHandlerRegistry()

    secrets = {}

    probes = [
        {
            "name": "lookup-file",
            "type": "probe",
            "tolerance": True,
            "provider": {
                "type": "python",
                "module": "os.path",
                "func": "exists",
                "arguments": {
                    "path": "${filename}"
                }
            }
        }
    ]

    experiment = {
        "title": "n/a",
        "description": "n/a",
        "steady-state-hypothesis": {
            "title": "n/a",
            "probes": probes
        },
        "method": []
    }

    journal = {
        "experiment": {
            "extensions": [
                {
                    "name": "dora"
                }
            ]
        }
    }

    with TemporaryDirectory() as d:
        p = Path(d) / "my.txt"
        p.touch()

        configuration = {
            "filename": p
        }

        configure_control(
            registry, None, 1, 6, True, configuration, secrets, {}, experiment
        )

        registry.running(experiment, journal, configuration, secrets, None, None)

        time.sleep(2)

        p.unlink()

        time.sleep(2)


        registry.finish(journal)

        time.sleep(2)

        x = find_extension_by_name(journal["experiment"], "dora")
        m = x["metrics"]

        assert m["detection_time"] is not None
        assert m["recovery_time"] is None
        assert m["outage_duration"] is None
        assert m["went_over_timeout"] is True
        assert m["timeout"] == 6
