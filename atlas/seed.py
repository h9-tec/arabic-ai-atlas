"""Parse the Awesome_Arabic_NLP README tables into draft atlas entries."""
import re
import sys

# (h2 substring, h3 substring, type, modality, tasks); first match wins.
# Empty h3 substring matches any h3. Matching is case-insensitive.
HEADING_MAP: list[tuple[str, str, str, str, list[str]]] = [
    ("key organizations", "", "org", "none", ["research"]),
    ("research institutions", "", "org", "none", ["research"]),
    ("companies", "", "org", "none", ["industry"]),
    ("benchmarks", "", "benchmark", "text", ["evaluation"]),
    ("", "large language models", "llm", "text", ["chat"]),
    ("", "multimodal models", "llm", "multimodal", ["multimodal"]),
    ("", "transformer-based", "llm", "text", ["encoder"]),
    ("", "embedding", "embedding", "text", ["embedding"]),
    ("", "task-specific", "llm", "text", ["task-specific"]),
    ("", "tts datasets", "dataset", "speech", ["tts"]),
    ("", "speech recognition", "asr", "speech", ["asr"]),
    ("", "text-to-speech", "tts", "speech", ["tts"]),
    ("", "ocr datasets", "dataset", "vision", ["ocr"]),
    ("", "traditional ocr", "tool", "vision", ["ocr"]),
    ("", "optical character", "ocr", "vision", ["ocr"]),
    ("", "image captioning", "llm", "multimodal", ["image-captioning"]),
    ("diacritization", "models", "tool", "text", ["diacritization"]),
    ("diacritization", "datasets", "dataset", "text", ["diacritization"]),
    ("dialect", "shared tasks", "benchmark", "text", ["dialect-id"]),
    ("dialect", "datasets", "dataset", "text", ["dialect-id"]),
    ("", "text datasets", "dataset", "text", ["nlp"]),
    ("", "speech datasets", "dataset", "speech", ["asr"]),
    ("", "vision & multimodal datasets", "dataset", "vision", ["multimodal"]),
    ("", "toolkits", "tool", "text", ["nlp-toolkit"]),
    ("", "specialized libraries", "tool", "text", ["nlp-toolkit"]),
    ("", "translation", "tool", "text", ["translation"]),
]

FLAGS = {"🇦🇪": "AE", "🇸🇦": "SA", "🇪🇬": "EG", "🇶🇦": "QA", "🇱🇧": "LB"}

DESC_COLUMNS = {"task", "key features", "description", "focus", "key contributions", "notable products"}

LINK_RE = re.compile(r"\]\((https?://[^)\s]+)\)")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _lookup(h2: str, h3: str):
    h2, h3 = h2.lower(), h3.lower()
    for h2_sub, h3_sub, typ, modality, tasks in HEADING_MAP:
        if h2_sub in h2 and h3_sub in h3 and (h2_sub or h3_sub):
            return typ, modality, tasks
    return None


def _country_from_text(text: str) -> str | None:
    for flag, code in FLAGS.items():
        if flag in text:
            return code
    if any("\U0001F1E6" <= ch <= "\U0001F1FF" for ch in text):
        return "INTL"
    if "international" in text.lower():
        return "INTL"
    return None


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _classify(url: str) -> str:
    if "huggingface.co" in url:
        return "hf"
    if "github.com" in url:
        return "github"
    if "arxiv.org" in url or "aclanthology.org" in url:
        return "paper"
    return "website"


def _clean(text: str) -> str:
    return text.replace("**", "").strip()


def _missing(text: str) -> bool:
    return text in ("", "-", "–", "—")


def parse_tables(markdown: str) -> list[dict]:
    """Return draft entries for every mapped table row in ``markdown``."""
    entries: list[dict] = []
    h2 = h3 = ""
    header: list[str] | None = None
    country_ctx = "INTL"
    for line in markdown.splitlines():
        if line.startswith("## "):
            h2, h3, header, country_ctx = line[3:], "", None, "INTL"
            continue
        if line.startswith("### "):
            h3, header = line[4:], None
            country_ctx = _country_from_text(h3) or "INTL"
            continue
        if not line.startswith("|"):
            header = None if not line.strip() else header
            continue
        cells = _cells(line)
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= set(":- "):
            continue  # separator row
        spec = _lookup(h2, h3)
        if spec is None:
            continue
        typ, modality, tasks = spec
        urls = LINK_RE.findall(cells[-1])  # last match is the outer link, not the badge image
        if not urls or not cells[0]:
            continue
        name = _clean(cells[0])
        slug = slugify(name)
        if not slug:
            continue
        url = urls[-1]
        links = {_classify(url): url}
        row = dict(zip(header, cells))
        country = country_ctx
        if "country" in row:
            country = _country_from_text(row["country"]) or "INTL"
        org = _clean(row.get("developer", row.get("developed by", "")))
        if typ == "org":
            org = name
        elif _missing(org):
            m = re.match(r"https://huggingface\.co/(?:datasets/|spaces/)?([^/]+)/", url)
            org = m.group(1) if m and links.get("hf") else "unknown"
        notes_parts = [_clean(row[c]) for c in header if c in DESC_COLUMNS and not _missing(_clean(row.get(c, "")))]
        entry = {
            "id": slug,
            "name": name,
            "type": typ,
            "country": country,
            "org": org,
            "license": "unknown",
            "modality": modality,
            "tasks": list(tasks),
            "links": links,
        }
        size = _clean(row.get("params", ""))
        if not _missing(size):
            entry["size"] = size
        if notes_parts:
            notes = " - ".join(notes_parts)
            entry["notes"] = notes if len(notes) <= 160 else notes[:157].rstrip() + "..."
        entries.append(entry)
    return entries


def dedupe(entries: list[dict]) -> list[dict]:
    """Keep the first entry per id; report dropped ids on stderr."""
    seen: set[str] = set()
    kept: list[dict] = []
    for e in entries:
        if e["id"] in seen:
            print(f"dropped duplicate id: {e['id']}", file=sys.stderr)
            continue
        seen.add(e["id"])
        kept.append(e)
    return kept
