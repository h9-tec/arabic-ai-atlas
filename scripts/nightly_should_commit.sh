#!/usr/bin/env bash
# Decide whether the staged nightly refresh is worth a commit.
#
# The nightly build re-stamps dates in README.md, assets/map.svg, dist/* and the
# HF cache every day. Committing a date-only diff would make every open data PR
# conflict with main for no content change, so we skip it.
#
# Exit 0: commit. Exit 1: skip (nothing staged, or the staged diff only moves dates).
# A commit is required as soon as any of these holds:
#   - a file outside the generated set changed;
#   - a file's added and deleted line counts differ;
#   - a changed line contains no date (YYYY-MM-DD, or the badge form YYYY--MM--DD).
set -euo pipefail

generated=" README.md assets/map.svg dist/llms.txt dist/atlas.json data/.cache/hf.json "

if git diff --cached --quiet; then
  echo "skip: nothing staged"
  exit 1
fi

while IFS=$'\t' read -r added deleted file; do
  case "$generated" in
    *" $file "*) ;;
    *) echo "commit: $file changed"; exit 0 ;;
  esac
  if [ "$added" != "$deleted" ]; then
    echo "commit: $file +$added -$deleted"
    exit 0
  fi
done < <(git diff --cached --numstat)

non_date=$( (git diff --cached -U0 | grep '^[+-][^+-]' | grep -vE '[0-9]{4}-{1,2}[0-9]{2}-{1,2}[0-9]{2}' || true) | wc -l)
if [ "$non_date" -gt 0 ]; then
  echo "commit: $non_date changed line(s) beyond dates"
  exit 0
fi

echo "skip: only dates changed"
exit 1
