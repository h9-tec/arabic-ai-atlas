# Arabic AI Atlas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `h9-tec/arabic-ai-atlas`: one YAML dataset of the Arabic AI ecosystem that generates an SVG landscape map, an awesome-style README, machine files, and an installable Claude Code plugin with an MCP server.

**Architecture:** `data/*.yaml` is the only hand-edited source. A small `atlas/` Python package loads, validates, enriches (HF metrics, cached), and renders three outputs (README, SVG, JSON/llms.txt). `scripts/build.py` is the single CLI used by humans and CI. `mcp/server.py` and `skills/` read the generated `dist/atlas.json`, never the network.

**Tech Stack:** Python 3.12 via `uv`, pyyaml, jsonschema, `mcp>=2,<3` (MCPServer API), pytest. SVG rendered with stdlib only. GitHub Actions for CI and nightly refresh.

**Spec:** `docs/superpowers/specs/2026-10-04-arabic-ai-atlas-design.md`

## Global Constraints

- Python `>=3.11`; all commands run through `uv run` (pyproject at repo root).
- `mcp>=2,<3`: import `from mcp.server.mcpserver import MCPServer`; `FastMCP` does not exist in 2.x.
- Map renderer uses stdlib only (no graphviz, no matplotlib).
- Every generated file (`README.md`, `assets/map.svg`, `dist/atlas.json`, `dist/llms.txt`) is deterministic for the same inputs: sorted by downloads desc then name, fixed `generated_at` passed in.
- MCP server and skills read `dist/atlas.json`; no network at runtime.
- Enrichment never fails the build: on any HF error keep the cached value and print a warning.
- Country enum: `SA AE EG QA MA JO TN LB KW OM BH INTL`. Type enum: `llm asr tts ocr embedding dataset tool benchmark org agent-skill`. Modality enum: `text speech vision multimodal none`. Dialect enum: `msa egy gulf lev magh iraqi sudanese yemeni classical mixed`.
- `notes` max 160 chars. `id` kebab-case `^[a-z0-9]+(-[a-z0-9]+)*$`, unique across all files.
- Licenses: MIT for code (`LICENSE`), CC BY 4.0 for `data/` (`LICENSE-DATA`).
- Plugin install flow (verified against Claude Code 2.1.289): `claude plugin marketplace add h9-tec/arabic-ai-atlas` then `claude plugin install arabic-ai-atlas@arabic-ai-atlas`. Repo root therefore needs both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
- Commit messages end with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

## Review Focus

1. Entry with no Hugging Face link: README shows `—` for downloads/updated, map node gets minimum size, nothing crashes. (Task 5, 6, 7)
2. HF API returns 429 or times out mid-run: previous cached metrics survive, warning printed, exit code 0. (Task 4)
3. Arabic or `&`/`<` characters in `name` or `notes`: SVG and Markdown stay well-formed (XML-escaped, pipes escaped). (Task 6, 7)
4. Duplicate `id` across two YAML files: validation error names both files. (Task 2)
5. `recommend()` with a task nobody matches, or a dialect filter on entries lacking `dialects`: returns an empty list or lower-scored entries, never raises. (Task 8)

---

### Task 1: Project scaffold

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `LICENSE`, `LICENSE-DATA`, `CLAUDE.md`, `atlas/__init__.py`, `tests/__init__.py`, `tests/test_smoke.py`

**Interfaces:**
- Produces: `uv run pytest` works; package `atlas` importable.

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "arabic-ai-atlas"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["pyyaml>=6", "jsonschema>=4.20", "mcp>=2,<3"]
[dependency-groups]
dev = ["pytest>=8"]
[tool.pytest.ini_options]
testpaths = ["tests"]
[tool.uv]
package = true
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["atlas"]
```

- [ ] **Step 2: Write `tests/test_smoke.py`** asserting `import atlas` works and `atlas.__version__ == "0.1.0"`.

- [ ] **Step 3: Run `uv run pytest -q`** → expected: 1 passed.

- [ ] **Step 4: Write `.gitignore`** (`.venv/`, `__pycache__/`, `.pytest_cache/`, `*.egg-info/`), `LICENSE` (MIT, holder "Hesham Haroon"), `LICENSE-DATA` (CC BY 4.0 notice pointing to creativecommons.org/licenses/by/4.0/), `CLAUDE.md` (three lines: data/ is source of truth; run `uv run python scripts/build.py all` after editing data; never hand-edit README.md, assets/, dist/).

- [ ] **Step 5: Commit** `chore: scaffold project`.

---

### Task 2: Schema, loader, validator

**Files:**
- Create: `data/schema.json`, `atlas/load.py`, `atlas/validate.py`, `tests/fixtures/data/{llms,tts,datasets}.yaml`, `tests/test_validate.py`

**Interfaces:**
- Produces: `load_entries(data_dir: Path) -> list[dict]` (each entry gets `_file: str` = basename); `validate_entries(entries: list[dict], schema: dict) -> list[str]` (empty list means valid; messages formatted `"{file}:{id}: {message}"`); `load_schema(path: Path) -> dict`.

- [ ] **Step 1: Write `data/schema.json`** — JSON Schema draft 2020-12 for ONE entry, fields and enums exactly as spec §3 and Global Constraints. `links` is an object with optional string keys `hf github paper website`, `minProperties: 1`, each value `format: uri` and pattern `^https?://`. `additionalProperties: false` except `_file` allowed.

