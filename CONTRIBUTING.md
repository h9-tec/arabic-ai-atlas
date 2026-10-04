# Contributing

## Add a resource

1. Pick the file under `data/` that matches the resource type (`llms.yaml`, `asr.yaml`, `tts.yaml`, `ocr.yaml`, `embeddings.yaml`, `datasets.yaml`, `tools.yaml`, `benchmarks.yaml`, `orgs.yaml`, `agent-skills.yaml`).
2. Copy the template entry below to the end of that file and fill in the fields.
3. Run `uv run python scripts/build.py build` to validate and regenerate the README, map and dist files. It reads the committed Hugging Face cache and needs no network; do not run `all`, which refetches metrics and touches every row (the nightly job does that).
4. Open a pull request with the YAML change and the regenerated files.

## Entry template

```yaml
- id: my-resource            # unique, lowercase, hyphen-separated
  name: My Resource          # display name
  type: llm                  # llm | asr | tts | ocr | embedding | dataset | tool | benchmark | org | agent-skill
  country: SA                # SA | AE | EG | QA | MA | JO | TN | LB | KW | OM | BH | INTL
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
```

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
- The generated files match `data/` byte for byte (`build --check`), rendered with the `generated_at` date in `dist/atlas.json`. A hand edit anywhere in `README.md`, `assets/` or `dist/` fails CI.

## Never edit by hand

`README.md`, `assets/` and `dist/` are generated. Edit `data/` (or `templates/`) and run `uv run python scripts/build.py build`.
