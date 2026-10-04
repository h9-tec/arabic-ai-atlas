---
name: tashkeel-check
description: Use when Arabic text may need diacritics (tashkeel) added or stripped, for TTS input, learner material, Quran or poetry, or when diacritization looks partial or inconsistent.
---

# Tashkeel Check

Decide whether Arabic text should carry diacritics, detect partial tashkeel, and point to diacritization tools in the Arabic AI Atlas.

## When to add or strip

- Add tashkeel for: TTS input (ambiguous words are mispronounced without it), Quran and classical poetry, children's and learner material, and words whose meaning depends on vowels (عَلِمَ / عِلْم / عَلَّمَ).
- Strip tashkeel for: search indexing, embeddings, deduplication, NER, and text matching, where diacritics fragment otherwise identical words.
- Leave it off for ordinary chat and UI text unless the user asks.

## Detecting partial tashkeel

Diacritics are the range U+064B to U+0652, as the regex `[ً-ْ]`. Count Arabic letters (`[ء-ي]`) and diacritic marks per text.

- Zero marks: undiacritized.
- Marks on most letters: fully diacritized.
- A low but non-zero ratio, or marks on only some words: partial. This is usually a mistake, because models read it as a signal to mix styles. Either complete it or strip it.

## Procedure

1. Classify the text (none, partial, full) with the regex above and state the ratio of marks to letters.
2. Decide the target from the use case in the section above. Say which you chose and why.
3. To add tashkeel, call the MCP tool `search(query="diacritization")` and recommend what the atlas returns (name, license, link). To strip, apply `re.sub("[ً-ْ]", "", text)` (add U+0670 and U+0640 if the user also wants the dagger alef and tatweel removed).

## Rules

- Never report a diacritization tool the atlas did not return. If `search` is unavailable or empty, say so.
- Do not auto-diacritize Quranic text; point to a verified source (Tanzil, King Fahd Complex).
- Machine diacritization has errors; ask for human review on anything publication-grade.
