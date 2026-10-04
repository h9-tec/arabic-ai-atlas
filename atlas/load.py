"""Load atlas entries from YAML files."""
from pathlib import Path

import yaml


def load_entries(data_dir: Path) -> list[dict]:
    """Merge every ``*.yaml`` list in ``data_dir``; tag each entry with ``_file``."""
    entries: list[dict] = []
    for path in sorted(Path(data_dir).glob("*.yaml")):
        if path.name.startswith("."):
            continue
        with path.open(encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        if doc is None:
            doc = []
        if not isinstance(doc, list):
            raise ValueError(f"{path.name}: expected a YAML list of entries, got {type(doc).__name__}")
        for entry in doc:
            if not isinstance(entry, dict):
                raise ValueError(f"{path.name}: every entry must be a mapping, got {type(entry).__name__}")
            entries.append({**entry, "_file": path.name})
    return entries
