#!/usr/bin/env python3
"""Measure tokenizer cost (fertility) of Arabic text vs English. Needs transformers."""
import argparse
import sys

DEFAULT_TOKENIZERS = ("gpt2,meta-llama/Llama-3.1-8B,Qwen/Qwen2.5-7B,"
                      "inceptionai/jais-family-590m,google/gemma-2-2b")
ENGLISH_REF = "The quick brown fox jumps over the lazy dog near the river bank today"


def fertility(token_count: int, text: str) -> float:
    words = len(text.split())
    return token_count / words if words else 0.0


def english_reference(word_count: int) -> str:
    base = ENGLISH_REF.split()
    return " ".join((base * (word_count // len(base) + 1))[:word_count])


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--text")
    g.add_argument("--file")
    p.add_argument("--tokenizers", default=DEFAULT_TOKENIZERS)
    args = p.parse_args(argv)
    text = args.text
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    try:
        from transformers import AutoTokenizer
    except ImportError:
        print("install transformers to run token cost: uv pip install transformers",
              file=sys.stderr)
        return 2
    words = len(text.split())
    english = english_reference(words)
    print(f"{'tokenizer':<36} | {'tokens':>6} | {'tokens/word':>11} | ratio vs English")
    for tid in (t.strip() for t in args.tokenizers.split(",") if t.strip()):
        try:
            tok = AutoTokenizer.from_pretrained(tid)
            n_ar = len(tok.encode(text, add_special_tokens=False))
            n_en = len(tok.encode(english, add_special_tokens=False))
        except Exception as e:  # noqa: BLE001
            print(f"{tid:<36} | error: {type(e).__name__}: {str(e)[:80]}")
            continue
        ratio = n_ar / n_en if n_en else 0.0
        print(f"{tid:<36} | {n_ar:>6} | {fertility(n_ar, text):>11.2f} | {ratio:.2f}x")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
