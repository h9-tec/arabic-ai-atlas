<div align="center">

<img src="assets/map.svg" alt="Arabic AI landscape map" width="100%"/>

# Arabic AI Atlas

**The Arabic AI ecosystem as a map, a list, and a skill your agent can install.**

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
![Entries](https://img.shields.io/badge/entries-271-0A7E8C)
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
| AraBERTv02 | AUB MIND Lab | 🇱🇧 LB | — | unknown | 555K | 2024-03-26 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/aubmindlab/bert-base-arabertv02) |
| Phi-4 | Microsoft | 🌍 INTL | 4B | mit | 449K | 2026-07-14 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/microsoft/phi-4) |
| Llama 3.3 | Meta | 🌍 INTL | 70B | llama3.3 | 399K | 2024-12-21 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) |
| opus-mt-ar-en | Helsinki-NLP | 🌍 INTL | — | apache-2.0 | 133K | 2023-08-16 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/Helsinki-NLP/opus-mt-ar-en) |
| MARBERTv2 | UBC-NLP | 🌍 INTL | — | unknown | 104K | 2022-03-30 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/UBC-NLP/MARBERTv2) |
| opus-mt-en-ar | Helsinki-NLP | 🌍 INTL | — | apache-2.0 | 27K | 2023-08-16 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/Helsinki-NLP/opus-mt-en-ar) |
| Fanar-1-9B | QCRI | 🇶🇦 QA | 9B | apache-2.0 | 11K | 2025-07-15 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/QCRI/Fanar-1-9B-Instruct) |
| Falcon Arabic | TII (UAE) | 🇦🇪 AE | 7B | falcon-llm-license | 11K | 2025-05-31 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/tiiuae/Falcon3-7B-Instruct) |
| ALLaM | SDAIA & IBM | 🇸🇦 SA | 7B | apache-2.0 | 11K | 2025-07-14 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/ALLaM-AI/ALLaM-7B-Instruct-preview) |
| AraT5 | UBC-NLP | 🌍 INTL | — | unknown | 3K | 2024-05-16 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/UBC-NLP/AraT5-base) |
| Ar-stablelm-2-chat | Stability AI | 🇸🇦 SA | 1.6B | other | 2K | 2024-06-03 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/stabilityai/stablelm-2-1_6b-chat) |
| AraELECTRA | AUB MIND Lab | 🇱🇧 LB | — | unknown | 2K | 2024-10-29 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/aubmindlab/araelectra-base-discriminator) |
| Cohere Command-A | Cohere | 🌍 INTL | 111B | cc-by-nc-4.0 | 2K | 2025-10-30 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/CohereForAI/c4ai-command-a-03-2025) |
| SILMA 1.0 | SILMA AI | 🇸🇦 SA | 9B | gemma | 1K | 2025-06-25 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/silma-ai/SILMA-9B-Instruct-v1.0) |
| Command R7B Arabic | Cohere | 🌍 INTL | 7B | cc-by-nc-4.0 | 1K | 2025-10-30 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/CohereLabs/c4ai-command-r7b-arabic-02-2025) |
| SILMA Kashif | SILMA AI | 🇸🇦 SA | 2B | gemma | 1K | 2025-06-11 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/silma-ai/SILMA-Kashif-2B-Instruct-v1.0) |
| CAMeLBERT-MSA-Sentiment | CAMeL Lab, NYUAD | 🇦🇪 AE | — | apache-2.0 | 696 | 2021-10-17 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/CAMeL-Lab/bert-base-arabic-camelbert-msa-sentiment) |
| SaudiBERT | King Saud University | 🇸🇦 SA | — | cc-by-nc-4.0 | 518 | 2024-05-23 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/faisalq/SaudiBERT) |
| NileChat-3B | UBC-NLP | 🌍 INTL | 3B | qwen-research | 361 | 2026-05-11 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/UBC-NLP/NileChat-3B) |
| t5-arabic-summarization | malmarjeh | 🌍 INTL | — | unknown | 342 | 2023-07-01 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/malmarjeh/t5-arabic-text-summarization) |
| ArabianGPT | Prince Sultan University | 🇸🇦 SA | 0.1B | apache-2.0 | 334 | 2024-02-27 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/riotu-lab/ArabianGPT-01B) |
| Yehia | Navid-AI | 🌍 INTL | 7B | apache-2.0 | 297 | 2026-01-06 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/Navid-AI/Yehia-7B) |
| JASMINE | UBC-NLP | 🌍 INTL | 0.3B-6.7B | unknown | 266 | 2024-05-01 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/UBC-NLP/Jasmine-350M) |
| GLiNER Arabic | NAMAA-Space | 🇸🇦 SA | — | apache-2.0 | 257 | 2025-04-13 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/NAMAA-Space/gliner_arabic-v2.1) |
| AraGPT2 | AUB MIND Lab | 🇱🇧 LB | 1.5B | other | 227 | 2024-10-24 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/aubmindlab/aragpt2-mega) |
| Masrawy Translator | NAMAA-Space | 🇸🇦 SA | — | cc-by-4.0 | 185 | 2025-01-27 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/NAMAA-Space/masrawy-english-to-egyptian-arabic-translator-v2.9) |
| arabic-gec-v1 | alnnahwi | 🌍 INTL | — | gemma | 137 | 2025-06-15 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/alnnahwi/gemma-3-1b-arabic-gec-v1) |
| EgyBERT | Faisal Qarah | 🇸🇦 SA | — | cc-by-nc-4.0 | 130 | 2024-08-19 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/faisalq/EgyBERT) |
| Noon | Naseej | 🇸🇦 SA | 7B | bigscience-bloom-rail-1.0 | 129 | 2023-06-21 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/Naseej/noon-7b) |
| Peacock | UBC-NLP | 🌍 INTL | 7B | other | 108 | 2024-11-25 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/UBC-NLP/Peacock) |
| SambaLingo-Arabic | SambaNova | 🌍 INTL | 7B, 70B | llama2 | 88 | 2024-04-16 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/sambanovasystems/SambaLingo-Arabic-Chat) |
| Calme 2.2 | MaziyarPanahi | 🌍 INTL | 72B | tongyi-qianwen | 43 | 2024-09-15 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/MaziyarPanahi/calme-2.2-qwen2-72b) |
| SA-BERT-V1 | Omartificial-Intelligence-Space | 🇸🇦 SA | — | apache-2.0 | 39 | 2025-11-28 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/Omartificial-Intelligence-Space/SA-BERT-V1) |
| Arabic-Text-Correction | SuperSl6 | 🌍 INTL | — | apache-2.0 | 27 | 2025-02-03 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/SuperSl6/Arabic-Text-Correction) |
| Dallah | UBC-NLP | 🌍 INTL | — | unknown | 24 | 2024-11-25 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/UBC-NLP/dallah) |
| Jais | Inception AI, Cerebras | 🇦🇪 AE | 13B, 30B | apache-2.0 | 20 | 2024-09-11 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/inceptionai/jais-30b-v3) |
| arat5-dialects-translation | PRAli22 | 🌍 INTL | — | apache-2.0 | 18 | 2024-03-01 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/PRAli22/arat5-arabic-dialects-translation) |
| blip-Arabic-flickr-8k | omarsabri8756 | 🌍 INTL | — | mit | 11 | 2025-05-10 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/omarsabri8756/blip-Arabic-flickr-8k) |
| AceGPT | FreedomIntelligence | 🌍 INTL | 7B | apache-2.0 | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/FreedomIntelligence/AceGPT) |
| AIN | MBZUAI | 🇦🇪 AE | 8B | mit | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/mbzuai-oryx/AIN) |
| ALLaM 34B | HUMAIN (Saudi) | 🇸🇦 SA | 34B | unknown | — | — | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.humain.com/en/news/humain-chat-launch) |
| ALLaM-2 | SDAIA & IBM | 🇸🇦 SA | 7B-70B | unknown | — | — | [![HF](https://img.shields.io/badge/-Hub-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/ALLaM-AI) |
| AraBERT | AUB MIND Lab | 🇱🇧 LB | — | unknown | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/aub-mind/arabert) |
| AraLLaMA | Bashar Talafha | 🌍 INTL | 7B | unknown | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/bashar-talafha/AraLLaMA) |
| Arcee-Meraj | Arcee AI | 🌍 INTL | 72B | unknown | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/arcee-ai/Arcee-Meraj) |
| Arcee-Meraj-Mini | Arcee AI | 🌍 INTL | 7B | unknown | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/arcee-ai/Arcee-Meraj-Mini) |
| Atlas-Chat | MBZUAI-Paris Lab | 🇦🇪 AE | 2B-27B | unknown | — | — | [![HF](https://img.shields.io/badge/-Collection-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/collections/MBZUAI-Paris/atlas-chat) |
| Aya-Expanse | Cohere | 🌍 INTL | 8B-32B | unknown | — | — | [![HF](https://img.shields.io/badge/-Collection-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/collections/CohereForAI/c4ai-aya-expanse-66f573116fef65271be752e9) |
| CAMeLBERT | CAMeL Lab, NYUAD | 🇦🇪 AE | — | mit | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/CAMeL-Lab/CAMeLBERT) |
| Falcon-H1-Arabic | TII (UAE) | 🇦🇪 AE | 3B-34B | unknown | — | — | [![HF](https://img.shields.io/badge/-Collection-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/collections/tiiuae/falcon-h1-6819f2795bc4d0b25a2567e3) |
| Fanar Star | QCRI (Qatar) | 🇶🇦 QA | 7B | unknown | — | — | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.fanar.qa/en) |
| Gemma 3 | Google | 🌍 INTL | 1B-27B | unknown | — | — | [![HF](https://img.shields.io/badge/-Collection-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/collections/google/gemma-3-release-67c6c6f89c4f76621268bb6d) |
| GemmAr | ClusterlabAi | 🌍 INTL | 7B | unknown | — | — | [![Paper](https://img.shields.io/badge/-Paper-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2407.02147) |
| Karnak | ITIDA (Egypt) | 🇪🇬 EG | 30B-70B | unknown | — | — | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://itida.gov.eg/English/PressReleases/Pages/egypt-national-ai-karnak-llm-launch-Ai-Everything-MEA-2026.aspx) |
| Kawn | Misraj AI (Saudi) | 🇸🇦 SA | — | unknown | — | — | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://misraj.ai/) |
| Kuwain | Misraj AI | 🇸🇦 SA | 1.5B | unknown | — | — | [![Paper](https://img.shields.io/badge/-Paper-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2504.15120) |
| Labess Chat | Linagora | 🌍 INTL | 7B | unknown | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/Linagora/Labess-chat-7b) |
| LlamAr | ClusterlabAi | 🌍 INTL | 8B | unknown | — | — | [![Paper](https://img.shields.io/badge/-Paper-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2407.02147) |
| MARBERT | UBC-NLP | 🌍 INTL | — | unknown | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/UBC-NLP/marbert) |
| Mistral Saba | Mistral | 🌍 INTL | 24B | unknown | — | — | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://mistral.ai/news/mistral-saba) |
| Mulhem | SDAIA | 🇸🇦 SA | — | unknown | — | — | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://sdaia.gov.sa/) |
| Mutarjim | Misraj AI | 🇸🇦 SA | 1.5B | unknown | — | — | [![Paper](https://img.shields.io/badge/-Paper-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2505.17894) |
| Nile-Chat | MBZUAI-Paris Lab | 🇦🇪 AE | 4B-12B | unknown | — | — | [![HF](https://img.shields.io/badge/-Collection-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/collections/MBZUAI-Paris/nile-chat) |
| NOOR | TII (UAE) | 🇦🇪 AE | 10B | unknown | — | — | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://noor.tii.ae/) |
| Nuha | Elm (Saudi) | 🇸🇦 SA | — | unknown | — | — | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://elm.sa/en/about-us/why-elm/case-studies/Pages/Nuha-Bridging-Technology-and-Arabic-Culture.aspx) |
| Qalam | UBC-NLP | 🌍 INTL | — | unknown | — | — | [![Paper](https://img.shields.io/badge/-Paper-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2407.13559) |
| Qwen 3 | Alibaba | 🌍 INTL | 0.6B-235B | unknown | — | — | [![HF](https://img.shields.io/badge/-Collection-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/collections/Qwen/qwen3-67dd247413f0e2e4f653967f) |
| Shahin | malhajar | 🌍 INTL | 14B | unknown | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/malhajar/Shahin-v0.1-14B) |

## 🎙️ Speech Recognition

| Name | Org | Country | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- |
| whisper-large-v3-turbo | OpenAI | 🌍 INTL | mit | 6.3M | 2024-10-04 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/openai/whisper-large-v3-turbo) |
| openai/whisper-large-v3 | OpenAI | 🌍 INTL | apache-2.0 | 4.1M | 2024-08-12 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/openai/whisper-large-v3) |
| wav2vec2-large-xlsr-53-arabic | jonatasgrosman | 🌍 INTL | apache-2.0 | 1.5M | 2022-12-14 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/jonatasgrosman/wav2vec2-large-xlsr-53-arabic) |
| MMS-1b-all | Meta | 🌍 INTL | cc-by-nc-4.0 | 304K | 2023-06-15 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/facebook/mms-1b-all) |
| SeamlessM4T v2 | Meta | 🌍 INTL | cc-by-nc-4.0 | 284K | 2024-01-04 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/facebook/seamless-m4t-v2-large) |
| Voxtral Mini | Mistral AI | 🌍 INTL | apache-2.0 | 179K | 2025-07-28 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507) |
| Whisper Quran | Tarteel AI | 🌍 INTL | apache-2.0 | 24K | 2022-12-13 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/tarteel-ai/whisper-base-ar-quran) |
| NVIDIA FastConformer Arabic (Diacritics) | NVIDIA | 🌍 INTL | cc-by-4.0 | 1K | 2025-10-21 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/nvidia/stt_ar_fastconformer_hybrid_large_pcd_v1.0) |
| NVIDIA FastConformer Arabic | NVIDIA | 🌍 INTL | cc-by-4.0 | 892 | 2025-10-23 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/nvidia/stt_ar_fastconformer_hybrid_large_pc_v1.0) |
| Whisper Arabic (small) | ayoubkirouane | 🌍 INTL | apache-2.0 | 397 | 2023-09-19 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/ayoubkirouane/whisper-small-ar) |
| EgypTalk-ASR-v2 | NAMAA-Space | 🇸🇦 SA | cc-by-4.0 | 220 | 2025-08-09 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/NAMAA-Space/EgypTalk-ASR-v2) |
| HuBERT Egyptian Arabic | Omar Adel, Alexandria University | 🇪🇬 EG | cc-by-nc-4.0 | 190 | 2023-03-19 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/omarxadel/hubert-large-arabic-egyptian) |
| MasriSwitch-Gemma3n | oddadmix | 🇪🇬 EG | apache-2.0 | 83 | 2026-04-17 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/oddadmix/MasriSwitch-Gemma3n-Transcriber-v1) |
| artst_asr_v3 | MBZUAI | 🇦🇪 AE | cc-by-nc-4.0 | 78 | 2025-09-10 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/MBZUAI/artst_asr_v3) |
| HuBERT-Large Arabic | asafaya | 🌍 INTL | mit | 73 | 2022-12-26 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/asafaya/hubert-large-arabic-transcribe) |
| SpeechBrain wav2vec2 Arabic | SpeechBrain | 🌍 INTL | apache-2.0 | 50 | 2024-02-26 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/speechbrain/asr-wav2vec2-commonvoice-14-ar) |
| KalemaTech Arabic STT | Salama1429 | 🌍 INTL | apache-2.0 | 38 | 2022-12-28 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/Salama1429/KalemaTech-Arabic-STT-ASR-based-on-Whisper-Small) |
| Klaam | ARBML | 🇸🇦 SA | mit | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/ARBML/klaam) |
| Whisper Egyptian Arabic | MAdel121 | 🌍 INTL | apache-2.0 | 0 | 2025-05-21 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/MAdel121/whisper-medium-egy) |

