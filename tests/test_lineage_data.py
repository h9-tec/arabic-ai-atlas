"""Curated `base_model` lineage in data/llms.yaml, each value read from the model card or paper."""

from pathlib import Path

from atlas.load import load_entries

ROOT = Path(__file__).resolve().parent.parent

CURATED = {
    "jais": ["from-scratch"],
    "allam": ["from-scratch"],
    "acegpt": ["meta-llama/llama-2-7b-hf"],
    "nile-chat": ["google/gemma-3-4b-pt", "google/gemma-3-12b-pt"],
    "atlas-chat": ["google/gemma-2-2b-it", "google/gemma-2-9b-it", "google/gemma-2-27b-it"],
    "falcon-arabic": ["tiiuae/falcon3-7b-base"],
    "fanar-1-9b": ["google/gemma-2-9b"],
    "fanar-2-27b-instruct": ["google/gemma-3-27b-pt"],
    "jais-adapted": ["inceptionai/jais-adapted-13b"],
    "jais-family-590m": ["from-scratch"],
    "jais-13b-chat": ["inception-mbzuai/jais-13b"],
    "aragpt2": ["from-scratch"],
    "nilechat-3b": ["qwen/qwen2.5-3b"],
    "yehia": ["allam-ai/allam-7b-instruct-preview"],
    "hala-350m": ["liquidai/lfm2-350m"],
    "command-r7b-arabic": ["coherelabs/c4ai-command-r7b-12-2024"],
}


def test_curated_base_models_present():
    by_id = {e["id"]: e for e in load_entries(ROOT / "data")}
    for i, base in CURATED.items():
        assert by_id[i].get("base_model") == base, i
    assert sum(1 for e in by_id.values() if e.get("base_model")) >= 40