- [ ] **Step 2: Write fixtures** — 6 entries total across the 3 fixture files: `jais-30b` (llm, AE, hf link, dialects [msa]), `allam-7b` (llm, SA, hf), `silma-9b` (llm, INTL, hf, on_device false), `fish-speech-ar` (tts, INTL, github only, no hf), `cidar` (dataset, SA, hf), `masader` (dataset, INTL, github only). Use realistic links.

- [ ] **Step 3: Write failing tests** in `tests/test_validate.py`:

```python
def test_load_merges_files_and_tags_source(fixture_dir):
    entries = load_entries(fixture_dir)
    assert len(entries) == 6
    assert {e["_file"] for e in entries} == {"llms.yaml", "tts.yaml", "datasets.yaml"}

def test_valid_fixture_passes(fixture_dir, schema):
    assert validate_entries(load_entries(fixture_dir), schema) == []

@pytest.mark.parametrize("field,value", [
    ("country", "XX"), ("type", "robot"), ("id", "Bad_ID"),
    ("notes", "x" * 161), ("links", {}), ("links", {"hf": "ftp://x"}),
])
def test_bad_field_fails(field, value, schema, good_entry):
    bad = {**good_entry, field: value}
    errs = validate_entries([bad], schema)
    assert len(errs) == 1 and errs[0].startswith("llms.yaml:")

def test_duplicate_ids_name_both_files(schema, good_entry):
    a = {**good_entry, "_file": "llms.yaml"}; b = {**good_entry, "_file": "tts.yaml"}
    errs = validate_entries([a, b], schema)
    assert any("llms.yaml" in e and "tts.yaml" in e and "duplicate id" in e for e in errs)
```

- [ ] **Step 4: Run `uv run pytest tests/test_validate.py -q`** → expected: FAIL, module not found.

- [ ] **Step 5: Implement `atlas/load.py`** (`load_entries` reads `*.yaml` in `data_dir` sorted, skips `schema.json` and dotfiles, each file is a YAML list) and `atlas/validate.py` (`load_schema`, `validate_entries` using `jsonschema.Draft202012Validator(schema).iter_errors`, plus duplicate-id pass producing `"{f1},{f2}:{id}: duplicate id"`).

- [ ] **Step 6: Run tests** → expected: all pass.

- [ ] **Step 7: Commit** `feat: data schema, loader and validator`.

---

### Task 3: Seed data from Awesome_Arabic_NLP

**Files:**
- Create: `atlas/seed.py`, `scripts/seed_from_awesome.py`, `tests/fixtures/awesome_sample.md`, `tests/test_seed.py`, `data/{llms,asr,tts,ocr,embeddings,datasets,tools,benchmarks,orgs,agent-skills}.yaml`

**Interfaces:**
- Consumes: Task 2 validator.
- Produces: `parse_tables(markdown: str) -> list[dict]` returning draft entries (schema-valid, `country` defaults `INTL`, `license` defaults `unknown`, `tasks` from a heading→tasks map).
- Produces: committed `data/*.yaml`, ≥180 entries, all validating.

- [ ] **Step 1: Write `tests/fixtures/awesome_sample.md`** — copy the LLM header + Jais row, ASR header + whisper row, Text Datasets header + masader row, UAE companies header + G42 row from `~/Awesome_Arabic_NLP/README.md` (lines 115-121, 221-226, 369-374, 564-568).

