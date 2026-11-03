# Changelog

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
