"""Build CLI: validate, enrich, build, all."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # works even when the package is not installed

from atlas.enrich import FETCHED_AT, apply_cached_licenses, build_hf_ids, fetch_hf_metrics, merge_metrics
from atlas.load import load_entries
from atlas.render_json import build_atlas_json, build_llms_txt
from atlas.render_wanted import render_wanted_block, render_wanted_table
from atlas.validate import load_schema, validate_entries
from atlas.wanted import evaluate, load_rules, newly_filled, validate_rules


def _validate(data: Path) -> tuple[list[dict], list[str]]:
    entries = load_entries(data)
    schema_path = data / "schema.json"
    if not schema_path.exists():  # fixtures carry no schema; use the repo's
        schema_path = ROOT / "data" / "schema.json"
    schema = load_schema(schema_path)
    errors = validate_entries(entries, schema)
    errors += validate_rules(load_rules(data / "wanted.yaml"), schema)
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
    print(f"enriched {sum(1 for k in cache if k != FETCHED_AT)} HF ids ({len(warnings)} warnings)")
    return 0


def render_outputs(entries: list[dict], data: Path, date: str) -> dict[str, str]:
    """Render every generated file in memory, keyed by path relative to --out."""
    cache = _load_cache(data)
    merged = merge_metrics(apply_cached_licenses(entries, cache), cache)
    wpath = data / ".cache" / "wanted.json"
    wdisk = json.loads(wpath.read_text(encoding="utf-8")) if wpath.exists() else {}
    statuses, wcache = evaluate(load_rules(data / "wanted.yaml"), merged, wdisk, date)
    wanted = [{k: v for k, v in s.items() if k != "query"} for s in statuses]
    doc = build_atlas_json(merged, date, extras={"wanted": wanted})
    outputs = {
        "dist/atlas.json": json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        "dist/llms.txt": build_llms_txt(merged, date),
        "data/.cache/wanted.json": json.dumps(wcache, indent=2, ensure_ascii=False) + "\n",
    }
    # README and map renderers arrive in later tasks; wire them in only when the
    # modules exist so those tasks need not touch this file.
    try:
        from atlas.render_readme import load_shipped_skills, render_readme
    except ImportError:
        render_readme = None
    try:
        from atlas.render_map import render_svg
    except ImportError:
        render_svg = None
    if render_readme:
        template = (ROOT / "templates" / "README.tmpl.md").read_text(encoding="utf-8")
        skills = load_shipped_skills(ROOT / "skills")
        outputs["README.md"] = render_readme(merged, template, date, skills, blocks={"WANTED": render_wanted_block(statuses)})
        from atlas.render_readme import render_tables
        outputs.update(render_tables(merged, date))
        outputs["docs/tables/wanted.md"] = render_wanted_table(statuses, date)
    if render_svg:
        outputs["assets/map.svg"] = render_svg(merged, date)
    from atlas.render_geo import render_geo_svg
    outputs["assets/geo.svg"] = render_geo_svg(merged, date)
    return outputs


def cmd_build(entries: list[dict], data: Path, out: Path, date: str) -> int:
    outputs = render_outputs(entries, data, date)
    for rel, text in outputs.items():
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"built {len(outputs)} files into {out}")
    return 0


def _on_disk_date(out: Path) -> str | None:
    """The `generated_at` of the committed dist/atlas.json, if readable."""
    try:
        return json.loads((out / "dist" / "atlas.json").read_text(encoding="utf-8"))["generated_at"]
    except (OSError, ValueError, KeyError, TypeError):
        return None


def cmd_check(entries: list[dict], data: Path, out: Path, date: str) -> int:
    """Re-render with the on-disk generation date and compare byte for byte."""
    date = _on_disk_date(out) or date
    drifted = []
    for rel, text in render_outputs(entries, data, date).items():
        path = out / rel
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            drifted.append(rel)
    for rel in drifted:
        print(f"drift: {rel}", file=sys.stderr)
    if drifted:
        print("generated files are stale or hand-edited: run `uv run python scripts/build.py build`", file=sys.stderr)
    else:
        print("generated files are up to date")
    return 1 if drifted else 0


def cmd_wanted(entries: list[dict], data: Path, date: str, base_cache: str | None) -> int:
    """Print one `closes wanted:<id>` line per rule filled relative to the base cache."""
    cache = _load_cache(data)
    merged = merge_metrics(apply_cached_licenses(entries, cache), cache)
    wpath = data / ".cache" / "wanted.json"
    wdisk = json.loads(wpath.read_text(encoding="utf-8")) if wpath.exists() else {}
    _, wcache = evaluate(load_rules(data / "wanted.yaml"), merged, wdisk, date)
    base: dict = {}
    if base_cache and Path(base_cache).exists():
        text = Path(base_cache).read_text(encoding="utf-8").strip()
        base = json.loads(text) if text else {}
    for rid in newly_filled(base, wcache):
        print(f"closes wanted:{rid}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="build.py")
    p.add_argument("command", choices=["validate", "enrich", "build", "all", "wanted"])
    p.add_argument("--data", default="data")
    p.add_argument("--out", default=".")
    p.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    p.add_argument("--check", action="store_true", help="build: re-render with the date in dist/atlas.json, compare byte-exact with disk, write nothing, exit 1 on drift")
    p.add_argument("--skip-enrich", action="store_true", help="build/all: use the cached HF metrics as is")
    p.add_argument("--base-cache", default=None, help="wanted: base branch data/.cache/wanted.json (missing or empty counts as {})")
    args = p.parse_args(argv)
    data, out = Path(args.data), Path(args.out)

    entries, errors = _validate(data)
    if errors:
        return _report_errors(errors)
    if args.command == "validate":
        print(f"{len(entries)} entries valid")
        return 0
    if args.command == "wanted":
        return cmd_wanted(entries, data, args.date, args.base_cache)
    if args.check:
        if args.command != "build":
            p.error("--check only works with the build command")
        return cmd_check(entries, data, out, args.date)
    if args.command == "enrich" or (args.command == "all" and not args.skip_enrich):
        cmd_enrich(entries, data, args.date)
    if args.command in ("build", "all"):
        return cmd_build(entries, data, out, args.date)
    return 0


if __name__ == "__main__":
    sys.exit(main())
