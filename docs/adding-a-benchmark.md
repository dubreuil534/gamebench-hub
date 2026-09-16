# Adding a benchmark

Add one YAML file under `src/gamebench_hub/manifests/`. Only official standalone tools are in
scope. Do not add manifests for a full paid game, unofficial repacks, mirrors, or extracted assets.

```yaml
schema_version: 1
id: example-benchmark
name: "Example Benchmark Tool"
description: "Official standalone benchmark by Example Studio."
platforms: [windows]
source:
  type: steam
  app_id: 123456
  store_url: "https://store.steampowered.com/app/123456/"
install:
  type: steam_client
launch:
  type: steam
  executable_names: [Example-Win64-Shipping.exe]
automation: manual_start
legal:
  redistribution: forbidden
  note: "Downloaded only from Steam; no game assets are included."
```

Before opening a change:

1. Confirm the AppID on the official Steam store page.
2. Confirm it is a standalone benchmark and does not require the complete game.
3. Confirm the current rendered process name from an installed copy or public depot metadata.
4. Run `pytest` and `gamebench list`.
5. Link the authoritative sources in the change description.

`executable_names` is passed to PresentMon as one or more `--process_name` filters. Include the
actual renderer process rather than only a small launcher executable.

