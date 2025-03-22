import time
import httpx
import respx

from chaoslib.run import EventHandlerRegistry
from chaosreliably.activities.safeguard.probes import call_endpoint
from chaosreliably.controls import ReliablyGuardian, ReliablySafeguardHandler, initialize, register, run_all


class TestReliablyGuardian(ReliablyGuardian):
    def _exit(self) -> None:
        time.sleep(2)


def test_prechecks_run_interrupts_execution(respx_mock):
    url = "https://example.com/try-me"

    m = respx_mock.get(url).mock(return_value=httpx.Response(
        200, json={"ok": False, "error": "boom"})
    )
    
    proxy = ReliablySafeguardHandler()
    registry = EventHandlerRegistry()
    initialize(registry, handler=proxy)
    register(url, handler=proxy, guardian_class=TestReliablyGuardian)

    experiment = {
        "title": "an experiment",
        "description": "n/a",
        "method": []
    }
    journal = {
        "experiment": experiment
    }

    try:
        run_all(experiment, None, None, handler=proxy)
        time.sleep(2)
    finally:
        registry.finish(journal)
        registry.handlers.clear()

    respx_mock.calls.assert_called_once()
    assert proxy.guardians[0].guardian.interrupted is True


def test_safeguard_expects_a_200(respx_mock):
    url = "https://example.com/try-me"

    respx_mock.get(url).mock(return_value=httpx.Response(400))
    assert call_endpoint(url) is False

    respx_mock.get(url).mock(return_value=httpx.Response(200, json={"ok": True}))
    assert call_endpoint(url) is True


def test_safeguard_not_ok_expects_error_message(respx_mock):
    url = "https://example.com/try-me"

    respx_mock.get(url).mock(return_value=httpx.Response(400))
    assert call_endpoint(url) is False

    respx_mock.get(url).mock(return_value=httpx.Response(200, json={
        "ok": False,
        "error": "boom"
    }))
    assert call_endpoint(url) is False


def test_prechecks_run_once(respx_mock):
    url = "https://example.com/try-me"

    m = respx_mock.get(url).mock(return_value=httpx.Response(200, json={"ok": True}))
    
    proxy = ReliablySafeguardHandler()
    registry = EventHandlerRegistry()
    initialize(registry, handler=proxy)
    register(url, handler=proxy, guardian_class=TestReliablyGuardian)

    experiment = {
        "title": "an experiment",
        "description": "n/a",
        "method": []
    }
    journal = {
        "experiment": experiment
    }

    try:
        run_all(experiment, None, None, handler=proxy)
        time.sleep(2)
    finally:
        registry.finish(journal)
        registry.handlers.clear()

    respx_mock.calls.assert_called_once()
    assert proxy.guardians[0].guardian.interrupted is False


def test_safeguard_run_periodically(respx_mock):
    url = "https://example.com/try-me"

    m = respx_mock.get(url).mock(side_effect=[
        httpx.Response(200, json={"ok": True}),
        httpx.Response(200, json={"ok": False, "error": "boom"}),
        httpx.Response(200, json={"ok": False, "error": "boom"}),
        httpx.Response(200, json={"ok": False, "error": "boom"})
    ])

    proxy = ReliablySafeguardHandler()
    registry = EventHandlerRegistry()
    initialize(registry, handler=proxy)
    register(url, frequency=0.5, handler=proxy, guardian_class=TestReliablyGuardian)

    experiment = {
        "title": "an experiment",
        "description": "n/a",
        "method": []
    }
    journal = {
        "experiment": experiment
    }

    try:
        run_all(experiment, None, None, handler=proxy)
        time.sleep(2)
    finally:
        registry.finish(journal)
        registry.handlers.clear()

    respx_mock.calls.calls.call_count > 1
    assert proxy.guardians[0].guardian.interrupted is True


def test_safeguard_run_interrupts_execution(respx_mock):
    url = "https://example.com/try-me"

    m = respx_mock.get(url).mock(side_effect=[
        httpx.Response(200, json={"ok": True}),
        httpx.Response(200, json={"ok": False, "error": "boom"}),
        httpx.Response(200, json={"ok": False, "error": "boom"}),
        httpx.Response(200, json={"ok": False, "error": "boom"})
    ])
    
    proxy = ReliablySafeguardHandler()
    registry = EventHandlerRegistry()
    initialize(registry, handler=proxy)
    register(url, frequency=0.5, handler=proxy, guardian_class=TestReliablyGuardian)

    experiment = {
        "title": "an experiment",
        "description": "n/a",
        "method": []
    }
    journal = {
        "experiment": experiment
    }

    try:
        run_all(experiment, None, None, handler=proxy)
        time.sleep(2)
    finally:
        registry.finish(journal)
        registry.handlers.clear()
        time.sleep(2)

    assert respx_mock.calls.call_count > 1
    assert proxy.guardians[0].guardian.interrupted is True


def test_safeguard_can_be_many(respx_mock):
    url = "https://example.com/try-me"

    m = respx.get(url).mock(side_effect=[
        httpx.Response(200, json={"ok": True}),
        httpx.Response(200, json={"ok": False, "error": "boom"}),
        httpx.Response(200, json={"ok": False, "error": "boom"}),
        httpx.Response(200, json={"ok": False, "error": "boom"})
    ])
    
    url2 = "https://example.com/try-me-as-well"

    m = respx.get(url2).mock(side_effect=[
        httpx.Response(200, json={"ok": True}),
        httpx.Response(200, json={"ok": True}),
        httpx.Response(200, json={"ok": True}),
        httpx.Response(200, json={"ok": True}),
    ])
    
    proxy = ReliablySafeguardHandler()
    registry = EventHandlerRegistry()
    initialize(registry, handler=proxy)
    register(url, frequency=0.5, handler=proxy, guardian_class=TestReliablyGuardian)
    register(url2, frequency=0.5, handler=proxy, guardian_class=TestReliablyGuardian)

    experiment = {
        "title": "an experiment",
        "description": "n/a",
        "method": []
    }
    journal = {
        "experiment": experiment
    }

    try:
        run_all(experiment, None, None, handler=proxy)
        time.sleep(2)
    finally:
        registry.finish(journal)
        registry.handlers.clear()

    assert respx_mock.calls.call_count > 1
    assert proxy.guardians[0].guardian.interrupted is True

    assert respx_mock.calls.call_count > 1
    assert proxy.guardians[1].guardian.interrupted is False
