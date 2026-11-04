# plugin-integrator-cboe

Cboe for [Liminal](https://github.com/pcxmac-dev/liminal-charts): the daily history of Cboe's indices
(VIX from 1990, VIX9D, VIX3M, VVIX, SKEW and the other volatility indices), read from Cboe's public
history files. No key. It is a closed archive: once an index's history is in, it is not asked again.

And VIX futures (`VX1!`, `VX2!`: a second feed of the plugin, `cboefutures`): Cboe publishes a daily
file for each contract (from March 2004), which the feed reads by the contract's final settlement
date; the library rolls the continuous chart from the contracts by volume. The feed is live: the
contracts trading on get their new days each run. Daily bars only.

A Liminal provider plugin released on its own. The app finds it through the entry point group
`liminal.providers` and lists it on the Plugins view and in `liminal-charts plugins`
as `package: plugin-integrator-cboe`, with this package's version.

## Install

Into the app's environment, from the app's folder:

```powershell
.venv\Scripts\python.exe -m pip install "plugin-integrator-cboe @ git+https://github.com/pcxmac-dev/plugin-integrator-cboe@v0.2.0"
```

or with the app's plugins (`pip install -e ".[plugins]"` in liminal-charts). The app loads it on its next
start.

## Compatibility

It is written for plugin API 2.0, the class contract (`PLUGINS`: each feed an instance of a `FeedPlugin`
subclass, `CboeIndices` and `CboeFutures` on the package's `CboeFeed`, a `PublicFeedPlugin`; liminal-libs
1.3.0 or later). An app offering 2.0 or a later 2.x loads it; an app of another major leaves it out and
says why on the Plugins view.

## Develop

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install "liminal-libs @ git+https://github.com/pcxmac-dev/liminal-libs@main"
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest -q
```

Tests never send requests (a fake session answers) and never read your keys.
