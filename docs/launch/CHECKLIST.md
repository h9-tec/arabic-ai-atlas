Post when: the repo is public at github.com/h9-tec/arabic-ai-atlas and CI is green (both true as of 2026-10-05).

# Launch checklist

## Before posting

- [ ] Open https://h9-tec.github.io/arabic-ai-atlas/ in a fresh browser; check Map/Grid toggle, search and a shared URL such as `#country=EG&type=tts`.
- [ ] Run the two install commands in a clean Claude Code session and ask "which open Arabic TTS runs on a phone?" (expect Piper and two MMS models). Requires `uv`.
- [ ] Confirm `docs/launch/geo-map.png` is current (re-render from `assets/geo.svg` if the data changed).
- [ ] Confirm the numbers in each post still match `dist/atlas.json` (`count` field).

## Order of posting (one day)

1. X thread in English (attach `docs/launch/geo-map.png` to tweet 1), then the Arabic tweets 1 to 3 as a separate short thread an hour later.
2. LinkedIn post, 30 to 60 minutes after the X thread.
3. Arabic Discord and Telegram groups, with the 2-line message.
4. Show HN, aimed at US morning (see times below). Stay available for comments for 3 hours.
5. r/MachineLearning `[P]` post, then r/LocalLLaMA the next day, so the two do not compete.

## Best times

- Gulf (GMT+3/+4) and Egypt (GMT+3) daytime: Sunday to Thursday, 10:00 to 13:00 Riyadh time for X, LinkedIn and Arabic groups. Avoid Friday midday and Iftar hours in Ramadan.
- Show HN and Reddit: weekday 08:00 to 10:00 US Eastern, which is 15:00 to 17:00 Riyadh/Cairo time, so it still lands in Arab-world working hours.

## Who to tag (categories, not names)

- Arabic NLP lab accounts and the research groups behind entries on the map (university labs, national AI programmes).
- Maintainers of the main open Arabic models and datasets listed in the atlas.
- Arabic NLP community organisers (workshop organisers for WANLP, ArabicNLP, OSACT; ARBML/Masader maintainers).
- Hugging Face and Claude Code / MCP community accounts that share community plugins.
- Arabic tech newsletters and podcasts.

Tag at most 3 to 4 accounts per post, and only where their work is on the map.

## After posting

- [ ] Reply to every correction with a link to the YAML file and CONTRIBUTING.md.
- [ ] Track missing-entry requests as issues; merge small PRs within a day.
- [ ] Around 2026-11-03 (30 days after launch), submit the atlas to sindresorhus/awesome if it meets their list guidelines.