## 🔊 Text-to-Speech

| Name | Org | Country | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- |
| XTTS-v2 | Coqui | 🌍 INTL | coqui-public-model-license | 6.7M | 2023-12-11 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/coqui/XTTS-v2) |
| facebook/mms-tts-ara | Meta | 🌍 INTL | cc-by-nc-4.0 | 6K | 2023-09-01 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/facebook/mms-tts-ara) |
| speecht5_tts_clartts_ar | MBZUAI | 🇦🇪 AE | cc-by-nc-4.0 | 1K | 2025-09-10 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/MBZUAI/speecht5_tts_clartts_ar) |
| Arabic-TTS-Spark | IbrahimSalah | 🌍 INTL | fair-noncommercial-research-license | 830 | 2025-11-27 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/IbrahimSalah/Arabic-TTS-Spark) |
| Arabic MMS Speech Synthesis | SeyedAli | 🌍 INTL | cc-by-nc-4.0 | 136 | 2023-09-20 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/SeyedAli/Arabic-Speech-synthesis-MMS) |
| F5-TTS-Arabic | IbrahimSalah | 🌍 INTL | unknown | 99 | 2025-11-13 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/IbrahimSalah/F5-TTS-Arabic) |
| LLMVoX | MBZUAI | 🇦🇪 AE | cc-by-nc-sa-4.0 | 28 | 2025-03-16 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/MBZUAI/LLMVoX) |
| Arabic Tacotron TTS | yoosif0 | 🌍 INTL | mit | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/yoosif0/arabic-tacotron-tts) |
| Arabic-F5-TTS-v2 | IbrahimSalah | 🌍 INTL | fair-noncommercial-research-license | 0 | 2025-11-13 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/IbrahimSalah/Arabic-F5-TTS-v2) |
| Piper TTS | Rhasspy | 🌍 INTL | mit | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/rhasspy/piper) |
| tts-arabic-pytorch | nipponjo | 🌍 INTL | unknown | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/nipponjo/tts-arabic-pytorch) |
| tts_arabic (ONNX) | nipponjo | 🌍 INTL | unknown | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/nipponjo/tts_arabic) |

