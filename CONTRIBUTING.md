# Contributing

## Add a resource

1. Pick the file under `data/` that matches the resource type (`llms.yaml`, `asr.yaml`, `tts.yaml`, `ocr.yaml`, `embeddings.yaml`, `datasets.yaml`, `tools.yaml`, `benchmarks.yaml`, `orgs.yaml`, `agent-skills.yaml`, `papers.yaml`).
2. Copy the template entry below to the end of that file and fill in the fields.
3. Run `uv run python scripts/build.py build` to validate and regenerate the README, map and dist files. It reads the committed Hugging Face cache and needs no network; do not run `all`, which refetches metrics and touches every row (the nightly job does that).
4. Open a pull request with the YAML change and the regenerated files.

## Entry template

```yaml
- id: my-resource            # unique, lowercase, hyphen-separated
  name: My Resource          # display name
  type: llm                  # llm | asr | tts | ocr | embedding | dataset | tool | benchmark | org | agent-skill | paper
  country: SA                # SA | AE | EG | QA | MA | JO | TN | LB | KW | OM | BH | DZ | LY | SD | IQ | SY | YE | PS | MR | SO | DJ | KM | INTL
  org: Example Lab           # maintaining organization
  license: apache-2.0        # SPDX id, or unknown
  modality: text             # text | speech | vision | multimodal | none
  tasks:                     # at least one free-text task
    - chat
  links:                     # at least one of hf, github, paper, website (full https:// URLs)
    hf: https://huggingface.co/example/my-resource
  size: 7B                   # optional: parameters or dataset size
  year: 2026                 # optional: release year (integer)
  on_device: false           # optional: true only if it runs on a phone or laptop CPU
  dialects:                  # optional: msa | egy | gulf | lev | magh | iraqi | sudanese | yemeni | classical | mixed
    - msa
  tags: []                   # optional: free-text tags
  notes: One short line.     # optional: at most 160 characters
  venue: ACL 2024            # optional (papers): "ACL 2024", "arXiv 2025", "Interspeech 2023"
  citations: 120             # optional (papers): integer citation count
```

For `type: paper`, `year` and `links.paper` (an arXiv or ACL Anthology URL) are required; `tasks` names the topic (`survey`, `pretraining`, `asr`, `benchmark`), `notes` is the one-line contribution, and `links.github` / `links.hf` may point to released artifacts. A paper qualifies if it is a peer-reviewed or arXiv paper about Arabic AI that is a survey, introduces a resource listed in the atlas, or is widely cited. Papers appear in the Papers list only, not on the maps.

## Rules

- One entry per real resource.
- Link to the authoritative source (the official repo, model card, or paper), not a mirror or a blog post.
- `notes` is at most 160 characters.
- `license` is a lowercase SPDX id (or the Hugging Face license id, such as `llama3.1` or `gemma`), or `unknown` when it is not stated. The build fills `unknown` from the Hugging Face model card when the card names a license.
- `country` is the country of the maintaining organization (`INTL` for multinational efforts).
- Set `on_device: true` only if it runs on a phone or laptop CPU.

## What CI checks

- Every entry passes the schema in `data/schema.json`.
- Ids are unique.
- The generated files match `data/` byte for byte (`build --check`), rendered with the `generated_at` date in `dist/atlas.json`. A hand edit anywhere in `README.md`, `docs/tables/`, `assets/` or `dist/` fails CI.

## Never edit by hand

`README.md`, `docs/tables/`, `assets/`, `dist/` and `data/.cache/` (including `assets/tree.svg`, `docs/tables/wanted.md` and `data/.cache/wanted.json`) are generated. Edit `data/` (or `templates/`) and run `uv run python scripts/build.py build`.

## Record a base model

Set `base_model` on a model entry (`llm`, `asr`, `tts`, `ocr` or `embedding` only) to say what it was trained from. It is a list of Hugging Face ids (`org/name`), atlas ids, or the literal `from-scratch`. Take it from the model card or the paper; when the YAML and the card disagree, the YAML wins. The build turns these links into the family tree and the MCP `lineage` tool.

```yaml
  base_model:
    - meta-llama/Llama-3.1-8B
```

## Propose or fill a wanted gap

`data/wanted.yaml` lists gaps the atlas does not yet fill. Each rule has:

- `id`: unique, lowercase, hyphen-separated.
- `title`: the short headline.
- `why`: at most 160 characters on why the gap matters.
- `query`: what a filling entry looks like. Fields: `type`, `country`, `dialects`, `license_class` (`open` or `any`), `on_device`, `tasks`. A list matches any of its values.

A rule is filled when any atlas entry matches its query, so you fill a gap by adding a matching entry under `data/`. CI prints `closes wanted:<id>` for each rule your PR fills. To propose a gap, add a rule. Never edit `data/.cache/wanted.json` by hand; the build writes it.

## Submit a model passport

Model passports are not accepted yet. The format and the probe suite are described in `probes/README.md` and in the [design spec](docs/superpowers/specs/2026-10-05-atlas-v0-2-design.md#d-model-passport-three-days--inference). Please do not open submission PRs until that page says otherwise.
