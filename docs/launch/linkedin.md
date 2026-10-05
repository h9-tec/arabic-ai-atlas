Post when: the repo is public at github.com/h9-tec/arabic-ai-atlas and CI is green (both true as of 2026-10-05).

# LinkedIn post

The Arabic AI Atlas now tracks 3,291 Arabic models, datasets, papers, tools and organisations, drawn on a real map of the Arab world. Countries are shaded by entry count, each type is a bubble sized by Hugging Face downloads, and a click on a country lists its work. 18 of the 22 Arab League countries have entries, led by Saudi Arabia, the UAE, Egypt and Qatar.

It also installs into Claude Code as a plugin. An offline MCP server answers questions like "which open Arabic TTS runs on a phone?" from a local JSON file, and five skills cover model choice, tashkeel, RTL linting, dialect prompts and tokenizer cost.

I built it from a full Hugging Face crawl plus GitHub, arXiv, Masader and the ACL Arabic workshops, then hand-reviewed 650 entries and checked every link. Gaps remain: four countries have no entries, and many licenses are unknown. Corrections are one YAML edit per PR.

```
claude plugin marketplace add h9-tec/arabic-ai-atlas
claude plugin install arabic-ai-atlas@arabic-ai-atlas
```

Map: https://h9-tec.github.io/arabic-ai-atlas/

#ArabicNLP #ArabicAI #LLM #MCP #OpenSource
