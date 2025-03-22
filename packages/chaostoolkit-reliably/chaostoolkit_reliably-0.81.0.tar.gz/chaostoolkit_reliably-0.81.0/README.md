# Chaos Toolkit extension for Reliably

[![Version](https://img.shields.io/pypi/v/chaostoolkit-reliably.svg)](https://img.shields.io/pypi/v/chaostoolkit-reliably.svg)
[![Python versions](https://img.shields.io/pypi/pyversions/chaostoolkit-reliably.svg)](https://www.python.org/)
[![License](https://img.shields.io/pypi/l/chaostoolkit-reliably.svg)](https://img.shields.io/pypi/l/chaostoolkit-reliably.svg)
[![Build](https://github.com/chaostoolkit-incubator/chaostoolkit-reliably/actions/workflows/build.yaml/badge.svg)](https://github.com/chaostoolkit-incubator/chaostoolkit-reliably/actions/workflows/build.yaml)

[Chaos Toolkit][chaostoolkit] extension for [Reliably][reliably].

[reliably]: https://reliably.com
[chaostoolkit]: http://chaostoolkit.org/

## Install

To be used from your experiment, this package must be installed in the Python
environment where [chaostoolkit][] already lives.

[chaostoolkit]: https://github.com/chaostoolkit/chaostoolkit

```
$ pip install chaostoolkit-reliably
```

## Authentication

To use this package, you must create have registered with 
[Reliably services](https://app.reliably.com/).

Then you need to set some environment variables as secrets.

* `RELIABLY_TOKEN`: the token to authenticate against Reliably's API
* `RELIABLY_HOST:`: the hostname to connect to, default to `app.reliably.com`

```json
{
    "secrets": {
        "reliably": {
            "token": {
                "type": "env",
                "key": "RELIABLY_TOKEN"
            },
            "host": {
                "type": "env",
                "key": "RELIABLY_HOST",
                "default": "app.reliably.com"
            }
        }
    }
}
```

## Usage

### As Steady Steate Hypothesis or Method

This extensions offers a
[variety of probes and tolerances](https://chaostoolkit.org/drivers/reliably/)
ready to be used in your steady-state blocks.

For instance:

```json
{
  "version": "1.0.0",
  "title": "SLO error-count-3h / Error budget 10%",
  "description": "Monitor the health of our demo service from our users perspective and ensure they have a high-quality experience",
  "runtime": {
    "hypothesis": {
      "strategy": "after-method-only"
    }
  },
  "steady-state-hypothesis": {
    "title": "Compute SLO and validate its Error Budget with our target",
    "probes": [
      {
        "type": "probe",
        "name": "get-slo",
        "tolerance": {
          "type": "probe",
          "name": "there-should-be-error-budget-left",
          "provider": {
            "type": "python",
            "module": "chaosreliably.activities.slo.tolerances",
            "func": "has_error_budget_left",
            "arguments": {
              "name": "cloudrun-service-availability"
            }
          }
        },
        "provider": {
          "type": "python",
          "module": "chaosreliably.activities.slo.probes",
          "func": "compute_slo",
          "arguments": {
            "slo": {
              "apiVersion": "sre.google.com/v2",
              "kind": "ServiceLevelObjective",
              "metadata": {
                "name": "cloudrun-service-availability",
                "labels": {
                  "service_name": "cloudrun",
                  "feature_name": "service",
                  "slo_name": "availability"
                }
              },
              "spec": {
                "description": "Availability of Cloud Run service",
                "backend": "cloud_monitoring_mql",
                "method": "good_bad_ratio",
                "exporters": [

                ],
                "service_level_indicator": {
                  "filter_good": "fetch cloud_run_revision | metric 'run.googleapis.com/request_count' | filter resource.project_id == '${CLOUDRUN_PROJECT_ID}' | filter resource.service_name == '${CLOUDRUN_SERVICE_NAME}' | filter metric.response_code_class == '2xx'",
                  "filter_valid": "fetch cloud_run_revision | metric 'run.googleapis.com/request_count' | filter resource.project_id == '${CLOUDRUN_PROJECT_ID}' | filter resource.service_name == '${CLOUDRUN_SERVICE_NAME}'"
                },
                "goal": 0.9
              }
            },
            "config": {
              "backends": {
                "cloud_monitoring_mql": {
                  "project_id": "${STACKDRIVER_HOST_PROJECT_ID}"
                }
              },
              "error_budget_policies": {
                "default": {
                  "steps": [
                    {
                      "name": "3 hours",
                      "burn_rate_threshold": 9,
                      "alert": false,
                      "window": 10800,
                      "message_alert": "Page the SRE team to defend the SLO",
                      "message_ok": "Last 3 hours on track"
                    }
                  ]
                }
              }
            }
          }
        }
      }
    ]
  },
  "method": [
    {
      "name": "inject-traffic-into-endpoint",
      "type": "action",
      "background": true,
      "provider": {
        "func": "inject_gradual_traffic_into_endpoint",
        "type": "python",
        "module": "chaosreliably.activities.load.actions",
        "arguments": {
          "endpoint": "${ENDPOINT}",
          "step_duration": 30,
          "test_duration": 300,
          "step_additional_vu": 3,
          "vu_per_second_rate": 1,
          "results_json_filepath": "./load-test-results.json"
        }
      }
    }
  ]
}
```

This above example will get the last 5 Objective Results for our `Must be good` SLO and determine if they were all okay or whether we've spent our [error budget](https://sre.google/workbook/error-budget-policy/#:~:text=Error%20budgets%20are%20the%20tool,with%20the%20pace%20of%20innovation.&text=The%20error%20budget%20forms%20a,has%20a%200.1%25%20error%20budget.)
they are allowed.


### As controls

You can use controls provided by `chaostoolkit-reliably` to track your experiments
within Reliably. The block is inserted automatically by Reliably when you
import the experiment into Reliably.

## Contribute

From a code perspective, if you wish to contribute, you will need to run a
Python 3.6+ environment. Please, fork this project, write unit tests to cover
the proposed changes, implement the changes, ensure they meet the formatting
standards set out by `black`, `ruff`, `isort`, and `mypy`, add an entry into
`CHANGELOG.md`, and then raise a PR to the repository for review

Please refer to the [formatting](#formatting-and-linting) section for more
information on the formatting standards.

The Chaos Toolkit projects require all contributors must sign a
[Developer Certificate of Origin][dco] on each commit they would like to merge
into the master branch of the repository. Please, make sure you can abide by
the rules of the DCO before submitting a PR.

[dco]: https://github.com/probot/dco#how-it-works

### Develop

If you wish to develop on this project, make sure to install the development
dependencies. First you will need to install globally
[pdm](https://pdm.fming.dev/latest/) and create a virtual environment:

```
$ pdm create venv
$ pdm use
$ $(pdm venv activate)
```

Then install the dependencies:

```console
$ pdm sync -d
```

### Test

To run the tests for the project execute the following:

```console
$ pdm run test
```

### Formatting and Linting

We use a combination of [`black`][black], [`ruff`][flake8], [`isort`][isort],
[`mypy`][mypy] and [`bandit`][] to both lint and format this repositories code.

[black]: https://github.com/psf/black
[ruff]: https://github.com/charliermarsh/ruff
[isort]: https://github.com/PyCQA/isort
[mypy]: https://github.com/python/mypy
[bandit]: https://bandit.readthedocs.io/en/latest/

Before raising a Pull Request, we recommend you run formatting against your
code with:

```console
$ pmd run format
```

This will automatically format any code that doesn't adhere to the formatting
standards.

As some things are not picked up by the formatting, we also recommend you run:

```console
$ pdm run lint
```

To ensure that any unused import statements/strings that are too long, etc.
are also picked up. It will also provide you with any errors `mypy` picks up.
