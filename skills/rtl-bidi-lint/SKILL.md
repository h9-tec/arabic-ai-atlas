---
name: rtl-bidi-lint
description: Use when reviewing or generating Arabic text, UI strings, HTML or Markdown that mixes RTL with LTR content, to catch digit mixing, unbalanced bidi isolates, stray LTR marks and hardcoded dir="ltr".
---

# RTL / Bidi Lint

Runs a small stdlib-only linter over text files and explains each finding.

## Run

```
python ${CLAUDE_PLUGIN_ROOT}/skills/rtl-bidi-lint/bidi_lint.py <files...>
```

Output lines look like `path:line: CODE message`. Exit code 1 means findings, 0 means clean.

## Codes and fixes

| Code | Meaning | Fix |
| --- | --- | --- |
| `MIXED_DIGITS` | Arabic-Indic (٠-٩ or ۰-۹) and ASCII (0-9) digits on one line | Pick one digit system per document. Use ASCII for code, IDs, prices and data; Arabic-Indic only for prose when the audience expects it. |
| `UNBALANCED_ISOLATE` | U+2066, U+2067 or U+2068 opened without a matching U+2069 | Close every isolate. Wrap embedded LTR runs (names, URLs, code) as U+2068 ... U+2069 (first-strong isolate). |
| `LTR_MARK_IN_ARABIC` | U+200E sits between Arabic letters | Remove it. It breaks letter joining and shaping. If direction needs forcing, use an isolate around the foreign run instead. |
| `HARDCODED_LTR` | `dir="ltr"` on a line that contains Arabic | Use `dir="auto"` for user content, or `dir="rtl"` for known-Arabic blocks. |

## Procedure

1. Run the script on the files in question (or write the text to a temp file first).
2. For each finding, show the line and apply the fix from the table.
3. Re-run until exit code 0.

## Limits

The linter is line-based and heuristic. It does not render text, so check the final result visually when layout matters.
