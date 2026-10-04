Post when: the repo is public at github.com/h9-tec/arabic-ai-atlas and the first CI run is green.

# LinkedIn post

I turned Awesome Arabic NLP into something an agent can use. The Arabic AI Atlas tracks 271 Arabic models, datasets, tools and organizations across Saudi Arabia, the UAE, Egypt, Qatar, Morocco and more, drawn as one map: columns by country, rows by modality, nodes sized by live Hugging Face downloads.

The part I care about most: it installs into Claude Code as a plugin. An MCP server answers questions like "which open Arabic TTS runs on a phone?" from a local JSON file, and five skills cover the work Arabic builders repeat: model selection, tashkeel, RTL/LTR linting, dialect prompts and tokenizer cost.

Everything is generated from YAML. CI rebuilds the map, README, JSON and llms.txt on every change, and a nightly job refreshes download counts for the 121 entries on Hugging Face. Country tags are still incomplete, and many entries still lack dialect tags and license data. PRs are one YAML file each.

```
claude plugin marketplace add h9-tec/arabic-ai-atlas
claude plugin install arabic-ai-atlas@arabic-ai-atlas
```

https://github.com/h9-tec/arabic-ai-atlas

#ArabicNLP #LLM #MCP #ClaudeCode #OpenSource
