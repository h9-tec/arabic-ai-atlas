# Arabic-ready badge: follow-up spec (stub)

Status: stub. Written after the v0.2 skeleton; not yet designed.

## Context

- Design: [atlas v0.2 design, section C](2026-10-05-atlas-v0-2-design.md#c-arabic-ready-badge-two-days)
- Skeleton: `/home/hesham/arabic-ready` (local repo, not pushed; GitHub repo `h9-tec/arabic-ready` not created). It has `action.yml` (composite, inputs `paths` and `strictness`), `arabic_ready/report.py` (`badge_endpoint`, `badge_markdown`) and tests.

## Deferred to this spec

Scoring rules, the `rtl-bidi-lint` and `token_cost` integration, publishing to gh-pages or a Gist, and the atlas `## 🏅 Arabic-ready repos` section.

## Open questions to settle before its plan

1. Score formula and per-check weights.
2. Which `rtl-bidi-lint` findings count toward the score.
3. gh-pages vs Gist as the default publish target, and the token scopes each needs.
4. Code-search query and caching for the atlas section: the unauthenticated limit, the cap of 100, and dedupe.
5. Whether `skills/rtl-bidi-lint/bidi_lint.py` is vendored into the action or installed.
