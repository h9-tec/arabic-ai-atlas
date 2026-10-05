"""Passes when the output uses Arabic-Indic digits (U+0660..U+0669) and no ASCII digits."""


def check(output: str, expected: dict) -> bool:
    indic = sum(1 for ch in output if "٠" <= ch <= "٩")
    ascii_digits = any("0" <= ch <= "9" for ch in output)
    return indic >= expected["min_digits"] and not ascii_digits
