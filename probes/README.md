# Probes and model passports

Status: model passports are **not accepted yet**. Please do not open submission PRs. This page documents the format so the first probes can be reviewed. Remaining work is tracked in [the follow-up spec](../docs/superpowers/specs/2026-10-05-model-passport-followup.md); design in [section D](../docs/superpowers/specs/2026-10-05-atlas-v0-2-design.md#d-model-passport-three-days--inference).

## Probe format

One folder per probe under `probes/`, named after its id:

- `probe.yaml` with keys `id` (matches the folder name), `title`, `prompts` (list of strings), `checker` (module name in the same folder, without `.py`) and `expected` (mapping passed to the checker).
- `<checker>.py` exposing `check(output: str, expected: dict) -> bool`. Stdlib only, no inference, deterministic.

Current probes: `arabic-indic-digits`.

## Passport format

A JSON file:

```json
{
  "model": "org/name",
  "date": "2026-10-05",
  "runner": "transformers",
  "results": {
    "arabic-indic-digits": {"pass": true, "outputs": ["..."]}
  }
}
```

Planned location: `data/.cache/passports/<id>.json` (naming for ids containing `/` is an open question).

## Verifying

```bash
uv run python scripts/passport.py verify path/to/passport.json
```

Re-runs each probe's `check` on the stored outputs and reports any probe whose stored `pass` disagrees, or whose id is unknown. Exit 1 on any message. No inference happens here.

`scripts/passport.py run <model-id>` is not implemented: it prints the follow-up spec path and exits 2.
