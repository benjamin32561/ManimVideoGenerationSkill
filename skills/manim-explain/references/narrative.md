# Narrative: how a script is built

Read before writing `script.yaml`. The evidence is `docs/research/narrative-pattern.md`:
10 hand-labelled videos by 3Blue1Brown, Welch Labs and Veritasium.

## The pattern

```text
Video    := Hook Q0 Unit+ Payoff
Unit     := question? Work Turn Cash-out Link
Work     := setup | dig | attempt | (a child unit)      at least one, before the turn
Turn     := wall -> revelation      the wall blocks progress; the revelation removes it
          | attempt -> revelation   "you might expect X, but..." (the intuition is refuted)
          | answer                  a plain build
Cash-out := consolidate+            name it, write the formula, test it, scale it up
Link     := causal | return | jump  how the next question follows
```

- **One central question (Q0)** is asked early and held open. Units chain beneath it.
- **The chain is causal.** 81% of revelations in the reference videos raise the next
  question, often because the fix has a cost that becomes the next wall.
- **One climax**: the revelation or answer that resolves Q0. It sits about two thirds in.
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
  initial_intuition: the reasonable idea worth testing
  anchor_example: one concrete situation that carries the whole video
  ending_insight: what the viewer can explain afterwards
```

Course material sets the content. The contract sets what the viewer starts from. A cold
viewer must be able to state the problem without the material's jargon.

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
   - **Walls** carry a turn word (but, however, problem, can't) and often a question.
   - **Revelations** answer; they do not ask.
   - **Attempts** voice the viewer's intuition in the narrator's voice ("you might
     expect..."). No narrated dialogue with characters.
4. Plan the picture per role:
   - at a wall, show the failure;
   - at a revelation, keep the anchor and add, box or recolour one thing;
   - at the climax, call back the hook's image.

## What the lint checks

`scripts/lint_script.py demos/<series>/<slug>`. Errors block `voice.py`; warnings are for you
to judge. Numbers come from the series' `style.yaml` (`narrative` and `speaker`).

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
| voiced | once voiced: numbers the voice said that the script never wrote (`misheard_number`) | warning |
| speaker | sentence length, questions, pronouns and contractions against the style; once voiced, also words per minute and long pauses | warning |
