from pathlib import Path

import pytest

from atlas.validate import load_schema

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def fixture_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "data"


@pytest.fixture
def schema() -> dict:
    return load_schema(ROOT / "data" / "schema.json")


@pytest.fixture
def good_entry() -> dict:
    return {
        "id": "jais-30b",
        "name": "Jais 30B",
        "type": "llm",
        "country": "AE",
        "org": "Inception AI",
        "license": "apache-2.0",
        "modality": "text",
        "size": "30B",
        "dialects": ["msa"],
        "tasks": ["chat"],
        "links": {"hf": "https://huggingface.co/inceptionai/jais-30b-v3"},
        "notes": "Bilingual Arabic-English foundation model.",
        "_file": "llms.yaml",
    }


@pytest.fixture
def fixture_entries(fixture_dir: Path) -> list[dict]:
    from atlas.load import load_entries

    return load_entries(fixture_dir)
