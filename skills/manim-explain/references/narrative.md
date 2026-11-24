# Narrative: how a script is built

Read before writing `script.yaml`. The evidence is `docs/research/narrative-pattern.md`
(10 hand-labelled videos by 3Blue1Brown, Welch Labs and Veritasium) and
`docs/research/intuitive-derivation.md` (how FloatHeadPhysics derives steps intuitively and
how all three channels ration numbers and math).

## The pattern

```text
Video    := Hook Q0 Unit+ Payoff
Unit     := question? Work Turn Cash-out Link
Work     := setup | dig | attempt | (a child unit)      at least one, before the turn
Turn     := wall -> revelation      the wall blocks progress; the revelation removes it
          | attempt -> revelation   "you might expect X, but..." (the intuition is refuted)
          | answer                  a plain build
Cash-out := consolidate+            name it, package/play with the rule, test a new case, scale it up
Link     := causal | return | jump  how the next question follows
```

- **One central question (Q0)** is asked early and held open. Units chain beneath it.
- **The chain is causal.** 81% of revelations in the reference videos raise the next
  question, often because the fix has a cost that becomes the next wall.
- **One climax**: the revelation or answer that resolves Q0. It sits in the second half
  (typically two thirds to four fifths in; `style.yaml` sets `climax_range`).
- **The payoff returns to the opening**, with a principle, open questions or a tease, as the
  style allows.

In the reference videos, setup, digging and attempts take 35–46% of runtime; that is the
work before a turn. Cash-out takes 16–26%. Walls are short pivots: a median of 16 s and about
8% of runtime. A script that is mostly "aha" beats is a list of facts, not an explanation.

## Before the beats: the viewer contract

```yaml
viewer_contract:
  starting_point: what the viewer already understands, in ordinary words
  central_question: the one question the video resolves
  bedrock_premise: the simplest undeniable fact(s) the whole argument builds from (recommended)
  initial_intuition: the reasonable idea worth testing
  anchor_example: one concrete situation that carries the whole video
  reasoning_spine: the 3–5 step thinking chain the viewer can reconstruct afterward (recommended)
  ending_insight: what the viewer can explain afterwards
```

Course material sets the content. The contract sets what the viewer starts from and the
thinking process they leave with. A cold viewer must be able to state the problem without the
material's jargon.

## Deriving steps intuitively (the thought-process craft)

The unit grammar (`question → work → turn → cash-out → link`) gives the video its shape. What
makes viewers feel they *rediscovered* the idea — instead of being lectured equations and
numbers — is how each step inside a unit is derived (`docs/research/intuitive-derivation.md`,
distilled from FloatHeadPhysics in single-narrator voice):

1. **Reject formula-as-explanation and label-as-explanation.** When a common textbook answer
   just points to an equation ("the denominator goes to zero") or a law's name ("because of
   principle X"), call out explicitly why that is not yet an explanation and ask what is
   actually happening underneath.
2. **Derive from the smallest bedrock premise.** Anchor the chain in one simple, undeniable
   truth so later steps feel logically forced rather than handed down from outside.
3. **Simplify before generalizing.** When the full problem is tangled, say so aloud and solve
   an easier special case first (one wave, one ion, a periodic signal, two separated
   detectors), then lift one restriction at a time.
