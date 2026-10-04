# Arabic AI Atlas — Design Spec

Date: 2026-10-04
Owner: h9-tec
Status: approved in conversation, pending written review

## 1. Goal

A GitHub repository that presents the Arabic AI ecosystem three ways from one
dataset: a generated SVG landscape map, an awesome-style README, and an
installable Claude Code plugin / MCP server so AI agents can query the list.
Success = trending on GitHub in its first two weeks, and becoming the default
reference an agent consults before picking an Arabic model, dataset or tool.

Non-goals (v1): running or benchmarking models, a hosted web app, a newsletter,
bilingual README (English only in v1, Arabic later).

## 2. Repository

- Name: `h9-tec/arabic-ai-atlas` (public, MIT for code, CC BY 4.0 for data).
- Tagline: "The Arabic AI ecosystem as a map, a list, and a skill your agent can install."
- Layout:

```
arabic-ai-atlas/
  data/                  # source of truth, hand-edited YAML
    llms.yaml asr.yaml tts.yaml ocr.yaml embeddings.yaml datasets.yaml
    tools.yaml benchmarks.yaml orgs.yaml agent-skills.yaml
    schema.json          # JSON Schema for one entry
  scripts/
    validate.py          # schema + uniqueness + link shape checks
    enrich.py            # pulls HF downloads/likes/lastModified into data/.cache/hf.json
    build_readme.py      # templates/README.tmpl.md + data -> README.md
    build_map.py         # data -> assets/map.svg
    build_json.py        # data -> dist/atlas.json, dist/llms.txt
  templates/README.tmpl.md
  assets/map.svg         # generated, committed
  dist/atlas.json        # generated, committed
  dist/llms.txt          # generated, committed
  .claude-plugin/plugin.json
  skills/
    arabic-ai-advisor/SKILL.md
    tashkeel-check/SKILL.md
    rtl-bidi-lint/SKILL.md
    arabic-dialect-prompts/SKILL.md
    arabic-token-cost/SKILL.md
  mcp/
    server.py            # FastMCP server, stdio
    pyproject.toml
  .mcp.json              # points at mcp/server.py via uv run
  .github/workflows/
    validate.yml         # on PR: validate + build, fail if generated files drift
    nightly.yml          # cron: enrich + build + commit if changed
  tests/
  CONTRIBUTING.md  LICENSE  LICENSE-DATA  README.md  CLAUDE.md
```

## 3. Data model

One YAML list per category file. Entry fields:

| field | type | required | notes |
|---|---|---|---|
| id | slug | yes | unique across all files, kebab-case |
| name | str | yes | display name |
| type | enum | yes | llm, asr, tts, ocr, embedding, dataset, tool, benchmark, org, agent-skill |
| org | str | yes | developer / maintainer |
| country | enum | yes | SA, AE, EG, QA, MA, JO, TN, LB, KW, OM, BH, INTL |
| tasks | list[str] | yes | e.g. chat, translation, diacritization, dialect-id |
| dialects | list[enum] | no | msa, egy, gulf, lev, magh, iraqi, sudanese, yemeni, classical, mixed |
| modality | enum | yes | text, speech, vision, multimodal, none |
| license | str | yes | SPDX id or "proprietary" / "unknown" |
| links | map | yes | at least one of hf, github, paper, website |
| size | str | no | "7B", "1.2GB", "500h" |
| on_device | bool | no | runs on a phone/laptop CPU |
| year | int | no | release year |
| notes | str | no | one sentence, max 160 chars |
| tags | list[str] | no | free-form |

Validation (CI, fails PR): schema conformance, id uniqueness, enum values, link
URL shape, notes length. Enrichment is read-only on data/: HF metrics live in
`data/.cache/hf.json` (committed) keyed by HF id.

Seeding: `scripts/seed_from_awesome.py` (one-off, kept in repo) parses the
Markdown tables of `~/Awesome_Arabic_NLP/README.md` into YAML drafts. Country
and type are inferred from section headings and org name, then hand-reviewed.
Target: ~200 entries at launch.

## 4. Generated outputs

### 4.1 Map (`assets/map.svg`)
- Grid: columns = countries (SA, AE, EG, QA, MA, Other, INTL), rows = modality
  bands (LLMs, Speech, Vision, Embeddings & Tools, Datasets & Benchmarks).
- Node = rounded rect with name; area scaled by log(HF downloads + 1), min size
  for entries without HF. Each node is an `<a href>` to its primary link.
