"""Discovery must never launch a browser (smart-extract was removed for this)."""
import importlib
import sys

import pytest

from kestrel import pipeline


def test_smartextract_module_is_gone():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("kestrel.discovery.smartextract")


def test_discover_stage_runs_only_browserless_sources(monkeypatch):
    from kestrel.discovery import composio, jobspy, workday

    called = []
    monkeypatch.setattr(jobspy, "run_discovery", lambda results_per_site=None: called.append("jobspy"))
    monkeypatch.setattr(workday, "run_workday_discovery", lambda workers=1: called.append("workday"))
    monkeypatch.setattr(composio, "run_composio_discovery", lambda: called.append("composio"))

    def no_browser(*a, **k):
        raise AssertionError("discover launched a browser")

    import kestrel.browser as browser
    monkeypatch.setattr(browser, "sync_playwright", no_browser)

    stats = pipeline._run_discover(workers=1)

    assert called == ["jobspy", "workday", "composio"]
    assert set(stats) - {"status"} == {"jobspy", "workday", "composio"}
    assert "kestrel.discovery.smartextract" not in sys.modules