- [ ] **Step 2: Write failing tests**:

```python
def test_parse_llm_row(sample):
    e = next(x for x in parse_tables(sample) if x["id"] == "jais")
    assert e["type"] == "llm" and e["modality"] == "text"
    assert e["links"]["hf"] == "https://huggingface.co/inceptionai/jais-30b-v3"
    assert e["size"] == "13B, 30B" and e["org"] == "Inception AI, Cerebras"

def test_parse_company_under_country_heading(sample):
    e = next(x for x in parse_tables(sample) if x["id"] == "g42")
    assert e["type"] == "org" and e["country"] == "AE" and e["modality"] == "none"

def test_all_drafts_validate(sample, schema):
    assert validate_entries(parse_tables(sample), schema) == []
```

- [ ] **Step 3: Run** → FAIL.

- [ ] **Step 4: Implement `atlas/seed.py`**: walk lines, track current `##`/`###` heading; `HEADING_MAP` dict from heading substring → `(type, modality, tasks)` for every heading listed in the spec's source README (LLMs→llm/text/[chat]; Multimodal→llm/multimodal; Transformer-based→llm/text/[encoder]; Embedding→embedding; Task-Specific→tool? no: llm/text/[task-specific]; ASR→asr/speech/[asr]; TTS→tts/speech/[tts]; TTS Datasets→dataset/speech; OCR→ocr/vision/[ocr]; OCR tools→tool/vision; OCR Datasets→dataset/vision; Image Captioning→llm/multimodal; Diacritization Models→tool/text/[diacritization]; Diacritization Datasets→dataset/text; Dialect Shared Tasks→benchmark; Dialect Datasets→dataset; Text/Speech/Vision Datasets→dataset; Toolkits/Specialized/Translation→tool; Benchmarks→benchmark; Organizations/Institutions/Companies→org; country headings with flags → country code). Parse table rows with regex on `| **Name** | ... | [badge](url) |`; strip `**`; derive `id` via slugify(name); first link URL classified into `links.hf/github/paper/website` by host. Column meaning per heading: 2nd col is `size` for LLM tables, `notes` otherwise (truncate 160); `org` from "Developer"/"Developed By" column when present else heading org.

- [ ] **Step 5: Run tests** → PASS.

- [ ] **Step 6: Write `scripts/seed_from_awesome.py`**: args `--src ~/Awesome_Arabic_NLP/README.md --out data/`; groups drafts by type into the 10 files (`embedding`→`embeddings.yaml`, `agent-skill`→`agent-skills.yaml`); dedupes by id (keep first); writes YAML with `sort_keys=False`, `allow_unicode=True`.

- [ ] **Step 7: Run it**, then `uv run python -c "..."` to count entries and run `validate_entries`; fix drafts by hand until zero errors. Hand-pass: set `country` for the ~40 obvious Gulf/Egypt orgs and models (SDAIA/ALLaM→SA, G42/Inception/TII/MBZUAI→AE, QCRI→QA, Egyptian startups→EG); set `license` from HF where known; set `on_device: true` for models ≤3B. Add 6 starter `agent-skills.yaml` entries found via web search (Arabic MCP servers, Arabic skills; verify each URL returns 200 with `curl -sI`).

- [ ] **Step 8: Commit** `feat: seed ~200 entries from Awesome_Arabic_NLP` (include `scripts/seed_from_awesome.py`).

---

### Task 4: Hugging Face enrichment with cache

**Files:**
- Create: `atlas/enrich.py`, `tests/test_enrich.py`

**Interfaces:**
- Produces: `hf_id_from_url(url: str) -> str | None` (`https://huggingface.co/datasets/a/b` → `datasets/a/b`; `https://huggingface.co/a/b` → `a/b`; trailing paths/tree stripped); `fetch_hf_metrics(hf_ids: list[str], cache: dict, fetch=_default_fetch, now: str) -> tuple[dict, list[str]]` returning (updated cache, warnings); cache shape `{hf_id: {"downloads": int, "likes": int, "lastModified": "YYYY-MM-DD", "fetched": now}}`; `merge_metrics(entries, cache) -> list[dict]` adds `metrics` key (dict or `None`).
- `_default_fetch(hf_id) -> dict` GETs `https://huggingface.co/api/{models|datasets}/{id}?expand[]=downloads&expand[]=likes&expand[]=lastModified` with 10s timeout and `User-Agent: arabic-ai-atlas`.