- Deterministic layout (sorted by downloads desc, then name), pure Python,
  stdlib only. Light and dark variants via CSS `prefers-color-scheme` inside the SVG.
- Footer: "Generated YYYY-MM-DD from N entries · arabic-ai-atlas".
- Width 1600px; must stay legible when GitHub scales it to 900px.

### 4.2 README
- Hero: map image, one-line install block for the plugin, badges (awesome,
  entries count, last-updated, stars).
- One table per category, columns chosen per type (e.g. LLM: Name, Org,
  Country, Size, License, HF downloads, Updated, Links).
- "Arabic Agent Skills" section listing agent-skills.yaml entries plus the 5
  skills shipped in this repo.
- Fully generated from `templates/README.tmpl.md`; hand edits to README.md are
  rejected by CI drift check.

### 4.3 Machine outputs
- `dist/atlas.json`: all entries merged with HF metrics.
- `dist/llms.txt`: llms.txt format summary with links to atlas.json and README.

## 5. Agent surface

### 5.1 Claude Code plugin
- `.claude-plugin/plugin.json` with name `arabic-ai-atlas`, description, author.
- Install line in README: `claude plugin add h9-tec/arabic-ai-atlas` (verify
  exact syntax against current Claude Code docs during implementation; fall
  back to the marketplace-add flow if direct GitHub install is not supported).
- Skills (`skills/*/SKILL.md`, each with frontmatter name + description):
  - `arabic-ai-advisor`: given a task/dialect/constraints, read `dist/atlas.json`
    and recommend 3 ranked options with reasoning. Instructs the agent to prefer
    the MCP `recommend` tool when available, else read the JSON directly.
  - `tashkeel-check`: detect missing/inconsistent diacritics in Arabic text in
    the working tree, recommend tools from the atlas.
  - `rtl-bidi-lint`: find bidi/RTL pitfalls in UI strings and Markdown
    (mixed digits, unbalanced isolates, hard-coded LTR).
  - `arabic-dialect-prompts`: prompt patterns per dialect, with register notes.
  - `arabic-token-cost`: estimate token cost of Arabic text across tokenizers
    (reuses `~/arabic-tokenizer-arena` logic, vendored as a small script).

### 5.2 MCP server (`mcp/server.py`)
- Python ≥3.11, `mcp` SDK (FastMCP), stdio transport, launched by `uv run`.
- Tools:
  - `search(query, type?, country?, modality?, limit=10)`: substring + tag match.
  - `recommend(task, dialect?, on_device?, license_filter?, limit=3)`: scored
    ranking: task match ×3, dialect match ×2, on_device/license filters hard,
    tie-break by HF downloads.
  - `get(id)`: full entry.
- Reads `dist/atlas.json` from the repo; no network at runtime.
- `.mcp.json` at repo root so the plugin registers it automatically.

## 6. CI

- `validate.yml` on pull_request and push: `uv run scripts/validate.py`, then
  all build scripts, then `git diff --exit-code` on README.md, assets/, dist/.
  Runs tests.
- `nightly.yml` at 03:00 UTC: enrich (HF API, unauthenticated, ~250 calls),
  build, commit as `github-actions[bot]` if changed.
- HF API failures: keep previous cached values, log a warning, never fail the build.

## 7. Existing repo

`h9-tec/Awesome_Arabic_NLP` is unchanged except: map image + one paragraph
linking to the atlas added at the top. Done after the atlas is public.

## 8. Testing

- `tests/test_validate.py`: good entry passes, each bad field fails.
- `tests/test_build.py`: build from a 6-entry fixture, compare README and SVG
  to committed snapshots.
- `tests/test_mcp.py`: start server in-process, call all three tools, assert
  shapes and a known recommendation.
- `tests/test_seed.py`: parse a fixture Markdown table into expected YAML.

## 9. Launch checklist (part of plan, not CI)

1. Push repo, enable Pages off (not needed), add topics: arabic, nlp, llm,
   awesome, awesome-list, mcp, claude-code, agent-skills.
2. Verify plugin install on a clean machine.
3. Post: X thread with the map image, LinkedIn post, r/MachineLearning,
   Hugging Face forum, Arabic AI Discord/Telegram groups.
4. Submit to sindresorhus/awesome after 30 days (their rule).

## 10. Risks

- Plugin install syntax may differ from assumption; verify first thing.
- HF unauthenticated rate limits: batch requests, back off, cache.
- Map legibility at 200+ nodes: cap visible nodes per cell to top 8, show
  "+N more" linking to the README section.
