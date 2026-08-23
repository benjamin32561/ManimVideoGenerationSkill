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
- [ ] 9. **Static gate — costs a second, run it after every edit:**
       `python scripts/check_names.py demos/<slug>/scenes/<f>.py`
       → undefined names, and calls that do not match their callee's signature.
       `from manim import *` blinds ruff's F821, so a helper used but never
       imported lints clean and only raises mid-render. On one series this found
       **20 latent crashes** across three scenes — 18 `note()` calls missing a
       required argument, plus two undefined names — each of which the render
       loop was otherwise discovering one per cycle.
       Also: `python scripts/find_leftovers.py demos/<slug>/scenes/<f>.py`
       → figures built in `construct` that never reach a disposal. Over-eager by
       design (closing recaps are meant to survive); it is a checklist to hold
       beside the contact sheet, not a verdict.

- [ ] 10. **Geometry pass — the whole scene, no movie:**
       `python "$MANIM_EXPLAIN_ROOT/scripts/geometry_pass.py" demos/<slug> scenes/<f>.py <Class>`
       Interpolates every play, samples AABBs ~10 Hz, writes occupancy /
       leftovers / overlap intervals, and Cairo-rasterizes only cue / play-end /
       overlap stills. **Do not use `--dry_run`:** it still Cairo-rasterizes
       every frame and only skips FFmpeg, so it costs about as much as `-ql`.
       **Never `-n 0,1`:** measured, it stops after animation 1 and *exits 0*.

- [ ] 10b. **Survey instead of grinding.** `assert_clear` raises on the *first*
       failure, so a scene with five bad placements costs five cycles. Add
       `MANIM_LAYOUT_COLLECT=1` and every failing site is recorded with its line
       number and printed at exit. Run it on the geometry pass. Fix the whole
       list, then walk again — a collecting render is a survey, never a pass.
       Clearance minimum is **0.17**; leave 0.25.

- [ ] 11. The geometry pass **is** the occupancy / timeline / stills gate.
       A full `-ql` movie is not required for QA. `-qm` is the delivery encode,
       once, behind `review_gate.py`.

- [ ] 12. **Motion audit:** `python scripts/check_sync.py demos/<slug>`
       → every silent cue is a beat the VO narrated and the picture ignored.
- [ ] 12b. **Layout audit:** `python scripts/check_layout.py demos/<slug>`
       → collisions that only exist mid-motion. Text-over-text always blocks;
       `box-cuts-text` is surfaced for the review to judge.
       Also read `out/occupancy.json` leftovers: figures present before 0.35×
       duration and still on stage after 0.90×.

- [ ] 12c. **THE REVIEW LOOP — repeat until the frames are right.** This is the
       centre of the process, not a final check. See references/review-loop.md.
         a. `qa_frames.py demos/<slug>` tiles `out/keyframes/` (already captured).
         b. **Read the contact sheet with your own eyes**, then the full frames
            for every beat you are not certain about. You have vision; use it.
            A thumbnail can only raise a doubt. Only a full frame settles it.
         c. Judge each frame twice: is anything obscured, clipped, invisible or
            left over — and does the picture actually say what the narration says
            at that moment?
         d. Any doubt → fix the scene → re-run the geometry pass → **look again**.
         e. Only when a whole pass is clean, record it:
            `review_gate.py demos/<slug> --record pass --frames N --notes '...'`
- [ ] 12d. `-qm` is **blocked** until that record exists and matches the current
       scene. `scripts/deliver_video.sh` enforces it; editing the scene after a
       pass reopens the gate, because the review described the old frames.
- [ ] 13. On craft feedback: update craft-laws (+ refs/templates) BEFORE or WITH the demo fix
- [ ] 14. Deliver (only past the gate in 12d): `output_videos/<series>/<slug>.mp4` + script, scenes, audio/, timing.json, one-line thesis
```

### The three audits (required after every render)

Reading a contact sheet of bookmark stills is not enough: it samples the moments
*you* chose, and both classic failures happen elsewhere — a described change that
never animates, and text that collides only while something is moving or at full
size. The render instruments itself, so all three are mechanical:

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/check_sync.py"   demos/<slug>   # silent cues
python "$MANIM_EXPLAIN_ROOT/scripts/check_layout.py" demos/<slug>   # live collisions
python "$MANIM_EXPLAIN_ROOT/scripts/qa_frames.py"    demos/<slug>    # tile captured stills
```

