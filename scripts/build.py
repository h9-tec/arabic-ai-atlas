"""Build CLI: validate, enrich, build, all."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # works even when the package is not installed

from atlas.enrich import build_hf_ids, fetch_hf_metrics, merge_metrics
from atlas.load import load_entries
from atlas.render_json import build_atlas_json, build_llms_txt
from atlas.validate import load_schema, validate_entries


def _validate(data: Path) -> tuple[list[dict], list[str]]:
    entries = load_entries(data)
    schema_path = data / "schema.json"
    if not schema_path.exists():  # fixtures carry no schema; use the repo's
        schema_path = ROOT / "data" / "schema.json"
    errors = validate_entries(entries, load_schema(schema_path))
    return entries, errors


def _report_errors(errors: list[str]) -> int:
    for err in errors:
        print(err, file=sys.stderr)
    print(f"{len(errors)} validation error(s)", file=sys.stderr)
    return 1


def _cache_path(data: Path) -> Path:
    return data / ".cache" / "hf.json"


def _load_cache(data: Path) -> dict:
    path = _cache_path(data)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def cmd_enrich(entries: list[dict], data: Path, date: str) -> int:
    cache, warnings = fetch_hf_metrics(build_hf_ids(entries), _load_cache(data), now=date)
    path = _cache_path(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    print(f"enriched {len(cache)} HF ids ({len(warnings)} warnings)")
    return 0


def cmd_build(entries: list[dict], data: Path, out: Path, date: str) -> int:
    merged = merge_metrics(entries, _load_cache(data))
    dist = out / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    doc = build_atlas_json(merged, date)
    (dist / "atlas.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (dist / "llms.txt").write_text(build_llms_txt(merged, date), encoding="utf-8")

    # README and map renderers arrive in later tasks; wire them in only when the
    # modules exist so those tasks need not touch this file.
    try:
        from atlas.render_readme import render_readme
    except ImportError:
        render_readme = None
    try:
        from atlas.render_map import render_svg
    except ImportError:
        render_svg = None
    if render_readme:
        from atlas.render_readme import load_shipped_skills

        template = (ROOT / "templates" / "README.tmpl.md").read_text(encoding="utf-8")
        skills = load_shipped_skills(ROOT / "skills")
        (out / "README.md").write_text(render_readme(merged, template, date, skills), encoding="utf-8")
    if render_svg:
        (out / "assets").mkdir(parents=True, exist_ok=True)
        (out / "assets" / "map.svg").write_text(render_svg(merged, date), encoding="utf-8")
    print(f"built {doc['count']} entries into {dist}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="build.py")
    p.add_argument("command", choices=["validate", "enrich", "build", "all"])
    p.add_argument("--data", default="data")
    p.add_argument("--out", default=".")
    p.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    p.add_argument("--skip-enrich", action="store_true", help="build/all: use the cached HF metrics as is")
    args = p.parse_args(argv)
    data, out = Path(args.data), Path(args.out)

    entries, errors = _validate(data)
    if errors:
        return _report_errors(errors)
    if args.command == "validate":
        print(f"{len(entries)} entries valid")
        return 0
    if args.command == "enrich" or (args.command == "all" and not args.skip_enrich):
        cmd_enrich(entries, data, args.date)
    if args.command in ("build", "all"):
        return cmd_build(entries, data, out, args.date)
    return 0


if __name__ == "__main__":
    sys.exit(main())
