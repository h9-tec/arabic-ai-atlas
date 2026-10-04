#!/usr/bin/env python3
"""Lint text files for common Arabic bidi problems. Stdlib only."""
import re
import sys

ARABIC_INDIC = re.compile("[٠-٩۰-۹]")
ASCII_DIGIT = re.compile("[0-9]")
ARABIC_LETTER = "[؀-ۿ]"
LTR_MARK_RE = re.compile(f"{ARABIC_LETTER}‎{ARABIC_LETTER}")
ARABIC_RE = re.compile(ARABIC_LETTER)
HARDCODED_LTR_RE = re.compile(r"""dir\s*=\s*(["'])ltr\1""")
OPENERS = "⁦⁧⁨"
CLOSER = "⁩"


def lint_text(text: str) -> list[tuple[int, str, str]]:
    findings = []
    for n, line in enumerate(text.splitlines(), 1):
        if ARABIC_INDIC.search(line) and ASCII_DIGIT.search(line):
            findings.append((n, "MIXED_DIGITS",
                             "Arabic-Indic and ASCII digits on one line; unify the digit system"))
        opens = sum(line.count(c) for c in OPENERS)
        if opens != line.count(CLOSER):
            findings.append((n, "UNBALANCED_ISOLATE",
                             "U+2066/2067/2068 isolate count differs from U+2069 count"))
        if LTR_MARK_RE.search(line):
            findings.append((n, "LTR_MARK_IN_ARABIC",
                             "U+200E inside an Arabic run; remove it or use an isolate"))
        if HARDCODED_LTR_RE.search(line) and ARABIC_RE.search(line):
            findings.append((n, "HARDCODED_LTR",
                             'dir="ltr" on a line containing Arabic; use dir="auto"'))
    return findings


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: bidi_lint.py <paths...>", file=sys.stderr)
        return 2
    found = False
    for path in argv:
        with open(path, encoding="utf-8") as f:
            for n, code, msg in lint_text(f.read()):
                print(f"{path}:{n}: {code} {msg}")
                found = True
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
