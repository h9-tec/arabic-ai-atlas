---
name: arabic-token-cost
description: Use when estimating or comparing how many tokens Arabic text costs across LLM tokenizers, or when Arabic prompts seem expensive, truncated or slow compared with English.
---

# Arabic Token Cost

Measures tokenizer fertility (tokens per word) on Arabic text against an English reference of the same word count.

## Run

```
python ${CLAUDE_PLUGIN_ROOT}/skills/arabic-token-cost/token_cost.py --text "النص العربي هنا" [--tokenizers id,id]
```

Use `--file path` for longer samples (at least a few hundred words gives stable numbers). Default tokenizers: `gpt2`, `meta-llama/Llama-3.1-8B`, `Qwen/Qwen2.5-7B`, `inceptionai/jais-family-590m`, `google/gemma-2-2b`.

It needs `transformers`. If missing it prints an install hint (`uv pip install transformers`) and exits 2. Tokenizers download from Hugging Face on first use; gated ones (such as Llama) may fail, and that row prints an error while the rest continue.

## Reading the table

Columns: `tokenizer | tokens | tokens/word | ratio vs English`.

- Under 1.5 tokens/word: efficient.
- 1.5 to 2.5: acceptable.
- Over 2.5: expensive. Context fills about twice as fast and cost and latency rise accordingly.
- Ratio vs English shows the Arabic penalty for that tokenizer; compare it across rows, not in absolute terms.

## Procedure

1. Run the script on a representative sample of the user's real text, not a single sentence.
2. Report the table and flag every tokenizer over 2.5 tokens/word.
3. If cost matters, call the MCP tool `search(query="tokenizer")` and recommend Arabic-aware tokenizers or models the atlas returns, with license and link.

## Rules

- Fertility depends on the text (dialect and diacritics raise it). State the sample used.
- Do not recommend models that the atlas did not return.
