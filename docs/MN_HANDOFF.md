# From Molecule to Neuron — session handoff

**Owner: the main session, working directly. No subagents.**
Read this file first when a conversation is summarized. Then update
`docs/MN_PROGRESS.md` and `docs/MN_TODO.md` at every state change.

Today's date when the series started: 2026-08-22.

## What this series is

Thirteen English Manim videos, one per week of HUJI 6164. Source of truth:
`/raid/ben/0Projects/StudyMaterial/HUJI/A/6164_From_Molecule_to_Neuron/From Molecule to Neuron.tex`

Spine: `docs/MN_SERIES_SPINE.md`
Script brief: `docs/MN_SCRIPT_BRIEF.md`
Scene brief: `docs/MN_SCENE_BRIEF.md`
Progress: `docs/MN_PROGRESS.md`
Todo: `docs/MN_TODO.md`

Thesis: not two glued subjects. One causal chain. Stable information in a
molecule must become a machine that works now, and that machine — a protein
in a membrane — is what turns a cell into an electrical computer.

**This course is independent of 6110, 6112, and every other HUJI track.**
Video 01 must **not** open with “you already know / you already own …” from
another course or from an EE résumé. It opens on *this* course’s problem:
chemistry in water, mixing, a fat barrier. Inherit-and-hand-off applies
inside this 13-video ladder only.

## Delivery layout

Finished MP4s live in series folders:

```
output_videos/computer-engineering/        ce-*
output_videos/philosophical-foundations/   pf-*
output_videos/introduction-to-language/    il-*
output_videos/molecule-to-neuron/          mn-*   (this series)
output_videos/thermal/                     thermal-*
output_videos/other/                       unmatched prefixes
```

Path helper: `python3 skills/manim-explain/scripts/skill_paths.py demos/<slug>`

## Resume protocol

1. Open `docs/MN_PROGRESS.md`. The first row that is not **delivered** is the
   work. If a row is **encoding**, check `/tmp/<slug>_deliver/` before starting
   a second `-qm`.
2. Open `docs/MN_TODO.md` and tick what is actually true on disk.
3. Stay in `/raid/ben/0Projects/StudyMaterial/ManimVideoGenerationSkill`.
   `source skills/manim-explain/scripts/env.sh` first. Use conda env
   `/raid/conda_envs/ben_envs/manim_env` (Python 3.11) for Manim.
4. Produce videos **01 then 02 … 13**. One lane per slug.
5. After every state change, write it into MN_PROGRESS and MN_TODO **before**
   starting the next expensive step.

## Pipeline (same as PF/IL — do not skip)

Per video:

1. Write `demos/<slug>/script.yaml` (18–22 beats) from the spine + `.tex` +
   `MN_SCRIPT_BRIEF.md`.
2. `lint_script.py demos/<slug>/script.yaml --strict` until 0 warnings.
   Bookmarks = first occurrence in the **whole** narration. No contractions.
   US spelling. Never cue numerals.
3. TTS: `tts_openrouter.py demos/<slug>/script.yaml` (Grok Voice `leo`)
4. Align: `align_words.py demos/<slug>` (demo dir, not `script.yaml`)
5. **Freeze** `script.yaml`, `timing.json`, `audio/`.
6. Scene: video 01 **creates** `utils/cell.py`; later videos copy it with
   `style.py`. `tn.attach` then `watch_layout`. `LayoutBoard(pad=0.25)`.
   Bands y: title 3.05–3.95, key 2.25–2.95, panel 1.70–2.10,
   bottom −3.55…−2.75.
7. `check_names.py`, `find_leftovers.py` (`_kill(` counts as a disposer)
8. `geometry_pass.py` (never `--dry_run`, never `-n 0,1`)
9. `check_sync` / `check_layout --min-duration 1.0`
10. Read contact sheet + full frames; `review_gate.py --record pass --frames N`
11. `./scripts/deliver_video.sh <slug> <file.py> <Class> /tmp/<slug>_deliver`

One `-qm` at a time per slug. Do not TTS n+1 while n is still outline-only.
If a cue dies in Whisper: change the bookmark to a word in both `say:` and
the transcript, then `--remap`. Do not edit `say:` / audio after TTS.

## Slugs

| # | slug | class | week |
|---|------|-------|------|
| 1 | mn-01-membrane | Membrane | א |
| 2 | mn-02-dna | Dna | ב |
| 3 | mn-03-transcription | Transcription | ג |
| 4 | mn-04-protein | Protein | ד |
| 5 | mn-05-regulation | Regulation | ה |
| 6 | mn-06-neuron | Neuron | ו |
| 7 | mn-07-nernst | Nernst | ז |
| 8 | mn-08-channels | Channels | ח |
| 9 | mn-09-action-potential | ActionPotential | ט |
| 10 | mn-10-conduction | Conduction | י |
| 11 | mn-11-synapse | Synapse | יא |
| 12 | mn-12-inhibition | Inhibition | יב |
| 13 | mn-13-plasticity | Plasticity | יג |

## `utils/cell.py` primitives (build in video 01)

`position`, `price`, `relation`, `bilayer`, `organelle`, `ion`, `channel`,
`pump`, `helix`, `spike`, `synapse_cleft`, `voltage_trace`, `chain_stack`,
`nernst_line`, `rc_membrane`, `dim_group`, `ring_around`. Copy into every
later demo.

Roles: information gold, membrane/ions teal, leak/mixing grey, devices blue,
fault red, debt yellow. Same `ROLE` keys as PF (`mind`, `body`, `behavior`,
`compute`, `fault`, `debt`) so the EE is not taught a second palette.

## What not to do

- Do not open video 01 with “you already know / you already own”.
- Do not commit unless asked.
- Do not kill other people's processes.
- Do not TTS video n+1 while n is still outline-only.
- Do not write scene code until that video's script lints clean.
- Do not start `-qm` until the review gate is recorded.
- Do not flatten `output_videos/` again.
- Do not start a second `-qm` of a slug that is already encoding.
- Do not transcribe `raw/`. Take claim, reason, and price from the `.tex`.
