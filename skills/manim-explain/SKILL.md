---
name: manim-explain
description: >-
  Creates 3Blue1Brown-style Manim explainer videos with synced voiceover.
  Use when the user asks for an explainer video, 3b1b-style animation, Manim
  with narration, teaching a concept visually with voiceover, or producing a
  timed lesson MP4. Mandates narrative planning before Manim code, OpenRouter
  TTS with word-timestamp sync, LaTeX on-screen with spoken-math
  narration, morph-not-respawn motion, and craft-laws updates from user feedback.
license: MIT
compatibility: >-
  Requires Manim Community, ffmpeg, a LaTeX install with dvisvgm, Python with
  requests + PyYAML, and an OPENROUTER_API_KEY for TTS and word alignment.
metadata:
  author: Ben Akhovan
  version: "0.1.0"
  repository: https://github.com/benjamin32561/ManimVideoGenerationSkill
---

# Manim Explainer (3b1b + voiceover)

## Hard rules

1. **Plan before code.** Write `script.yaml` (thesis, pattern, beats with cues) — then TTS/align — then Manim.
   **Run end to end without approval gates.** Do not stop to ask whether the arc is OK;
   self-review against the craft laws, ship the MP4, then iterate on feedback.
2. **Audio-first sync.** Never stretch audio to fit a pre-timed video as the primary mode.
3. **LaTeX on screen** (`MathTex` / `Tex`). Classic dark 3b1b look.
4. **TTS never gets raw LaTeX.** Narration uses spoken math only. See [references/spoken-math.md](references/spoken-math.md).
5. **Tone split:** curious hooks / story; documentary explanations. Lead-in **question**, not “let’s start…”.
6. **Progressive reveal.** One idea per beat. Concrete hook → abstract forever (unless a tiny toy).
7. **Morph, don’t respawn.** Related A→B transforms in place. First charts must animate, then soft-idle.
8. **Every spoken change has a visible one.** If the VO gives an object a verb or
   an adjective — grows, spreads, cancels, crowds, peakier, frozen — that motion
   plays *on that word*. `lint_script.py` checks this against `show:` before TTS;
   `check_sync.py` checks the rendered result against the real timeline. Neither
   is optional.
9. **Picture matches the spoken noun.** Show the structure VO names; labels on the correct side (inputs↔classes). Questions move referents; named objects pop then settle in a **baked audio pause** (`tts_chunk` split + `pause_after`); causal pairs move both sides; procedures staged. Never put prose on a live graph.
10. **Math develops on screen.** Formula beats: spoken meaning for each piece + `MathTex` morph stages (BUILD_UP) — not a one-shot final equation. After questions / heavy morphs, bake long `pause_after` (questions 0.9–1.3s).
11. **Use project scripts** under this skill’s `scripts/` — no ad-hoc TTS/mux paths. Run `lint_script.py` before TTS.
12. **Feedback → abstract skill law.** User craft corrections update [references/craft-laws.md](references/craft-laws.md) as *general* rules (plus related refs/templates), not only the current demo. Regen TTS when pauses/wording are wrong; visual-only only when VO is already correct.

**Read first:** [references/craft-laws.md](references/craft-laws.md)

## Environment

```bash
source "$MANIM_EXPLAIN_ROOT/scripts/env.sh"   # or <skill-dir>/scripts/env.sh
```

`env.sh` resolves the skill from its own location, finds the project root (git
root, else cwd), and loads `OPENROUTER_API_KEY` from the project `.env` — TTS
*and* STT both go through it. Set `MANIM_ENV=/path/to/env` in that `.env` when
Manim lives in a dedicated interpreter. Never hard-code install paths in a demo:
use `MANIM_EXPLAIN_ROOT`, or `scripts/skill_paths.py` from Python.

## Workflow checklist

```
- [ ] 1. Concept brief + narrative pattern (Wrong→Right, etc.)
- [ ] 2. Write demos/<slug>/script.yaml (beats, say, show, bookmarks, tts_chunk)
- [ ] 3. Self-review script against craft laws + sources (no approval gate — keep going)
- [ ] 4. Encode any new craft notes into references/craft-laws.md (abstracted)
- [ ] 5. `python scripts/lint_script.py demos/<slug>/script.yaml` (pauses, formula BUILD_UP)
- [ ] 6. TTS: python scripts/tts_openrouter.py demos/<slug>/script.yaml
- [ ] 7. Align: python scripts/align_words.py demos/<slug>
- [ ] 8. Implement Manim (morphs, formula BUILD_UP, soft idle, ask_about, LayoutBoard, `play_before`)
       — first two lines of `construct`: `tn.attach(self)` then `watch_layout(self, DEMO_DIR)`
- [ ] 9. pytest tests/test_layout.py → render -qm
- [ ] 10. **Motion audit:** `python scripts/check_sync.py demos/<slug>`
       → every silent cue is a beat the VO narrated and the picture ignored. Fix them.
- [ ] 11. **Layout audit:** `python scripts/check_layout.py demos/<slug>`
       → text that collided *during* motion, which bookmark stills never show. Fix them.
- [ ] 12. **Pixel QA:** `qa_frames.py demos/<slug> --from-timeline --contact-sheet`
       → samples motion ends + collisions, not just cue times. Read the sheet, then
       full frames for anything suspicious → fix → re-render → re-audit
- [ ] 13. On craft feedback: update craft-laws (+ refs/templates) BEFORE or WITH the demo fix
- [ ] 14. Deliver: script, scenes, audio/, timing.json, MP4, one-line thesis
```

