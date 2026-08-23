# Brief for writing one Philosophical Foundations script.yaml

You are writing **one** `script.yaml` for one video of a thirteen-video series.
Read these first, in this order:

1. `docs/PF_SERIES_SPINE.md` — the ladder. Find your row. Your video **must**
   open on its "opens on" question and **must** close on its "closes on"
   question. Read the per-video note for your number.
2. `skills/manim-explain/references/craft-laws.md` — non-negotiable. Especially:
   every spoken change has a visible one; no unmotivated posits; depth sets
   length; picture matches the spoken noun.
3. `skills/manim-explain/assets/script_template.yaml` — the shape.
4. `StudyMaterial/HUJI/A/6110_Philosophical_Foundations/Philosophical Foundations.tex`
   — source of truth for the argument. Do not transcribe it. Take claim,
   reason, and price. The Hebrew is the exam track; you write English `say:`.
5. `docs/PF_SERIES_SPINE.md` § Visual vocabulary — describe `show:` in terms of
   `position`, `price`, `relation`, `room`, `level_stack`, `module_sandwich`.

## Audience

An electrical engineer in a cognitive-science master's. He knows causes, closed
physical systems, and machines. He has **no** philosophy background. Explain
every piece of philosophical vocabulary from nothing. Never explain what a
cause, a voltage, or a Turing machine's *physics* is — do explain *res
cogitans*, qualia, disposition, type, token, module.

## This series is textual — that is a constraint, not a license

The content is arguments. The picture is still the argument. A beat that only
puts a sentence on a black frame is a defect. Prefer:

- two cards and a labelled relation that morphs (identity / cause /
  supervenes / plays-the-role);
- a price chip that stays when the view dies;
- a room, a table, a sandwich, a three-pane stack.

Wallpaper quotations of Descartes or Searle are a defect. If the VO names a
noun, that noun is an object on stage.

## Non-negotiables

- **18–22 beats.** Length follows teaching. Dualism's three pressures are three
  beats, not a list in one breath. Do not compress an exam distinction to stay
  near the length of the last video.
- **Exam relations on screen.** If the notes force a choice of relation, draw
  both candidates and refuse one. Semantic vs metaphysical, type vs token,
  analytic vs synthetic, Turing-as-indicator vs behaviorism-as-identity —
  these are pictures, not asides.
- **Never use a layer that has not been built yet** (spine rule 2). Forward
  glances are named debts.
- **`say` is spoken English.** No LaTeX, no symbols. US spelling (`behavior`,
  `defense`). No contractions in any word you cue. Speak "C fibers" not
  "C-fibers" if the hyphen will split a cue. Hebrew terms belong in `show:`
  labels if at all, not in `say:`.
- **`latex` field** only for formula beats (almost none here). Marr's "thirty
  seven" vs binary is a morph of representations, not a BUILD_UP of an
  equation, unless you actually write one.
- **Questions get `pause_after` 0.9–1.3.** Naming a position: 0.55–0.75. Heavy
  morph (a relation breaking): 0.7–1.0.

## Bookmarks — the part that breaks if you are careless

Bookmarks are cue words matched forward-only against a Whisper transcript.

- 2–3 per beat, and each must be the **first occurrence of that word in the
  entire narration**. Scan every earlier beat before choosing.
- They must appear **in spoken order within the beat**.
- **Never cue a numeral.** Cue a distinctive lexical word beside it.
- **Never cue a word Whisper mangles**, or a philosopher's name that has a
  common English homophone. Prefer "category", "disposition", "imitation",
  "isomorphic" over "Ryle", "wug", "Gall". If you must cue a name, use the
  full distinctive form once ("functionalism") and never again as a cue.
- **US spelling always.**
- Avoid cueing words that are also common function words (`mind` is dangerous
  late in the series; cue it only in video 1 if at all).

## `show:` — the visual coverage contract

`lint_script.py` is a word-stem matcher. Every motion or state word spoken in
`say` (break, occupy, translate, seal, stack, …) must also appear in that
beat's `show:`, and every `show:` needs at least one animation keyword
(`STAGED`, `MORPH`, `BUILD_UP`, `POP`, or a verb like slide/pulse/sweep).

Write `show:` as **staged motion**, not a static end-state. Say what moves, in
what order, and on which spoken word. When a view fails, `MORPH` it into the
price chip — do not `FadeOut` the argument and `FadeIn` a moral.

## Deliverable

Write `demos/<slug>/script.yaml`. Then run, from the repo root:

```
source skills/manim-explain/scripts/env.sh
python "$MANIM_EXPLAIN_ROOT/scripts/lint_script.py" demos/<slug>/script.yaml
```

**Iterate until it reports 0 warnings.** Also verify by hand that every bookmark
is a genuine first occurrence.

Report back: the slug, the beat count, the final lint result, and the one
sentence thesis. Do not write scene code — that is a separate pass.
