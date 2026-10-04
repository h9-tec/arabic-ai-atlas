from pathlib import Path

import pytest

from atlas.seed import dedupe, parse_tables, slugify
from atlas.validate import validate_entries


@pytest.fixture
def sample() -> str:
    return (Path(__file__).parent / "fixtures" / "awesome_sample.md").read_text(encoding="utf-8")


def test_parse_llm_row(sample):
    e = next(x for x in parse_tables(sample) if x["id"] == "jais")
    assert e["type"] == "llm" and e["modality"] == "text"
    assert e["links"]["hf"] == "https://huggingface.co/inceptionai/jais-30b-v3"
    assert e["size"] == "13B, 30B" and e["org"] == "Inception AI, Cerebras"


def test_parse_company_under_country_heading(sample):
    e = next(x for x in parse_tables(sample) if x["id"] == "g42")
    assert e["type"] == "org" and e["country"] == "AE" and e["modality"] == "none"


def test_all_drafts_validate(sample, schema):
    assert validate_entries(parse_tables(sample), schema) == []


def test_asr_and_dataset_rows(sample):
    drafts = {e["id"]: e for e in parse_tables(sample)}
    asr = drafts["openai-whisper-large-v3"]
    assert asr["type"] == "asr" and asr["modality"] == "speech" and asr["org"] == "openai"
    ds = drafts["masader"]
    assert ds["type"] == "dataset" and ds["links"]["github"] == "https://github.com/ARBML/masader"
    assert ds["license"] == "unknown" and ds["country"] == "INTL"


def test_slugify_and_dedupe(capsys):
    assert slugify("  Qwen 3 (0.6B-235B)! ") == "qwen-3-0-6b-235b"
    kept = dedupe([{"id": "a", "n": 1}, {"id": "a", "n": 2}, {"id": "b", "n": 3}])
    assert [e["n"] for e in kept] == [1, 3]
    assert "a" in capsys.readouterr().err