- [ ] **Step 1: Write failing tests**:

```python
def test_hf_id_from_url_model_and_dataset():
    assert hf_id_from_url("https://huggingface.co/inceptionai/jais-30b-v3") == "inceptionai/jais-30b-v3"
    assert hf_id_from_url("https://huggingface.co/datasets/ARBML/CIDAR/tree/main") == "datasets/ARBML/CIDAR"
    assert hf_id_from_url("https://github.com/x/y") is None

def test_fetch_updates_cache_and_keeps_old_on_error():
    cache = {"a/b": {"downloads": 5, "likes": 1, "lastModified": "2026-01-01", "fetched": "2026-01-01"}}
    def fake(hf_id):
        if hf_id == "a/b": raise TimeoutError("boom")
        return {"downloads": 42, "likes": 3, "lastModified": "2026-09-30T10:00:00.000Z"}
    new, warns = fetch_hf_metrics(["a/b", "c/d"], cache, fetch=fake, now="2026-10-04")
    assert new["a/b"]["downloads"] == 5            # kept
    assert new["c/d"] == {"downloads": 42, "likes": 3, "lastModified": "2026-09-30", "fetched": "2026-10-04"}
    assert len(warns) == 1 and "a/b" in warns[0]

def test_merge_metrics_none_without_hf(fixture_entries):
    merged = merge_metrics(fixture_entries, {})
    assert all(e["metrics"] is None for e in merged if "hf" not in e["links"])
```

- [ ] **Step 2: Run** → FAIL. **Step 3: Implement.** **Step 4: Run** → PASS.

- [ ] **Step 5: Commit** `feat: HF metrics enrichment with cache`.

---

### Task 5: Machine outputs (atlas.json, llms.txt) and build CLI

**Files:**
- Create: `atlas/render_json.py`, `scripts/build.py`, `tests/test_render_json.py`, `tests/test_cli.py`

**Interfaces:**
- Consumes: Tasks 2 and 4.
- Produces: `build_atlas_json(merged: list[dict], generated_at: str) -> dict` with keys `generated_at`, `count`, `entries` (sorted by `(-(metrics.downloads or 0), name)`, `_file` removed); `build_llms_txt(merged, generated_at) -> str` (llms.txt format: `# Arabic AI Atlas`, blockquote summary, `## Models` / `## Datasets` / `## Tools & Benchmarks` / `## Organizations` / `## Agent Skills` sections, each line `- [name](primary_link): notes`, max 25 per section, then `## Optional` linking `dist/atlas.json`).
- Produces: `scripts/build.py` subcommands `validate`, `enrich`, `build`, `all` (= validate, enrich, build), `--date YYYY-MM-DD` override for determinism (default today UTC), `--skip-enrich` (use `data/.cache/hf.json` as is, no network), `--data data/ --out .`. `build` writes `dist/atlas.json`, `dist/llms.txt`, `README.md`, `assets/map.svg` (the last two land in Tasks 6 and 7; `build` calls their renderers once they exist, so wire them in those tasks). Exit code 1 on validation errors, 0 otherwise.

- [ ] **Step 1: Write failing tests**: `test_atlas_json_sorted_and_clean` (first entry has highest downloads; no `_file` keys; `count == 6`), `test_llms_txt_has_sections_and_links` (contains `## Models` and the Jais HF URL), `test_cli_validate_exit_code` (run `scripts/build.py validate --data tests/fixtures/data` via subprocess → returncode 0; with a broken temp copy → 1 and stderr contains `llms.yaml:`).

- [ ] **Step 2: Run** → FAIL. **Step 3: Implement.** **Step 4: Run** → PASS.

- [ ] **Step 5: Commit** `feat: atlas.json, llms.txt and build CLI`.

---

### Task 6: README renderer

**Files:**
- Create: `atlas/render_readme.py`, `templates/README.tmpl.md`, `tests/test_render_readme.py`, `tests/snapshots/README.md`
- Modify: `scripts/build.py` (wire `build` to write `README.md`)

