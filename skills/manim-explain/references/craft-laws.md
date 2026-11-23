# Craft laws (every style)

Laws that hold whatever the style. Style-specific ones (pace, palette, fonts, emphasis moves,
whether exact numbers belong in the narration) live in `styles/<name>/style.yaml` and
`STYLE.md` (decision 21).

**Feedback becomes a law.** When the user corrects a video, write the lesson down as an
abstract rule before patching the video:

- here, if it holds for every style;
- in the style pack, if it holds for that style only.

**Abstraction test:** a law that names a specific video's object as the rule, not as an
example, is not abstract yet.

## Process

1. **Research first, then run end to end.** A video request means:
   1. research and brief (`SOURCE_NOTES.md`, plus alignment questions when the input leaves
      style, scope or viewer background open);
   2. script and lint;
   3. voice;
   4. plan and plan check;
   5. render and render check;
   6. frame review;
   7. delivery.

   Align up front on bare topics so the direction is right before drafting; once aligned, run
   steps 2–7 in one pass, self-reviewing against these laws. Stop only for a blocked tool (a
   missing key, a provider refusal), or when the user asked for the optional checkpoint.
2. **Fix in the cheapest place.**
   - Wording or pacing: `say`, then lint and voice again.
   - Layout or timing: the plan, then plan check.
   - Never patch a render by hand.

## Narrative

1. **Orient before teaching.** Show an understandable situation, establish what someone wants,
   let the obstacle appear, then ask the central question. Never open on a definition, a
   benchmark, an acronym or a conclusion.
2. **The viewer contract comes first.** State what the viewer already knows, the central
   question, the intuition worth testing, the anchor example and the ending insight. Domain
   expertise does not imply knowing this material's notation or history.
3. **Each video stands alone.** A series may build up, but a new viewer still gets a
   one-sentence orientation.
4. **Keep one concrete anchor alive.** Return to it whenever a new term, equation or limit
   appears: anchor → idea → anchor. A second example only tests whether the idea generalizes.
5. **A causal chain, not a topic list.** Each beat answers the current question or creates
   the next one, and is joined by "because", "but" or "therefore". If two neighbouring beats
   could be swapped, it is a list.
6. **Let the viewer attempt it.** Show the tempting intuition, give it room to seem right,
   then show what it cannot explain. Never announce the answer before the viewer has met the
   gap it fills.
7. **Meaning before names.** Show what something does before naming it. Define a term at
   first use and keep its colour and picture. Project-internal labels stay in source notes.
8. **Motivate → manipulate → name.** Do the operation on the anchor first, then compress it
   into notation and give it its standard name.
9. **No unmotivated posits.** Before a move the viewer could not predict, say what was known,
   what failed, and what constrained the move.
10. **Every spoken number is true on screen.** Compute readouts with the same values that
    draw the figure. If the voice says "five more", five more appear.
11. **Resolve by returning to the opening.** Apply the new model to the original anchor and
    leave one transferable insight. Never end on a list to memorize.

## Picture

1. **The picture matches the spoken noun.** When the voice names a whole system, show the
   whole system. When it narrows to a part, focus that part.
2. **Every spoken change has a visible one, on its phrase.** If the voice says something
   grows, splits or cancels, it does so on screen across the phrase that says it (decision
   18).
3. **Stillness is allowed; idle motion is not.** Hold the frame while the voice explains it.
   Nothing pulses or breathes to look busy.
4. **Morph, don't respawn.** Related A → B changes in place (`change`, `morph`, `copy_to`).
   Fade out and in only for unrelated objects.
5. **Text enters from somewhere.** It writes on, flies out of the object it names, or slides
   from its source. It never just pops in.
6. **Math develops on screen.** A derived formula builds term by term as the voice explains
   each piece; terms come out of the figure. A finished formula never appears in one go.
7. **A question points at its referent.** While the voice asks about X, X is visibly the
   subject (coloured, highlighted, or everything else dimmed).
8. **Causal pairs move together.** When the voice says A changes B, both move in the same
   event.
9. **Procedures are staged.** Each verb of a multi-step process (choose, rank, cut, build) is
   its own visible step.
10. **Dimming is not deletion.** A suppressed object stays legible (0.2–0.5 opacity) next to
    the full-strength one it is compared with.
11. **Check parametric figures at their extremes.** When a figure's geometry comes from a
    quantity, compute it at every value the video animates to, and make sure what the beat
    needs still exists inside the frame.

## Layout

1. **Plan the frame before anything moves** (decision 20). Every object has a pixel place in
   `plan/layout.json`.
2. **Every text has a home and a budget.**
   - It sits next to what it names (3b1b) or in its style's fixed slot (Welch).
   - It stays within the style's word budget.
   - It is never shrunk to fit: break the line or cut words instead.
3. **Lone signs are drawn, not typed.** A `+`, `−` or `×` set in a font reads as a hairline;
   draw it as a `symbol`.
4. **Flights and crowds are planned.**
   - Copies that would cross labels get an arc or a delay.
   - Groups passing through a gap get an order and a stagger.
5. **One colour per concept,** everywhere it appears.
6. **A label leaves with its idea.** Fade or dim it when its section ends; never let it
   describe something no longer on screen.
