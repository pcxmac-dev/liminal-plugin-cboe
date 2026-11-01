# liminal-plugin-cboe

Cboe for [Liminal](https://github.com/pcxmac-dev/liminal): the daily history of Cboe's indices
(VIX from 1990, VIX9D, VIX3M, VVIX, SKEW and the other volatility indices), read from Cboe's public
history files. No key. It is a closed archive: once an index's history is in, it is not asked again.

A Liminal provider plugin released on its own. The app finds it through the entry point group
`liminal.providers` and lists it on the Plugins view and in `python -m liminal plugins`
as `package: liminal-plugin-cboe`, with this package's version.

## Install

Into the app's environment, from the app's folder:

```powershell
.venv\Scripts\python.exe -m pip install "liminal-plugin-cboe @ git+https://github.com/pcxmac-dev/liminal-plugin-cboe@v1.2.0"
```

or with the app's plugins (`pip install -e ".[plugins]"` in liminal). The app loads it on its next
start.

## Compatibility

It is written for plugin API 1.6 (`PLUGIN.api`). An app offering 1.6 or a later 1.x loads it; an
app of another major, or one older than 1.6, leaves it out and says why on the Plugins view.

## Develop

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install "liminal @ git+https://github.com/pcxmac-dev/liminal@feature/collector"
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest -q
```

Tests never send requests (a fake session answers) and never read your keys.