**Interfaces:**
- Consumes: merged entries from Task 4.
- Produces: `render_readme(merged, template: str, generated_at: str, shipped_skills: list[dict]) -> str`. Template placeholders: `{{COUNT}}`, `{{DATE}}`, `{{TABLE:<type>}}` for each type, `{{SHIPPED_SKILLS}}`. `shipped_skills` = list of `{name, description, path}` read from `skills/*/SKILL.md` frontmatter by `load_shipped_skills(skills_dir) -> list[dict]` (returns `[]` if dir missing).
- Table columns per type: llm → `Name | Org | Country | Size | License | ⬇ Downloads | Updated | Links`; asr/tts/ocr/embedding → same minus Size; dataset → `Name | Org | Country | Size | License | ⬇ | Updated | Links`; tool/benchmark → `Name | Org | Country | License | Links | Notes`; org → `Name | Country | Focus (notes) | Links`; agent-skill → `Name | Org | Notes | Links`. Downloads formatted `1.2M / 340K / 980`; missing metrics → `—`. Links cell = badges in order hf, github, paper, website using the shields.io badge style from `~/Awesome_Arabic_NLP/README.md`. Markdown cells escape `|` as `\|`.

- [ ] **Step 1: Write `templates/README.tmpl.md`**: centered hero with `assets/map.svg`, tagline from spec §2, badges (awesome.re, `entries-{{COUNT}}`, `updated-{{DATE}}`, stars), "Install into your agent" code block with the two verified commands plus the MCP `.mcp.json` snippet for non-Claude clients, a 4-line "How this repo works" (YAML → CI → map/README/JSON/plugin), TOC, one `## ` section per type with its `{{TABLE:type}}`, `## 🧩 Arabic Agent Skills` containing `{{SHIPPED_SKILLS}}` then `{{TABLE:agent-skill}}`, Contributing (edit YAML, run build, open PR), License (MIT code / CC BY 4.0 data), "Sister project" link to Awesome_Arabic_NLP.

- [ ] **Step 2: Write failing tests**: `test_readme_matches_snapshot` (render fixtures with `generated_at="2026-10-04"`, compare to `tests/snapshots/README.md`; regenerate snapshot with `UPDATE_SNAPSHOTS=1`), `test_missing_metrics_show_dash` (the `fish-speech-ar` row contains `| — | — |`), `test_pipe_in_name_is_escaped` (entry named `A|B` renders `A\|B`), `test_ampersand_safe` (name `R&D Lab` appears verbatim).

- [ ] **Step 3: Run** → FAIL. **Step 4: Implement** `render_readme`, `load_shipped_skills`, `fmt_downloads(n: int | None) -> str`. **Step 5: Run** → PASS; generate snapshot once; re-run → PASS.

- [ ] **Step 6: Commit** `feat: README renderer and template`.

---

### Task 7: SVG map renderer

**Files:**
- Create: `atlas/render_map.py`, `tests/test_render_map.py`, `tests/snapshots/map.svg`
- Modify: `scripts/build.py` (wire `build` to write `assets/map.svg`)

**Interfaces:**
- Produces: `render_svg(merged, generated_at: str) -> str`.
- Layout constants: width 1600; columns in order `SA AE EG QA MA OTHER INTL` where `OTHER` = JO TN LB KW OM BH; rows (bands) in order `LLMs` (type llm), `Speech` (asr, tts), `Vision` (ocr), `Embeddings & Tools` (embedding, tool, benchmark), `Datasets` (dataset); orgs and agent-skills are not drawn. Per cell: top 8 by downloads then name; if more, last slot is a `+N more` node linking to `README.md#<section-anchor>`. Node area ∝ `log10(downloads+1)+1`, clamped to widths 90–220px, height 34px, 6px gap, flow-wrap inside cell. Each node `<a href="primary_link" target="_blank"><rect/><text/></a>`; label truncated to fit with `…`. Colors via CSS variables inside `<style>` with `@media (prefers-color-scheme: dark)` override. Footer text `Generated {generated_at} from {count} entries · github.com/h9-tec/arabic-ai-atlas`. All text XML-escaped. Empty cell shows nothing.

- [ ] **Step 1: Write failing tests**: `test_svg_matches_snapshot`, `test_svg_is_well_formed_xml` (parse with `xml.etree.ElementTree` an entry named `R&D <lab>`), `test_no_hf_entry_has_min_width` (rect for `fish-speech-ar` has `width="90"`), `test_cell_caps_at_8_with_more_node` (12 synthetic SA llm entries → 7 named nodes + one `+5 more`), `test_orgs_not_drawn`.

- [ ] **Step 2: Run** → FAIL. **Step 3: Implement.** **Step 4: Run** → PASS; snapshot generated.

