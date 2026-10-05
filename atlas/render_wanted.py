"""Render the Most Wanted board: README block and docs/tables/wanted.md."""
from atlas.render_readme import README_CAP, SITE, esc
from atlas.wanted import rule_text

LEAD = ("_Gaps nobody has filled yet. Add an entry that matches a rule and it moves to Recently filled. "
        "Rules live in [data/wanted.yaml](data/wanted.yaml)._")
ALL_FILLED = "_Every wanted gap is filled. Propose a new one in [data/wanted.yaml](data/wanted.yaml)._"


def _gap_row(s: dict) -> str:
    return f"| [{esc(s['title'])}]({SITE}{s['hash']}) | {esc(s['why'])} | `{esc(rule_text(s['query']))}` |"


def render_wanted_block(statuses: list[dict]) -> str:
    open_ = [s for s in statuses if s["status"] == "open"]
    recent = [s for s in statuses if s["status"] == "filled" and s["recent"]]
    lines = [LEAD, ""]
    if open_:
        lines += ["| Gap | Why | Rule |", "| --- | --- | --- |"]
        lines += [_gap_row(s) for s in open_[:README_CAP]]
        if len(open_) > README_CAP:
            lines += ["", f"[all {len(open_)} gaps](docs/tables/wanted.md)"]
    else:
        lines.append(ALL_FILLED)
    if recent:
        lines += ["", "**Recently filled:**", ""]
        lines += [f"- {s['title']}, filled {s['filled_on']} by {', '.join(s['by'])}" for s in recent]
    return "\n".join(lines)


def render_wanted_table(statuses: list[dict], generated_at: str) -> str:
    n_open = sum(1 for s in statuses if s["status"] == "open")
    lines = [f"# Most Wanted ({n_open} open of {len(statuses)})", "",
             f"[← README](../../README.md) · [interactive map]({SITE})", "",
             "| Gap | Why | Rule | Status |", "| --- | --- | --- | --- |"]
    for s in statuses:
        status = "open" if s["status"] == "open" else f"filled {s['filled_on']}"
        lines.append(f"{_gap_row(s)} {status} |")
    lines += ["", "---", "", f"_Generated {generated_at}. Do not edit by hand._"]
    return "\n".join(lines) + "\n"
