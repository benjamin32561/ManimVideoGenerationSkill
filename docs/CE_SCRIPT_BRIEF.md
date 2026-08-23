# Brief for writing one Computer Engineering script.yaml

You are writing **one** `script.yaml` for one video of a fifteen-video series.
Read these first, in this order:

1. `docs/CE_SERIES_SPINE.md` — the ladder. Find your row. Your video **must**
   open on its "opens on" question and **must** close on its "closes on"
   question. Read the per-video note for your number.
2. `skills/manim-explain/references/craft-laws.md` — non-negotiable.
3. `skills/manim-explain/assets/script_template.yaml` — the shape.
4. Your volume's `.tex` in `StudyMaterial/Computer Engineering/` — this is the
   source of truth for content. Do not transcribe it; take the argument.
5. `demos/_ce_shared/cpu.py` — the visual vocabulary your `show:` notes should
   describe in terms of (`bitfield`, `reg_file`, `mem_column`, `mem_grid`,
   `block`, `stage_strip`, `clock_trace`, `ring_around`).

## Audience

An electrical engineer. He knows MOSFETs, semiconductor physics, and how a
binary number decodes into a selection of gates. He has **no** software
background. Explain every piece of software vocabulary from nothing; never
explain a transistor, a voltage, or a capacitor. Where an electrical explanation
exists, prefer it.

## Non-negotiables

- **18–22 beats.** Length follows teaching. Do not pad, do not compress a
  derivation to stay short.
- **RV32I is the anchor.** Real encodings, real register names, real CSR names.
- **Never use a layer that has not been built yet** (see spine rule 2). If you
  must gesture forward, name it as a debt.
- **`say` is spoken text.** No LaTeX, no symbols, no digits-as-symbols. Write
  "x one" not "x1" if it must be spoken. No contractions in any word you cue.
- **`latex` field** carries the on-screen formula for formula beats; those beats
  need `BUILD_UP` or `MORPH` in `show:`.
- **Questions get `pause_after` 0.9–1.3.** Naming an object: 0.55–0.75. Heavy
  morph: 0.7–1.0.

## Bookmarks — the part that breaks if you are careless

Bookmarks are cue words matched forward-only against a Whisper transcript.

- 2–3 per beat, and each must be the **first occurrence of that word in the
  entire narration**. Scan every earlier beat before choosing. This is the most
  common failure.
- They must appear **in spoken order within the beat**.
- **Never cue a numeral** ("four", "sixteen"). Cue a distinctive lexical word
  beside it.
- **Never cue a word Whisper mangles.** Observed failures in this project:
  "guards"→"gods", "bench"→"bent". Avoid short, low-frequency, easily-confused
  words. Prefer distinctive multi-syllable words.
- **US spelling always** ("initialize", "behavior").
- Avoid cueing words that are also common function words.

## `show:` — the visual coverage contract

`lint_script.py` is a word-stem matcher. Every motion or state word spoken in
`say` (grow, slide, cancel, freeze, identical, flat, spread, drop, …) must also
appear in that beat's `show:`, and every `show:` needs at least one animation
keyword (`STAGED`, `MORPH`, `BUILD_UP`, `POP`, or a verb like slide/pulse/sweep).

Write `show:` as **staged motion**, not a static end-state. Say what moves, in
what order, and on which spoken word.

## Deliverable

Write `demos/<slug>/script.yaml`. Then run, from the repo root:

```
source skills/manim-explain/scripts/env.sh
python "$MANIM_EXPLAIN_ROOT/scripts/lint_script.py" demos/<slug>/script.yaml
```

**Iterate until it reports 0 warnings.** Also verify by hand that every bookmark
is a genuine first occurrence — the linter checks order within a beat but cannot
see that beat 12 reused a word from beat 3.

Report back: the slug, the beat count, the final lint result, and the one
sentence thesis. Do not write scene code — that is a separate pass.