- [ ] **Step 5: Render the real data** `uv run python scripts/build.py build --date 2026-10-04`, open `assets/map.svg` in a browser (`xdg-open`), check legibility at 900px width; adjust font size (start 13px) if labels clip. Commit generated outputs.

- [ ] **Step 6: Commit** `feat: SVG landscape map renderer`.

---

### Task 8: Query library and MCP server

**Files:**
- Create: `atlas/query.py`, `mcp/server.py`, `.mcp.json`, `tests/test_query.py`, `tests/test_mcp.py`

**Interfaces:**
- Produces (`atlas/query.py`, pure functions over `entries: list[dict]` as in `atlas.json`):
  - `search(entries, query: str, type: str | None = None, country: str | None = None, modality: str | None = None, limit: int = 10) -> list[dict]` — case-insensitive substring over name, org, notes, tasks, tags; filters are exact; order by downloads desc then name.
  - `recommend(entries, task: str, dialect: str | None = None, on_device: bool | None = None, license_filter: str | None = None, limit: int = 3) -> list[dict]` — score = 3·(task in tasks) + 2·(dialect in dialects) + 1·(task substring in notes); hard filters: `on_device` must equal when given; `license_filter="open"` excludes `proprietary`/`unknown`; entries with score 0 dropped; ties by downloads desc; each result gets `score` and `why: str`.
  - `get(entries, id: str) -> dict | None`.
- Produces (`mcp/server.py`): `MCPServer("arabic-ai-atlas")` with tools `search`, `recommend`, `get` (same params, return JSON-serialisable lists/dicts) reading `dist/atlas.json` located relative to `__file__` (`Path(__file__).resolve().parents[1] / "dist" / "atlas.json"`), loaded once at startup. `if __name__ == "__main__": server.run("stdio")`.
- `.mcp.json`: `{"mcpServers": {"arabic-ai-atlas": {"command": "uv", "args": ["run", "--directory", "${CLAUDE_PLUGIN_ROOT}", "python", "mcp/server.py"]}}}`.

- [ ] **Step 1: Write failing tests** `tests/test_query.py`: `test_search_by_org_case_insensitive`, `test_search_filter_type`, `test_recommend_ranks_task_and_dialect` (fixture: jais has dialects [msa], task chat → jais first with score 5 when dialect msa), `test_recommend_no_match_returns_empty`, `test_recommend_dialect_filter_tolerates_missing_dialects` (entries without `dialects` still returned with score 3), `test_recommend_license_open_excludes_unknown`, `test_get_missing_returns_none`.

- [ ] **Step 2: Run** → FAIL. **Step 3: Implement `atlas/query.py`.** **Step 4: Run** → PASS.

- [ ] **Step 5: Write failing `tests/test_mcp.py`**: builds a temp `dist/atlas.json` from fixtures, launches the server via `mcp.client.stdio.stdio_client(StdioServerParameters(command="uv", args=["run","python","mcp/server.py"], env={**os.environ, "ATLAS_JSON": tmp_path}))`, asserts `list_tools` names == `{"search","recommend","get"}` and `call_tool("get", {"id": "jais-30b"})` returns text containing `"jais-30b"`. (Server honours `ATLAS_JSON` env override for tests.) Verified pattern: `ClientSession(r, w)`, `await c.initialize()`.

- [ ] **Step 6: Run** → FAIL. **Step 7: Implement `mcp/server.py` and `.mcp.json`.** **Step 8: Run** → PASS.

- [ ] **Step 9: Commit** `feat: query library and MCP server`.

---

### Task 9: Plugin manifests and advisor skill

**Files:**
- Create: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `skills/arabic-ai-advisor/SKILL.md`

**Interfaces:**
- Consumes: `.mcp.json` from Task 8.
- Produces: `claude plugin validate .` passes.

- [ ] **Step 1: Write `.claude-plugin/plugin.json`**: `{"name": "arabic-ai-atlas", "version": "0.1.0", "description": "The Arabic AI ecosystem as a map, a list, and a skill your agent can install.", "author": {"name": "Hesham Haroon", "url": "https://github.com/h9-tec"}}`.

- [ ] **Step 2: Write `.claude-plugin/marketplace.json`** following the verified shape: `$schema` `https://www.schemastore.org/claude-code-marketplace.json`, `name: "arabic-ai-atlas"`, `owner.name`, `plugins: [{"name": "arabic-ai-atlas", "description": ..., "source": "./", "category": "development"}]`.

