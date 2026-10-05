# Model Passport: follow-up spec (stub)

Status: stub. Written after the v0.2 skeleton; not yet designed.

## Context

- Design: [atlas v0.2 design, section D](2026-10-05-atlas-v0-2-design.md#d-model-passport-three-days--inference)
- Skeleton: `probes/README.md` (formats), `probes/arabic-indic-digits/`, `atlas/passport.py` (`load_probes`, `verify_passport`), `scripts/passport.py` (`verify` works; `run` prints this path and exits 2).

## Deferred to this spec

The other 11 probes, inference (`transformers` and OpenAI-compatible runners), the stamp strip, the `passport` object in `atlas.json`, and `recommend(min_passport=...)`.

## Remaining probes (11)

1. Tashkeel preservation
2. Dialect adherence (Egyptian, Gulf, Maghrebi)
3. MSA drift under instruction
4. Quran quotation accuracy (exact match against a bundled verse table)
5. Code-switch handling
6. RTL punctuation
7. Tokenizer fertility
8. Refusal of hallucinated Arabic entities (asks about 5 nonexistent models, uses the atlas)
9. Translation sanity
10. Summarization length control
11. JSON-in-Arabic output validity

## Open questions to settle before its plan

1. The design says passports store a raw-outputs hash, yet CI re-runs checkers on stored outputs. Decide whether outputs are stored in full (size) or CI only checks the hash.
2. Where the Quran verse table comes from, and its license.
3. How dialect adherence is judged without a model.
4. Passport file naming for HF ids containing `/`.
5. The stamp strip's README column budget.
