# Project Rules

- data/ is source of truth
- run `uv run python scripts/build.py build` after editing data (`all` also refetches HF metrics; leave that to the nightly job)
- never hand-edit README.md, docs/tables/, assets/, dist/
