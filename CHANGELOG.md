# Changelog

## 1.3.0 (2026-11-02)

VIX futures (the user: "lets include futures"): a second feed of the plugin, `cboefutures`, reads Cboe's daily
file of each VX contract (`VX/VX_<final settlement date>.csv`, from 2004-03-26: Trade Date, Open, High, Low, Close,
Settle, Total Volume), asked for by the library's contract names (VXX6) through Cboe's settlement rule (the
Wednesday 30 days before the next month's third Friday, holiday-shifted), so the continuous chart `VX1!` is
rolled by volume from them; a day without a trade is its settlement at all four prices with no volume. The
feed is live (its front contracts trade on), on the same public server, its market `cfe`, its exchange the
Cboe Futures Exchange (XCBF). The plugin's entry point is now the module (`PLUGINS`: `cboe`, `cboefutures`);
plugin API 1.12.

## 1.2.1 (2026-11-02)

The plugin imports the library as `liminal_lib` and depends on liminal-lib (the app, renamed liminal-app, is no longer needed to run the tests; the user, 2026-11-02: "lets rename the app to liminal-app").

## 1.2.0 (2026-10-31)

- Released as its own package, `liminal-plugin-cboe`, registered under the entry point group
  `liminal.providers`; its version is the distribution's.
- Its plan and request caps are in it (`TIER`, `PER_RUN`, `PER_DAY`), no longer in the app's
  `config.PUBLIC_FEEDS`.
- Plugin API 1.6.
- Renamed with the app before its first publication (massive -> liminal, 2026-11-01): the
  package was to be `massive-plugin-cboe`.

## 1.1.0 (2026-10-31)

- Built into the app (then massive-collate): its source class and client in its module (plugin API 1.6).

## 1.0.0 (2026-10-29)

- Built into the app (then massive-collate): the first versioned release (plugin API 1.0).
