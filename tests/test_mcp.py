import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from atlas.enrich import build_hf_ids, merge_metrics
from atlas.render_json import build_atlas_json

ROOT = Path(__file__).resolve().parent.parent


async def _run(atlas_json: Path):
    params = StdioServerParameters(
        command=sys.executable,
        args=["mcp/server.py"],
        cwd=str(ROOT),
        env={**os.environ, "ATLAS_JSON": str(atlas_json)},
    )
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as c:
            await c.initialize()
            tools = await c.list_tools()
            got = await c.call_tool("get", {"id": "jais-30b"})
            rec = await c.call_tool("recommend", {"task": "chat", "dialect": "msa", "limit": 10})
            srch = await c.call_tool("search", {"query": "jais"})
            missing = await c.call_tool("get", {"id": "nope"})
            typed = await c.call_tool("recommend", {"task": "chat", "type": "dataset"})
            schema = next(t.input_schema for t in tools.tools if t.name == "recommend")
            assert "type" in schema["properties"]
            assert not [x for x in typed.content if "jais-30b" in x.text]
            return (
                {t.name for t in tools.tools},
                got.content[0].text,
                "\n".join(c.text for c in rec.content),
                missing.content[0].text,
                srch.content,
            )


def test_mcp_server_roundtrip(tmp_path, fixture_entries):
    ids = build_hf_ids(fixture_entries)
    cache = {i: {"downloads": 10, "likes": 1, "lastModified": None} for i in ids}
    doc = build_atlas_json(merge_metrics(fixture_entries, cache), "2026-10-04")
    p = tmp_path / "atlas.json"
    p.write_text(json.dumps(doc))
    names, got, rec, missing, srch = asyncio.run(_run(p))
    assert names == {"search", "recommend", "get"}
    assert "jais-30b" in got
    assert "jais-30b" in rec
    assert "unknown id" in missing
    assert len(srch) == 1 and "jais-30b" in srch[0].text
