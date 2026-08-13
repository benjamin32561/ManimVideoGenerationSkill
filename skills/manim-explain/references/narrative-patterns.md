# Narrative patterns (3b1b)

## Principles

1. Visual is the mystery — striking picture first; narration explains.
2. Specific before abstract — concrete example → pattern → rule.
3. One idea per beat — progressive reveal.
4. Story, not lecture — curiosity → productive confusion → partial clarity → aha → settle.
5. Misconception engine (when relevant) — show the wrong intuition, then correct it.

## Patterns

| Pattern | Skeleton |
|---------|----------|
| Mystery → Investigation → Resolution | Paradox → explore → principle → generalize |
| Build Up → Payoff | Simple blocks → combine → surprising result |
| Two Perspectives → Unity | View A → View B → same thing |
| Wrong → Less Wrong → Right | Naive → fails → refine → correct |
| Specific → General | Concrete case → pattern → abstract → apply |

Most good videos combine patterns (e.g. mystery hook + build-up).

## Conceptual lane

Advance one layer of the story at a time. Do not reopen a closed concept under a
wrong name (e.g. finish the class-mean *distribution*, then talk as if we are
back to raw activations). Name the *current* object: activations → means →
distribution → mass / shape → number.

Spoken state-words with on-screen avatars (spread, piled, gold, cutoff, scale…)
must trigger that avatar **on the word** — label + matching morph.

## Show-notes checklist (every beat)

Before coding Manim, `show:` should answer:

1. What structure does the spoken noun require on screen?
2. If there is a question about X, how does X move *during* the ask?
3. If there is a procedure, what are the staged steps (not the end state alone)?
4. What morphs from the previous beat (identity link)?

## Metric / definition explainers (research metrics)

Preferred blend:

1. **Hook:** lead-in question (situation + stake), matching system visual.
2. **Wrong path:** show the tempting shortcut failing.
3. **Concrete toy:** tiny readable instance (only as long as needed).
4. **Formula reveal** (LaTeX on screen; spoken form in VO) — **BUILD_UP / morph**
   each piece while speaking its meaning (not a one-shot final equation).
5. **Contrast siblings:** nearby-but-different quantities.
6. **Settle:** one-line takeaway.

## The provenance beat (before any posit)

Between "the old idea fails" and "here is the fix" there is a beat most
explanations skip: **where the fix came from**. Without it the resolution arrives
by authorial fiat and the viewer learns a result instead of an argument.

Answer, in order:

1. What was already known that survived (the constraint the fix had to respect).
2. What was tried, and how it failed.
3. What pinned this *particular* form — a limit it had to reproduce, a symmetry,
   a scaling law, a fit to data.
4. What was **still unjustified** when it was proposed.

Historical honesty belongs here. If the author guessed, say so and say what the
guess was fitted to: "he had no mechanism, only these two constraints and a
formula that worked" is a stronger teaching beat than a confident non-answer.

## Empty vs developed explanations

| Hollow | Developed |
|--------|-----------|
| “Call this CKA” + flash final formula | Walk numerator → denominator → name, morphing MathTex |
| “We use the Frobenius product” | “Matching cells: both say alike → contribute; multiply & sum → *that* is ⟨·,·⟩_F” |
| “We center” + static \(\tilde K\) | Show \(H\), then \(HKH\), then heatmap morph |
| Question → immediate next sentence | Question → **0.9–1.3s pause** → answer |

**Order:** plain-language measurement → arithmetic on screen → formal name/notation.
Never lead with the jargon name of an operator.

## Length

No fixed target. Write the beats needed to teach cleanly; TTS sets absolute time.
Bake pauses after questions and after heavy morphs so length includes thinking time.