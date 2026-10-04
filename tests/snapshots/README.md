<div align="center">

<a href="https://h9-tec.github.io/arabic-ai-atlas/"><img src="assets/map.svg" alt="Arabic AI landscape map" width="100%"/></a>

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

## Contents

- [🧠 Large Language Models](#-large-language-models)
- [🎙️ Speech Recognition](#️-speech-recognition)
- [🔊 Text-to-Speech](#-text-to-speech)
- [📖 OCR](#-ocr)
- [🔤 Embeddings](#-embeddings)
- [📊 Datasets](#-datasets)
- [🔧 Tools](#-tools)
- [🏆 Benchmarks](#-benchmarks)
- [🏢 Organizations](#-organizations)
- [🧩 Arabic Agent Skills](#-arabic-agent-skills)
- [🤝 Contributing](#-contributing)

## 🧠 Large Language Models

| Name | Org | Country | Size | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ALLaM 7B | SDAIA | 🇸🇦 SA | 7B | apache-2.0 | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/humain-ai/ALLaM-7B-Instruct-preview) |
| Jais 30B | Inception AI | 🇦🇪 AE | 30B | apache-2.0 | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/inceptionai/jais-30b-v3) |
| SILMA 9B | SILMA AI | 🌍 INTL | 9B | gemma | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/silma-ai/SILMA-9B-Instruct-v1.0) |

## 🎙️ Speech Recognition

| Name | Org | Country | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- |

## 🔊 Text-to-Speech

| Name | Org | Country | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- |
| Fish Speech (Arabic) | Fish Audio | 🌍 INTL | cc-by-nc-sa-4.0 | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/fishaudio/fish-speech) |

## 📖 OCR

| Name | Org | Country | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- |

## 🔤 Embeddings

| Name | Org | Country | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- |

## 📊 Datasets

| Name | Org | Country | Size | License | ⬇ | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CIDAR | ARBML | 🇸🇦 SA | — | cc-by-4.0 | — | — | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/arbml/CIDAR) |
| Masader | ARBML | 🌍 INTL | — | mit | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/ARBML/masader) |

## 🔧 Tools

| Name | Org | Country | License | Links | Notes |
| --- | --- | --- | --- | --- | --- |

## 🏆 Benchmarks

| Name | Org | Country | License | Links | Notes |
| --- | --- | --- | --- | --- | --- |

## 🏢 Organizations

| Name | Country | Focus | Links |
| --- | --- | --- | --- |

## 🧩 Arabic Agent Skills

Skills shipped in this repo:

_No skills shipped yet._

Other Arabic agent skills in the wild:

| Name | Org | Notes | Links |
| --- | --- | --- | --- |

## 🤝 Contributing

1. Edit the YAML in `data/`.
2. Run `uv run python scripts/build.py build` (it uses the committed Hugging Face cache; the nightly job refreshes metrics).
3. Open a PR.

CI rejects hand edits to `README.md`, `assets/` and `dist/`.

## 📜 License

Code: MIT. Data: CC BY 4.0.

## 🔗 Sister project

[Awesome Arabic NLP](https://github.com/h9-tec/Awesome_Arabic_NLP), the curated reading list this atlas grew alongside.

---

_Generated 2026-10-04 from 6 entries. Do not edit README.md by hand._