- [ ] **Step 3: Write `skills/arabic-ai-advisor/SKILL.md`**: frontmatter `name: arabic-ai-advisor`, `description: Use when choosing an Arabic LLM, ASR, TTS, OCR, embedding model, dataset or tool — recommends ranked options from the Arabic AI Atlas with licenses, dialect coverage and on-device fit.` Body: (1) if MCP tools `search/recommend/get` are available call `recommend` first; (2) otherwise read `${CLAUDE_PLUGIN_ROOT}/dist/atlas.json`; (3) answer format: 3 ranked options, each name, org, license, dialects, size, one-line why, link; (4) always state the atlas `generated_at` date; (5) never invent entries not in the atlas.

- [ ] **Step 4: Run `claude plugin validate .`** → expected: no errors. Fix any reported path issues.

- [ ] **Step 5: Run `uv run python scripts/build.py build --date 2026-10-04`** so README lists the shipped skill; commit `feat: Claude Code plugin manifests and advisor skill`.

---

### Task 10: Four Arabic agent skills

**Files:**
- Create: `skills/tashkeel-check/SKILL.md`, `skills/rtl-bidi-lint/SKILL.md`, `skills/rtl-bidi-lint/bidi_lint.py`, `skills/arabic-dialect-prompts/SKILL.md`, `skills/arabic-dialect-prompts/dialects.md`, `skills/arabic-token-cost/SKILL.md`, `skills/arabic-token-cost/token_cost.py`, `tests/test_skill_scripts.py`

**Interfaces:**
- `bidi_lint.py`: CLI `python bidi_lint.py <paths...>`; `lint_text(text: str) -> list[tuple[int, str, str]]` (line, code, message); codes: `MIXED_DIGITS` (Arabic-Indic and ASCII digits on one line), `UNBALANCED_ISOLATE` (U+2066–2068 without U+2069), `LTR_MARK_IN_ARABIC` (U+200E inside an Arabic run), `HARDCODED_LTR` (`dir="ltr"` on a line containing Arabic).
- `token_cost.py`: CLI `python token_cost.py --text "..." [--tokenizers id,id]`; default tokenizer ids: `gpt2`, `meta-llama/Llama-3.1-8B`, `Qwen/Qwen2.5-7B`, `inceptionai/jais-family-590m`, `google/gemma-2-2b`; prints a table `tokenizer | tokens | tokens/word | ratio vs English`. Uses `transformers` only if importable; otherwise prints an install hint and exits 2. Pure helper `fertility(token_count: int, text: str) -> float` = tokens / whitespace words.

- [ ] **Step 1: Write failing tests** `tests/test_skill_scripts.py`: `test_bidi_mixed_digits` (`"عدد 3 و ٤"` → `MIXED_DIGITS`), `test_bidi_unbalanced_isolate`, `test_bidi_clean_text_no_findings` (`"مرحبا بالعالم"` → `[]`), `test_fertility` (`fertility(10, "a b c d") == 2.5`).

- [ ] **Step 2: Run** → FAIL. **Step 3: Implement the two scripts.** **Step 4: Run** → PASS.

- [ ] **Step 5: Write the four SKILL.md files.** Each frontmatter `name` + one-sentence `description` beginning "Use when …". Bodies:
  - tashkeel-check: when to add/strip diacritics, how to detect partial tashkeel (regex `[ً-ْ]`), recommend tools via MCP `search(query="diacritization")`, 3-step procedure.
  - rtl-bidi-lint: run `python ${CLAUDE_PLUGIN_ROOT}/skills/rtl-bidi-lint/bidi_lint.py <files>`, explain each code with the fix (use U+2068/U+2069 isolates, unify digit system, `dir="auto"`).
  - arabic-dialect-prompts: table in `dialects.md` of the 10 dialect enum values × register, example system-prompt line per dialect in Arabic, common failure (model drifts to MSA) and the fix (few-shot in dialect, explicit "لا تستخدم الفصحى").
  - arabic-token-cost: run `token_cost.py`, interpret fertility (>2.5 tokens/word = expensive), recommend Arabic-aware tokenizers from the atlas via `search(query="tokenizer")`.

- [ ] **Step 6: Run `claude plugin validate .` and `uv run python scripts/build.py build --date 2026-10-04`**; confirm README "Arabic Agent Skills" lists 5 skills.

- [ ] **Step 7: Commit** `feat: tashkeel, bidi-lint, dialect-prompts and token-cost skills`.

