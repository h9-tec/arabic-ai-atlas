<div align="center">

<img src="assets/map.svg" alt="Arabic AI landscape map" width="100%"/>

# Arabic AI Atlas

**The Arabic AI ecosystem as a map, a list, and a skill your agent can install.**

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
![Entries](https://img.shields.io/badge/entries-{{COUNT}}-0A7E8C)
![Updated](https://img.shields.io/badge/updated-{{DATE_BADGE}}-555)
[![Stars](https://img.shields.io/github/stars/h9-tec/arabic-ai-atlas?style=flat)](https://github.com/h9-tec/arabic-ai-atlas/stargazers)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

## Install into your agent

```bash
claude plugin marketplace add h9-tec/arabic-ai-atlas
claude plugin install arabic-ai-atlas@arabic-ai-atlas
```

Then ask Claude: *which open Arabic TTS runs on a phone?* It answers from this atlas via the `recommend` MCP tool.

<details>
<summary>Any MCP client</summary>

Add this to your `.mcp.json`:

```json
{"mcpServers": {"arabic-ai-atlas": {"command": "uv", "args": ["run", "--directory", "/path/to/arabic-ai-atlas", "python", "mcp/server.py"]}}}
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

{{TABLE:llm}}

## 🎙️ Speech Recognition

{{TABLE:asr}}

## 🔊 Text-to-Speech

{{TABLE:tts}}

## 📖 OCR

{{TABLE:ocr}}

## 🔤 Embeddings

{{TABLE:embedding}}

## 📊 Datasets

{{TABLE:dataset}}

## 🔧 Tools

{{TABLE:tool}}

## 🏆 Benchmarks

{{TABLE:benchmark}}

## 🏢 Organizations

{{TABLE:org}}

## 🧩 Arabic Agent Skills

Skills shipped in this repo:

{{SHIPPED_SKILLS}}

Other Arabic agent skills in the wild:

{{TABLE:agent-skill}}

## 🤝 Contributing

1. Edit the YAML in `data/`.
2. Run `uv run python scripts/build.py all`.
3. Open a PR.

CI rejects hand edits to `README.md`, `assets/` and `dist/`.

## 📜 License

Code: MIT. Data: CC BY 4.0.

## 🔗 Sister project

[Awesome Arabic NLP](https://github.com/h9-tec/Awesome_Arabic_NLP), the curated reading list this atlas grew alongside.

---

_Generated {{DATE}} from {{COUNT}} entries. Do not edit README.md by hand._