4. **Build a staged failure ladder, not a single strawman.** After the obvious guess fails,
   test the *plausible repair* a smart viewer would try next — let it seem to work, then
   expose the subtle hidden assumption where it breaks ("we only got lucky because our axes
   lined up").
5. **State the constraint in plain English *before* the move.** Before introducing a
   mathematical trick or architectural piece, specify exactly what job the missing move must
   do ("we need an operation that squares *only this term*, leaves the others untouched, and
   stays linear"). Then the move itself feels deduced rather than pulled from a hat.
6. **Voice active `"why / why not / what if"` stress-tests.** Push back on your own
   explanation with the sharp questions a skeptical thinker would ask ("Wait — that works for
   a toy clock, but what about a real physical clock?", "What if I just double the fuel?",
   "Why doesn't this break conservation?"). Each objection closes a real logical gap.
7. **Qualitative mechanism → packaged equation → play with cases (or honest hand-waving).**
   Build the physical or geometric logic first; compress it into symbols only once the viewer
   sees *why* every term and operation must be there. Immediately test the equation on 2–3
   revealing cases (low/boundary, midpoint, extreme, or doubling an input) so the math sharpens
   the intuition. If an exact derivation is outside the video's scope, say plainly what is
   qualitative instead of presenting an asserted formula as a derivation.
8. **Ration spoken numbers and new jargon.** Across all 24 measured reference videos
   (FloatHeadPhysics, 3Blue1Brown and Welch Labs), spoken numeric mentions average 11–18 per
   1,000 words and never exceed ~33/1k. Keep derivations on effortless numbers (clean squares,
   clean doublings) so arithmetic never steals working memory from the logic; keep secondary
   benchmarks, ablation tables and constants in `SOURCE_NOTES.md`. Keep the new-vocabulary
   list short.

## Beat fields

| Field | When | Meaning |
|---|---|---|
| `id` | always | unique |
| `narrative_role` | always | `hook`, `question`, `setup`, `dig`, `attempt`, `wall`, `revelation`, `answer`, `consolidate`, `bridge`, `aside`, `payoff` |
| `unit` | always | `u0` is the macro arc (hook, Q0, bridges, payoff); `u1`, `u2`... are units |
| `parent` | first beat of a unit | the unit it nests in (`u0` for top-level units) |
| `role_sub` | walls, consolidations | wall: `fail`, `contra`, `cost`, `mystery`, `gap`; consolidate: `name`, `formal`, `gen`, `test`, `scale`, `recap` |
| `obstruction` | walls | what blocks progress, in 15 words or fewer |
| `against` | walls | the earlier attempt or revelation the wall blocks |
| `resolves` | revelations, answers | the wall or attempt (revelation) or question (answer) it resolves |
| `link` | revelations, answers | `causal`, `return` or `jump` (a jump needs a roadmap `bridge` first, and Welch never jumps) |
| `climax` | exactly one beat | the turn that resolves Q0 |
| `say` | always | the spoken words |
| `show` | always | what the picture does, in words |

## Writing the beats

1. Write the contract, then the macro question and the climax that resolves it. Set a turn
   budget for the target length: the style's turns per 10 minutes × minutes. Videos are
   6–12 minutes with at least 2–3 full units (decision 25).
2. Plan units top-down as a chain. For each unit, state:
   - its question;
   - the work on the anchor;
   - the turn (which attempt or wall, and why it fails);
   - the cash-out;
   - the link that makes the next question unavoidable.

   Prefer links where the fix's own cost or limit is the next wall. Nest a child unit when a
   step needs its own fix.
3. Write `say` last.
   - **Work (`setup` / `dig` / `attempt`)** walks through the thought experiment on the anchor:
     easier case first, plausible repair tested, constraint stated in plain words before a
     trick or formula lands. Use one sharp contrast rather than chaining intermediate
     arithmetic in prose.
   - **Walls** carry a turn word (but, however, problem, can't) and often a sharp `"why"` or
     `"what if"` question.
   - **Revelations** answer and deduce the move from the stated constraint; they do not ask.
   - **Attempts** voice the viewer's intuition in the narrator's voice ("you might expect...",
     or "we might expect..." in documentary styles like Welch). No narrated dialogue with
     characters.
   - **Consolidations** keep the voice conceptual — never read a multi-term equation out loud
     term by term in prose or re-verify the same arithmetic twice. Let the screen show the
     symbols morphing while the voice says what each piece *does*, then frame 2–3 test cases
     as live `"what if?"` checks ("What if the next block is smaller? Does rescaling break?").
     Do not add a separate `role_sub: formal` beat if the revelation already packaged the
     formula; spend the cash-out playing with extremes or testing a new case.
4. Plan the picture per role:
   - in work, visualize the thought experiment (easier case, side-by-side cases, hypothesis test);
   - at a wall, show the failure or mark the broken prediction;
   - at a revelation, keep the anchor and add, box or recolour one thing;
   - in consolidation, animate the test case or extreme value on the anchor;
   - at the climax, call back the hook's image.

## What the lint checks

`scripts/lint_script.py demos/<series>/<slug>`. Errors block `voice.py`; warnings are for you
to judge. Numbers come from the series' `style.yaml` (`narrative`, `speaker`, and `rules`).

| Rule | Check | Level |
|---|---|---|
| N1 | Q0 exists in u0, is a question, and arrives within `intro_max_s` | error |
| N2 | a hook comes before Q0 (when the style requires one) | warning |
| N3 | every unit has a turn, with setup/dig/attempt before it | error |
| N4 | each wall is resolved by a later revelation, after a gap within `tension_s` (unless a child unit carries it) | error / warning |
| N5 | a wall has an `obstruction`, an earlier `against` beat, and a turn word or question | error / warning |
| N6 | a revelation resolves an earlier wall or attempt; an answer resolves a question | error |
| N7 | every turn is cashed out before the next wall; the cash-out share is at least `cashout_min` | warning |
| N8 | turns per 10 minutes within the style's range; revelations under 20% of beats and time | warning / error |
| N9 | the work share is at least `work_min` | warning |
| N10 | the causal-link share is at least `causal_min`; jumps only where the style allows | warning / error |
| N11 | exactly one climax, a turn, inside `climax_range`, followed by a cash-out and the payoff | error / warning |
| N12 | the last beat is a payoff that shares a key word with the hook or Q0 (or asks open questions where allowed) | error / warning |
| N13 | unit depth at most `max_depth` | warning |
| N14 | revelations do not ask; evaluative words (beautiful, clever...) only in revelations and the payoff | warning |
| N15 | no narrated dialogue | error |
| narration | no LaTeX in `say`; exact numbers only where the style allows; no number phrases that sound like another number ("seventy too") | error / warning |
| numbers | `number_density` (total spoken numbers per 1k words over the style ceiling), `spec_overload` (exact decimals / % / 3+-digit specs per 1k words over the ceiling), `number_dump` (single beat cramming too many numbers) | warning |
| voiced | once voiced: numbers the voice said that the script never wrote (`misheard_number`) | warning |
| speaker | sentence length, questions, pronouns and contractions against the style; once voiced, also words per minute and long pauses | warning |
