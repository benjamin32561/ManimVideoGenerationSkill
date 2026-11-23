# Research and brief: understanding the topic before scripting

Read before writing `script.yaml`. Do not design a storyline or invent examples from vague
memory. Every video begins by understanding the subject deeply enough to identify its real
mechanism, its genuine obstacles, and its verified numbers, recorded in
`demos/<series>/<slug>/SOURCE_NOTES.md`.

## Two input modes

### 1. Course material provided (notes, slides, PDFs, papers, code)

- Read the material thoroughly first. Extract the syllabus scope, exact notation, constants,
  derivations, and stated misconceptions into `SOURCE_NOTES.md`.
- Group neighbouring topics into 6–12 minute videos holding 2–3 full units (decision 25).
- Research outside the provided material only for genuine gaps (historical motivation, a
  missing constant, verifying a real-world scale-up). Mark every outside fact explicitly in
  `SOURCE_NOTES.md`.
- Ask the user only what the material leaves open (for example, which style a new series
  should use, or how to group topics). Do not re-ask questions the material already settles.

### 2. Bare topic (no material provided)

- **Read primary sources first:** foundational papers, textbooks, official specs, or
  reference implementations. For fast-moving fields, verify the current state up to today.
- **Understand the mechanism before the script.** You are ready to align with the user only
  when you can explain, from verified sources:
  1. what concrete problem forced the idea into existence;
  2. which naive intuition fails, and *why* it fails mechanically or mathematically;
  3. how the real mechanism fixes it, down to the exact components, equations, and numbers;
  4. what cost, limit, or second failure mode the fix introduces (the causal link to the next
     unit);
  5. real measurements or scale-up numbers that show the payoff.
- **Ask brief alignment questions once you know the landscape.** Research first so the
  questions offer sharp, accurate options rather than generic guesses. Ask only what changes
  the video:
  - **Style and series** (`3b1b` vs `welch`), if no `series.yaml` exists yet;
  - **Scope / narrative arc**, when the topic spans multiple eras, papers, or subfields that
    cannot all fit in 2–3 deep units;
  - **Assumed viewer background** (sets `viewer_contract.starting_point`);
  - **Specific focus or exclusions**, if the user has a particular angle or paper in mind.

Once aligned, run the rest of the pipeline end to end without extra stops (unless the user
asked for the optional storyboard checkpoint).

## What `SOURCE_NOTES.md` must hold

Keep `demos/<series>/<slug>/SOURCE_NOTES.md` concise, factual, and auditable:

1. **Sources:** exact titles, authors, years, and URLs or local file paths. Distinguish
   provided course material from researched references.
2. **Core mechanism and model choices:** exact equations, architectures, dimensions, and
   published numbers. Explicitly label any simplified or illustrative numbers chosen for the
   running example versus measured numbers from sources.
3. **Derived numbers:** every computed quantity spoken or drawn, checked with a short script
   when arithmetic is non-trivial.
4. **Genuine walls and misconceptions:** the real obstacles that drive the units (never
   strawmen invented to pad the script).
5. **Facts by beat:** updated alongside `script.yaml` so every spoken claim and figure traces
   back to a source.

## Ready-to-script check

Before writing `script.yaml`, confirm:

- Every claim, formula, and benchmark you plan to use is verified against a primary source or
  derived from explicitly stated toy values.
- You have one concrete anchor example that can carry the whole video from hook to payoff.
- The 2–3 units form a causal chain of real obstacles, not a survey list of papers or topics.
- Any open alignment questions with the user are answered.
