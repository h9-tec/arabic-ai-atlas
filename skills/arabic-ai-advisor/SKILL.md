---
name: arabic-ai-advisor
description: Use when choosing an Arabic LLM, ASR, TTS, OCR, embedding model, dataset or tool — recommends ranked options from the Arabic AI Atlas with licenses, dialect coverage and on-device fit.
---

# Arabic AI Advisor

Recommends Arabic AI models, datasets and tools from the Arabic AI Atlas, a curated catalogue with Hugging Face download metrics.

## When to use

- The user needs an Arabic (or dialect-specific) LLM, ASR, TTS, OCR or embedding model.
- The user asks which Arabic dataset, benchmark or tool fits a task.
- The user has constraints such as a license, a dialect, or running on-device.

## Procedure

1. Call the MCP tool `recommend` with the `task` and the `type` the user wants (`llm`, `asr`, `tts`, `ocr`, `embedding` for a model; `dataset`, `benchmark` or `tool` otherwise), plus `dialect`, `on_device` and `license_filter` when the user gave them. Example: `recommend(task="tts", type="tts", on_device=true, license_filter="open")`.
2. If the MCP tools are unavailable, read `${CLAUDE_PLUGIN_ROOT}/dist/atlas.json` and filter entries by `tasks`.
3. For breadth, or when `recommend` returns too little, call `search` (and `get` for one entry by id).
4. Format the answer as described below.

## Answer format

Give 3 ranked options. For each: name, org, license, dialects, size, a one-line why, and a link. Then state the atlas `generated_at` date.

If nothing fits, say: "Not in the atlas: I found no entry matching this request." Do not guess.

## Rules

- Never invent entries; only report what the atlas returns.
- Prefer open licenses when the user does not say.
- Say when metrics (downloads, size, license) are missing.
- If two options tie, prefer the one updated more recently.

## Valid values

| Parameter | Values |
| --- | --- |
| type | llm, asr, tts, ocr, embedding, dataset, benchmark, tool, agent-skill, org, paper |
| country | SA, AE, EG, LB, QA, JO, MA, TN, KW, OM, BH, DZ, LY, SD, IQ, SY, YE, PS, MR, SO, DJ, KM, INTL |
| modality | text, speech, vision, multimodal, none |
| dialect | msa, egy, gulf, lev, magh, iraqi, sudanese, yemeni, classical, mixed |
| task (examples) | chat, tts, asr, ocr, embedding, translation |