* **check_sync** — cue windows with no animation. A cue marks a visual event by
  definition, so a silent window is a beat where the narration moved and the
  picture did not. Also flags *thin* windows (a token pulse standing in for a
  described change) and long frozen stretches.
* **check_layout** — every text-vs-text overlap the renderer actually produced,
  with the interval it lasted. Requires `watch_layout(self, DEMO_DIR)` in the
  scene; it samples the live frame, so it sees collisions no snapshot can.
* **qa_frames** — tiles the stills the geometry pass already captured at
  motion ends, cues, and overlap openings. It does not seek an MP4.

The audits are the *cheap* gate, not the real one. They are mechanical, so they
cannot see the two things that matter most: whether anything is obscured, and
whether the frame means what the voice is saying over it. That is why step 12 is
a loop you stay in until the pictures are right, and why `-qm` is blocked behind
`review_gate.py`. Never ship on code review and green audits alone.

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
output_videos/<series>/<slug>.mp4  # the delivery — one finished MP4 per demo, grouped by series

demos/<slug>/                 # working tree: everything else
  script.yaml
  audio/narration.mp3
  timing.json
  scenes/*.py
  utils/style.py
  utils/layout_snapshots.py   # overlap tests
  out/timeline.json           # what moved, when (written by TimedNarration)
  out/layout_violations.json  # live text collisions (written by layout_watch)
  out/occupancy.json          # AABB samples + leftover checklist
  out/keyframes/              # sparse Cairo stills + contact sheet
  out/stills/                 # named-time QA PNGs (render_stills.py; snapshots if present)
  out/snapshots/              # compact mobject dumps; stills without re-construct
  out/wireframe.png           # labelled boxes, no Cairo
```

`render_and_mux.sh` writes the finished video to
`$MANIM_EXPLAIN_PROJECT/output_videos/<series>/<slug>.mp4` and nowhere else, so the
deliverables of a project sit together and are named after their demo. Nothing
else is copied there — stills, audio and timelines stay in the working tree.

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
| [build-loop.md](references/build-loop.md) | Always — the four gates, cheapest first, and how to read a stalled render |
| [narrative-patterns.md](references/narrative-patterns.md) | Arc + hooks |
| [layout-craft.md](references/layout-craft.md) | Bands, morph rule, LayoutBoard |
| [review-loop.md](references/review-loop.md) | **The look-at-the-frames loop + the -qm gate** |
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
| `scripts/geometry_pass.py` | Inner loop: interpolate `construct`, occupancy + sparse stills, no movie |
| `scripts/render_stills.py` | Cairo-rasterize named times / plays / violation midpoints into `out/stills/` |
| `scripts/qa_frames.py` | Tile captured stills — `--from-timeline` is not an MP4 seek |
| `scripts/render_and_mux.sh` | Default `-qm` (30fps) — only after the review gate |
| `scripts/review_gate.py` | Records the frame review; `--check` blocks `-qm` without one |
| `scripts/find_leftovers.py` | Static list of figures built in `construct` that never reach a disposal |
| `scripts/check_names.py` | Undefined names + bad call signatures, resolving through `import *` |
| `scripts/finish_video.sh` | Carries a video to review-ready, then **stops** |
| `scripts/deliver_video.sh` | `-qm` + deliver; refuses without a current review |
| `scripts/layout_watch.py` | `watch_layout(scene, demo_dir)` — records live text collisions |
| `scripts/check_sync.py` | Silent / thin cues from the rendered timeline |
| `scripts/check_layout.py` | Verdict on the recorded collisions |
| `scripts/cue_doctor.py` | Why a cue did not survive STT, with replacement candidates from the same beat |
| `scripts/cue_repair.py` | Re-cue unresolved bookmarks automatically and re-map for free |
| `scripts/skill_paths.py` | Locate the skill / project from any install path |

## Inspiration (do not copy runtime)

[AmitSubhash/3brown1blue](https://github.com/AmitSubhash/3brown1blue) (`pip install 3brown1blue`, MIT) — pedagogy, Designing Math, teaching TTS rewrites. This skill replaces its Kokoro/atempo sync with the word-timestamp pipeline; no runtime dependency on it.
