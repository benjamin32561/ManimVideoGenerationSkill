# Introduction to Language — persistent todo

**Owner: the main session, working directly. No subagents.**
Update this file and `docs/IL_PROGRESS.md` at every state change.

Handoff: `docs/IL_HANDOFF.md`. Spine: `docs/IL_SERIES_SPINE.md`.

## Infra (2026-08-22)

- [x] Prefix `il-` in `skill_paths.py` → `introduction-to-language/`
- [x] Spine + script brief + scene brief + this todo + handoff

## Per video

Do not TTS *n+1* while *n* is still outline-only.
Do not write scene code until that video's script lints clean.
Do not start `-qm` until `review_gate.py --check` passes.

| # | slug | script | lint | TTS | scene | geom | review | encode |
|---|------|--------|------|-----|-------|------|--------|--------|
| 01 | il-01-descriptive | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| 02 | il-02-competence | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| 03 | il-03-learnability | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 04 | il-04-phonetics-ipa | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 05 | il-05-phonetics-acoustic | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 06 | il-06-phonemes | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 07 | il-07-categorical | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 08 | il-08-morphology | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 09 | il-09-lexicon | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 10 | il-10-syntax | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 11 | il-11-hierarchy | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 12 | il-12-semantics-pragmatics | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 13 | il-13-acquisition | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

## Resume this session

Write and lint `il-03-learnability`, then TTS. Class `Learnability`.
