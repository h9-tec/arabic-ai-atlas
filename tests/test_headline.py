"""The README's headline question must have an answer in the shipped atlas."""

from pathlib import Path

from atlas.query import load_atlas, recommend

ATLAS = Path(__file__).resolve().parent.parent / "dist" / "atlas.json"


def test_open_on_device_tts_question_has_answers():
    # README: "which open Arabic TTS runs on a phone?"
    res = recommend(load_atlas(ATLAS), task="tts", on_device=True, license_filter="open")
    assert res, "the headline demo returns nothing"
    assert all(r["type"] == "tts" for r in res)
    assert all(r["on_device"] is True for r in res)
    assert all(r["license"] not in {"unknown", "proprietary"} for r in res)


def test_headline_question_with_type_filter():
    res = recommend(load_atlas(ATLAS), task="tts", type="tts", on_device=True, license_filter="open")
    assert len(res) >= 1 and {r["type"] for r in res} == {"tts"}
