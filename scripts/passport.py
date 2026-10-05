"""Model passport CLI. `verify` re-checks stored outputs; `run` is not implemented yet."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from atlas.passport import load_probes, verify_passport  # noqa: E402

FOLLOWUP = "docs/superpowers/specs/2026-10-05-model-passport-followup.md"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="passport")
    sub = parser.add_subparsers(dest="cmd", required=True)
    ver = sub.add_parser("verify", help="re-check stored outputs in passport files")
    ver.add_argument("files", nargs="+")
    run = sub.add_parser("run", help="run probes against a model (not implemented)")
    run.add_argument("model_id")
    args = parser.parse_args(argv)

    if args.cmd == "run":
        print(f"passport run is not implemented yet: see {FOLLOWUP}", file=sys.stderr)
        print(FOLLOWUP)
        return 2

    probes = load_probes(ROOT / "probes")
    failed = False
    for name in args.files:
        try:
            passport = json.loads(Path(name).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"{name}: cannot read passport: {exc}", file=sys.stderr)
            failed = True
            continue
        for msg in verify_passport(passport, probes):
            print(f"{name}: {msg}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