### The three audits (required after every render)

Reading a contact sheet of bookmark stills is not enough: it samples the moments
*you* chose, and both classic failures happen elsewhere — a described change that
never animates, and text that collides only while something is moving or at full
size. The render instruments itself, so all three are mechanical:

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/check_sync.py"   demos/<slug>   # silent cues
python "$MANIM_EXPLAIN_ROOT/scripts/check_layout.py" demos/<slug>   # live collisions
python "$MANIM_EXPLAIN_ROOT/scripts/qa_frames.py"    demos/<slug> --from-timeline --contact-sheet
```

* **check_sync** — cue windows with no animation. A cue marks a visual event by
  definition, so a silent window is a beat where the narration moved and the
  picture did not. Also flags *thin* windows (a token pulse standing in for a
  described change) and long frozen stretches.
* **check_layout** — every text-vs-text overlap the renderer actually produced,
  with the interval it lasted. Requires `watch_layout(self, DEMO_DIR)` in the
  scene; it samples the live frame, so it sees collisions no snapshot can.
* **qa_frames --from-timeline** — stills at motion *ends* (where a growing shape
  is largest and a moving label has just landed) and at collision midpoints.

Then **Read** the contact sheet and the full-resolution frames for anything the
audits flagged. Do not ship on code review alone.

### Visual-only pass (no new audio)

When the user asks to improve visuals and VO is fine:

```
- [ ] Edit scenes / style only
- [ ] Keep timing.json + narration.mp3 unchanged
- [ ] Re-render with scripts/render_and_mux.sh … -qm
- [ ] Still encode any new craft lesson into craft-laws.md
```

## Artifacts per demo

```
demos/<slug>/
  script.yaml
  audio/narration.mp3
  timing.json
  scenes/*.py
  utils/style.py
  utils/layout_snapshots.py   # overlap tests
  out/final.mp4
  out/timeline.json           # what moved, when (written by TimedNarration)
  out/layout_violations.json  # live text collisions (written by watch_layout)
```

## Script contract

Each beat:

- `id`, `say` (spoken, **no LaTeX**), `bookmarks`, `show`, optional `latex`
- `emotional_beat`: curiosity | productive_confusion | partial_clarity | aha | settle
- `tts_chunk`: letter/id grouping beats into one TTS request (fewer prosody seams)
- `show:` must describe **staged motion** that matches spoken nouns (not static end-states)
- Length follows teaching after TTS — no preset duration

Template: [assets/script_template.yaml](assets/script_template.yaml)

## References (read before coding)

| Doc | When |
|-----|------|
| [craft-laws.md](references/craft-laws.md) | Always — accumulated production laws |
| [narrative-patterns.md](references/narrative-patterns.md) | Arc + hooks |
| [layout-craft.md](references/layout-craft.md) | Bands, morph rule, LayoutBoard |
| [sync-pipeline.md](references/sync-pipeline.md) | Timing / bookmarks |
| [tts-stt.md](references/tts-stt.md) | Models |
| [vo-tips.md](references/vo-tips.md) | Less-dead VO |
| [spoken-math.md](references/spoken-math.md) | Pronunciation |

## Utility scripts

| Script | Role |
|--------|------|
| `scripts/tts_openrouter.py` | The VO path — Grok Voice `leo`, `chunk_by: tts_chunk` |
| `scripts/align_words.py` | Whisper word timestamps (`--remap` re-maps cues with no STT call) |
| `scripts/lint_script.py` | Pre-TTS checks: question pauses, formula BUILD_UP, **spoken change-words vs `show:`** |
| `scripts/layout_check.py` | AABB overlap / safe frame |
| `scripts/qa_frames.py` | Post-render stills — `--from-timeline` samples motion ends + collisions |
| `scripts/render_and_mux.sh` | Default `-qm` (30fps); avoid `-ql` |
| `scripts/layout_watch.py` | `watch_layout(scene, demo_dir)` — records live text collisions |
| `scripts/check_sync.py` | Silent / thin cues from the rendered timeline |
| `scripts/check_layout.py` | Verdict on the recorded collisions |
| `scripts/skill_paths.py` | Locate the skill / project from any install path |

## Inspiration (do not copy runtime)

[AmitSubhash/3brown1blue](https://github.com/AmitSubhash/3brown1blue) (`pip install 3brown1blue`, MIT) — pedagogy, Designing Math, teaching TTS rewrites. This skill replaces its Kokoro/atempo sync with the word-timestamp pipeline; no runtime dependency on it.
