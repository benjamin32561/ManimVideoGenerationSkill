# Spoken math

On screen: LaTeX (`math` objects in the layout). In `say`: natural spoken English. The lint
rejects LaTeX characters in `say`.

When unsure how to speak a symbol, look it up (MathSpeak, ClearSpeak, or Wikipedia's
"mathematical pronunciation") and keep the choice consistent across the series.

## Patterns

| Written | Spoken |
|---|---|
| a/b, \frac{a}{b} | "a over b", or say what it means: "the ratio of outside to inside" |
| a_b | "a sub b", or its name: "the class mean for unit j" |
| a^b | "a to the b"; a² "a squared" |
| \sum | "the sum of" |
| \prod | "the product of" |
| \approx | "about" or "approximately" |
| \gg | "much greater than" |
| \in | "in" |
| \lVert x \rVert | "the norm of x" |
| \ln | "the log of" (natural log unless the base matters) |
| −89 mV | "minus eighty-nine millivolts" |
| 10% | "ten percent" |

## Deriving and speaking equations intuitively

Equations are **packaged sentences**, not explanations on their own (`docs/research/intuitive-derivation.md`).
Follow a four-step cycle whenever a real equation belongs in the video:

1. **Qualitative mechanism first.** Establish what depends on what — and *why* — on the
   diagram in plain English before writing a single symbol.
2. **Motivate every operation.** Never drop a named formula from authority ("the equation
   named after X tells you…"). Show why each operation (a ratio, a difference, a square, a
   log, a product, a sum) is forced by the geometry or logic — or say plainly what part is
   qualitative and outside the video's scope.
3. **Voice carries the concept; the screen carries the algebra.** Never dictate multi-term
   equations or step-by-step arithmetic in prose ("the new sum is the old sum times e to the
   gap, plus the block's sum times its own gap…", or "half of one plus a quarter of two plus
   two times three eighths…"). Say what the step *does* conceptually ("shrink the old total
   to the new max, fold in the new block, and divide once at the end") while the screen morphs
   the clean symbols term by term, and immediately translate the boxed equation back into one
   plain sentence.
4. **Play with the equation as live `"what if?"` checks.** Test 2–3 revealing cases so the
   symbols sharpen intuition: a boundary where the term disappears ("What if the speed is
   small? The factor stays near one, which is why Newton works"), doubling one input and
   tracing *why* the output scales as it does, or an extreme where it blows up.

## Habits

- **Say what a formula means, not its symbols.** "The thermal energy per unit charge, times
  the log of the concentration ratio" beats reading RT over zF.
- **Speak each new piece as it appears.** The voice names a term while that part writes on.
- **Pick effortless numbers during derivations.** Choose clean values (like 36% → square root
  0.6, or a factor of 2) so arithmetic never pulls working memory away from the logic.
- **Keep numbers speakable, rounded, and rationed.** Even where the style allows exact
  numbers (Welch), reserve them for the 2–3 moments that prove a wall or land a payoff —
  never read a table of decimals aloud. Whisper writes spoken numbers as digits, so anchor
  events on a word next to the number.
