Post when: the repo is public at github.com/h9-tec/arabic-ai-atlas and the first CI run is green.

# Hacker News

**Title:** Show HN: Arabic AI Atlas, 271 Arabic models and datasets as a map and MCP server

**URL:** https://github.com/h9-tec/arabic-ai-atlas

**Body:**

I maintain Awesome Arabic NLP, a hand-curated list. Lists go stale, so I rebuilt it as data: 271 entries (LLMs, ASR, TTS, OCR, embeddings, datasets, benchmarks, orgs) in YAML. CI generates a landscape map by country and modality, the README, a JSON file and llms.txt. A nightly job refreshes Hugging Face download counts for 121 entries.

The plugin angle: the repo is also a Claude Code plugin. An offline MCP server exposes search, recommend and get over the JSON, plus five skills (model picking, tashkeel, RTL lint, dialect prompts, token cost), so your agent can answer "which open Arabic TTS runs on a phone?" itself.

Missing: Egypt and Morocco coverage, dialect tags, licenses. Feedback on the schema and map welcome.

# r/MachineLearning

**Title:** [P] Arabic AI Atlas: 271 Arabic LLMs, speech models and datasets as YAML, a map, JSON and an MCP server

**Body:**

Arabic AI resources are spread across Hugging Face orgs, university labs, government programs and papers. I kept a hand-curated awesome list for a while and rebuilt it as structured data.

What is in it: 271 entries, including 68 LLMs, 53 datasets, 19 ASR, 17 benchmarks, 12 TTS, 8 OCR and 6 embedding models, plus 61 organizations. Each entry has country, modality, tasks, license and links. 121 entries carry Hugging Face download counts refreshed nightly by a GitHub Action.

Outputs, all generated from the YAML: an SVG landscape map (columns by country, rows by modality, nodes sized by downloads), a README, dist/atlas.json and llms.txt. The repo also works as a Claude Code plugin with an offline MCP server (search, recommend, get) and five Arabic-specific skills.

Known gaps: thin coverage for Egypt and Morocco, incomplete dialect tags and licenses. Corrections and missing entries are one YAML file per PR. What would you add?

# r/LocalLLaMA

**Title:** Arabic AI Atlas: every open Arabic LLM, ASR and TTS model I could find, sized by downloads, queryable from your agent via MCP

# Arabic AI Discord / Telegram groups

أطلقت "أطلس الذكاء الاصطناعي العربي": 271 نموذجا وبيانات وأداة عربية في خريطة واحدة وملف JSON، ويمكن تثبيته كإضافة في Claude Code ليجيب وكيلك عن أسئلة مثل "أي نموذج TTS عربي يعمل على الجوال؟".
التغطية ناقصة لمصر والمغرب ووسوم اللهجات، ومساهماتكم مرحب بها: https://github.com/h9-tec/arabic-ai-atlas
