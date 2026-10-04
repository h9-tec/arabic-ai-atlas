Post when: the repo is public at github.com/h9-tec/arabic-ai-atlas and the first CI run is green.

# X thread

**1/6**

The Arabic AI ecosystem as one map: 271 models, datasets, tools and orgs, by country and modality, sized by Hugging Face downloads.

Install it into Claude Code:
claude plugin marketplace add h9-tec/arabic-ai-atlas
claude plugin install arabic-ai-atlas@arabic-ai-atlas

[attach assets/map.svg rendered as PNG]

**2/6**

The idea: don't just read the list, install it into your agent. Ask "which open Arabic TTS runs on a phone?" and its MCP server answers from the atlas offline, with licenses and download counts where known.

**3/6**

How it works: every entry is a YAML record. CI validates them and regenerates the map, the README, atlas.json, llms.txt and the plugin data. A nightly GitHub Action pulls fresh Hugging Face download counts, so the map tracks real usage.

**4/6**

5 skills ship with it:
arabic-ai-advisor: pick an LLM, ASR, TTS, OCR or embedding model
tashkeel-check: add or strip diacritics
rtl-bidi-lint: catch broken RTL/LTR mixing
arabic-dialect-prompts: prompts in a target dialect
arabic-token-cost: compare tokenizer cost

**5/6**

Numbers: 271 entries (68 LLMs, 53 datasets, 19 ASR, 12 TTS, 8 OCR), 7 countries plus international, 121 with live download counts.

Gaps I need PRs for: country tags still incomplete, more dialect tags and licenses. One YAML file per change.

**6/6**

Repo: https://github.com/h9-tec/arabic-ai-atlas
Sister list (hand-curated, 700+ lines): https://github.com/h9-tec/Awesome_Arabic_NLP
For LLMs: https://raw.githubusercontent.com/h9-tec/arabic-ai-atlas/main/dist/llms.txt

---

## Arabic versions

**1/6 (عربي)**

الذكاء الاصطناعي العربي في خريطة واحدة: 271 نموذجا ومجموعة بيانات وأداة وجهة، حسب الدولة والمجال، وحجم كل نقطة بتحميلات Hugging Face.

ثبتها في Claude Code:
claude plugin marketplace add h9-tec/arabic-ai-atlas
claude plugin install arabic-ai-atlas@arabic-ai-atlas

[attach assets/map.svg rendered as PNG]

**2/6 (عربي)**

الفكرة: القائمة ليست للقراءة فقط، بل يستخدمها وكيلك مباشرة. اسأله "أي نموذج TTS عربي مفتوح يعمل على الجوال؟" فيجيبك من الأطلس دون إنترنت، مع الرخصة وعدد التحميلات حيثما توفرت.
