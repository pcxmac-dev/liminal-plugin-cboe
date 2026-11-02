"""The Cboe plugin, run against the app installed beside it: its history files read, and the app
loading it from this package with its own version and the facts it had as a built-in."""
from __future__ import annotations

from datetime import date, datetime
from importlib.metadata import version

import pytest

from liminal import composite
from liminal.config import load_settings
from liminal.errors import NotEntitled, SourceError
from liminal.sources import is_archive, markets, provider, rate_window, registry, supports
from liminal.sources.archive import ET, ms
from liminal.sources.http import PublicClient
from liminal.symbols import resolve

import liminal_plugin_cboe
from liminal_plugin_cboe import PER_DAY, PER_RUN, TIER, CboeSource

from .conftest import FakeResponse, FakeSession


def _cboe(*texts: str):
    session = FakeSession([FakeResponse(200, t) for t in texts])
    return CboeSource(PublicClient("https://x.test/api", session=session, sleep=lambda s: None)), session


def test_cboe_reads_one_file_for_all_history():
    src, session = _cboe("DATE,OPEN,HIGH,LOW,CLOSE\n01/02/1990,17.24,17.24,17.24,17.24\n01/03/1990,18.19,18.5,18.0,18.19\n")
    bars = next(src.bar_pages("I:VIX", date(1990, 1, 1), date(1990, 1, 2), "day"))
    assert [b["c"] for b in bars] == [17.24] and bars[0]["t"] == ms(datetime(1990, 1, 2, tzinfo=ET))
    assert len(next(src.bar_pages("VIX", date(1990, 1, 1), date(1990, 1, 31), "day"))) == 2
    assert len(session.calls) == 1 and session.calls[0][0].endswith("/VIX_History.csv")  # cached
    with pytest.raises(NotEntitled):
        next(src.bar_pages("I:COMP", date(1990, 1, 1), date(1990, 1, 2), "day"))
    with pytest.raises(NotEntitled):
        next(src.bar_pages("I:VIX", date(1990, 1, 1), date(1990, 1, 2), "minute"))


def test_a_cboe_file_with_closes_only_is_read():
    src, _ = _cboe("﻿DATE,VVIX\n01/03/2007,87.63\n01/04/2007,88.19\n")
    bars = next(src.bar_pages("I:VVIX", date(2007, 1, 1), date(2007, 1, 31), "day"))
    assert [(b["o"], b["h"], b["l"], b["c"]) for b in bars] == [(87.63,) * 4, (88.19,) * 4]
    src, _ = _cboe("DATE,OPEN,HIGH,LOW,CLOSE\n01/02/1990,,,,17.24\n01/03/1990,18.19,18.5,18.0,18.19\n")
    bars = next(src.bar_pages("I:VIX", date(1990, 1, 1), date(1990, 1, 31), "day"))
    assert [b["h"] for b in bars] == [17.24, 18.5]  # a day with its close only, beside full days


def test_a_cboe_file_that_reads_as_nothing_is_an_error_not_an_empty_history():
    src, _ = _cboe("Date;Index;Value\n2007-01-03;VVIX;87.63\n")  # a format of its own
    with pytest.raises(SourceError, match="no daily rows"):
        next(src.bar_pages("I:VVIX", date(2007, 1, 1), date(2007, 1, 31), "day"))
    with pytest.raises(SourceError):
        next(_cboe("")[0].bar_pages("I:SKEW", date(2007, 1, 1), date(2007, 1, 31), "day"))


def test_the_app_loads_it_from_this_package_with_its_own_version():
    registry.reload()
    p = provider("cboe")
    assert p is not None, dict(registry.errors())
    assert p.origin in {"package: liminal-plugin-cboe (liminal_plugin_cboe:PLUGIN)", "plugins/liminal-plugin-cboe (liminal_plugin_cboe:PLUGIN)"}  # its package, or its checkout in the workspace\'s plugin directory
    assert p.version == version("liminal-plugin-cboe") and liminal_plugin_cboe.PLUGIN.version == ""
    assert registry.api_refusal(p.api) is None
    assert not [why for where, why in registry.errors() if "cboe" in where or "cboe" in why]
    row = {r["name"]: r for r in registry.menu()}["cboe"]
    assert (row["version"], row["api"]) == (version("liminal-plugin-cboe"), "1.6")


def test_it_keeps_the_facts_it_had_built_in():
    registry.reload()
    s = load_settings(env={}, env_file=None)
    view = s.for_source("cboe")
    assert (view.tier, view.max_requests_per_run, view.max_requests_per_day) == (TIER, PER_RUN, PER_DAY)
    assert rate_window("cboe", s)[0] == 30
    assert is_archive("cboe") and markets("cboe", s) == {"index": "index"}
    assert supports("cboe", resolve("I:VIX")) and not supports("cboe", resolve("IXIC"))
    assert composite.feed_kind("cboe", "index") == "official"