## 📖 OCR

| Name | Org | Country | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- |
| Arabic-English-handwritten-OCR-v3 | sherif1313 | 🌍 INTL | apache-2.0 | 1K | 2025-12-29 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/sherif1313/Arabic-English-handwritten-OCR-v3) |
| Qari-OCR-0.1-VL-2B-Instruct | NAMAA-Space | 🇸🇦 SA | apache-2.0 | 189 | 2025-06-10 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/NAMAA-Space/Qari-OCR-0.1-VL-2B-Instruct) |
| arabic-small-nougat | MohamedRashad | 🌍 INTL | gpl-3.0 | 121 | 2024-11-28 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/MohamedRashad/arabic-small-nougat) |
| arabic-large-nougat | MohamedRashad | 🌍 INTL | gpl-3.0 | 101 | 2024-11-28 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/MohamedRashad/arabic-large-nougat) |
| AtlasOCR | atlasia | 🇲🇦 MA | unknown | 0 | 2025-09-16 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/atlasia/AtlasOCR) |
| Baseer | Misraj | 🇸🇦 SA | unknown | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/Misraj/Baseer-Qwen2.5-VL-3B-Instruct) |
| DIMI-Arabic-OCR | AhmedZaky1 | 🌍 INTL | apache-2.0 | 0 | 2025-10-08 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/AhmedZaky1/DIMI-Arabic-OCR) |
| QARI-OCR v0.2 | NAMAA-Space | 🇸🇦 SA | unknown | — | — | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/NAMAA-Space/Qari-OCR-0.2-VL-2B-Instruct) |

