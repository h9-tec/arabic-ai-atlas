"""Validate atlas entries against the JSON schema."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator


def load_schema(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_entries(entries: list[dict], schema: dict) -> list[str]:
    """Return error messages (empty list means valid)."""
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for entry in entries:
        file = entry.get("_file", "<no file>")
        eid = entry.get("id", "<no id>")
        for err in sorted(validator.iter_errors(entry), key=lambda e: list(e.absolute_path)):
            where = ".".join(str(p) for p in err.absolute_path)
            msg = f"{where}: {err.message}" if where else err.message
            errors.append(f"{file}:{eid}: {msg}")
    seen: dict[str, str] = {}
    for entry in entries:
        eid = entry.get("id")
        if not isinstance(eid, str):
            continue
        file = entry.get("_file", "<no file>")
        if eid in seen:
            errors.append(f"{seen[eid]},{file}:{eid}: duplicate id")
        else:
            seen[eid] = file
    return errors
