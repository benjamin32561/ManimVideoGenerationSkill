# Research and brief: understanding the topic before scripting

Read before writing `script.yaml`. Do not design a storyline or invent examples from vague
memory. Every video begins by understanding the subject deeply enough to **rediscover its
logic from scratch**, identify its genuine obstacles, and separate the few numbers that do
logical work from the reference-only ledger recorded in `demos/<series>/<slug>/SOURCE_NOTES.md`.

**Know 10× more than you say.** `SOURCE_NOTES.md` is a fact-check and derivation ledger, NOT
a checklist of equations, hyperparameters and benchmark rows to read aloud. Evidence:
`docs/research/intuitive-derivation.md`.

## Two input modes

### 1. Course material provided (notes, slides, PDFs, papers, code)

- Read the material thoroughly first. Extract the **thinking-process outcome** (what chain of
  reasoning the learner should be able to reconstruct), the simplest bedrock premise, the
  derivation steps, genuine misconceptions, and verified notation/constants into
  `SOURCE_NOTES.md`.
- Group neighbouring topics into 6–12 minute videos holding 2–3 full units (decision 25).
- Research outside the provided material only for genuine gaps (a missing physical/logical
  "why", historical motivation, a missing constant, verifying a real-world scale-up). Mark
  every outside fact explicitly in `SOURCE_NOTES.md`.
- Ask the user only what the material leaves open (for example, which style a new series
  should use, or how to group topics). Do not re-ask questions the material already settles.

### 2. Bare topic (no material provided)

- **Read primary sources first:** foundational papers, textbooks, official specs, or
  reference implementations. For fast-moving fields, verify the current state up to today.
- **Interrogate the logic before the script (Feynman-gap test).** You are ready to align with
  the user only when you can explain in plain words, from verified sources:
  1. what concrete problem forced the idea into existence — and why reciting the textbook
     formula or label does not explain it;
  2. the **single bedrock premise** (or smallest set of starting truths) from which the core
     mechanism can be derived step by step;
  3. which naive intuition fails, what **plausible repair** a smart learner would try next,
     and *why* both break mechanically or logically;
  4. how the real mechanism is forced by those constraints — including any easier special case
     that makes the derivation click, and what **exact equations or numbers** actually earn a
     place in the narration;
  5. what `"why / why not / what if"` objections test the explanation, and what cost or limit
     of the fix creates the causal link to the next unit;
  6. which 2–3 verified scale-up or test numbers prove the payoff (leaving the rest of the
     paper's tables as reference-only).
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

Keep `demos/<series>/<slug>/SOURCE_NOTES.md` concise, factual, logic-first and auditable:

1. **Sources:** exact titles, authors, years, and URLs or local file paths. Distinguish
   provided course material from researched references.
2. **Outcome & thinking-process spine (backward design, before storyline):**
   - *Thinking-process summary:* 3–5 bullet steps of the reasoning chain the viewer should be
     able to reconstruct from scratch without memorizing formulas.
   - *Bedrock premise:* the simplest undeniable fact(s) the derivation starts from.
   - *Prerequisites:* what the viewer already needs (and any 1-sentence recap to include).
   - *Minimal jargon budget:* the small set of new terms truly needed to reason forward;
     anything else stays in plain English.
3. **Intuitive derivation steps & honesty boundaries:**
   - Walk through each key leap: the easier special case (if any), the plain-English logical
     constraint before each mathematical or architectural move, how each equation packages the
     logic, and 2–3 revealing values/extremes to play with afterward.
   - Explicitly flag any mathematical step that will be kept **qualitative** (hand-wave
     honesty) rather than formally derived.
4. **Genuine walls, plausible repairs & `"why / why not / what if"` objections:** the real
   obstacles that drive the units plus the sharp follow-up questions a skeptic would ask
   (never strawmen invented to pad the script).
5. **Numbers & equations — spoken vs reference-only:**
   - *Spoken (few, purposeful):* the effortless toy values used during derivations and the
     2–3 verified numbers that expose a contradiction or land the payoff — every derived value
     checked with a short script when arithmetic is non-trivial.
   - *Reference-only (stays in `SOURCE_NOTES.md`, not narrated):* secondary ablation rows,
     hyperparameters, exact constants, and model-dimension lookup tables that back up accuracy
     without crowding the voiceover.
6. **Facts by beat:** updated alongside `script.yaml` so every spoken claim and figure traces
   back to a source.

## Ready-to-script check

Before writing `script.yaml`, confirm:

- Every step of the core mechanism can be explained in plain words without hiding behind a
  formula name, buzzword or authority claim.
- Every equation you plan to put on screen has a step-by-step intuitive derivation of *why*
  each term and operation is there — or an explicit honesty note stating what is qualitative.
- Every spoken number does concrete logical work (contradiction, pattern, effortless toy step,
  or payoff), while secondary specs and tables remain reference-only.
- You have one concrete anchor example and a small bedrock premise that carry the whole video
  from hook to payoff.
- The 2–3 units form a causal chain of real obstacles and `"why / why not"` tests, not a
  survey list of papers, specs or topics.
- Any open alignment questions with the user are answered.