## 🔤 Embeddings

| Name | Org | Country | License | ⬇ Downloads | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- |
| GATE-AraBert-v1 | Omartificial-Intelligence-Space | 🇸🇦 SA | apache-2.0 | 14K | 2025-09-07 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/Omartificial-Intelligence-Space/GATE-AraBert-v1) |
| asafaya/bert-base-arabic | asafaya | 🌍 INTL | unknown | 12K | 2023-03-17 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/asafaya/bert-base-arabic) |
| Arabic-Triplet-Matryoshka-V2 | Omartificial-Intelligence-Space | 🇸🇦 SA | apache-2.0 | 6K | 2025-09-07 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/Omartificial-Intelligence-Space/Arabic-Triplet-Matryoshka-V2) |
| DIMI-embedding | AhmedZaky1 | 🌍 INTL | apache-2.0 | 86 | 2025-05-30 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/AhmedZaky1/DIMI-embedding-matryoshka-arabic) |
| ModernBERT-Arabic | BounharAbdelaziz | 🌍 INTL | unknown | 3 | 2024-12-29 | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/BounharAbdelaziz/ModernBERT-Arabic-Embeddings) |
| Swan | UBC-NLP | 🌍 INTL | unknown | — | — | [![Paper](https://img.shields.io/badge/-Paper-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2411.01192) |

## 📊 Datasets

| Name | Org | Country | Size | License | ⬇ | Updated | Links |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SARD | riotu-lab | 🇸🇦 SA | — | cc-by-nc-nd-4.0 | 56K | 2026-05-20 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/riotu-lab/SARD) |
| Mixed Arabic Datasets (MAD) | M-A-D | 🌍 INTL | — | unknown | 2K | 2023-10-16 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/M-A-D/Mixed-Arabic-Datasets-Repo) |
| 101 Billion Arabic Words | ClusterlabAi | 🌍 INTL | — | apache-2.0 | 2K | 2024-06-16 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/ClusterlabAi/101_billion_arabic_words_dataset) |
| arabic-img2md | MohamedRashad | 🌍 INTL | — | gpl-3.0 | 840 | 2024-11-28 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/MohamedRashad/arabic-img2md) |
| ArVoice | MBZUAI | 🇦🇪 AE | — | cc-by-4.0 | 781 | 2025-10-31 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/MBZUAI/ArVoice) |
| ArabicText-Large | Jr23xd23 | 🌍 INTL | — | apache-2.0 | 773 | 2025-10-27 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/Jr23xd23/ArabicText-Large) |
| ClArTTS | MBZUAI | 🇦🇪 AE | — | cc-by-4.0 | 769 | 2025-10-01 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/MBZUAI/ClArTTS) |
| Egyptian Arabic ASR Clean | MAdel121 | 🌍 INTL | — | unknown | 668 | 2025-05-04 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/MAdel121/arabic-egy-cleaned) |
| Arabic-OpenHermes-2.5 | 2A2I | 🌍 INTL | — | apache-2.0 | 641 | 2024-03-15 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/2A2I/Arabic-OpenHermes-2.5) |
| CIDAR | ARBML | 🇸🇦 SA | — | apache-2.0 | 460 | 2025-07-01 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/arbml/CIDAR) |
| Arabic-VLM-Full-Pearl | MohamedRashad | 🌍 INTL | — | unknown | 443 | 2025-12-08 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/MohamedRashad/Arabic-VLM-Full-Pearl) |
| Arabic Speech Corpus | halabi2016 | 🌍 INTL | — | cc-by-4.0 | 417 | 2024-08-14 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/halabi2016/arabic_speech_corpus) |
| Shifaa Medical | Ahmed Selem | 🇪🇬 EG | — | apache-2.0 | 394 | 2025-02-28 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/Ahmed-Selem/Shifaa_Arabic_Medical_Consultations) |
| ArabicWeb24 | lightonai | 🌍 INTL | — | odc-by | 392 | 2024-09-23 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/lightonai/ArabicWeb24) |
| KFUPM Arabic AI Text Detection | KFUPM-JRCAI | 🇸🇦 SA | — | unknown | 383 | 2026-05-22 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/KFUPM-JRCAI/arabic-generated-abstracts) |
| Arabic Tweets | Mohammad Albarham | 🌍 INTL | — | cc-by-4.0 | 304 | 2023-04-08 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/pain/Arabic-Tweets) |
| Arabic-English Code-Switching | MohamedRashad | 🌍 INTL | — | gpl | 272 | 2024-07-04 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/MohamedRashad/arabic-english-code-switching) |
| SADA | SDAIA | 🇸🇦 SA | — | cc-by-4.0 | 254 | 2024-09-12 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/m6011/sada2022) |
| Arabic POS Dialect | QCRI | 🇶🇦 QA | — | apache-2.0 | 235 | 2024-01-09 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/QCRI/arabic_pos_dialect) |
| Arabic Billion Words | MohamedRashad | 🌍 INTL | — | unknown | 211 | 2023-12-16 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/MohamedRashad/arabic-billion-words) |
| Arabic_Function_Calling | HeshamHaroon | 🌍 INTL | — | apache-2.0 | 199 | 2025-12-14 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/HeshamHaroon/Arabic_Function_Calling) |
| BAREC Corpus | CAMeL Lab, NYUAD | 🇦🇪 AE | — | cc-by-sa-4.0 | 177 | 2025-09-02 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/CAMeL-Lab/BAREC-Corpus-v1.0) |
| Rasaif | ImruQays | 🌍 INTL | — | cc-by-4.0 | 166 | 2024-03-22 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/ImruQays/Rasaif-Classical-Arabic-English-Parallel-texts) |
| QADI | Abdelrahman-Rezk | 🌍 INTL | — | unknown | 139 | 2022-05-17 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/Abdelrahman-Rezk/Arabic_Dialect_Identification) |
| Shifaa Mental Health | Ahmed Selem | 🇪🇬 EG | — | apache-2.0 | 137 | 2025-03-08 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/Ahmed-Selem/Shifaa_Arabic_Mental_Health_Consultations) |
| MADIS5 | badrex | 🌍 INTL | — | cc | 122 | 2025-06-02 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/badrex/MADIS5-spoken-arabic-dialects) |
| palm | UBC-NLP | 🌍 INTL | — | cc-by-nc-nd-4.0 | 103 | 2025-10-28 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/UBC-NLP/palm) |
| SADA22 (MSA) | badrex | 🌍 INTL | — | cc-by-nc-sa-4.0 | 101 | 2025-05-12 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/badrex/arabic-speech-SADA22-MSA) |
| The Arabic E-Book Corpus | mohres | 🌍 INTL | — | cc-by-4.0 | 98 | 2024-06-09 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/mohres/The_Arabic_E-Book_Corpus) |
| arabic-hate-speech-superset | manueltonneau | 🌍 INTL | — | unknown | 72 | 2024-11-28 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/manueltonneau/arabic-hate-speech-superset) |
| Alpaca Arabic Instruct | Yasbok | 🌍 INTL | — | unknown | 59 | 2024-04-21 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/Yasbok/Alpaca_arabic_instruct) |
| Arabic Reasoning Dataset | Omartificial-Intelligence-Space | 🇸🇦 SA | — | apache-2.0 | 52 | 2024-12-01 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/Omartificial-Intelligence-Space/Arabic_Reasoning_Dataset) |
| NileChat Arabizi-Egypt | UBC-NLP | 🌍 INTL | — | cc-by-nc-4.0 | 49 | 2025-11-11 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/UBC-NLP/nilechat-arabizi-egy) |
| Egyptian Dialogue | fr3on | 🌍 INTL | — | cc-by-4.0 | 45 | 2025-12-22 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/fr3on/egyptian-dialogue) |
| PEARL | UBC-NLP | 🌍 INTL | — | cc-by-nc-nd-4.0 | 42 | 2025-10-27 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/UBC-NLP/PEARL) |
| NileChat LHV-Egypt | UBC-NLP | 🌍 INTL | — | cc-by-nc-4.0 | 40 | 2025-11-11 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/UBC-NLP/nilechat-lhv-egy) |
| STMC | Faisal Qarah | 🇸🇦 SA | — | cc-by-nc-4.0 | 37 | 2024-05-08 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/faisalq/STMC) |
| Arabic Dialects to MSA | PRAli22 | 🌍 INTL | — | afl-3.0 | 35 | 2024-03-01 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/PRAli22/Arabic_dialects_to_MSA) |
| Arabic-Image-Captioning_100M | Misraj | 🇸🇦 SA | — | unknown | 20 | 2026-09-17 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/Misraj/Arabic-Image-Captioning_100M) |
| ArabicCorpus2B | tarekeldeeb | 🌍 INTL | — | other | 7 | 2022-12-14 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/tarekeldeeb/ArabicCorpus2B) |
| Arabic-OCR-Dataset | mssqpi | 🌍 INTL | — | unknown | — | — | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/mssqpi/Arabic-OCR-Dataset) |
| arabic-text-diacritization | AliOsm | 🌍 INTL | — | mit | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/AliOsm/arabic-text-diacritization) |
| ArabicaQA | DataScienceUIBK | 🌍 INTL | — | mit | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/DataScienceUIBK/ArabicaQA) |
| Calliar | ARBML | 🇸🇦 SA | — | mit | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/ARBML/Calliar) |
| Casablanca | UBC-NLP | 🌍 INTL | — | unknown | — | — | [![Paper](https://img.shields.io/badge/-Paper-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2410.04527) |
| dialogue-arabic-dialects | tareknaous | 🌍 INTL | — | mit | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/tareknaous/dialogue-arabic-dialects) |
| Gazelle | UBC-NLP | 🌍 INTL | — | unknown | — | — | [![HF](https://img.shields.io/badge/-Paper-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/papers/2410.18163) |
| masader | ARBML | 🇸🇦 SA | — | gpl-3.0 | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/ARBML/masader) |
| Misraj-DocOCR Benchmark | Misraj | 🇸🇦 SA | — | unknown | — | — | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/Misraj/Misraj-DocOCR-Benchmark) |
| Open-Source Arabic TTS Benchmark | SILMA AI | 🇸🇦 SA | — | unknown | — | — | [![HF](https://img.shields.io/badge/-Space-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/spaces/silma-ai/opensource-arabic-tts-benchmark) |
| SawtArabi | unknown | 🌍 INTL | — | unknown | — | — | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.isca-archive.org/interspeech_2025/lodagala25_interspeech.pdf) |
| Tashkeela | Anwarvic | 🌍 INTL | — | unknown | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/Anwarvic/Arabic-Tashkeela-Model) |
| Wojood | SinaLab | 🌍 INTL | — | mit | — | — | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/SinaLab/ArabicNER) |

