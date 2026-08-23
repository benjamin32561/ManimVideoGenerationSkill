# Brief for writing one Introduction to Language script.yaml

You are writing **one** `script.yaml` for one video of a thirteen-video series.
Read these first, in this order:

1. `docs/IL_SERIES_SPINE.md` — the ladder. Find your row. Your video **must**
   open on its "opens on" question and **must** close on its "closes on"
   question. Read the per-video note for your number.
2. `skills/manim-explain/references/craft-laws.md` — non-negotiable.
3. `skills/manim-explain/assets/script_template.yaml` — the shape.
4. `StudyMaterial/HUJI/A/6112_Introduction_to_Language/Introduction to Language.tex`
   — source of truth. Do not transcribe it. Take claim, reason, and price.
   Hebrew is the exam track; you write English `say:`.
5. `docs/IL_SERIES_SPINE.md` § Visual vocabulary — describe `show:` in terms of
   `position`, `price`, `relation`, `wave`, `min_pair`, `bracket`, `wug`,
   `level_stack`.

## Audience

An electrical engineer in a cognitive-science master's. He knows signals,
filters, finite tables, and estimators. He has **no** linguistics background.
Explain every piece of linguistic vocabulary from nothing. Never explain what
a spectrum or a finite-state machine *is* — do explain phoneme, allophone,
morpheme, constituent, implicature.

## This series is structural — that is a constraint, not a license

The content is distinctions. The picture is still the argument. Prefer:

- two cards and a labelled relation that morphs (describes / scolds;
  system / utterance; phone / phoneme; inflection / derivation);
- a continuous wave that gets cut at a boundary;
- a tree that is not a string;
- a novel item that takes a rule nobody reinforced;
- a price chip that stays when the view dies.

Wallpaper quotations of Chomsky or Saussure are a defect.

## Non-negotiables

- **18–22 beats.** Length follows teaching. Do not compress an exam distinction
  to stay near the length of the last video.
- **Exam relations on screen.** Draw both candidates and refuse one.
- **Never use a layer that has not been built yet** (spine rule 2).
- **`say` is spoken English.** No LaTeX, no IPA glyphs in the voice. US
  spelling. No contractions in any word you cue. Speak "voice onset time" or
  "V O T" spelled out; never cue a numeral. Hebrew terms belong in `show:`
  labels if at all.
- **Questions get `pause_after` 0.9–1.3.** Naming a position: 0.55–0.75.
  Heavy morph: 0.7–1.0.

## Bookmarks

- 2–3 per beat, each the **first occurrence of that word in the entire
  narration**. Scan every earlier beat before choosing.
- Spoken order within the beat.
- **Never cue a numeral.**
- **Never cue a word Whisper mangles**, or a linguist's name with a common
  homophone. Prefer "descriptive", "phoneme", "wug" is dangerous (Whisper
  hears "wag"); cue "novel" or "plural" instead. Do not cue `Chomsky`,
  `Saussure`, `Grice`, `Austin`, `Genie`, `gavagai` if Whisper will eat them.
- US spelling always.

## `show:` — visual coverage

Every motion or state word spoken in `say` (cut, stack, slide, fill, infinite,
finite, equal, break, gather) must also appear in that beat's `show:` (or a
lint-accepted synonym). `lint_script.py --strict` until 0 warnings.

## Spoken numerals are a contract

Any number the narration says must be a named constant in the scene module.
Video 01 speaks **thirteen** weeks — that count is `N_VIDEOS` in `lang.py`.
The script header lists which numerals it spoke.

## Inherit and hand off

The first spoken sentence restates last week's close. The last spoken sentence
is next week's open. The next video number may be spoken as "the next video",
not as a digit.
