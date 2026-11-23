---
name: manim-explain
description: >-
  Creates narrated educational explainer videos in a chosen style (3Blue1Brown or Welch Labs)
  from course material or a topic. Use when the user asks for an explainer video, a
  3b1b-style or Welch-Labs-style animation, a narrated lesson, or teaching a concept visually
  with voiceover. Writes a script as a chain of question → wall → revelation units under one
  central question, voices it through OpenRouter, plans every frame in pixels, binds each
  change to the phrase that describes it, renders beats in parallel with manimgx, and gates
  delivery on mechanical checks plus a frame review.
license: MIT
metadata:
  author: Ben Akhovan
  version: "0.2.0"
  repository: https://github.com/benjamin32561/ManimVideoGenerationSkill
---

# Explainer videos in a chosen style

## Hard rules

1. **Research and plan before code.** Research the topic into `SOURCE_NOTES.md` (and align
   with the user when style, scope or background are open), then write the script (narrative
   grammar), then voice, then a pixel layout plan and phrase-bound events, then render. The
   runtime builds exactly the plan; never place things freehand in code.
2. **The series' style governs.** `demos/<series>/series.yaml` names the style; every video
   in the series uses it. Read `styles/<style>/STYLE.md` before writing.
3. **One central question, a chain of units, one climax, a payoff that returns to the
   opening** (`references/narrative.md`). Videos are 6–12 minutes with at least 2–3 full
   units. Merge short neighbouring topics rather than make thin videos.
4. **Every visual change runs across the phrase that describes it.** Between events the frame
   holds still; there is no idle motion.
5. **No narrated dialogue, no LaTeX in narration.** The narrator voices the viewer's intuition
   ("you might expect..."). Write math as spoken words (`references/spoken-math.md`).
6. **Gates are not optional.** Each step refuses to run until the previous check passed for
   the current files: lint → voice → plan check → render, render check → review → deliver.
7. **Look at the frames.** Mechanical checks cannot judge meaning. Read every contact sheet
   and judge each frame: is anything covered or left over, and does the picture say what the
   voice says?
8. **Feedback becomes a law** in `references/craft-laws.md` (every style) or in the style pack
   (one style), written as an abstract rule, before the video is patched.

## Setup

```bash
source "$MANIM_EXPLAIN_ROOT/scripts/env.sh"    # or <skill>/scripts/env.sh
```

It loads the project's `.env`, which needs:

- `OPENROUTER_API_KEY`: voice and word timings;
- `MANIM_ENV`: a Python 3.13 environment with `manimgx`, `requests`, `pyyaml` and `pillow`.

It also puts that environment first on PATH.

Fonts are checked at render time, and rendering fails without them:

- CMU Serif in `~/.local/share/fonts/cmu` (both styles);
- Source Sans 3 in `~/.local/share/fonts/source-sans-3` (Welch).

## Workflow

```
demos/<series>/series.yaml            title + style        (assets/series_template.yaml)
demos/<series>/<slug>/script.yaml     the narrated script  (assets/script_template.yaml)
```

1. **Research & brief (`references/research.md`).**
   - With course material: read it thoroughly, group neighbouring topics into 6–12 minute
     videos, extract exact notation, values and misconceptions into
     `demos/<series>/<slug>/SOURCE_NOTES.md`, and research only genuine gaps.
   - With a bare topic: read primary sources first until you understand the mechanism, exact
     numbers and real failure modes, write `SOURCE_NOTES.md`, and ask brief alignment
     questions for anything open (style/series, scope/arc, assumed viewer background).
   - Pick the series style in `demos/<series>/series.yaml`.
2. **Script.** Write the viewer contract, then the unit chain (`references/narrative.md`),
   then `say` and `show` for every beat.
   `python scripts/lint_script.py demos/<series>/<slug>`: fix every error, and judge the
   warnings.
3. **Voice.** `python scripts/voice.py demos/<series>/<slug>` writes the narration and
   `audio/words.json`. Re-run the lint: it now measures real pace and pauses.
4. **Plan.** Turn each beat's `show` into `plan/layout.json` and `plan/events.yaml`
   (`references/plan.md`). Anchors are phrases from `audio/words.json`.
   `python scripts/plan_check.py demos/<series>/<slug>`: fix errors in the plan and re-run
   until clean.
5. **Render.** `python scripts/render.py demos/<series>/<slug>` renders beats in parallel on
   the CPU and writes `out/video.mp4`. It never touches a GPU unless you name one
   (`--gpus 3`), and only when the user allows it.
6. **Check.** `python scripts/check_render.py demos/<series>/<slug>` checks sync to the
   voice, and writes review frames and contact sheets to `out/review/`.
7. **Review.** Read every sheet, and the full frames for anything unclear
   (`references/review.md`). Fix problems in the plan and loop back to step 4. Fix rounds are
   cheap: steps 4–6 redo only the windows and beats your fix changed, and the check names
   the sheets with new frames, so read those. When a pass is clean:
   `python scripts/review.py record demos/<series>/<slug> --notes "..."`
8. **Deliver.** `python scripts/review.py deliver demos/<series>/<slug>` copies the video to
   `output_videos/<series>/<slug>.mp4`.

Optional checkpoint (decision 13, off by default): if the user asks, stop after the first
render check and show them the script and the first contact sheet.

## Files per video

```
demos/<series>/<slug>/
  script.yaml            narrative beats (say, show, roles)
  SOURCE_NOTES.md        sources, exact values, provenance
  audio/                 narration.wav, narration.mp3, words.json, voice.json
  plan/                  layout.json, events.yaml, events.json (resolved by plan_check)
  custom.py              optional components for this video (`custom:<name>`)
  out/                   lint.json, plan_check.json, probe/, inspect.*, beats/, video.mp4,
                         render.json, render_check.json, review/, review.json
output_videos/<series>/<slug>.mp4   the delivered video
```

## Styles

| Style | Voice | Look | Narrative |
|---|---|---|---|
| `3b1b` | conversational, 170–205 wpm | black, ManimGL colours, CMU Serif, labels next to objects | 2.5–4 turns per 10 min, toy numbers, ends on a principle or puzzle |
| `welch` | measured documentary "we", 150–185 wpm | black, tan/brown/yellow, Source Sans 3 caps labels in fixed slots | 1.2–2.5 turns per 10 min, real numbers, no jumps, ends on open questions |

## References

| Doc | Read when |
|---|---|
| `references/research.md` | first: researching a topic or course material, writing `SOURCE_NOTES.md`, aligning with the user |
| `references/narrative.md` | writing or fixing a script |
| `references/plan.md` | writing the layout plan and events |
| `references/voice.md` | voicing; writing anchors |
| `references/review.md` | rendering, checking, reviewing, delivering |
| `references/craft-laws.md` | always: laws for every style |
| `references/spoken-math.md` | any math in the narration |
| `styles/<style>/STYLE.md` | before writing anything for a series in that style |

## Scripts

| Script | Does |
|---|---|
| `scripts/lint_script.py` | narrative grammar N1–N15, narration rules, speaker profile → `out/lint.json` |
| `scripts/voice.py` | TTS (style voice) + Whisper word times, dropped-speech check → `audio/` |
| `scripts/plan_check.py` | resolve anchors, validate the plan, geometry at every frame, `manimgx inspect` → `out/plan_check.json` |
| `scripts/render.py` | parallel per-beat render on the CPU (changed beats only), frame-exact join, narration mux → `out/video.mp4` |
| `scripts/check_render.py` | frame count, sync to the voice, review frames and sheets → `out/render_check.json` |
| `scripts/review.py` | `record` the frame review; `deliver` the reviewed video |
