# Brief for writing one From Molecule to Neuron script.yaml

You are writing **one** `script.yaml` for one video of a thirteen-video series.
Read these first, in this order:

1. `docs/MN_SERIES_SPINE.md` — the ladder. Find your row. Your video **must**
   open on its "opens on" question and **must** close on its "closes on"
   question. Read the per-video note for your number.
2. `skills/manim-explain/references/craft-laws.md` — non-negotiable.
   Especially: independent series open on their own question.
3. `skills/manim-explain/assets/script_template.yaml` — the shape.
4. `StudyMaterial/HUJI/A/6164_From_Molecule_to_Neuron/From Molecule to Neuron.tex`
   — source of truth. Do not transcribe it. Take claim, reason, and price.
   Hebrew is the exam track; you write English `say:`.
5. `docs/MN_SERIES_SPINE.md` § Visual vocabulary — describe `show:` in terms of
   `position`, `price`, `relation`, `bilayer`, `organelle`, `ion`, `channel`,
   `pump`, `helix`, `spike`, `synapse_cleft`, `voltage_trace`, `chain_stack`.

## Audience

An electrical engineer in a cognitive-science master's. He has **no** cell
biology or neuroscience background for *this* course. Explain every piece of
this vocabulary from nothing. Do **not** open as if he just finished 6110 or
6112. Do **not** say “you already know”, “you already own”, “as an engineer
you have filters.” RC / capacitor / table may appear *inside* a later beat
when they are this week’s mechanism (week 8: the membrane *is* RC). Then
explain them from the membrane, not from last semester.

## Video 01 is this course’s first sentence

Video 01 opens on chemistry in water and the problem of mixing. It never
opens on the viewer’s résumé. Videos 2–13 open on last week’s close.

## This series is mechanistic — that is a constraint, not a license

The content is *why the mechanism must look like this*. The picture is still
the argument. Prefer:

- two cards and a labelled relation that morphs (archive / working copy;
  Nernst / Goldman; channel / pump; analog / digital);
- a bilayer that blocks charge;
- a voltage trace that escapes toward sodium and comes back;
- a coincidence detector that needs two keys;
- a price chip that stays when the view dies.

Wallpaper quotations of Cajal or Hodgkin are a defect.

## Non-negotiables

- **18–22 beats.** Length follows teaching. Do not compress an exam distinction
  to stay near the length of the last video.
- **Exam relations on screen.** Draw both candidates and refuse one.
- **Never use a layer that has not been built yet** (spine rule 3).
- **`say` is spoken English.** No LaTeX in the voice. US spelling. No
  contractions in any word you cue. Never cue a numeral. Hebrew terms belong
  in `show:` labels if at all.
- **Questions get `pause_after` 0.9–1.3.** Naming a position: 0.55–0.75.
  Heavy morph: 0.7–1.0.

## Bookmarks

- 2–3 per beat, each the **first occurrence of that word in the entire
  narration**. Scan every earlier beat before choosing.
- Spoken order within the beat.
- **Never cue a numeral.**
- **Never cue a word Whisper mangles**, or a biologist’s name with a common
  homophone. Do not cue `Nernst`, `Goldman`, `Hodgkin`, `Huxley`, `SNARE`,
  `NMDA` (until 13, and only if STT keeps it), `Cajal`, `Golgi`, `Hebb`,
  `phospholipid`, `cytoskeleton`. Prefer `bilayer`, `equilibrium`, `clamp`,
  `threshold`, `myelin`, `shunting`, `coincidence`.
- US spelling always.

## `show:` — visual coverage

Every motion or state word spoken in `say` (mix, block, fold, leak, clamp,
sum, fuse, shunt) must also appear in that beat's `show:` (or a
lint-accepted synonym). `lint_script.py --strict` until 0 warnings.

## Spoken numerals are a contract

Any number the narration says must be a named constant in the scene module.
Video 01 speaks **thirteen** weeks — that count is `N_VIDEOS` in `cell.py`.
The script header lists which numerals it spoke.

## Inherit and hand off

Video 01: first spoken sentence is *this* course’s situation, not last
course’s close. Videos 2–13: first spoken sentence restates last week’s
close. The last spoken sentence is next week’s open. The next video number
may be spoken as "the next video", not as a digit.