---

### Task 11: CI workflows and contributor docs

**Files:**
- Create: `.github/workflows/validate.yml`, `.github/workflows/nightly.yml`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/add-resource.yml`

- [ ] **Step 1: Add `--check` to `scripts/build.py`** with a failing test `test_cli_check_detects_drift` (fixture build to a temp dir, edit one char in README.md, `build.py build --check --out tmp` → returncode 1 and stderr names `README.md`; unmodified → 0). `--check` renders in memory and compares with disk, ignoring lines that contain the `generated_at` date. Implement, run, PASS.

- [ ] **Step 1b: Write `validate.yml`**: on `pull_request` and `push` to `main`; `astral-sh/setup-uv@v5`, `uv sync`, `uv run pytest -q`, `uv run python scripts/build.py validate`, `uv run python scripts/build.py build --check --skip-enrich`.

- [ ] **Step 2: Write `nightly.yml`**: `schedule: cron "0 3 * * *"` + `workflow_dispatch`; `permissions: contents: write`; `uv run python scripts/build.py all --date "$(date -u +%F)"`; `git diff --quiet || (git config user.name github-actions[bot]; git config user.email 41898282+github-actions[bot]@users.noreply.github.com; git add -A; git commit -m "chore: nightly refresh $(date -u +%F)"; git push)`.

- [ ] **Step 3: Write `CONTRIBUTING.md`** (add an entry: pick the YAML file, copy the template entry, run `uv run python scripts/build.py all`, open PR; CI rejects hand-edited README), the PR template (checklist: YAML only, build ran, link verified), and the issue form with fields name/type/country/link/why.

- [ ] **Step 4: Run `uv run pytest -q`** → PASS. **Step 5: Commit** `ci: validation and nightly refresh workflows`.

---

### Task 12: Publish and cross-link

**Files:**
- Modify: `~/Awesome_Arabic_NLP/README.md` (top of file, after the banner)

- [ ] **Step 1: Authenticate** — needs the user: run `! gh auth login` in this session (browser flow). Stop and ask if not logged in.

- [ ] **Step 2: Create and push**: `gh repo create h9-tec/arabic-ai-atlas --public --source . --remote origin --description "The Arabic AI ecosystem as a map, a list, and a skill your agent can install." --push`; then `gh repo edit --add-topic arabic,arabic-nlp,llm,awesome,awesome-list,mcp,mcp-server,claude-code,agent-skills,speech,tts,asr`.

- [ ] **Step 3: Verify CI green**: `gh run watch` on the first push; fix and re-push if red.

- [ ] **Step 4: Install test on a clean path**: `claude plugin marketplace add h9-tec/arabic-ai-atlas && claude plugin install arabic-ai-atlas@arabic-ai-atlas`, then in a fresh `claude` session ask "which open Arabic TTS runs on device?" and confirm the MCP `recommend` tool is called. Record the exact working commands in README if they differ.

- [ ] **Step 5: Cross-link**: in `~/Awesome_Arabic_NLP/README.md` insert after the banner: the map image (raw GitHub URL of `assets/map.svg`) and one paragraph "🗺️ New: the Arabic AI Atlas — this list as a live map, JSON, and a Claude Code plugin → link". Commit `docs: link to Arabic AI Atlas` and push.

- [ ] **Step 6: Launch kit** (text files only, user posts them): write `docs/launch/x-thread.md` (6 tweets, first one is the map image + the install one-liner), `docs/launch/linkedin.md`, `docs/launch/hn-reddit.md` (Show HN title ≤80 chars, r/MachineLearning [P] post). Commit `docs: launch kit`.

---

## Self-review notes

- Spec §2 layout differs in one place: shared logic lives in `atlas/` package and `scripts/build.py` is one CLI instead of five scripts. Spec §4.1 "Other" column covers JO TN LB KW OM BH. Spec §5.1 install line replaced with the verified two-command marketplace flow. Spec §6 drift check implemented as `build.py --check`. Everything else maps 1:1: §3→Task 2/3, §4.1→7, §4.2→6, §4.3→5, §5.1→9/10, §5.2→8, §6→11, §7→12, §8→tests in each task, §9→12.
- Type consistency checked: `load_entries`, `validate_entries`, `merge_metrics`, `render_readme`, `render_svg`, `build_atlas_json`, `search/recommend/get` names are used identically across tasks.
