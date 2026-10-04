# Arabic dialect prompt reference

> Dialect lines were drafted by a model and still need native-speaker review, especially magh, sudanese and yemeni.

Codes match the `dialect` enum used by the atlas and its MCP `recommend` tool.

| Code | Name | Register notes | Example system-prompt line |
| --- | --- | --- | --- |
| `msa` | الفصحى المعاصرة (Modern Standard Arabic) | Formal, neutral, understood everywhere. News, documents, official support. | أنت مساعد رسمي. أجب بلغة عربية فصيحة واضحة ومختصرة. |
| `egy` | العامية المصرية (Egyptian) | Most widely understood dialect, dominant in media. Friendly, informal, humorous. | إنت مساعد ودود. اتكلم مصري ببساطة وماتستخدمش الفصحى. |
| `gulf` | اللهجة الخليجية (Gulf) | Khaliji across Saudi, UAE, Kuwait, Qatar, Bahrain, Oman. Polite and warm, with local expressions. | أنت مساعد ودود. تكلم باللهجة الخليجية وخلك مختصر وما تستخدم الفصحى. |
| `lev` | اللهجة الشامية (Levantine) | Syria, Lebanon, Jordan, Palestine. Soft, conversational. | أنت مساعد لطيف. احكي باللهجة الشامية بشكل بسيط وما تستعمل الفصحى. |
| `magh` | اللهجة المغاربية (Maghrebi / Darija) | Morocco, Algeria, Tunisia. Heavy French and Amazigh borrowing, often written in Latin script too. Hardest for models. | راك مساعد مزيان. هضر بالدارجة المغربية وما تستعملش الفصحى. |
| `iraqi` | اللهجة العراقية (Iraqi) | Distinct vocabulary and pronouns, close to Gulf in the south. Direct, expressive. | إنت مساعد حبوب. جاوب باللهجة العراقية وبلا فصحى. |
| `sudanese` | اللهجة السودانية (Sudanese) | Calm, respectful tone with its own idioms. Little training data, so expect more drift. | إنت مساعد سمح. اتكلم سوداني زي ناس الخرطوم، وما تستخدم الفصحى. |
| `yemeni` | اللهجة اليمنية (Yemeni) | Several regional varieties (Sanaani, Adeni, Hadrami). Pick one and say which. Little training data. | إنت مساعد طيّب. اتكلّم صنعاني زي ما يتكلّموا في صنعاء، وما تجيبش فصحى. |
| `classical` | العربية الكلاسيكية (Classical Arabic) | Quranic and heritage register, full case endings, archaic vocabulary. Often needs tashkeel. | أجب بلسان عربي فصيح على نهج التراث، واضبط الكلمات بالشكل. |
| `mixed` | لغة مختلطة (Mixed / code-switching) | Dialect blended with English or French words, as in everyday chat. Mirror the user's mix. | أنت مساعد عصري. رد بنفس أسلوب المستخدم، عامية مع كلمات إنجليزية لو استخدمها. |

## Common failure: drift to MSA

Models default to formal Arabic. The first reply may be in dialect, then later turns slide back to MSA, especially after a long context or a factual question.

Fix, in order of strength:

1. Few-shot in the dialect: put 2 to 3 user/assistant exchanges written in the target dialect in the prompt, including at least one factual answer.
2. Explicit instruction, in the dialect, for example «اتكلم مصري ببساطة وماتستخدمش الفصحى».
3. Write the whole system prompt in the dialect, not in English.
4. Re-state the instruction near the end of long contexts, or add a short style reminder to each turn.
5. If drift persists, try a model with stronger coverage of that dialect (`recommend(task="chat", dialect="<code>")`).
