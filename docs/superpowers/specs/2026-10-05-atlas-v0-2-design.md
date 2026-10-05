# Arabic AI Atlas v0.2 — Design Spec

Date: 2026-10-05 · Owner: h9-tec · Status: approved in conversation (design presented 2026-10-04, approved 2026-10-05)

## Goal
Four features that turn the atlas from a list into an instrument: a Most-Wanted board (gaps as a rally point), a family tree (lineage of Arabic models), an "Arabic-ready" badge (growth loop through other repos), and Model Passports (measured capabilities). Delivered in that order so A and B ship first. Plugin version bumps to 0.2.0.

Baseline: 3,291 entries, 22-country enum, `paper` type, geographic map (static + live), README capped at 20 rows per section with full tables under docs/tables/, nightly refresh, drift-checked outputs.

## A. Most-Wanted board (half day)
- `data/wanted.yaml`: list of gap rules `{id, title, why (≤160), query: {type?, country?, dialects?, license_class?: open|any, on_device?: bool, tasks?}}`.
- Build evaluates each rule against the merged entries with the same semantics as `atlas.query` (license_class open = not proprietary/unknown and no "nc"). Unfilled rules render as `## 🎯 Most Wanted` in README (table: Gap · Why · Rule) and `docs/tables/wanted.md`; filled rules move to a "Recently filled" list for 30 days (store `filled_on` in the cache file `data/.cache/wanted.json`, not in YAML).
- CI on PRs: if a PR fills a rule, the validate job prints `closes wanted:<id>` in the job summary (`$GITHUB_STEP_SUMMARY`).
- Site: a "Most wanted" panel listing unfilled rules, each a deep link to the filtered map view that shows the gap.
- Seed 15 rules from the data (e.g. open commercial-license Gulf TTS, Moroccan OCR dataset, Sudanese ASR, Mauritanian anything, Yemeni dataset, on-device Arabic embedding, Iraqi TTS, Libyan corpus, Syrian LLM fine-tune, Palestinian ASR, Omani dialect dataset, Kuwaiti dataset, Bahraini dataset, Comoros/Djibouti/Somalia Arabic resource, open Arabic OCR benchmark for handwriting).

## B. Family tree (two days)
- Schema: optional `base_model: [str]` on model types (HF ids or atlas ids). Enrichment stores `cardData.base_model` / `base_model:` tags in the HF cache; merge rule: YAML value wins, cache fills gaps.
- `atlas/render_tree.py` → `assets/tree.svg`: roots are base families inferred by regex over base ids (llama, qwen, gemma, mistral, falcon, bert, electra, whisper, wav2vec, xlsr, mms, t5, bloom, phi, deepseek, from-scratch), edges to atlas models, node size by downloads, color by type, Arabic labels where available. Deterministic, stdlib only, light/dark.
- README section `## 🌳 Family tree` with the image and a stats table (models per root, most-reused datasets by `tasks`/`tags` mention). Site: a "Tree" view (D3 tree/force, vendored) with the same data; MCP tool `lineage(id)` returning ancestors and descendants from the JSON.
- Curated `base_model` for the ~40 best-known Arabic LLMs where cards omit it (ALLaM→Llama 2, SILMA→Gemma 2, Jais→from-scratch, Fanar→Gemma/from-scratch per card, AceGPT→Llama 2, NileChat→Qwen2.5, Atlas-Chat→Gemma 2, Falcon Arabic→Falcon3, etc.).

## C. Arabic-ready badge (two days)
- New repo `h9-tec/arabic-ready`: composite GitHub Action. Inputs: paths (default repo), strictness. Steps: run `rtl-bidi-lint` over text/Markdown/HTML/JSON/YAML string files; run `token_cost` on sampled Arabic strings if `transformers` is available (optional, off by default); check `dir=` attributes and `lang="ar"` in HTML; detect Arabic fonts in CSS. Output: score 0–100 and a JSON report; writes `arabic-ready.json` to the repo's `gh-pages` branch or a Gist (user-provided token), and the Action prints a shields.io endpoint badge Markdown: `https://img.shields.io/endpoint?url=<raw json url>` linking to the atlas.
- Atlas README gets `## 🏅 Arabic-ready repos` generated nightly from a GitHub code search for the badge URL (cached; unauthenticated search is rate-limited, so cap at 100 and dedupe).
- Ships with its own tests and a sample workflow snippet.

## D. Model Passport (three days + inference)
- `probes/`: 12 probes, each `probe.yaml` (prompt(s), checker type, expected) + `check.py`: tashkeel preservation, Arabic-Indic digits, dialect adherence (Egyptian/Gulf/Maghrebi), MSA drift under instruction, Quran quotation accuracy (exact match against a bundled verse table), code-switch handling, RTL punctuation, tokenizer fertility, refusal of hallucinated Arabic entities (uses the atlas: asks about 5 nonexistent models), translation sanity, summarization length control, JSON-in-Arabic output validity.
- `scripts/passport.py <model-id> [--endpoint URL]`: runs via `transformers` locally or an OpenAI-compatible endpoint; writes `data/.cache/passports/<id>.json` (per-probe pass/fail + raw outputs hash + date + runner). CI re-verifies submitted passports by re-running checkers on stored outputs (no inference in CI).
- Render: stamp strip per model row in README/tables (✓/✗ per probe, hover text in site), `passport` object in atlas.json, `recommend(min_passport=…)` filter. First run: the 20 most-downloaded open Arabic LLMs on the maintainer's machine.

## Shared
All generated outputs stay drift-checked; nightly job gains the tree and wanted outputs; site remains dependency-free beyond vendored libs; plugin 0.2.0; CONTRIBUTING documents `base_model`, `wanted.yaml`, and passport submission.

## Non-goals
Hosting inference, scoring closed APIs at scale, a newsletter, bilingual README.
