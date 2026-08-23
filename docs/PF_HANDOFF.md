# Philosophical Foundations — session handoff

**Owner: the main session, working directly. No subagents.**
Read this file first when a conversation is summarized. Then update
`docs/PF_PROGRESS.md` and `docs/PF_TODO.md` at every state change.

Today's date when grouping landed: 2026-08-22.

## What this series is

Thirteen English Manim videos, one per week of HUJI 6110. Source of truth:
`/raid/ben/0Projects/StudyMaterial/HUJI/A/6110_Philosophical_Foundations/Philosophical Foundations.tex`

Spine: `docs/PF_SERIES_SPINE.md`
Script brief: `docs/PF_SCRIPT_BRIEF.md`
Scene brief: `docs/PF_SCENE_BRIEF.md`
Progress: `docs/PF_PROGRESS.md`
Todo: `docs/PF_TODO.md`

Thesis: each theory of mind fails; the next pays a different price. Then the
question flips to how psychology, computation, and brain join without swallowing
each other.

## Delivery layout (do this before any PF `-qm`)

Finished MP4s live in series folders, **not** the root of `output_videos/`:

```
output_videos/computer-engineering/   ce-01 … ce-15  (done)
output_videos/thermal/                thermal-*
output_videos/philosophical-foundations/   pf-*  (this series)
output_videos/other/                  unmatched prefixes
```

Path helper: `python3 skills/manim-explain/scripts/skill_paths.py demos/<slug>`
`render_and_mux.sh` and `scripts/deliver_video.sh` already use it.

## Resume protocol

1. Open `docs/PF_PROGRESS.md`. The first row that is not **delivered** is the
   work. If a row is **encoding**, check `/tmp/<slug>_deliver/<slug>.status`
   and the matching `.qm.log` before starting a second `-qm`.
2. Open `docs/PF_TODO.md` and tick what is actually true on disk.
3. Stay in `/raid/ben/0Projects/StudyMaterial/ManimVideoGenerationSkill`.
   `source skills/manim-explain/scripts/env.sh` first. Use conda env
   `/raid/conda_envs/ben_envs/manim_env` (Python 3.11) for Manim.
4. Produce videos **01 then 02 … 13**. One lane per slug.
5. After every state change, write it into PF_PROGRESS and PF_TODO **before**
   starting the next expensive step. That is how the next session continues.

## Pipeline (same as CE — do not skip)

Per video:

1. Write `demos/<slug>/script.yaml` (18–22 beats) from the spine row + per-video
   note + `.tex` + `PF_SCRIPT_BRIEF.md`.
2. `python skills/manim-explain/scripts/lint_script.py demos/<slug>/script.yaml --strict`
   until 0 warnings. Bookmarks = first occurrence in the **whole** narration.
   No contractions. US spelling (`behavior`). Never cue numerals.
3. TTS: `python skills/manim-explain/scripts/tts_openrouter.py demos/<slug>/script.yaml`
4. Align: `python skills/manim-explain/scripts/align_words.py demos/<slug>`
   (pass the demo directory, not `script.yaml`.)
5. **Freeze** `script.yaml`, `timing.json`, `audio/`. Never edit them to suit
   the scene.
6. Scene: copy a CE demo's `utils/style.py` etc.; video 01 **creates**
   `utils/mind.py`; later videos copy it. `tn.attach` then `watch_layout`.
   `LayoutBoard`. Bands y: title 3.05–3.95, key 2.25–2.95, panel 1.70–2.10,
   bottom −3.55…−2.75. `assert_clear` pad **0.25**.
7. Static: `check_names.py`, `find_leftovers.py`
8. `geometry_pass.py` (not `--dry_run`, never `-n 0,1`)
   or `./scripts/finish_video.sh <slug> <file.py> <Class> /tmp/<slug>_finish`
9. `check_sync` / `check_layout --min-duration 1.0`
10. Read contact sheet + full frames; `review_gate.py --record pass --frames N`
11. `./scripts/deliver_video.sh <slug> <file.py> <Class> /tmp/<slug>_deliver`

One `-qm` at a time per slug. Unique `--media_dir` is already in
`render_and_mux.sh`. Do not start 13 concurrent encodes.

## Slugs

| # | slug | class (suggested) | week |
|---|------|-------------------|------|
| 1 | pf-01-mind-body | MindBody | א |
| 2 | pf-02-dualism | Dualism | ב |
| 3 | pf-03-logical-behaviorism | LogicalBehaviorism | ג |
| 4 | pf-04-psychological-behaviorism | PsychologicalBehaviorism | ד |
| 5 | pf-05-identity-theory | IdentityTheory | ה |
| 6 | pf-06-cognitivism | Cognitivism | ו |
| 7 | pf-07-turing-test | TuringTest | ז |
| 8 | pf-08-functionalism | Functionalism | ח |
| 9 | pf-09-chinese-room | ChineseRoom | ט |
| 10 | pf-10-mental-architecture | MentalArchitecture | י |
| 11 | pf-11-integration | Integration | יא |
| 12 | pf-12-marr-levels | MarrLevels | יב |
| 13 | pf-13-mechanism | Mechanism | יג |

## Hard rules (from the spine — do not rediscover)

- Inherit-and-hand-off: open on previous close, close on next open.
- Never use a later position early. Debts are named chips, not sneak previews.
- Exam distinctions are pictures (semantic vs metaphysical, type vs token,
  Turing-as-indicator vs behaviorism-as-identity, syntax vs semantics).
- The picture is the argument. Wallpaper quotes are a defect.
- Name the price. EE audience. `utils/mind.py` shared.
- Roles: mind gold, body teal, behavior grey, compute blue, fault red, debt yellow.

## `utils/mind.py` primitives (build in video 01)

`position`, `price`, `relation`, `room`, `level_stack`, `module_sandwich`,
`dim_group`. Copy into every later demo. Pain in video 5 must look like pain
in video 8.

## What not to do

- Do not commit unless asked.
- Do not kill other people's processes.
- Do not TTS video n+1 while n is still outline-only.
- Do not write scene code until that video's script lints clean.
- Do not start `-qm` until the review gate is recorded.
- Do not flatten `output_videos/` again.
