from atlas.lineage import ORG_ALIASES, ROOTS, build_lineage, canonical, root_family
from atlas.query import lineage


def m(i, base=None, hf=None, t="llm", dl=0):
    e = {"id": i, "name": i.upper(), "type": t, "links": {"hf": hf} if hf else {"website": "https://x"}, "metrics": {"downloads": dl}}
    return {**e, "base_model": base} if base else e


def test_root_family_order():
    assert [root_family(x) for x in ("facebook/mms-1b-all", "facebook/wav2vec2-xls-r-300m", "aubmindlab/bert-base-arabertv2",
            "google/mt5-base", "microsoft/phi-3-mini", "graphic/philosophy-model", "from-scratch", "x/unknown",
            "ubc-nlp/arat5v2-base-1024", "ubc-nlp/arat5-base", "coqui/xtts-v2", "swivid/f5-tts", "baai/bge-m3",
            "intfloat/multilingual-e5-base", "facebook/nllb-200-distilled-600m", "coherelabs/c4ai-command-r7b-12-2024",
            "facebook/seamless-m4t-v2-large")] == \
           ["mms", "xlsr", "bert", "t5", "phi", "other", "from-scratch", "other",
            "t5", "t5", "xtts", "f5", "bge", "e5", "nllb", "cohere", "seamless"]


def test_roots_in_global_order():
    assert [r[0] for r in ROOTS] == ["whisper", "mms", "xlsr", "wav2vec", "electra", "bert", "t5", "llama", "qwen",
                                     "gemma", "mistral", "falcon", "bloom", "phi", "deepseek", "xtts", "f5", "bge", "e5",
                                     "nllb", "cohere", "seamless", "from-scratch"]


def test_base_resolves_by_hf_url_and_atlas_id():
    doc = build_lineage([m("base", ["meta-llama/Llama-2-7b"], hf="https://huggingface.co/Org/Base-7B"),
                         m("ft1", ["https://huggingface.co/org/base-7b"]), m("ft2", ["base"])])
    assert ["base", "ft1"] in doc["edges"] and ["base", "ft2"] in doc["edges"]
    assert doc["root_of"] == {"base": "llama", "ft1": "llama", "ft2": "llama"}


def test_cycle_terminates():
    doc = build_lineage([m("a", ["b"]), m("b", ["a"]), m("c", ["c"])])
    assert doc["root_of"] == {"a": "other", "b": "other", "c": "other"}
    assert lineage({"entries": [], "lineage": doc}, "a")["ancestors"] == ["b"]


def test_query_lineage():
    doc = {"lineage": build_lineage([m("base", ["qwen/qwen2.5-7b"]), m("ft", ["base"]), m("ft2", ["ft"])]), "entries": []}
    assert lineage(doc, "ft") == {"id": "ft", "root": "qwen", "ancestors": ["base", "qwen/qwen2.5-7b"], "descendants": ["ft2"]}
    assert lineage(doc, "nope") == {"error": "unknown id", "id": "nope"}


def test_org_alias_resolves_renamed_hf_org():
    assert {"allam-ai": "humain-ai", "inception-mbzuai": "inception42", "inceptionai": "inception42",
            "core42": "inception42"}.items() <= ORG_ALIASES.items()
    assert canonical("https://huggingface.co/ALLaM-AI/ALLaM-7B-Instruct-preview") == "humain-ai/allam-7b-instruct-preview"
    doc = build_lineage([
        m("allam", ["from-scratch"], hf="https://huggingface.co/ALLaM-AI/ALLaM-7B-Instruct-preview"),
        m("allam-7b-instruct-preview", ["from-scratch"], hf="https://huggingface.co/humain-ai/ALLaM-7B-Instruct-preview"),
        m("yehia", ["allam-ai/allam-7b-instruct-preview"]),
        m("mawrooth", ["humain-ai/allam-7b-instruct-preview"]),
    ])
    assert ["allam-7b-instruct-preview", "yehia"] in doc["edges"]
    assert ["allam-7b-instruct-preview", "mawrooth"] in doc["edges"]
    assert doc["root_of"]["yehia"] == "from-scratch"


def test_external_aliases_collapse_and_output_sorted():
    doc = build_lineage([m("z", ["allam-ai/x-7b", "humain-ai/x-7b"]), m("a", ["google/gemma-2-9b"])])
    assert doc["edges"] == [["google/gemma-2-9b", "a"], ["humain-ai/x-7b", "z"]]
    assert doc["roots"] == [{"id": "gemma", "label": "Gemma", "label_ar": "جيما", "count": 1},
                            {"id": "other", "label": "Other", "label_ar": "أخرى", "count": 1}]
    assert build_lineage([m("a", ["google/gemma-2-9b"]), m("z", ["allam-ai/x-7b", "humain-ai/x-7b"])]) == doc


def test_dead_end_atlas_parent_classified_by_its_hf_id():
    merged = [m("arabertv02", hf="https://huggingface.co/aubmindlab/bert-base-arabertv02"), m("sbert", ["arabertv02"]),
              m("ft", ["base"]), m("base"), m("solo")]
    doc = {"lineage": build_lineage(merged), "entries": merged}
    assert doc["lineage"]["root_of"] == {"arabertv02": "bert", "base": "other", "ft": "other", "sbert": "bert"}
    assert lineage(doc, "base") == {"id": "base", "root": "other", "ancestors": [], "descendants": ["ft"]}
    assert lineage(doc, "solo") == {"id": "solo", "root": None, "ancestors": [], "descendants": []}


def test_lineage_of_external_id():
    q = {"lineage": build_lineage([m("ft", ["Qwen/Qwen2.5-7B"])]), "entries": [m("ft", ["Qwen/Qwen2.5-7B"])]}
    assert lineage(q, "qwen/qwen2.5-7b") == {"id": "qwen/qwen2.5-7b", "root": "qwen", "ancestors": [], "descendants": ["ft"]}


def test_parent_without_base_roots_by_its_hf_id():
    doc = build_lineage([m("arabert", hf="https://huggingface.co/aubmindlab/bert-base-arabertv02"), m("ft", ["arabert"])])
    assert doc["root_of"] == {"arabert": "bert", "ft": "bert"}
    assert doc["edges"] == [["arabert", "ft"]]
