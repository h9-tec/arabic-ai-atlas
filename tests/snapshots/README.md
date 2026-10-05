<div align="center">

<a href="https://h9-tec.github.io/arabic-ai-atlas/"><img src="assets/geo.svg" alt="Map of the Arabic AI ecosystem: entries per Arab country, with one bubble per entry type sized by downloads" width="100%"/></a>

**[Open the interactive map →](https://h9-tec.github.io/arabic-ai-atlas/)** · search, filter by dialect or license, share a filtered link.

# Arabic AI Atlas

**The Arabic AI ecosystem as a map, a list, and a skill your agent can install.**

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
![Entries](https://img.shields.io/badge/entries-6-0A7E8C)
![Updated](https://img.shields.io/badge/updated-2026--10--04-555)
[![Stars](https://img.shields.io/github/stars/h9-tec/arabic-ai-atlas?style=flat)](https://github.com/h9-tec/arabic-ai-atlas/stargazers)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

## Install into your agent

```bash
claude plugin marketplace add h9-tec/arabic-ai-atlas
claude plugin install arabic-ai-atlas@arabic-ai-atlas
```

Requires [uv](https://docs.astral.sh/uv/) on PATH.

Then ask Claude: *which open Arabic TTS runs on a phone?* It answers from this atlas via the `recommend` MCP tool.

<details>
<summary>Any MCP client</summary>

Add this to your `.mcp.json`:

```json
{"mcpServers": {"arabic-ai-atlas": {"command": "uv", "args": ["run", "--frozen", "--no-dev", "--directory", "/path/to/arabic-ai-atlas", "python", "mcp/server.py"]}}}
```

</details>

## How this repo works

- YAML in `data/` is the only hand-edited source.
- CI validates every PR against `data/schema.json`.
- A nightly job pulls Hugging Face downloads and regenerates the map, README, `dist/atlas.json` and `dist/llms.txt`.
- The repo is itself a Claude Code plugin: 5 skills + an MCP server that reads the atlas offline.

### Entries by country

| Country | Entries | LLM | ASR | TTS | OCR | Embedding | Datasets | Tools | Benchmarks | Papers | Orgs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 🌍 [International](https://h9-tec.github.io/arabic-ai-atlas/#country=INTL) | 3 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| 🇸🇦 [Saudi Arabia](https://h9-tec.github.io/arabic-ai-atlas/#country=SA) | 2 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| 🇦🇪 [United Arab Emirates](https://h9-tec.github.io/arabic-ai-atlas/#country=AE) | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Grid view

The same atlas as a country-by-type grid, with the most downloaded entries named in each cell.

<a href="https://h9-tec.github.io/arabic-ai-atlas/#view=grid"><img src="assets/map.svg" alt="Arabic AI landscape grid: entries by country and type" width="100%"/></a>

## Contents

- [🌳 Family tree](#-family-tree)
- [🧠 Large Language Models](#-large-language-models)
- [🎙️ Speech Recognition](#️-speech-recognition)
- [🔊 Text-to-Speech](#-text-to-speech)
- [📖 OCR](#-ocr)
- [🔤 Embeddings](#-embeddings)
- [📊 Datasets](#-datasets)
- [🔧 Tools](#-tools)
- [🏆 Benchmarks](#-benchmarks)
- [📄 Papers](#-papers)
- [🏢 Organizations](#-organizations)
- [🧩 Arabic Agent Skills](#-arabic-agent-skills)
- [🎯 Most Wanted](#-most-wanted)
- [🤝 Contributing](#-contributing)

## 🧠 Large Language Models

_3 entries · [all on the map](https://h9-tec.github.io/arabic-ai-atlas/#type=llm) · [full table](docs/tables/llm.md)_

| Name | Org | Country | Size | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ALLaM 7B | SDAIA | 🇸🇦 SA | 7B | apache-2.0 | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/humain-ai/ALLaM-7B-Instruct-preview) |
| Jais 30B | Inception AI | 🇦🇪 AE | 30B | apache-2.0 | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/inceptionai/jais-30b-v3) |
| SILMA 9B | SILMA AI | 🌍 INTL | 9B | gemma | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/silma-ai/SILMA-9B-Instruct-v1.0) |

## 🎙️ Speech Recognition

_0 entries · [all on the map](https://h9-tec.github.io/arabic-ai-atlas/#type=asr) · [full table](docs/tables/asr.md)_

| Name | Org | Country | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- |

## 🔊 Text-to-Speech

_1 entries · [all on the map](https://h9-tec.github.io/arabic-ai-atlas/#type=tts) · [full table](docs/tables/tts.md)_

| Name | Org | Country | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- |
| Fish Speech (Arabic) | Fish Audio | 🌍 INTL | cc-by-nc-sa-4.0 | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/fishaudio/fish-speech) |

## 📖 OCR

_0 entries · [all on the map](https://h9-tec.github.io/arabic-ai-atlas/#type=ocr) · [full table](docs/tables/ocr.md)_

| Name | Org | Country | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- |

## 🔤 Embeddings

_0 entries · [all on the map](https://h9-tec.github.io/arabic-ai-atlas/#type=embedding) · [full table](docs/tables/embedding.md)_

| Name | Org | Country | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- |

## 📊 Datasets

_2 entries · [all on the map](https://h9-tec.github.io/arabic-ai-atlas/#type=dataset) · [full table](docs/tables/dataset.md)_

| Name | Org | Country | Size | License | ⬇ | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CIDAR | ARBML | 🇸🇦 SA | — | cc-by-4.0 | — | — | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/arbml/CIDAR) |
| Masader | ARBML | 🌍 INTL | — | mit | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/ARBML/masader) |

## 🔧 Tools

_0 entries · [all on the map](https://h9-tec.github.io/arabic-ai-atlas/#type=tool) · [full table](docs/tables/tool.md)_

| Name | Org | Country | License | Links | Notes |
| --- | --- | --- | --- | --- | --- |

## 🏆 Benchmarks

_0 entries · [all on the map](https://h9-tec.github.io/arabic-ai-atlas/#type=benchmark) · [full table](docs/tables/benchmark.md)_

| Name | Org | Country | License | Links | Notes |
| --- | --- | --- | --- | --- | --- |

## 📄 Papers

_0 entries · [all on the map](https://h9-tec.github.io/arabic-ai-atlas/#type=paper) · [full table](docs/tables/paper.md)_

| Title | Venue | Year | Topic | Links |
| --- | --- | --- | --- | --- |

## 🏢 Organizations

_0 entries · [all on the map](https://h9-tec.github.io/arabic-ai-atlas/#type=org) · [full table](docs/tables/org.md)_

| Name | Country | Focus | Links |
| --- | --- | --- | --- |

## 🧩 Arabic Agent Skills

Skills shipped in this repo:

_No skills shipped yet._

Other Arabic agent skills in the wild:

_0 entries · [all on the map](https://h9-tec.github.io/arabic-ai-atlas/#type=agent-skill) · [full table](docs/tables/agent-skill.md)_

| Name | Org | Notes | Links |
| --- | --- | --- | --- |

## 🎯 Most Wanted

_Gaps nobody has filled yet. Add an entry that matches a rule and it moves to Recently filled. Rules live in [data/wanted.yaml](data/wanted.yaml)._

| Gap | Why | Rule |
| --- | --- | --- |
| [Fixture open rule A](https://h9-tec.github.io/arabic-ai-atlas/#type=asr&country=MR) | Unmatched by any fixture entry. | `type=asr · country=MR` |
| [Fixture open rule B](https://h9-tec.github.io/arabic-ai-atlas/#type=ocr&dialect=sudanese) | Unmatched by any fixture entry. | `type=ocr · dialects=sudanese` |

**Recently filled:**

- Fixture filled rule, filled 2026-10-04 by jais-30b

## 🌳 Family tree



## 🤝 Contributing

1. Edit the YAML in `data/`.
2. Run `uv run python scripts/build.py build` (it uses the committed Hugging Face cache; the nightly job refreshes metrics).
3. Open a PR.

CI rejects hand edits to `README.md`, `docs/tables/`, `assets/` and `dist/`.

## 📜 License

Code: MIT. Data: CC BY 4.0.

## 🔗 Sister project

[Awesome Arabic NLP](https://github.com/h9-tec/Awesome_Arabic_NLP), the curated reading list this atlas grew alongside.

---

_Generated 2026-10-04 from 6 entries. Do not edit README.md by hand._