## 🔧 Tools

| Name | Org | Country | License | Links | Notes |
| --- | --- | --- | --- | --- | --- |
| arabic-stop-words | mohataher | 🌍 INTL | mit | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/mohataher/arabic-stop-words) | Largest list of Arabic stop words |
| arabic_vocalizer | nipponjo | 🌍 INTL | mit | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/nipponjo/arabic_vocalizer) | Deep-learning diacritization (ONNX format) |
| arabicprocess | unknown | 🌍 INTL | unknown | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://pypi.org/project/arabicprocess/) | Python library for Arabic preprocessing |
| camel_tools | CAMeL Lab, NYUAD | 🇦🇪 AE | mit | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/CAMeL-Lab/camel_tools) | Suite of Arabic NLP tools (morphology, POS, NER, etc.) |
| CATT | Abjad AI | 🌍 INTL | unknown | [![Paper](https://img.shields.io/badge/-Paper-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2407.03236) | Character-based Tashkeel Transformer, SOTA results |
| EasyOCR | JaidedAI | 🌍 INTL | apache-2.0 | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/JaidedAI/EasyOCR) | Ready-to-use OCR with Arabic support (80+ languages) |
| Farasa | QCRI | 🇶🇦 QA | unknown | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://farasa.qcri.org/) | Fast and accurate Arabic text processing toolkit |
| Fine-Tashkeel | unknown | 🌍 INTL | unknown | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.researchgate.net/publication/372616004) | Fine-tuned ByT5, 40% WER reduction |
| MADAMIRA | CAMeL Lab, NYUAD | 🇦🇪 AE | unknown | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://nyuad.nyu.edu/en/research/faculty-labs-and-projects/computational-approaches-to-modeling-language-lab/research/morphological-analysis-of-arabic.html) | Morphological analysis, diacritization, POS tagging |
| Maha | TRoboto | 🌍 INTL | bsd-3-clause | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/TRoboto/Maha) | Text processing library for Arabic text |
| Mishkal | linuxscout | 🌍 INTL | gpl-3.0 | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/linuxscout/mishkal) | Rule-based diacritizer with dictionary lookups |
| PaddleOCR | PaddlePaddle | 🌍 INTL | apache-2.0 | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/PaddlePaddle/PaddleOCR) | High-performance multilingual OCR with Arabic support |
| PyArabic | linuxscout | 🌍 INTL | gpl-3.0 | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/linuxscout/pyarabic) | Python package for Arabic text manipulation |
| Qalsadi | linuxscout | 🌍 INTL | unknown | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/linuxscout/qalsadi) | Arabic morphological analyzer and lemmatizer |
| qawafi | ARBML | 🇸🇦 SA | mit | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/ARBML/qawafi) | Arabic poetry analysis |
| Sadeed | Misraj AI | 🇸🇦 SA | unknown | [![Paper](https://img.shields.io/badge/-Paper-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2504.21635) | Small language model for diacritization |
| Shakkala | AliOsm | 🌍 INTL | mit | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/AliOsm/shakkelha) | Neural vocalization using bidirectional LSTM |
| SinaTools | SinaLab | 🌍 INTL | mit | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/SinaLab/sinatools) | Open source toolkit by SinaLab (Python APIs, CLI) |
| Tesseract OCR | Tesseract OCR | 🌍 INTL | apache-2.0 | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/tesseract-ocr/tesseract) | Open-source OCR engine with Arabic language packs |
| tkseem | ARBML | 🇸🇦 SA | mit | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/ARBML/tkseem) | Arabic Tokenization |
| tnkeeh | ARBML | 🇸🇦 SA | mit | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/ARBML/tnkeeh) | Arabic text cleaning, normalization, preprocessing |

