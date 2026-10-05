"""Wanted-list gap rules: declarative queries for resources the atlas lacks."""
import re
from datetime import date as _date
from pathlib import Path
from urllib.parse import quote

import yaml

from atlas.query import license_class

RULE_KEYS = ("type", "country", "dialects", "license_class", "on_device", "tasks")
LICENSE_CLASSES = ("open", "any")
MAX_WHY = 160
_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_ENUM_KEYS = ("type", "country", "dialects")


def load_rules(path: Path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if doc is None:
        return []
    if not isinstance(doc, list):
        raise ValueError(f"{path.name}: expected a YAML list of rules, got {type(doc).__name__}")
    return doc


def _as_list(value) -> list:
    if value is None:
        return []
    return list(value) if isinstance(value, (list, tuple)) else [value]


def _enum(schema: dict, key: str) -> list[str]:
    prop = schema["properties"][key]
    return list((prop.get("items") or prop)["enum"])


def validate_rules(rules: list[dict], schema: dict) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for rule in rules:
        rid = rule.get("id") if isinstance(rule, dict) else None
        pre = f"wanted.yaml:{rid if rid is not None else '<no id>'}: "
        if not isinstance(rule, dict):
            errors.append(pre + "rule must be a mapping")
            continue
        if not isinstance(rid, str) or not _ID_RE.match(rid):
            errors.append(pre + f"id {rid!r} must match {_ID_RE.pattern}")
        elif rid in seen:
            errors.append(pre + "duplicate id")
        else:
            seen.add(rid)
        title = rule.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(pre + "title must be a non-empty string")
        why = rule.get("why")
        if not isinstance(why, str) or not why.strip():
            errors.append(pre + "why must be a non-empty string")
        elif len(why) > MAX_WHY:
            errors.append(pre + f"why is {len(why)} chars, max {MAX_WHY}")
        query = rule.get("query")
        if not isinstance(query, dict):
            errors.append(pre + "query must be a mapping")
            continue
        if not query:
            errors.append(pre + "query is empty")
            continue
        for key in query:
            if key not in RULE_KEYS:
                errors.append(pre + f"unknown query key {key!r} (allowed: {', '.join(RULE_KEYS)})")
        for key in _ENUM_KEYS:
            if key in query:
                allowed = _enum(schema, key)
                for v in _as_list(query[key]):
                    if v not in allowed:
                        errors.append(pre + f"{key} value {v!r} not in schema enum")
        if "license_class" in query and query["license_class"] not in LICENSE_CLASSES:
            errors.append(pre + f"license_class {query['license_class']!r} must be one of {', '.join(LICENSE_CLASSES)}")
        if "on_device" in query and not isinstance(query["on_device"], bool):
            errors.append(pre + "on_device must be true or false")
        if "tasks" in query:
            ts = _as_list(query["tasks"])
            if not ts or not all(isinstance(t, str) and t.strip() for t in ts):
                errors.append(pre + "tasks must be non-empty strings")
    return errors


def match_rule(entry: dict, query: dict) -> bool:
    etype = entry.get("type")
    if etype == "paper" and "paper" not in _as_list(query.get("type")):
        return False
    if "type" in query and etype not in _as_list(query["type"]):
        return False
    if "country" in query and entry.get("country") not in _as_list(query["country"]):
        return False
    if "dialects" in query and not set(_as_list(query["dialects"])) & set(entry.get("dialects") or []):
        return False
    lc = query.get("license_class")
    if lc == "open" and license_class(entry.get("license")) != "open":
        return False
    if "on_device" in query:
        if (entry.get("on_device") is True) != bool(query["on_device"]):
            return False
    if "tasks" in query:
        have = {str(t).lower() for t in (entry.get("tasks") or []) + (entry.get("tags") or [])}
        if not {str(t).lower() for t in _as_list(query["tasks"])} & have:
            return False
    return True


def matches(rule: dict, entries: list[dict]) -> list[str]:
    query = rule.get("query") or {}
    return sorted(e["id"] for e in entries if match_rule(e, query))


FILLED_WINDOW_DAYS = 30
_HASH_KEYS = (("type", "type"), ("country", "country"), ("dialects", "dialect"))


def wanted_hash(query: dict) -> str:
    """Site hash for a rule, in the same key order as site/app.js serializeHash."""
    enc = lambda v: quote(str(v), safe="-_.!~*'()")  # encodeURIComponent
    parts = []
    tasks = _as_list(query.get("tasks"))
    if len(tasks) == 1:
        parts.append("q=" + enc(tasks[0]))
    for key, name in _HASH_KEYS:
        vals = _as_list(query.get(key))
        if vals:
            parts.append(name + "=" + ",".join(enc(v) for v in vals))
    if query.get("license_class") == "open":
        parts.append("license=open")
    if query.get("on_device") is True:
        parts.append("on_device=1")
    return "#" + "&".join(parts) if parts else ""


def rule_text(query: dict) -> str:
    parts = []
    for key in RULE_KEYS:
        if key not in query:
            continue
        v = query[key]
        if isinstance(v, bool):
            v = "true" if v else "false"
        else:
            v = ",".join(str(x) for x in _as_list(v))
        label = "license" if key == "license_class" else key
        parts.append(f"{label}={v}")
    return " · ".join(parts)


def evaluate(rules: list[dict], entries: list[dict], cache: dict, date: str) -> tuple[list[dict], dict]:
    today = _date.fromisoformat(date)
    statuses, new_cache = [], {}
    for rule in rules:
        by = matches(rule, entries)
        filled_on = None
        if by:
            prior = cache.get(rule["id"]) or {}
            filled_on = prior.get("filled_on") or date
            new_cache[rule["id"]] = {"filled_on": filled_on, "by": by}
        recent = bool(by) and 0 <= (today - _date.fromisoformat(filled_on)).days <= FILLED_WINDOW_DAYS
        statuses.append({
            "id": rule["id"], "title": rule["title"], "why": rule["why"], "query": rule["query"],
            "status": "filled" if by else "open", "filled_on": filled_on, "by": by,
            "recent": recent, "hash": wanted_hash(rule["query"]),
        })
    return statuses, dict(sorted(new_cache.items()))
