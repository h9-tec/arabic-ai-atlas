import pytest

from atlas.enrich import apply_cached_licenses, build_hf_ids, card_license, fetch_hf_metrics, hf_id_from_url, merge_metrics


def test_hf_id_from_url_model_and_dataset():
    assert hf_id_from_url("https://huggingface.co/inceptionai/jais-30b-v3") == "inceptionai/jais-30b-v3"
    assert hf_id_from_url("https://huggingface.co/datasets/ARBML/CIDAR/tree/main") == "datasets/ARBML/CIDAR"
    assert hf_id_from_url("https://github.com/x/y") is None


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://huggingface.co/a/b/", "a/b"),
        ("https://huggingface.co/a/b/tree/main", "a/b"),
        ("https://huggingface.co/a/b/blob/main/README.md", "a/b"),
        ("https://huggingface.co/a/b/resolve/main/x.bin", "a/b"),
        ("https://huggingface.co/a/b?library=transformers", "a/b"),
        ("http://huggingface.co/a/b", "a/b"),
        ("https://www.huggingface.co/a/b", "a/b"),
        ("http://www.huggingface.co/datasets/a/b/", "datasets/a/b"),
        ("https://huggingface.co/a", None),
        ("https://huggingface.co/datasets/a", None),
        ("https://huggingface.co/", None),
        ("https://nothuggingface.co/a/b", None),
        ("https://huggingface.co/spaces/OALL", None),
        ("https://huggingface.co/spaces/o/app", None),
        ("https://huggingface.co/collections/google", None),
        ("https://huggingface.co/papers/2410.18163", None),
    ],
)
def test_hf_id_from_url_shapes(url, expected):
    assert hf_id_from_url(url) == expected


def test_fetch_updates_cache_and_keeps_old_on_error():
    cache = {"a/b": {"downloads": 5, "likes": 1, "lastModified": "2026-01-01", "fetched": "2026-01-01"}, "fetched_at": "2026-01-01"}

    def fake(hf_id):
        if hf_id == "a/b":
            raise TimeoutError("boom")
        return {"downloads": 42, "likes": 3, "lastModified": "2026-09-30T10:00:00.000Z", "cardData": {"license": "Apache-2.0"}}

    new, warns = fetch_hf_metrics(["a/b", "c/d"], cache, fetch=fake, now="2026-10-04")
    assert new["a/b"] == {"downloads": 5, "likes": 1, "lastModified": "2026-01-01"}  # legacy stamp dropped
    assert new["c/d"] == {"downloads": 42, "likes": 3, "lastModified": "2026-09-30", "license": "apache-2.0"}
    assert new["fetched_at"] == "2026-10-04"
    assert not any("fetched" in v for v in new.values() if isinstance(v, dict))
    assert len(warns) == 1 and "a/b" in warns[0]
    assert "TimeoutError: boom" in warns[0]
    assert "c/d" not in cache


def test_fetch_error_without_old_entry_stays_absent_and_defaults():
    def fake(hf_id):
        if hf_id == "x/y":
            raise ValueError("bad json")
        return {}

    new, warns = fetch_hf_metrics(["x/y", "m/n"], {}, fetch=fake, now="2026-10-04")
    assert "x/y" not in new
    assert new["m/n"] == {"downloads": 0, "likes": 0, "lastModified": None}
    assert len(warns) == 1


def test_merge_metrics_none_without_hf(fixture_entries):
    merged = merge_metrics(fixture_entries, {})
    assert all(e["metrics"] is None for e in merged if "hf" not in e["links"])
    assert all("metrics" not in e for e in fixture_entries)


def test_merge_metrics_attaches_cache(fixture_entries):
    ids = build_hf_ids(fixture_entries)
    cache = {i: {"downloads": 1, "likes": 2, "lastModified": None, "license": "mit"} for i in ids}
    cache["fetched_at"] = "2026-10-04"
    merged = merge_metrics(fixture_entries, cache)
    for e in merged:
        if "hf" in e["links"]:
            assert e["metrics"] == {"downloads": 1, "likes": 2, "lastModified": None}  # license is not a metric


def test_build_hf_ids_unique_first_seen_order():
    entries = [
        {"links": {"hf": "https://huggingface.co/b/b"}},
        {"links": {"github": "https://github.com/x/y"}},
        {"links": {"hf": "https://huggingface.co/a/a/tree/main"}},
        {"links": {"hf": "https://huggingface.co/b/b/"}},
    ]
    assert build_hf_ids(entries) == ["b/b", "a/a"]


@pytest.mark.parametrize(
    "card,expected",
    [
        ({"license": "MIT"}, "mit"),
        ({"license": ["cc-by-4.0", "mit"]}, "cc-by-4.0"),
        ({"license": "other", "license_name": "Llama3.1"}, "llama3.1"),
        ({"license": "other"}, None),
        ({"license": "custom"}, None),
        ({"license": "cc"}, None),
        ({}, None),
        (None, None),
    ],
)
def test_card_license(card, expected):
    assert card_license({"cardData": card}) == expected


def test_apply_cached_licenses_fills_only_unknown():
    url = {"hf": "https://huggingface.co/o/m"}
    entries = [
        {"id": "u", "license": "unknown", "links": url},
        {"id": "k", "license": "gemma", "links": url},
        {"id": "g", "license": "unknown", "links": {"github": "https://github.com/o/m"}},
    ]
    cache = {"o/m": {"downloads": 1, "likes": 0, "lastModified": None, "license": "apache-2.0"}, "fetched_at": "d"}
    out = apply_cached_licenses(entries, cache)
    assert [e["license"] for e in out] == ["apache-2.0", "gemma", "unknown"]
    assert entries[0]["license"] == "unknown"  # inputs are not mutated
