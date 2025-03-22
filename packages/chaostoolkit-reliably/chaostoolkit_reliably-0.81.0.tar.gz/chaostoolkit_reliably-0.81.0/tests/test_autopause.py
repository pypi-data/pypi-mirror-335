import os

from chaoslib import substitute
from chaosreliably.controls.autopause import configure_control


def test_autopause_method_actions():
    experiment = {
        "title": "an experiment",
        "description": "n/a",
        "method": [
            {
                "name": "A",
                "type": "action",
                "provider": {"module": "os"}
            },
            {
                "name": "B",
                "type": "action",
                "provider": {"module": "os"}
            },
            {
                "name": "C",
                "type": "probe",
                "provider": {"module": "os"}
            },
            {
                "name": "D",
                "type": "action",
                "provider": {"module": "os"}
            }
        ]
    }

    configure_control(experiment, {
        "method": {
            "actions": {
                "enabled": True,
                "pause_duration": 5
            }
        }
    })

    activities = experiment.get("method", [])
    for index, activity in enumerate(activities):
        if activity["name"] in ("A", "B", "D"):
            assert activities[index+1]["provider"]["module"] == "chaosreliably.activities.pauses"
            assert activities[index+1]["provider"]["arguments"]["duration"] == 5
        if activity["name"] == "C":
            assert activities[index+1]["provider"]["module"] != "chaosreliably.activities.pauses"


def test_autopause_method_probes():
    experiment = {
        "title": "an experiment",
        "description": "n/a",
        "method": [
            {
                "name": "A",
                "type": "action",
                "provider": {"module": "os"}
            },
            {
                "name": "B",
                "type": "action",
                "provider": {"module": "os"}
            },
            {
                "name": "C",
                "type": "probe",
                "provider": {"module": "os"}
            },
            {
                "name": "D",
                "type": "action",
                "provider": {"module": "os"}
            }
        ]
    }

    configure_control(experiment, {
        "method": {
            "probes": {
                "enabled": True,
                "pause_duration": 5
            }
        }
    })

    activities = experiment.get("method", [])
    for index, activity in enumerate(activities):
        if activity["name"] in ("A", "B", "D"):
            assert activities[index+1]["provider"]["module"] != "chaosreliably.activities.pauses"
        if activity["name"] == "C":
            assert activities[index+1]["provider"]["module"] == "chaosreliably.activities.pauses"
            assert activities[index+1]["provider"]["arguments"]["duration"] == 5


def test_autopause_method_probes():
    experiment = {
        "title": "an experiment",
        "description": "n/a",
        "method": [
            {
                "name": "A",
                "type": "action",
                "provider": {"module": "os"}
            },
            {
                "name": "B",
                "type": "action",
                "provider": {"module": "os"}
            },
            {
                "name": "C",
                "type": "probe",
                "provider": {"module": "os"}
            },
            {
                "name": "D",
                "type": "action",
                "provider": {"module": "os"}
            },
            {
                "name": "E",
                "type": "probe",
                "provider": {"module": "os"}
            },
        ]
    }

    configure_control(experiment, {
        "method": {
            "actions": {
                "enabled": False,
            },
            "probes": {
                "enabled": True,
                "pause_duration": 5
            }
        }
    })

    activities = experiment.get("method", [])
    for index, activity in enumerate(activities):
        if activity["name"] in ("A", "B", "D"):
            assert activities[index+1]["provider"]["module"] != "chaosreliably.activities.pauses"
        if activity["name"] in ("C", "E"):
            assert activities[index+1]["provider"]["module"] == "chaosreliably.activities.pauses"
            assert activities[index+1]["provider"]["arguments"]["duration"] == 5


def test_autopause_rollbacks():
    experiment = {
        "title": "an experiment",
        "description": "n/a",
        "rollbacks": [
            {
                "name": "A",
                "type": "action",
                "provider": {"module": "os"}
            },
            {
                "name": "B",
                "type": "action",
                "provider": {"module": "os"}
            },
            {
                "name": "C",
                "type": "action",
                "provider": {"module": "os"}
            },
        ]
    }

    configure_control(experiment, {
        "rollbacks": {
            "enabled": True,
            "pause_duration": 5
        }
    })

    activities = experiment.get("method", [])
    for index, activity in enumerate(activities):
        if activity["name"] in ("A", "B", "C"):
            assert activities[index+1]["provider"]["module"] == "chaosreliably.activities.pauses"
            assert activities[index+1]["provider"]["arguments"]["duration"] == 5


def test_autopause_ssh():
    experiment = {
        "title": "an experiment",
        "description": "n/a",
        "steady-state-hypothesis": {
            "probes":[
                {
                    "name": "A",
                    "type": "probe",
                    "provider": {"module": "os"}
                },
                {
                    "name": "B",
                    "type": "probe",
                    "provider": {"module": "os"}
                },
                {
                    "name": "C",
                    "type": "probe",
                    "provider": {"module": "os"}
                },
            ]
        }
    }

    configure_control(experiment, {
        "steady-state-hypothesis": {
            "enabled": True,
            "pause_duration": 5
        }
    })

    activities = experiment.get("method", [])
    for index, activity in enumerate(activities):
        if activity["name"] in ("A", "B", "C"):
            assert activities[index+1]["provider"]["module"] == "chaosreliably.activities.pauses"
            assert activities[index+1]["provider"]["arguments"]["duration"] == 5


def test_autopause_from_env():
    os.putenv("RELIABLY_PROBE_PAUSE_DURATION", "10.4")
    experiment = {
        "title": "an experiment",
        "description": "n/a",
        "steady-state-hypothesis": {
            "probes":[
                {
                    "name": "A",
                    "type": "probe",
                    "provider": {"module": "os"}
                },
                {
                    "name": "B",
                    "type": "probe",
                    "provider": {"module": "os"}
                },
                {
                    "name": "C",
                    "type": "probe",
                    "provider": {"module": "os"}
                },
            ]
        }
    }

    configure_control(experiment, {
        "method": {
            "probes": {
                "enabled": True,
                "pause_duration": substitute({
                    "env": "type",
                    "key": "RELIABLY_PROBE_PAUSE_DURATION",
                }, {}, {})
            }
        },
    })

    activities = experiment.get("method", [])
    for index, activity in enumerate(activities):
        if activity["name"] in ("A", "B", "C"):
            assert activities[index+1]["provider"]["module"] == "chaosreliably.activities.pauses"
            assert activities[index+1]["provider"]["arguments"]["duration"] == 10.4
