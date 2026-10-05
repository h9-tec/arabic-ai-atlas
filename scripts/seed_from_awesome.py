"""Seed data/*.yaml from the Awesome_Arabic_NLP README.

Usage: uv run python scripts/seed_from_awesome.py --src ~/Awesome_Arabic_NLP/README.md --out data/
"""
import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from atlas.seed import dedupe, parse_papers, parse_tables  # noqa: E402

FILES = {
    "llm": "llms.yaml",
    "asr": "asr.yaml",
    "tts": "tts.yaml",
    "ocr": "ocr.yaml",
    "embedding": "embeddings.yaml",
    "dataset": "datasets.yaml",
    "tool": "tools.yaml",
    "benchmark": "benchmarks.yaml",
    "org": "orgs.yaml",
    "agent-skill": "agent-skills.yaml",
    "paper": "papers.yaml",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=Path("~/Awesome_Arabic_NLP/README.md"))
    ap.add_argument("--out", type=Path, default=Path("data"))
    ap.add_argument("--force", action="store_true", help="overwrite non-empty data files")
    args = ap.parse_args()
    if not args.force:
        for fname in FILES.values():
            path = args.out / fname
            if path.exists() and yaml.safe_load(path.read_text(encoding="utf-8")):
                print(f"refusing to overwrite curated {path}; pass --force to override", file=sys.stderr)
                sys.exit(2)
    markdown = args.src.expanduser().read_text(encoding="utf-8")
    entries = dedupe(parse_tables(markdown)) + parse_papers(markdown)
    args.out.mkdir(parents=True, exist_ok=True)
    for typ, fname in FILES.items():
        group = [e for e in entries if e["type"] == typ]
        if not group:
            continue  # never clobber hand-written files (e.g. agent-skills.yaml)
        text = yaml.safe_dump(group, sort_keys=False, allow_unicode=True, width=1000)
        (args.out / fname).write_text(text, encoding="utf-8")
        print(f"{fname}: {len(group)}")


if __name__ == "__main__":
    main()
