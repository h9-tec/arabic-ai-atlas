---
name: arabic-dialect-prompts
description: Use when writing system prompts or few-shot examples for an Arabic-speaking agent in a specific dialect, or when a model answers in formal Arabic (MSA) instead of the requested dialect.
---

# Arabic Dialect Prompts

Reference for prompting LLMs in a specific Arabic dialect. The table in `${CLAUDE_PLUGIN_ROOT}/skills/arabic-dialect-prompts/dialects.md` covers the 10 dialect codes used across the atlas (msa, egy, gulf, lev, magh, iraqi, sudanese, yemeni, classical, mixed), each with register notes and an example system-prompt line in Arabic.

## Procedure

1. Identify the dialect (ask if unclear) and read its row in `dialects.md`.
2. Start the system prompt from that row's example line and adapt tone to the product.
3. Add 2 to 3 few-shot exchanges written in the dialect. Examples teach the dialect better than instructions alone.
4. State explicitly what to avoid, for example «لا تستخدم الفصحى».
5. Test with a few real user messages; if replies drift toward MSA, see "Common failure" in `dialects.md`.

## Picking a model

If the user also needs a model with good coverage of that dialect, call `recommend(task="chat", dialect="<code>")`, or `search(query="<dialect> dialect", type="llm")`. Report only what the atlas returns.

## Rules

- Write the system prompt itself in the target dialect; an English prompt pulls output toward MSA or English.
- Dialect support in models is uneven; say so for sudanese, yemeni and magh.
- Keep user-facing safety and legal text in clear MSA when accuracy matters more than tone.
