"""Model passport: probe loading and stored-output verification (no inference)."""
import importlib.util
from pathlib import Path

import yaml

PROBE_KEYS = ("id", "title", "prompts", "checker", "expected")


def _load_checker(folder: Path, module: str):
    spec = importlib.util.spec_from_file_location(f"probe_{folder.name.replace('-', '_')}_{module}", folder / f"{module}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.check


def load_probes(probes_dir: Path) -> dict[str, dict]:
    probes_dir = Path(probes_dir)
    out: dict[str, dict] = {}
    for yaml_path in sorted(probes_dir.glob("*/probe.yaml")):
        doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        folder = yaml_path.parent
        missing = [k for k in PROBE_KEYS if k not in doc]
        if missing:
            raise ValueError(f"{folder.name}/probe.yaml: missing keys {missing}")
        if doc["id"] != folder.name:
            raise ValueError(f"{folder.name}/probe.yaml: id {doc['id']!r} does not match folder name")
        doc["check"] = _load_checker(folder, doc["checker"])
        out[doc["id"]] = doc
    return dict(sorted(out.items()))


def verify_passport(passport: dict, probes: dict) -> list[str]:
    model = passport.get("model", "<no model>")
    messages: list[str] = []
    for pid, res in (passport.get("results") or {}).items():
        probe = probes.get(pid)
        if probe is None:
            messages.append(f"{model}: unknown probe {pid!r}")
            continue
        outputs = res.get("outputs") or []
        rerun = bool(outputs) and all(probe["check"](o, probe["expected"]) for o in outputs)
        if rerun != bool(res.get("pass")):
            messages.append(f"{model}: probe {pid!r} stored pass={res.get('pass')} but re-check gives {rerun}")
    return messages