## 🏆 Benchmarks

| Name | Org | Country | License | Links | Notes |
| --- | --- | --- | --- | --- | --- |
| ArabicMMLU | MBZUAI | 🇦🇪 AE | cc-by-nc-4.0 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/MBZUAI/ArabicMMLU) | Multi-task language understanding from school exams |
| ArabicRAGB | HeshamHaroon | 🌍 INTL | cc-by-sa-4.0 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/HeshamHaroon/ArabicRAGB) | Arabic RAG Benchmark (multi-dialect) |
| SILMA RAGQA Benchmark | SILMA AI | 🇸🇦 SA | apache-2.0 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/silma-ai/silma-rag-qa-benchmark-v1.0) | Evaluates Arabic/English LMs in Extractive QA tasks |
| ACVA | FreedomIntelligence | 🌍 INTL | apache-2.0 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/FreedomIntelligence/ACVA-Arabic-Cultural-Value-Alignment) | Arabic Cultural Value Alignment (8000+ questions, 58 areas) |
| Arabic Broad Benchmark (ABB) | SILMA AI | 🇸🇦 SA | apache-2.0 | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/silma-ai/arabic-broad-benchmark) | Comprehensive evaluation tool for Arabic LLMs |
| ALUE | Mawdoo3 | 🇯🇴 JO | unknown | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.alue.org/) | Arabic Language Understanding Evaluation benchmark |
| Arabic Broad Leaderboard (ABL) | SILMA AI | 🇸🇦 SA | unknown | [![HF](https://img.shields.io/badge/-Space-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/spaces/silma-ai/Arabic-LLM-Broad-Leaderboard) | NextGen evaluation for Arabic LLMs by SILMA AI |
| AraDiCE | QCRI | 🇶🇦 QA | unknown | [![Paper](https://img.shields.io/badge/-Paper-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2409.11404) | Benchmarks for dialectal and cultural capabilities of LLMs |
| BALSAM | King Salman Global Academy for Arabic Language | 🇸🇦 SA | unknown | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://benchmarks.ksaa.gov.sa/) | Benchmark of Arabic Language AI Systems and Models |
| GATmath and GATLc | unknown | 🌍 INTL | unknown | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0329129) | Benchmarks from Saudi GAT exams |
| KITAB-Bench | MBZUAI | 🇦🇪 AE | unknown | [![HF](https://img.shields.io/badge/-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/MBZUAI/KITAB-Bench) | Arabic OCR benchmark: 8,809 samples, 9 domains, 36 sub-domains (MBZUAI) |
| MTEB Arabic Leaderboard | MTEB | 🌍 INTL | unknown | [![HF](https://img.shields.io/badge/-Space-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/spaces/mteb/leaderboard) | Massive Text Embedding Benchmark for Arabic |
| NADI 2024 | UBC-NLP | 🌍 INTL | unknown | [![Paper](https://img.shields.io/badge/-Paper-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2407.04910) | NADI 2024 - Fifth Nuanced Arabic Dialect Identification |
| NADI 2025 | UBC-NLP | 🌍 INTL | unknown | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://nadi.dlnlp.ai/2025/) | NADI 2025 - Multidialectal Arabic Speech Processing (8-way dialect + ASR) |
| NADI Shared Tasks | UBC-NLP | 🌍 INTL | unknown | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://nadi.dlnlp.ai/) | NADI Shared Tasks - Ongoing series of Arabic DID shared tasks |
| Open Arabic LLM Leaderboard | OALL | 🌍 INTL | unknown | [![HF](https://img.shields.io/badge/-Space-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/spaces/OALL/Open-Arabic-LLM-Leaderboard) | Evaluation of Arabic LLMs across multiple benchmarks |
| Open Universal Arabic ASR Leaderboard | Elm Research Center | 🇸🇦 SA | unknown | [![HF](https://img.shields.io/badge/-Space-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/spaces/elmresearchcenter/open_universal_arabic_asr_leaderboard) | Multi-dialectal Arabic speech recognition benchmark |

## 🏢 Organizations

| Name | Country | Focus | Links |
| --- | --- | --- | --- |
| King Saud University | 🇸🇦 SA | SaudiBERT, Saudi dialect corpora (STMC, SFC) | [![HF](https://img.shields.io/badge/-Model-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/faisalq/SaudiBERT) |
| Ain Shams University | 🇪🇬 EG | Arabic NLP, sentiment analysis, NER research | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://cis.asu.edu.eg/) |
| Arabic.AI (Tarjama) | 🇦🇪 AE | Arabic-first autonomous AI - Pronoia Arabic LLM, Agentic AI platform | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.tarjama.com/) |
| Arabot | 🇦🇪 AE | Conversational AI for Arabic - Arabic NLP chatbot engine | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://arabot.io/) |
| ARBML | 🇸🇦 SA | Democratizing Arabic NLP - masader, klaam, tkseem | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/ARBML) |
| AUB MIND Lab | 🇱🇧 LB | Foundational Arabic NLP models - AraBERT, AraGPT2, AraELECTRA | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/aub-mind) |
| CAMeL Lab (NYU Abu Dhabi) | 🇦🇪 AE | CAMeLBERT, camel_tools, morphological analysis | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://camel-lab.com/) |
| CAMeL Lab, NYUAD | 🇦🇪 AE | Arabic NLP tools and models - CAMeLBERT, camel_tools | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/CAMeL-Lab) |
| Cohere | 🌍 INTL | Multilingual LLMs - Command R Arabic, RAG optimization | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://cohere.com/) |
| Convertedin | 🇪🇬 EG | AI marketing automation - Arabic/English e-commerce personalization, $3M funded | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.converted.in/) |
| Crowd Analyzer | 🇪🇬 EG | Arabic social media monitoring - Arabic NLP analytics, sentiment analysis, media monitoring | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://crowdanalyzer.com/) |
| DXwand | 🇪🇬 EG | Generative AI for Arabic business - ORXTRA platform, Arabic dialect chatbots, 20+ LLM support | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://dxwand.com/) |
| Elm | 🇸🇦 SA | Digital transformation, gov AI (PIF-backed) - Nuha Arabic LLM, legal AI assistant, gov platform | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://elm.sa/en/) |
| Elves | 🇪🇬 EG | Conversational commerce - Arabic AI-assisted concierge, human-in-the-loop ML | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.elves.com/) |
| FreedomIntelligence | 🌍 INTL | Arabic LLMs and alignment - AceGPT, Arabic cultural datasets | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/FreedomIntelligence) |
| Future Look ITC (FLITC) | 🇸🇦 SA | Arabic-native AI solutions, venture studio - LABEAH, Smart Hire, Rayee Media, Nabadat | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://flitc.ai/) |
| G42 | 🇦🇪 AE | AI holding company, Arabic LLMs - Jais LLM, enterprise AI solutions | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.g42.ai/) |
| G42 / Inception AI | 🇦🇪 AE | Arabic-centric LLMs - Jais LLM family | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.g42.ai/) |
| Hazen.ai | 🇸🇦 SA | AI traffic safety & computer vision - Deep learning road safety, seatbelt/phone detection | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.hazen.ai/) |
| Helsinki-NLP | 🌍 INTL | Machine translation models - OPUS-MT Arabic translation models | [![HF](https://img.shields.io/badge/-Hub-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/Helsinki-NLP) |
| Hudhud AI | 🇸🇦 SA | Arabic conversational AI (no-code SaaS) - Saudi-accent chatbots, Arabic-first customer engagement | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://hudhud.ai/) |
| HUMAIN | 🇸🇦 SA | PIF-backed full-stack AI company - ALLaM 34B, HUMAIN Chat, 8PB Arabic training data | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.humain.com/) |
| HUMAIN (Saudi PIF) | 🇸🇦 SA | Full-stack AI company - ALLaM 34B, HUMAIN Chat, AI factories | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.humain.com/) |
| Inception AI | 🇦🇪 AE | Arabic-centric foundation models - Jais model family (with Cerebras) | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.g42.ai/) |
| Intella | 🇪🇬 EG | Arabic speech AI intelligence - Arabic STT across 25+ dialects (95.7% accuracy), Ziila digital human | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://intella.ai/) |
| ITIDA / MCIT | 🇪🇬 EG | National AI authority, sovereign models - Karnak LLM, SIA AI tutor, AcQua NLP, BelMasry, Torgoman | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://itida.gov.eg/) |
| ITIDA / MCIT (Egypt) | 🇪🇬 EG | Egypt's national AI, sovereign models - Karnak LLM, BelMasry, Torgoman, SIA, AcQua | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://itida.gov.eg/) |
| KAUST | 🇸🇦 SA | AI research, Arabic NLP - Center of Excellence in Generative AI | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://cemse.kaust.edu.sa/) |
| KAUST (CEMSE) | 🇸🇦 SA | Generative AI center, Arabic NLP research, sentiment analysis | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://cemse.kaust.edu.sa/) |
| KFUPM-JRCAI | 🇸🇦 SA | Joint SDAIA-KFUPM AI research - Arabic AI text detection datasets | [![HF](https://img.shields.io/badge/-Hub-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/KFUPM-JRCAI) |
| Kngine | 🇪🇬 EG | Semantic search & NLP - Arabic semantic search, data mining, knowledge engine | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://kngine.com/) |
| LightOn AI | 🌍 INTL | Arabic web data - ArabicWeb24 corpus (39B+ tokens) | [![HF](https://img.shields.io/badge/-Hub-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/lightonai) |
| Lucidya | 🇸🇦 SA | AI customer experience analytics - Arabic social listening, sentiment analysis | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.lucidya.com/) |
| Maqsam | 🇯🇴 JO | Arabic speech AI, call center AI - Arabic dialect STT, AI voice bots, surpasses Google/Microsoft | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://maqsam.com/) |
| Mawdoo3 | 🇯🇴 JO | Arabic AI & content, NLP toolkit - Arabic LLMs, largest Arabic website, Saudi expansion | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://mawdoo3.com/) |
| MBZUAI | 🇦🇪 AE | Multimodal and speech models - AIN, ArTST, ClArTTS | [![HF](https://img.shields.io/badge/-Hub-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/MBZUAI) |
| Misraj AI | 🇸🇦 SA | Arabic-first AI ecosystem - Kawn LLM, Baseer OCR, Mutarjim, Workforces, SeamlessAPI | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://misraj.ai/) |
| Mistral AI | 🌍 INTL | Multilingual LLMs - Mistral Saba (Arabic-optimized) | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://mistral.ai/) |
| Monta AI | 🇪🇬 EG | Enterprise AI solutions - LLM & RAG-based Arabic business automation | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://monta-ai.com/) |
| Mozn | 🇸🇦 SA | Enterprise AI, Arabic NLU - OSOS Arabic NLU platform, FOCAL compliance suite | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.mozn.ai/) |
| NAMAA-Space | 🇸🇦 SA | Arabic NLP models & dialect hub - Qari-OCR, EgypTalk-ASR, Masrawy translator, GLiNER Arabic | [![HF](https://img.shields.io/badge/-Hub-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/NAMAA-Space) |
| Nile University | 🇪🇬 EG | AI research, M.Sc. in AI co-designed with MIT/IBM | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://nu.edu.eg/) |
| Omartificial-Intelligence-Space | 🇸🇦 SA | Arabic embedding models - GATE, Matryoshka embeddings | [![HF](https://img.shields.io/badge/-Hub-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/Omartificial-Intelligence-Space) |
| Prince Sultan University (RIOTU Lab) | 🇸🇦 SA | ArabianGPT, Arabic IoT/robotics AI | [![HF](https://img.shields.io/badge/-Hub-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/riotu-lab) |
| Prince Sultan University (RIOTU) | 🇸🇦 SA | Arabic language models - ArabianGPT, Arabic IoT AI | [![HF](https://img.shields.io/badge/-Hub-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/riotu-lab) |
| QCRI | 🇶🇦 QA | Arabic LLMs, text processing - Fanar LLMs, AraDiCE, Farasa | [![HF](https://img.shields.io/badge/-Hub-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/QCRI) |
| Saal.ai | 🇦🇪 AE | Cognitive AI solutions - Arabic NLP, speech, generative AI | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://saal.ai/) |
| SambaNova Systems | 🌍 INTL | Arabic language adaptation - SambaLingo Arabic models | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://sambanova.ai/) |
| SDAIA | 🇸🇦 SA | Sovereign AI, national data authority - ALLaM model, SADA dataset, NCAI, BALSAM benchmark | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://sdaia.gov.sa/) |
| SDAIA (Saudi Data & AI Authority) | 🇸🇦 SA | Sovereign Arabic LLM, national AI strategy - ALLaM model, SADA dataset, BALSAM benchmark | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://sdaia.gov.sa/) |
| SDAIA-KFUPM Joint Research Center (JRCAI) | 🇸🇦 SA | Arabic AI text detection, Arabic NLP datasets | [![HF](https://img.shields.io/badge/-Hub-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/KFUPM-JRCAI) |
| SILMA AI | 🇸🇦 SA | State-of-the-art Arabic LLMs - SILMA LLMs, Arabic Broad Benchmark | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://silma.ai/) |
| SinaLab | 🌍 INTL | SinaTools, Wojood NER corpus | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/SinaLab) |
| SinaLab, Birzeit University | 🌍 INTL | Arabic NLP tools and datasets - SinaTools, Wojood NER | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/SinaLab) |
| Synapse Analytics | 🇪🇬 EG | AI for financial inclusion - ML-powered credit scoring, Arabic data analytics | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://synapseanalytics.com/) |
| Technology Innovation Institute (TII) | 🇦🇪 AE | Open-source LLMs, research - Falcon LLM family | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.tii.ae/) |
| TII (Technology Innovation Institute) | 🇦🇪 AE | Arabic LLM benchmarks, Falcon - Open Arabic LLM Leaderboard, Falcon LLM | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.tii.ae/) |
| UBC-NLP | 🌍 INTL | Dialectal Arabic, multimodal models - MARBERT, AraT5, NileChat, PEARL, Dallah | [![HF](https://img.shields.io/badge/-Hub-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/UBC-NLP) |
| Unifonic | 🇸🇦 SA | Conversational AI platform - Arabic-first CX Intelligence, AI chatbots | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://www.unifonic.com/) |
| WideBot AI | 🇪🇬 EG | Arabic-first conversational AI - AQL Arabic LLM, chatbots, voicebots, AI agents | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://widebot.ai/) |
| Wittify.ai | 🇸🇦 SA | Conversational AI for Arabic - Interactive Arabic AI agents | [![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)](https://wittify.ai/) |

## 🧩 Arabic Agent Skills

Skills shipped in this repo:

| Skill | What it does | Install |
| --- | --- | --- |
| arabic-ai-advisor | Use when choosing an Arabic LLM, ASR, TTS, OCR, embedding model, dataset or tool — recommends ranked options from the Arabic AI Atlas with licenses, dialect coverage and on-device fit. | `skills/arabic-ai-advisor` |
| arabic-dialect-prompts | Use when writing system prompts or few-shot examples for an Arabic-speaking agent in a specific dialect, or when a model answers in formal Arabic (MSA) instead of the requested dialect. | `skills/arabic-dialect-prompts` |
| arabic-token-cost | Use when estimating or comparing how many tokens Arabic text costs across LLM tokenizers, or when Arabic prompts seem expensive, truncated or slow compared with English. | `skills/arabic-token-cost` |
| rtl-bidi-lint | Use when reviewing or generating Arabic text, UI strings, HTML or Markdown that mixes RTL with LTR content, to catch digit mixing, unbalanced bidi isolates, stray LTR marks and hardcoded dir="ltr". | `skills/rtl-bidi-lint` |
| tashkeel-check | Use when Arabic text may need diacritics (tashkeel) added or stripped, for TTS input, learner material, Quran or poetry, or when diacritization looks partial or inconsistent. | `skills/tashkeel-check` |

Other Arabic agent skills in the wild:

| Name | Org | Notes | Links |
| --- | --- | --- | --- |
| arabic-bidi-engineering | MosaabGalmod | Agent skill for correct Arabic RTL/BiDi in chat, terminal and documents | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/MosaabGalmod/arabic-bidi-engineering) |
| awesome-arabic-claude-skills | EngDawood | Curated library of open-source Arabic skills for Claude Code and agents | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/EngDawood/awesome-arabic-claude-skills) |
| karem-arabic-presentation | karem505 | Claude Code skill for Arabic/English bilingual RTL HTML presentations | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/karem505/karem-arabic-presentation) |
| quran-mcp | Quran.com | MCP server giving AI assistants grounded access to Quran text | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/quran/quran-mcp) |
| rtl-skill | mhamedmohammed92-arch | Teaches coding agents to build correct RTL UIs with a checker | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/mhamedmohammed92-arch/rtl-skill) |
| turath-mcp | opin22 | MCP server for turath.io: classical Arabic and Islamic books | [![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)](https://github.com/opin22/turath-mcp) |

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

_Generated 2026-10-04 from 271 entries. Do not edit README.md by hand._
