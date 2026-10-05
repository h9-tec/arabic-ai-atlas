"""MCP server exposing the Arabic AI Atlas (search / recommend / get / lineage)."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # append: the SDK `mcp` package must win over this repo's mcp/ dir

from mcp.server.mcpserver import MCPServer  # noqa: E402

from atlas import query as atlas_query  # noqa: E402

ATLAS_PATH = Path(os.environ.get("ATLAS_JSON") or ROOT / "dist" / "atlas.json")
DOC = atlas_query.load_doc(ATLAS_PATH)
ENTRIES = DOC["entries"]

server = MCPServer("arabic-ai-atlas")


@server.tool()
def search(
    query: str,
    type: str | None = None,
    country: str | None = None,
    modality: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Search the Arabic AI Atlas, a curated catalogue of Arabic models, datasets, benchmarks,
    tools and organizations with Hugging Face download metrics.

    Case-insensitive substring match over name, org, notes, tasks and tags; the optional
    type/country/modality filters are exact. Results are ordered by downloads, most first.

    Valid values:
      type: llm, asr, tts, ocr, embedding, dataset, benchmark, tool, agent-skill, org, paper
      country: SA, AE, EG, QA, MA, JO, TN, LB, KW, OM, BH, DZ, LY, SD, IQ, SY, YE, PS, MR, SO, DJ, KM, INTL
      modality: text, speech, vision, multimodal, none

    Example: search(query="speech", type="asr", limit=5)
    """
    return atlas_query.search(ENTRIES, query, type=type, country=country, modality=modality, limit=limit)


@server.tool()
def recommend(
    task: str,
    dialect: str | None = None,
    on_device: bool | None = None,
    license_filter: str | None = None,
    limit: int = 3,
    type: str | None = None,
) -> list[dict]:
    """Recommend entries from the Arabic AI Atlas for a task, ranked with an explanation.

    Score = 3 if the task is in the entry's tasks, +2 if the dialect matches, +1 if the task
    word appears in its notes; zero-score entries are dropped. Each result carries `score`
    and `why`. Ties go to models (llm, asr, tts, ocr, embedding) over datasets, benchmarks,
    tools and orgs, then papers (literature, not model picks; pass type="paper" to get them), then to downloads.

    task: e.g. chat, tts, asr, ocr, embedding, translation.
    dialect: msa, egy, gulf, lev, magh, iraqi, sudanese, yemeni, classical, mixed (optional; entries lacking dialect data still match on task).
    on_device: true keeps only entries marked on-device (phone or laptop CPU); false drops those; omit for no filter.
    license_filter: "open" excludes proprietary/unknown licenses; any other string must equal the license exactly (optional).
    type: exact entry type, e.g. "tts" to get models only, "dataset" for training data, "paper" for research papers (optional).

    Example: recommend(task="tts", type="tts", on_device=true, license_filter="open")
    """
    return atlas_query.recommend(
        ENTRIES, task, dialect=dialect, on_device=on_device, license_filter=license_filter, limit=limit, type=type
    )


@server.tool()
def get(id: str) -> dict:
    """Fetch one full Arabic AI Atlas entry by its id (e.g. "jais-30b"), including links and metrics.

    Returns {"error": "unknown id", "id": ...} when no entry has that id. Use `search` to find ids.

    Example: get(id="jais-30b")
    """
    return atlas_query.get(ENTRIES, id) or {"error": "unknown id", "id": id}


@server.tool()
def lineage(id: str) -> dict:
    """Family tree of one model in the Arabic AI Atlas: what it was built on and what was built on it.

    Returns {"id", "root", "ancestors", "descendants"}:
      root: the base family the chain ends in, or null for an atlas entry with no recorded base.
      ancestors: parent first, then grandparents, up to the first id outside the atlas.
      descendants: atlas models fine-tuned from it, breadth-first (children, then grandchildren).
    Ids are atlas ids (e.g. "jais-30b") or, for bases outside the atlas, lowercase Hugging Face
    ids (e.g. "qwen/qwen2.5-7b"); both are accepted as `id`. Returns {"error": "unknown id", "id": ...}
    when the id is neither an entry nor part of any lineage.

    Roots: whisper, mms, xlsr, wav2vec, electra, bert, t5, llama, qwen, gemma, mistral, falcon,
    bloom, phi, deepseek, from-scratch, other.

    Example: lineage(id="silma-1-0")
    """
    return atlas_query.lineage(DOC, id)


if __name__ == "__main__":
    server.run("stdio")
