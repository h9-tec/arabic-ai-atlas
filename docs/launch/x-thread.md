Post when: the repo is public at github.com/h9-tec/arabic-ai-atlas and CI is green (both true as of 2026-10-05).

# X thread

**1/7**

3,291 Arabic AI models, datasets, papers and tools on one map of the Arab world. Countries shaded by entry count, bubbles sized by Hugging Face downloads. Click a country to see its work.

https://h9-tec.github.io/arabic-ai-atlas/

[attach docs/launch/geo-map.png]

**2/7**

It is also a Claude Code plugin. An offline MCP server (search, recommend, get) reads the atlas JSON, so you can ask "which open Arabic TTS runs on a phone?" and get Piper and two MMS models back.

claude plugin marketplace add h9-tec/arabic-ai-atlas

**3/7**

18 of the 22 Arab League countries have entries. Saudi Arabia 355, UAE 184, Egypt 144, Qatar 128, Morocco 71, Algeria 42, Palestine 30.

1,586 entries carry dialect tags: MSA, Egyptian, Gulf, Levantine, Maghrebi, Iraqi, Sudanese, Yemeni, Classical.

**4/7**

1,159 datasets and 732 papers, plus 387 LLMs, 173 ASR and 85 TTS models.

Built from a full Hugging Face crawl (23k models, 16k datasets examined), GitHub, arXiv, Masader and ACL Arabic workshops: 8,300 candidates filtered, 650 hand-reviewed, every link checked.

**5/7**

5 skills ship with the plugin:
arabic-ai-advisor: pick an LLM, ASR, TTS, OCR or embedder
tashkeel-check: add or strip diacritics
rtl-bidi-lint: catch broken RTL/LTR mixing
arabic-dialect-prompts: prompts in a target dialect
arabic-token-cost: compare tokenizer cost

**6/7**

Gaps: Mauritania, Somalia, Djibouti and Comoros have no entries yet. Many licenses read "unknown" because the model card omits them. Most papers lack affiliations.

Fixes are a PR: edit the YAML, run one build command.

**7/7**

Repo: https://github.com/h9-tec/arabic-ai-atlas
Map: https://h9-tec.github.io/arabic-ai-atlas/
For LLMs: https://raw.githubusercontent.com/h9-tec/arabic-ai-atlas/main/dist/llms.txt
Sister list: https://github.com/h9-tec/Awesome_Arabic_NLP

Data CC BY 4.0, code MIT.

---

## Arabic versions

**1/7 (عربي)**

3,291 نموذجا ومجموعة بيانات وورقة بحثية وأداة وجهة في الذكاء الاصطناعي العربي، على خريطة واحدة للعالم العربي. اضغط على أي دولة لترى ما أُنجز فيها.

https://h9-tec.github.io/arabic-ai-atlas/

[attach docs/launch/geo-map.png]

**2/7 (عربي)**

الأطلس أيضا إضافة لـ Claude Code. خادم MCP يعمل دون إنترنت ويقرأ بيانات الأطلس، فتسأل وكيلك "أي نموذج TTS عربي مفتوح يعمل على الجوال؟" فيقترح Piper ونموذجين من MMS.

claude plugin marketplace add h9-tec/arabic-ai-atlas

**3/7 (عربي)**

18 دولة من 22 في الجامعة العربية لها مدخلات. السعودية 355، الإمارات 184، مصر 144، قطر 128، المغرب 71، الجزائر 42، فلسطين 30.

و1,586 مدخلا موسومة باللهجة: الفصحى والمصرية والخليجية والشامية والمغاربية والعراقية وغيرها.
