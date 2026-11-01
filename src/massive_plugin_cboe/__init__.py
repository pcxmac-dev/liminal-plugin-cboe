"""Cboe (cboe.com) for Massive: daily history of Cboe's indices (VIX from 1990), no key; a closed archive.

A Massive plugin released on its own (massive_collate.sources.registry: Provider), registered under
the entry point group `massive_collate.providers`. Its version is its distribution's (pyproject.toml);
it relies on plugin API 1.6 and nothing of the app outside it (docs/ARCHITECTURE.md in massive:
"Providers are plugins").
"""
from __future__ import annotations

import csv
import io
from datetime import date, datetime
from typing import Iterator

from massive_collate.config import Tier
from massive_collate.errors import NotEntitled, SourceError
from massive_collate.models import Instrument
from massive_collate.sources.archive import ET, Archive, bounds, ms
from massive_collate.sources.http import PublicClient
from massive_collate.sources.registry import Provider, public_client

BASE_URL = "https://cdn-api.cboe.com/api/global/us_indices/daily_prices"
# its plan and caps: a public file server with no published limits, one file an index
TIER = Tier("cboe-public", requests_per_minute=30, history_years=None, history_start=date(1990, 1, 1))
PER_RUN, PER_DAY = 50, 200

CBOE_INDICES = {"VIX", "VIX9D", "VIX3M", "VIX6M", "VIX1Y", "VVIX", "SKEW", "VXN", "VXD", "RVX", "OVX", "GVZ",
                "VXEEM", "VXSLV", "VXAZN", "VXAPL", "VXGOG", "VXGS", "VXIBM", "BXM", "PUT"}


class CboeSource(Archive):
    """Cboe's daily history files: one request returns an index's whole history."""

    name = "cboe"
    assets = ("index",)

    def __init__(self, client: PublicClient):
        super().__init__(client)
        self._files: dict[str, list[dict]] = {}

    def resolutions(self, asset: str) -> tuple[str, ...]:
        return ("day",) if asset == "index" else ()

    def covers(self, ticker: str) -> bool:
        return ticker.upper().removeprefix("I:") in CBOE_INDICES

    def _history(self, code: str) -> list[dict]:
        """An index's whole daily history. Most files have DATE, OPEN, HIGH, LOW, CLOSE; some only
        a close (VVIX, SKEW: DATE and a column named after the index), whose bars are that close
        at all four prices. A file with rows of which none can be read is an error, never an empty
        history: the archive would be closed as complete without it."""
        if code not in self._files:
            text = self.client.text(f"/{code}_History.csv")
            bars, rows = [], 0
            for row in csv.DictReader(io.StringIO(text)):
                rows += 1
                row = {(k or "").strip("﻿ \t").upper(): v.strip() for k, v in row.items() if isinstance(v, str)}
                try:
                    d = datetime.strptime(row["DATE"], "%m/%d/%Y")
                    if all(row.get(k) for k in ("OPEN", "HIGH", "LOW")):
                        o, h, l, c = (float(row[k]) for k in ("OPEN", "HIGH", "LOW", "CLOSE"))
                    else:  # a close-only file (or a day it gives the close of only)
                        o = h = l = c = float(row.get("CLOSE") or row[code])
                except (KeyError, ValueError):
                    continue
                # day bars are stamped at midnight US/Eastern of the session date, like the other feeds'
                bars.append({"t": ms(datetime(d.year, d.month, d.day, tzinfo=ET)), "o": o, "h": h, "l": l, "c": c,
                             "v": None, "vw": None, "n": None})
            if not bars:  # answered (200), but nothing in it: not an outage, and not an empty history
                raise SourceError(200, f"Cboe {code}: no daily rows read from the history file ({rows} lines; "
                                       "format changed?); the archive stays open")
            self._files[code] = bars
        return self._files[code]

    def bar_pages(self, ticker, start, end, timespan, multiplier=1, descending=False, asset="index",
                  limit: int | None = None) -> Iterator[list[dict]]:
        if timespan != "day":
            raise NotEntitled(0, "Cboe publishes daily history only")
        code = ticker.upper().removeprefix("I:")
        if code not in CBOE_INDICES:
            raise NotEntitled(0, f"Cboe has no history file for {code}")
        a, b = bounds(start, end, ET)
        bars = [x for x in self._history(code) if a <= x["t"] < b]
        bars.sort(key=lambda x: -x["t"] if descending else x["t"])
        yield bars[:limit] if limit else bars

    def instrument(self, ticker: str, resolve_exchange: bool = True) -> Instrument:
        code = ticker.upper().removeprefix("I:")
        return Instrument(ticker=code, name=f"Cboe {code} index", details={"source": "Cboe daily history"})


PLUGIN = Provider(
    api="1.6",  # the contract it needs (sources.http, sources.archive); its version: the distribution's
    name="cboe", title="Cboe",
    build=lambda settings, budget: CboeSource(public_client("cboe", BASE_URL, settings, budget)),
    assets=frozenset({"index"}), order=50, about="daily history of Cboe's indices, VIX from 1990 (no key)",
    archival=True, tier=TIER, per_run=PER_RUN, per_day=PER_DAY, limits="none published (a public file server)",
    kind="official", markets=lambda settings: {"index": "index"},
    provides={"index": ("day",)}, per_request={"day": None},  # one file per index: its whole history
    carries=lambda spec: spec.source_ticker.upper().removeprefix("I:") in CBOE_INDICES,
)
