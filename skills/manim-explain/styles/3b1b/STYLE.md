# 3Blue1Brown style

A conversational teacher builds one idea from a concrete example until the viewer feels they
invented it. Numbers in `style.yaml` are measured; the evidence is
`docs/research/styles/3blue1brown.md` and `docs/research/narrative-pattern.md`.

## Flow

- **Cold open, then the central question.** Open on something concrete: a digit, a dice roll,
  a surprising fact. The central question lands by 90 s at the latest. Never open with
  "let's start" or a definition.
- **2.5–4 turns per 10 minutes.** Mostly wall → revelation, some "you might expect X, but…",
  a quarter plain builds. Walls take 6–40 s to resolve; a sub-unit can carry a longer one.
- **Work before every turn.** Operate on the running example before naming anything. Name
  second: "this number is called the prior". Names are scarce.
- **Cash out every revelation.** Name it, write the formula from the picture, test it on a
  new case. Then the next question follows from what just happened.
- **The viewer's objection, voiced by the narrator.** "You might be wondering…". No
  characters talking.
- **End by returning to the opening** with a portable principle, an open puzzle, or a tease
  of the next video. Never a recap list.

## Voice

- One conversational register throughout: no switch to a lecture voice for formulas.
- 170–205 wpm with few long pauses (0.3–2 per minute). Long, flowing sentences (18–32 words
  on average) and contractions.
- Mostly "you", some "we" and "I".
- Questions are rare (under 1 per minute) and sit at turning points.
- Toy numbers are fine; exact results and run ids stay in `SOURCE_NOTES`.

## Look

- Black background, ManimGL colours: `yellow` `#FFFF00` for the thing in question, `blue`
  and `teal` for primary objects, `red` for the second variable or "wrong", `green` for
  "right", `pink` and `gold` for third quantities, greys for axes and dimmed items.
- **One colour per concept, everywhere.** The same quantity keeps the same colour in the
  narration's on-screen labels, in every formula (set part colours) and in the figure.
- Text is CMU Serif, matching LaTeX. Labels are 2 words on median, 3 at most. Lines break by
  hand at about 30 characters; text never shrinks to fit.
- Labels sit next to what they name. Give a label `backstroke: true` only when it must sit
  over a busy figure.
- One primary figure, large: centred, or right of centre with text to its left. A title
  appears per section or not at all; never one title for the whole video.

## Motion

- Text writes on in 1–2 s. Equations build term by term: write a part as the voice names it,
  and `copy_to` terms out of the figure into the formula.
- Algebra steps `morph` the formula in place in 0.6–0.8 s; matching parts move, unlike parts
  cross-fade.
- **Stillness is fine.** Holds of 15–30 s while the voice explains are normal. No idle motion.
- Emphasis: `recolor` the term, `flash` behind it, or `dim` the rest. No pulsing or wiggling.
- The picture follows the voice: each change starts on its phrase, within 0.25 s.

## Components (`components.py`)

- `number_line`: horizontal axis with ticks and math tick labels.
- `axes`: plain x/y axes with arrow tips.
- `curve`: a smooth curve through points (sample the function in the plan).

## Avoid

- Captioning the narration on screen.
- Text in bands at the top or bottom.
- A parked key sentence.
- Boxes around every concept.
- Breathing or pulsing objects.
- Several texts entering at once.
