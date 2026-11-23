# Motion typography and layout: why our frames look flat, and what polished explainers do

Started 2026-11-21. Question from Ben: the output looks "kinda ass": things are badly placed,
there is barely any text animation (the voice is handled elsewhere). This doc covers:

1. what the baseline frames get wrong (§1);
2. how top explainer channels animate text and equations, with timings (§2);
3. motion-design rules turned into numbers a style pack can hold (§3);
4. what each candidate engine offers for text motion, automatic layout and math (§4);
5. showcases to watch per engine (§5);
6. newer explainer-generation systems (§6);
7. sources (§7).

Claims are marked **[verified: source]**, **[measured]** (we measured it, method stated) or
**[inferred: from what]**. Scratch files (frames, downloads, scripts) live in
`research_cache/motion/` (gitignored).

Already decided (see [README](README.md)): per-phrase sync with still frames allowed (18), one
short scene per beat (19), a layout plan per beat (20), style packs with 3Blue1Brown and Welch
Labs first (1, 8, 21).

## Summary

- **The baseline fails on three separate axes** (§1): a motion vocabulary of 0.35 s fades only
  (no write-on, no morph, no stagger); no layout system (one title for 158 s, content in a thin
  central strip, objects parked at the edges, words in boxes); and content form (the Nernst video
  never shows the Nernst equation). Small labels also lose their spaces (`thision`).
- **Two fixes need no redesign** [verified: §4.1]: the spacing bug is fixed upstream in
  ManimPango 0.7.0, while our vendored CE and `manim_env` still run 0.6.1; and `style.py` sets no
  font, so text falls back to DejaVu Serif.
- **Reference text motion** (§2): 3b1b writes text on in 1–2 s (manimgl `Write`, linear, per-glyph
  stagger), brings terms in from the diagram (`TransformFromCopy`), and changes equations by
  morphing matched symbols (0.6–2 s), then holds. Welch writes caps labels letter by letter
  (~11 letters/s), fades prose in 0.6 s, re-parks labels in 1.4 s and lets a 3 s camera move do
  the layout. Kurzgesagt and Veritasium use 0.2–0.6 s entrances with overshoot. None captions the
  narration; all give text a source (stroke, leader line, travel, mask) instead of just fading it.
- **Rules a pack can hold** (§3): ease-out in, ease-in out, exits shorter; one text element entering
  at a time; groups staggered at `lag_ratio` ≈ 0.1; text ≥ 3.5% of frame height inside a 5% safe
  margin; unspoken text visible ≥ `max(1.5 s, 0.6 s/word)`; no idle loops. §3.8 has a 3b1b and a
  Welch column of values.
- **Engines** (§4): strongest typography motion is HyperFrames + GSAP (GSAP, SplitText and MorphSVG
  are now free); strongest automatic layout is the browser engines (CSS plus Remotion's
  `layout-utils` / HyperFrames' text linter); strongest math is manimgl (`tex["x"]` on any
  substring, longest-common-substring morphs). No engine leads on all three. manimgx is CE's API
  plus Typst math without TeX, a built-in layout checker and a vendor-measured 90× speed-up over
  CE.
- **Newer systems** (§6): nothing beats 3b1b or Welch on math; Claude Motion (available on Ben's
  account as an artifact type) has the best web typography but no math; explainroo is the only
  browser renderer seen with real math.

## 1. Baseline: what `mn-07-nernst.mp4` shows is wrong

Source: `output_videos/molecule-to-neuron/mn-07-nernst.mp4` (1280×720, 30 fps, 158.5 s).
19 frames pulled with ffmpeg (3–156 s) plus a 5 fps strip of 9.0–10.2 s, viewed by eye;
glyph heights and content extents measured with a pixel threshold on the PNGs; animation
counts from `demos/mn-07-nernst/out/timeline.json` and `scenes/nernst.py`
[measured: research_cache/motion/baseline/].

### Text animation: there is none

- **Every text element enters by `FadeIn` and leaves by `FadeOut`.** The 253 recorded plays
  contain 48 `FadeIn`, 38 `FadeOut`, 13 `Indicate`, 8 `Create`, 5 `Transform`, 1 `LaggedStart`,
  and **zero `Write`, zero `AddTextLetterByLetter`, zero `TransformMatching*`** [measured:
  timeline.json]. 422 of the logged sub-animations are `.animate` builders, most of them the
  1.1 s "breaths" diagnosed in the README.
- Entrances are short snaps: median play 0.47 s, 83 of 253 plays ≤ 0.4 s; a label `FadeIn` is
  typically 0.35 s (`self.play(FadeIn(ratio), run_time=0.35)`, `nernst.py:425`) [measured].
- No stagger inside a text block, no write-on, no label growing out of its object, no term-by-term
  equation build, no morph from one wording to the next. Words simply appear.

### No math in a video about an equation

- The beat cued on "equation" (70.4 s) and "ratio" (72.0 s) shows a rounded box containing the
  word `ratio`, alone on the left of an otherwise empty frame, for at least 6 s (frames at 72 s
  and 76 s are identical) [measured: frames]. `nernst.py` contains no `MathTex` / `Tex` at all
  [verified: grep]. The Nernst equation never appears in the Nernst video.
- The "potential levels" figure (95–130 s) is three horizontal ticks with no axis, no scale, no
  numbers and no units; the labels `sodium`, `chloride`, `potassium`, `rest` sit in boxes
  beside them [measured: frames 95, 110, 125, 130 s].

### Typography

- **Broken word spacing.** Small labels lose or squeeze spaces: `thision` (68 s, for "this ion"),
  `cellrest` (68 s), `energy isspent` (150 s), `cell dies` with uneven gaps (140 s), `ce ll` in
  the title [measured: frames]. Cause [verified: CE issue #2844, ManimPango#130,
  `vendor/manim/manim/mobject/text/text_mobject.py:85,836–838`]: Manim CE's `Text` is laid out in
  Pango at `font_size / 4.8` points (an 18 px label at 3.75 pt) and Pango rounds glyph positions to
  whole pixels. ManimPango 0.7.0 (2026-10-01) fixed it; our vendored fork and `manim_env` still run
  manimpango 0.6.1 (§4.1). The old workaround is to build text large and `scale()` it down.
- **Font is DejaVu Serif**, the system fallback, because `style.py` never sets a font
  (`fc-match serif` → DejaVu Serif; CMU Serif and Source Sans 3 are not installed)
  [verified: fc-match, fc-list, style.py].
- **Two sizes only.** Title glyphs are 34 px tall (4.7% of frame height, ascender to descender);
  every other label is 16–22 px (2.2–3.1%) [measured]. 3b1b's OCR text boxes have a median
  height of 3.1–6.9% and Welch's 3.6–4.2% (box includes padding, so not identical, but ours is
  at or below the bottom of both ranges). Labels are small for 720p and for phones.
- **Low-contrast "inactive" text**: grey `pulls` / `cell rest` inside a dark red outline at
  ~40% opacity (30 s, 68 s) reads as disabled UI, not as dimmed context [measured: frames].

### Layout

- **One title pinned for the whole video.** `One ion is not the cell` sits top-centre from 0 to
  158 s, through at least six different topics (fight of forces, leak, equilibrium, three
  ions, pump vs channel) [measured: every sampled frame]. 3b1b titles are per-section and
  often absent; Welch swaps the title at each section.
- **Everything is a word in a box.** `concentration`, `charge`, `anion`, `negative`, `ratio`,
  `steady`, `equilibrium`, `channel`, `pump`, `pulse waits`: concepts are rounded rectangles
  with a word inside, not labels attached to objects. Neither reference style boxes ordinary
  labels; 3b1b boxes only a result, Welch only the one boxed result per derivation (§6 of both
  style docs).
- **A thin strip in the middle, the rest empty.** Below the title, the bounding box of all
  content covers 3–28% of the frame (median of 5 frames: 8%); lit pixels are 0.4–1.5% of the
  frame [measured]. At 20 s the whole idea (two boxes and an arrow labelled `fight`) sits in a
  strip 84 px tall in a 720 px frame.
- **Objects parked at the frame edge with no relation to the figure.** K⁺ ions at x≈100 px and
  x≈1090 px while the membrane is centred (42–68 s); a `rest` box floats far left of the level
  plot (110–130 s); `anion` and `negative` boxes hang below empty space (55 s) [measured: frames].
- **Mixed alignment axes.** The yellow question `How do ion gradients become rest potential?`
  is left-aligned at x≈53 px while the title is centred (10 s); bottom captions are centred
  boxes at y≈640 px; side labels are at arbitrary x [measured: frames]. Nothing sits on a shared
  grid line.
- **Placeholder look.** Two empty dashed rectangles above `channel` and `pump` (156 s) read as
  unfilled slots [measured: frame].
- **Emphasis by recolouring the whole object**: the entire membrane turns yellow at 10 s, which
  reads as a different object rather than "look here" [measured: frame strip].

### What this adds up to

The frames fail on three separate axes, and fixing one won't fix the others:

1. **Motion vocabulary**: fades only, short, no stagger, no write-on, no morph (§2–§3 give the
   alternatives with timings).
2. **Layout**: no grid, no slots, no attachment, small content in a big empty frame, a title
   that never changes (§3.4 gives grid and safe-area numbers).
3. **Content form**: words in boxes where a figure, a labelled axis or an equation should be.
   That is a script/storyboard problem (the `show:` field), not a rendering one, but no amount
   of easing will hide it.

## 2. How top explainers animate text and equations

Method. Timings come from two kinds of evidence:

- **Code counts** over 3Blue1Brown's 2024–26 scene code (`3b1b/videos` at `31f8ffe`, 89 files,
  120,884 lines) and Reducible's 2022 code (`nipunramk/Reducible` at `88f4f8f`, 21 files,
  32,428 lines) [measured: regex counts, `research_cache/motion/`].
- **Frame stepping** of short downloaded clips at 10–30 fps with a frame-difference motion
  detector (`research_cache/motion/scripts/motion_segments.py`) and frame strips read by eye:
  3b1b *Bayes theorem* 6:30–7:45 and *Reinventing Entropy* (2026) 14:10–15:50, Welch Labs
  *Bitter Lesson* 12:05–12:45, Veritasium
  *Randomness is a lie* (2026) 4:38–4:52 and 12:56–13:26, Kurzgesagt *How Are Memories Stored*
  (2026) 0:52–1:22 and 2:44–3:04 [measured]. Durations from the detector undercount eased
  moves by about 0.1–0.2 s, because the slow ends fall under the threshold.

One sample clip per channel is thin. Treat the per-channel numbers as "what this looks like",
not as averages.

### 2.1 3Blue1Brown (manimgl)

**Vocabulary and frequency** (per 1,000 lines of 2024–26 scene code) [measured: code]:

| Move | per 1k lines | Default timing in manimgl | What it does on screen |
|---|---:|---|---|
| `FadeIn` / `FadeOut` | 18.0 / 16.2 | 1 s, `smooth` | the workhorse; 9% of `FadeIn`s add a drift (`shift=`), mostly `UP`/`DOWN` of 0.25–1 unit, 3% a `scale=` (often 2 or 1.5, i.e. shrinking in) |
| `Write` | 8.2 | 1 s if < 15 glyphs, else 2 s; `lag_ratio = min(4/(n+1), 0.2)`; **linear** rate | stroke outline per glyph, then fill; reserved for text and equations |
| `ShowCreation` | 6.3 | 1 s, `smooth` | curves, graphs, arrows |
| `TransformFromCopy` | 6.0 | 1 s | a term or label **flies from its object** into a formula or a new place |
| `LaggedStart` / `LaggedStartMap` | 4.8 / 4.2 | – | staggered groups; median `lag_ratio` across the code 0.1 (p25 0.1, p75 0.35) |
| `SurroundingRectangle` | 3.9 | – | box around a term |
| `GrowArrow` / `GrowFromCenter` | 2.2 / 1.5 | 1 s | arrows grow from the tail; braces/labels grow from their middle |
| `FadeTransform` | 1.9 | 1 s | cross-fade one shape into another |
| `set_backstroke` | 1.6 | width 3 | black outline behind glyphs |
| `TransformMatchingTex` / `…Strings` / `…Shapes` | 0.9 / 0.4 / 0.6 | **2 s**, lag 0 | equation morph: matching parts move, the rest fade |
| `FlashAround` / `VShowPassingFlash` / `FlashUnder` | 0.6 / 0.2 / 0.07 | 1 s, `time_width` 1 (2 for Under) | a light sweep around or under a term |
| `Indicate` | 0.2 | – | almost unused |

[verified: defaults in `manimlib/animation/creation.py:152–181` (`Write`),
`transform_matching_parts.py:29–30`, `animation.py:19,34` (1 s, `smooth`),
`indication.py:255–286`; counts measured]

- **Explicit timings.** When a run time is written out: `Write` median 2.0 s (p10 1, p90 3, n =
  157), `TransformMatchingTex` median 1.0 s (n = 24 of 111 calls; the other 87 use the 2 s
  default), `TransformFromCopy` 2.0 s, `FlashAround` 2.0 s, `FadeIn` 2.0 s (p10 0.8)
  [measured: code]. Nothing in his text vocabulary runs under about 0.8 s.
- **Waits.** 3,117 bare `self.wait()` (1 s) against 418 `wait(2)` and 222 `wait(3)`
  [measured: code]: animate, hold a beat, animate.
- **What `Write` looks like in practice.** For a 19-glyph label, the defaults give 2 s total,
  lag 0.2, so each glyph's stroke-then-fill takes about 0.43 s and a new glyph starts every
  0.087 s, about 11.5 glyphs per second. A 60-glyph equation also takes 2 s, at about 37 glyphs
  per second [inferred: from the formula]. The write time is nearly constant per object, not per
  character: **short labels write in 1 s, anything longer in 2 s.**

**Equation build, measured in *Bayes theorem* 6:30–7:45** [measured: clip]:

- The formula is assembled term by term from the diagram below it. Each term (`P(H)`,
  `P(E|H)`, …) **flies up from its label on the diagram** into its slot while a brace above
  stretches and a live count ticks down from 210 to 10, easing to a stop. One such step takes
  about 1.1 s (6:41.3–6:42.4).
- Placeholder factors that drop out (the person-count icons) are crossed in red, then fade while
  the remaining terms **slide together to close the gap**; the diagram dims to about 30% at the
  same moment. About 1.0 s (7:11.3–7:12.3).
- The finished formula gets a teal box and a title, `Bayes' theorem`, fading in above it. When
  the compact form `P(H)P(E|H)/P(E)` is derived, **box and title glide together** from the long
  form to the short one, about 1.0 s (7:23.0–7:24.0).
- 83% of the 75 s clip is still; motion bursts run 0.4–1.0 s with 2–9 s holds between them.

**Algebra steps, measured in the 2026 entropy video (*Reinventing Entropy*, 14:10–15:50)**
[measured: clip, 10 fps strip]:

- `p = 2^{-n}` → `log₂(p) = log₂(2^{-n})`: the new `log₂(` pieces **grow from their insertion
  points** on both sides while `p` and `2^{-n}` slide apart to make room. About 0.7 s
  (14:12.4–14:13.1).
- `log₂(2^{-n})` → `-n`: the exponent slides down into place while the rest fades out where it
  stands. About 0.6 s (14:13.5–14:14.1).
- `log₂(p) = -n` → `-log₂(p) = n`: the minus sign **travels on an arc over the equals sign** to
  the front. About 0.7 s (14:14.5–14:15.2).
- Steps are separated by 0.4–0.5 s, each tied to its spoken clause, and the result is then
  boxed. In 2026 a single algebra step is shorter than the 2 s default (0.6–0.8 s of visible
  motion), but still a morph of matched symbols, never a re-typeset.

**Rules this implies for a 3b1b pack:** text writes on (`Write`) or arrives from its source
(`TransformFromCopy`), equations change by morphing matched parts, emphasis is a box or a light
sweep, never a pulse; 1–2 s per text move; one move at a time; hold after each.

### 2.2 Welch Labs (manimgl + Illustrator overlays)

From the code counts in [welch-labs.md](styles/welch-labs.md) §7 and the *Bitter Lesson* clip
12:05–12:45 [measured: clip]:

- **Labels write on letter by letter** with manimgl's `Write`: the outline of each capital is
  drawn bright, then filled in the muted tan. In `LARGE LANGUAGE MODEL`, a new letter starts
  about every 0.09 s (about 11 letters per second) and each letter takes about 0.35–0.45 s from
  first stroke to fill (12:22.4–12:23.1). That matches manimgl's default `Write` for 19 glyphs
  (2 s, lag 0.2). The network diagram above it draws on the same way: strokes appear bright
  white and settle to dim tan as they fill.
- **Example sentences fade in whole**, with their arrow, in about 0.6 s
  (`Mr. and Mrs. Dursley, of number →`, 12:25.9–12:26.5). Caps labels write; serif prose fades.
- **Labels move out of the way.** When an image replaces the word `STATE`, the label slides down
  under where the image will be, then the image fades in; the move takes about 1.4 s
  (12:07.9–12:09.3). Same for `ACTION` 4 s later. The label is kept and re-parked, not deleted.
- **The camera does the layout.** A 3.0 s pull-back (12:20.4–12:23.4) shrinks the whole
  AlphaGo row to make room for a new LLM row underneath, which draws on while the camera is
  still moving. Text is never resized on its own; it scales with the camera.
- 85% of the 40 s clip is still. Code: `LaggedStart` 254, `lag_ratio` 538, `ReplacementTransform`
  1,282 against `FadeIn` 1,551 [verified: welch-labs.md].
- **Highlight sweeps on documents**: a yellow or orange highlighter on the key sentence of a
  paper or essay (F 5:00, B 15:00) [verified: welch-labs.md §6].

### 2.3 Veritasium (2026, After Effects team)

[measured: *Randomness is a lie*, 2026-11-18]

- Graphics live on a **green-felt backdrop** that matches the set. Text is a clean geometric
  sans in white, with colour-coded words (`new` red, `a`, `current`, `m` yellow).
- **The equation enters as a physical object**: the pill holding `new = a · current mod m`
  rises from below the frame tilted a few degrees, levels out and settles, in about 0.5 s
  (13:03.6–13:04.1), with a small overshoot. It then holds, bottom-centre, for 10+ s while a plot
  builds above it.
- Caps labels under objects (`ABSORBED`) fade out with their object in about 0.5 s.
- A numbered claim (`1) Use the probabilities for its new situation`, 4:45) sits beside the
  object it describes, never as a subtitle.
- Older Veritasium (2020 *logistic map*) writes equations by hand on a paper pad on camera, then
  overlays the equation top-right on screen recordings [measured: contact sheet]. "Write-on" there
  is literal.

### 2.4 Kurzgesagt (After Effects)

[measured: *How Are Memories Stored Inside Your Brain?*, 2026-06-16]

- **Text is rare and has fixed forms**: rounded pill tags (`86 Billion Neurons`,
  `Chemical Synapse`, `10,000 Connections`); thin leader lines ending in a short underlined
  label (`Visual Cortex`, `Auditory Cortex`, `Language Areas`); full-frame white chapter cards
  with small spaced caps (`LOCAL COLUMNS`, `CEREBRAL CORTEX`, `ASSEMBLY`, `HIPPOCAMPUS`);
  hand-lettered titles (`How to Store the Past`); speech bubbles.
- **Leader-line label**: the line draws out of the object in about 0.2 s (an angled segment,
  then a horizontal), then the label types on along the line in about 0.2–0.3 s, roughly 50–70
  characters per second, so it reads as a quick wipe rather than typing (2:56.9–2:57.3). It
  holds 2.5–3 s, then **reverses**: the text erases letter by letter and the line retracts, about
  0.5 s. The next label starts within about 0.5 s.
- **Pill tag**: the coloured box expands sideways from its centre, revealing the text through
  it as it grows, about 0.4 s with roughly 4% overshoot, settling in another 0.2 s
  (1:13.7–1:14.3). The tag is pinned to the world, so it drifts with camera pans.
- Tags hold 2.5–6 s. Labels come one at a time, each with its own short entrance and exit.

### 2.5 Reducible (Manim CE)

[measured: 2022 code]

- `FadeIn` 27.0 and `Write` 12.7 per 1k lines dominate; `TransformFromCopy` 2.9,
  `ReplacementTransform` 1.8, `LaggedStartMap` 1.6, `AddTextLetterByLetter` 0.15,
  `TransformMatchingTex` 0. Explicit rate functions are mostly `linear` (33 of 42).
- Fonts set explicitly: `CMU Serif` (with `REDUCIBLE_FONT`) and `SF Mono` [verified: code].
- So Reducible's text motion is CE's default `Write` plus fades: the same family of moves as
  3b1b, with less morphing.

### 2.6 Patterns side by side

| Pattern | 3b1b | Welch | Veritasium | Kurzgesagt | Our baseline |
|---|---|---|---|---|---|
| Label entrance | `Write` 1–2 s, or fly in from source 1–2 s | `Write` letter by letter (~11 letters/s, 0.4 s per letter) | fade or slide with the object | leader line 0.2 s + type-on 0.2–0.3 s; pill mask from centre 0.4 s | `FadeIn` 0.35 s |
| Prose / example sentence | rare; `Write` or fade | fade whole, 0.6 s | numbered claim beside object | speech bubble | box with a word |
| Equation build | term by term, each term travelling from the diagram | written under its object; numbers substituted in place | pill rises with tilt + settle, 0.5 s | none | none |
| Equation change | matched-symbol morph: 2 s default, 1 s when set, 0.6–0.8 s per algebra step in 2026; strike + slide together 1 s | stack and dim; strike-through; boxed result | – | – | none |
| Emphasis | colour, `FlashAround`/`FlashUnder` sweep, box; dim the rest | dim the rest to 0.2–0.5, small yellow arrow, outline box | colour-coded words | glow on object | `Indicate`, recolour whole object |
| Exit | fade with the figure, or morph into the next thing | dim in place; camera moves away | fade with object | reverse of entrance (erase + retract), 0.5 s | `FadeOut` |
| Captions of narration | never | never | never | never | none (correct) |
| Typical text-move length | 0.6–2 s | 0.6–2 s (camera 3 s) | 0.5 s | 0.2–0.6 s | 0.2–0.4 s |
| Still between moves | 2–9 s holds, 83% of clip still | 85% still | 10+ s hold on the equation | 2.5–6 s tag holds | breathing idles |

**What the reference styles share** [inferred: from the table]:

1. **Text has a source.** It writes on stroke by stroke, grows out of its object along a leader,
   travels from where it was defined, or is revealed by its container. It does not just appear.
2. **One text move at a time**, then a hold long enough to read it.
3. **Exits mirror entrances** (Kurzgesagt) or are replaced by dimming in place (3b1b, Welch).
4. **Equations are never re-typeset from scratch**: terms move, strike, slide and box.
5. **Speed depends on the style.** The two "lecture" styles use 0.6–2 s text moves; the two
   motion-design styles use 0.2–0.6 s entrances with overshoot. Our 0.35 s `FadeIn` has the
   motion-design speed with none of the motion-design shape.

## 3. Motion-design rules as numbers a style pack can hold

UI motion systems (Material 3, IBM Carbon, Apple HIG) are written for feedback in an app, where
the user starts the motion and wants it over quickly. Explainer video is the opposite: the viewer
can't pause the motion's meaning, and must read while listening. So the **shape** rules transfer
(ease-out on entry, ease-in on exit, longer for bigger moves, one focal move at a time) but the
**durations** in explainers are 2–5× the UI tokens: 3b1b's text moves are 0.6–2 s where Material's
largest token is 1 s [inferred: §2 measurements vs tokens below].

### 3.1 Easing

Reference curves [verified: sources in each row; numbers measured by sampling each curve,
`research_cache/motion/` one-liner]:

| Curve | Definition | Time to go from 5% to 95% of the change | Peak speed vs linear | Use |
|---|---|---|---|---|
| manimgl `smooth` | quintic, `t³(10s² + 5st + t²)`, zero 1st and 2nd derivative at both ends (`manimlib/utils/rate_functions.py:17`) | middle 62% of the run | 1.9× | 3b1b default for every move except `Write` |
| Manim CE `smooth` | normalised sigmoid, inflection 10 (`vendor/manim/manim/utils/rate_functions.py:156`) | middle **56%** of the run | 2.5× | CE default |
| `linear` | – | 90% | 1× | manimgl and CE `Write` (the per-glyph stagger supplies the shape); 3b1b's most common explicit rate (140 uses) |
| Material 3 *emphasized decelerate* | `cubic-bezier(0.05, 0.7, 0.1, 1)` | first 50% | – (fast start) | entering elements |
| Material 3 *emphasized accelerate* | `cubic-bezier(0.3, 0, 0.8, 0.15)` | – | – | exiting elements |
| Material 3 *standard* | `cubic-bezier(0.2, 0, 0, 1)` | 6–66% | 4.1× | moves that start and end on screen |
| Carbon expressive entrance / exit | `cubic-bezier(0, 0, 0.3, 1)` / `(0.4, 0.14, 1, 1)` | 2–74% (entrance) | 3.3× | "expressive" = significant moments |
| Carbon productive entrance / exit | `cubic-bezier(0, 0, 0.38, 0.9)` / `(0.2, 0, 1, 0.9)` | – | – | "productive" = efficient UI |

[verified: Material tokens from material-components-android `docs/theming/Motion.md`; Carbon
from carbondesignsystem.com/elements/motion/overview]

**Consequence for our baseline** [measured: curve sampling]: a 0.35 s CE `FadeIn` with CE
`smooth` shows no visible change for its first 77 ms and does 90% of its change in 0.20 s. It
reads as a pop, and lands up to 0.08 s after the cue it was timed to.

**Rules** [verified: Material "decelerate for entering, accelerate for exiting, standard for on
screen"; Carbon "duration should scale with the size of the animation"]:

1. Entrances decelerate (fast start, soft landing). Exits accelerate and are shorter. Moves that
   start and end on screen use a symmetric ease.
2. Duration grows with distance and area: a label appearing in place is short, a term flying
   across the frame or a camera move is long.
3. Write-on is linear in time per glyph; the stagger makes it feel eased.
4. Vary the ease by role. HyperFrames' skill: arrivals `expo.out` / `power4.out`, camera moves
   `power2.inOut`, exits `power3.in`, linear only for rotation and progress; "the same
   `power2.out` at 0.5 s on everything is the flat default that makes a film feel generated"
   [verified: hyperframes `references/motion.md`]. Our 0.35 s CE-`smooth` fade on everything is
   the Manim version of that default.
5. Overshoot (a spring or back-ease of 3–5%) is a motion-design signature (Kurzgesagt pills,
   Veritasium's equation pill). Neither 3b1b nor Welch overshoot text [measured: §2]. So overshoot
   belongs in a style pack, not the core.

### 3.2 Durations

| Token | UI systems | 3b1b (measured) | Welch (measured) | Motion-design channels (measured) |
|---|---|---|---|---|
| small fade / appear | Material short2 100 ms, Carbon fast-02 110 ms | `FadeIn` 1 s default, 0.8 s p10 | prose fade 0.6 s | pill 0.4 s + 0.2 s settle |
| text write-on | – | 1 s (< 15 glyphs), 2 s (longer) | ~11 letters/s, 0.4 s per letter | type-on 0.2–0.3 s (50–70 chars/s) |
| move across frame / reflow | Material long1 450 ms, Carbon slow-01 400 ms | 1–2 s (`TransformFromCopy` median 2.0) | label re-park 1.4 s | – |
| equation morph | – | 2 s default, 1 s when set, 0.6–0.8 s per algebra step (2026) | stack and dim, box result | – |
| camera / layout change | Material extra-long ≤ 1,000 ms | – | 3.0 s pull-back | – |
| emphasis sweep | – | `FlashAround` 1–2 s | yellow arrow on for one clause | glow |
| exit | Material fade-out 75 ms vs fade-in 150 ms | fade with the figure | dim in place | reverse of entrance, ~0.5 s |

[verified: Material/Carbon tokens as above; channel figures measured in §2]

### 3.3 Stagger

- **Per glyph** (write-on): `Write` uses `lag_ratio = min(4/(n+1), 0.2)` in manimgl
  (`min(4/max(1, n), 0.2)` in CE and manimgx) over a 1–2 s run. That gives a new glyph every
  0.03–0.09 s (11–37 glyphs/s), with 5 glyphs in flight at once for short labels and up to about
  15 for long equations [verified: code; rates inferred from the formula]. CE's `AddTextLetterByLetter`
  defaults to 0.1 s per character (10 chars/s), linear, with no overlap
  [verified: `vendor/manim/manim/animation/creation.py:564,579`]; that is the typewriter look,
  not the 3b1b look. HyperFrames' skill: "letters a frame apart, words 60–120 ms, list items
  40–80 ms" [verified: hyperframes `references/motion.md`].
- **Per item** in a group: 3b1b's median `lag_ratio` is 0.1 (p25 0.1, p75 0.35; n = 1,897)
  [measured: code]. With `LaggedStart`, `lag_ratio` 0.1 means each item starts when the previous
  one is 10% done, so a list of 5 reads almost as one move; 0.35+ reads as a sequence.
- **Per word / per line** for anything longer than a short label: letter-level reveals slow
  reading of sentences; practitioners reserve them for single words or short labels and
  sequence sentences by word or line [verified: practitioner guidance, cursa.app "Text Animation
  for Readability"; weak source]. Kurzgesagt types only 1–3 word labels; Welch writes caps labels
  letter by letter but fades sentences whole [measured: §2].

### 3.4 Layout: safe areas, grid, hierarchy

- **Safe areas.** EBU R95 v1.1 (2017): action-safe margin **3.5%** and graphics-safe margin
  **5%** at top, bottom and sides of a 16:9 frame [verified: EBU R95 PDF]. At 1920×1080 that is
  96 px left/right and 54 px top/bottom for graphics; on Manim's 14.22 × 8 frame, 0.71 and 0.40
  units. Online video has no overscan, so this is a composition margin, not a technical one.
  HyperFrames' skill is stricter: content inside 90% action-safe, key text inside 80% title-safe
  (5% and 10% margins per side) [verified: hyperframes `SKILL.md`].
- **Text size band** [measured: style docs and §1]:
  - 3b1b text boxes: median 3.1–6.9% of frame height; default `font_size` 48 ≈ 4.2%.
  - Welch: 3.6–4.2% for nearly all text; titles distinguished by caps and tracking, not size.
  - Our labels: glyph extent 2.2–3.1% (title 4.7%).
  - Proposed floor for a pack: rendered glyph extent (ascender to descender) **≥ 3.5% of frame
    height** for any label, title 1.0–1.5× label (Welch) or up to 2× (3b1b's 72 vs 36–48)
    [inferred].
  - Engine floors for comparison: HyperFrames warns under 2.6% of the frame's short side
    (`text_below_floor`); manimgx `inspect` flags text under 20 px at 1080p (1.85%); HyperFrames
    titles 4–9% of frame height [verified: §4].
- **Words per text item** [verified: style docs]: 3b1b median 2 words, 74% ≤ 3, lines broken at
  ~30 characters; Welch caps labels of 1–4 words, longest item per frame 9–22 characters. Netflix
  allows 42 characters per subtitle line [verified: Netflix English timed-text guide], a ceiling
  for any single line of prose.
- **Grid.** The reference styles don't use a visible column grid: 3b1b attaches labels to objects
  (`next_to`, 0.25 buffer), Welch reserves slots (title band top 15%, caption under object,
  dims lower right, footnotes bottom right) [verified: style docs]. A pack therefore needs both:
  (a) a coarse region grid for primary objects, and (b) attachment rules for labels. Code2Video's
  6×6 grid is the published precedent for (a) (agentic-systems.md).
- **Hierarchy through brightness, not boxes.** Welch: primary text tan/white, secondary brown,
  focus yellow; context dimmed to 0.2–0.5 opacity [verified: welch-labs.md §8]. 3b1b: dim the
  rest, colour the term [verified: 3blue1brown.md §8]. Our grey-in-a-red-box "inactive" labels
  invert this.
- **Fill the frame with the idea, not with empty space.** Our content's bounding box covers a
  median 8% of the area below the title (§1). Reference frames place one primary figure large,
  usually centred or right of centre, with text left or above (3b1b) or a diagram filling the
  frame with lots of black between parts (Welch) [verified: style docs]. A layout check can
  enforce a minimum extent for the primary figure (proposal: its bounding box spans ≥ 40% of the
  safe-area width) [inferred].

### 3.5 How many things move at once

- **One focal move at a time**, plus moves that are consequences of it. In the 3b1b clip, the
  strike-out, the slide-together and the diagram dimming happen in the same second, because they
  are one idea [measured: §2.1]. Kurzgesagt sequences labels strictly one after another
  [measured: §2.4]. Carbon: "related movements should have a unified relationship"; Apple: "Don't
  add motion for the sake of adding motion" [verified: Carbon, Apple HIG motion page].
- Proposed check [inferred]: at most **one** text element entering at any instant (a
  `LaggedStart` group counts as one), and at most **two** concurrent animation groups, where the
  second must be a dim, a camera move, or the source object of the first.

### 3.6 Entrances and exits

- Text enters with a source: write-on, from its object (leader line, grow-from-point), from
  where it was defined (fly-from-copy), or revealed by its container (mask) [measured: §2.6].
- Exits are shorter than entrances (Material: fade-in 150 ms, fade-out 75 ms; HyperFrames: "40–50%
  shorter than their entrances") or mirror them (Kurzgesagt: erase + retract ~0.5 s) [verified:
  Material Motion.md, hyperframes `references/motion.md`; measured: §2.4].
- Overlap: "the next element starts when the previous is 30–50% done; fully sequential looks
  robotic, all at once looks cheap" (HyperFrames). 3b1b's median group `lag_ratio` of 0.1 is far
  more overlapped than that; its separate moves are fully sequential with holds between [verified:
  hyperframes; measured: §2.1]. The two registers differ here.
- In the lecture styles, most text never exits mid-scene: it dims in place and leaves with the
  scene cut [verified: style docs].

### 3.7 Reading time

- **Subtitle standards** [verified: Netflix timed-text guides]: at most 20 characters per second
  for adult content (17 for children's), 42 characters per line, 2 lines, and a minimum
  duration of 20 frames (≈ 0.83 s).
- **Practitioner rule for on-screen text** [verified: SSW rule "do you give enough time to read
  texts in your videos"]: keep it up long enough to be read **twice** by a slow reader at 200
  words per minute, i.e. **0.6 s per word**.
- **HyperFrames' skill**: "a line the viewer must read holds about 0.5 s plus 0.3 s a word, the
  film's last line at least 2 s" [verified: hyperframes `references/motion.md`]. That is half the
  SSW figure for long lines, because a kinetic-type line is usually also spoken.
- **Ofcom/BBC**: subtitles should not exceed 160–180 wpm [verified: secondary sources only; the
  BBC pages could not be fetched].
- **Labels compete with the voice.** A label that is spoken as it appears costs almost no extra
  reading; text that is not spoken must be read over the narration. So the dwell rule matters
  most for unspoken text (dims, footnotes, axis labels, quotes) [inferred: Mayer's redundancy and
  temporal-contiguity results in landscape.md].
- Proposed pack rule [inferred]: an unspoken text item stays fully visible for at least
  `max(1.5 s, 0.6 s × words, characters / 15 cps)`; the scene may not cut away or dim it before
  that; the entrance must finish at least 0.3 s before the end of that window.

### 3.8 A style-pack schema with values

A proposal, filled from the measurements above. Every value is [inferred] from §2–§3 unless the
cell says otherwise.

| Key | 3Blue1Brown pack | Welch Labs pack | Notes |
|---|---|---|---|
| `text.entrance.default` | `write` | `write` (caps labels), `fade` (prose) | |
| `text.write.run_time` | 1.0 s if < 15 glyphs, else 2.0 s (manimgl default) | same | [verified: manimgl code] |
| `text.write.lag_ratio` | `min(4/(n+1), 0.2)` | same | [verified: code] |
| `text.fade.run_time` | 1.0 s, optional drift 0.25–0.5 units | 0.6 s, no drift | [measured] |
| `text.from_source.run_time` | 1.0–2.0 s | 1.4 s (re-park) | [measured] |
| `equation.morph` | match symbols (manimgl-style), 0.6–2.0 s, `smooth` | stack + dim older lines, box result | [measured / verified style docs] |
| `emphasis.allowed` | colour change, `FlashAround`/`FlashUnder` (1–2 s), box, dim others | dim others to 0.2–0.5, yellow arrow, outline box | [verified style docs] |
| `emphasis.banned` | `Indicate`, `Wiggle`, scale pulses | same | [verified style docs] |
| `ease.move` | manimgl `smooth` (quintic) | manimgl `smooth` | use the quintic, not CE's sigmoid |
| `ease.enter` / `ease.exit` | `smooth` / `smooth` | `smooth` / dim | lecture styles don't use asymmetric eases |
| `overshoot` | 0 | 0 | motion-design packs: 3–5% |
| `stagger.group_lag_ratio` | 0.1 (sequence feel: 0.35) | `LaggedStart` default | [measured: 3b1b code] |
| `concurrency.max_text_entering` | 1 | 1 | |
| `hold.after_move.min` | 1.0 s | 1.0 s | [measured: 3b1b bare `wait()`] |
| `read.dwell` | `max(1.5, 0.6·words, chars/15)` s | same | |
| `layout.safe_margin` | 5% | 5% | [verified: EBU R95] |
| `text.size.label` | ≥ 3.5% of frame height | 3.6–4.2% | [measured] |
| `text.size.title_ratio` | ≤ 2.0 × label | ≤ 1.3 × label, caps + tracking | [measured] |
| `text.words.label_max` | 3 (median 2) | 4 | [verified style docs] |
| `text.line_chars_max` | 30 | 22 | [verified style docs] |
| `text.backstroke` | black, width 3–8 behind glyphs | none (text kept off busy areas) | [verified style docs] |
| `title.persistence` | per section or none | per section, top band 15% | never one title for a whole video |

If a browser engine is chosen, a third, motion-design pack (Kurzgesagt / Veritasium register)
can start from HyperFrames' numbers rather than ours: entrances 0.3–0.6 s with `expo.out` or a
spring at damping ratio 0.7–0.85, exits 40–50% shorter with `power3.in`, overlap 30–50%, word
stagger 60–120 ms, per-word blur-in (6 px → 0 in 0.13 s), hold `0.5 s + 0.3 s/word`, titles 4–9%
of frame height, 10% title-safe margins [verified: §4.2]. Kurzgesagt's measured leader-line and
pill timings (§2.4) fall inside those ranges [inferred].

## 4. Engines: text motion, automatic layout, math

### 4.0 Capability table

Detail and sources in §4.1–§4.2. "Built in" means shipped by the engine or its official
packages.

| | Manim CE 0.21 (ours) / 0.22.1 | manimgl | manimgx 0.1.1 | HyperFrames + GSAP | Remotion | Motion Canvas / Revideo |
|---|---|---|---|---|---|---|
| **Text write-on / reveal** | `Write` (1–2 s, linear, glyph stagger), `AddTextLetterByLetter` (0.1 s/char), `TypeWithCursor`; `AddTextWordByWord` documented as broken | `Write` (same timing), `ShowIncreasingSubsets`, `AddTextWordByWord` with real word groups; no letter-by-letter typewriter | CE's set, same defaults; `AddTextWordByWord` works with a VGroup of words | none built in; GSAP SplitText (chars/words/lines, masks, autoSplit) and registry blocks (`typewriter`, `kinetic-type-swap`) | none built in; `spring()`/`interpolate()`; typewriter by string slicing (official skill rule) | `Txt` text tween (left-to-right char swap); generic tweens |
| **Emphasis** | `Indicate`, `Circumscribe`, `ShowPassingFlash`, `Flash`, `FocusOn`, `Wiggle` | `FlashAround`, `FlashUnder`, `VShowPassingFlash`, `set_backstroke` | CE's set (no `FlashAround`, no backstroke helper) | anything CSS/SVG can do (blur, masks, clip-path, highlight sweeps) | `@remotion/rough-notation` (highlight, circle, strike) | generic |
| **Text morph** | `TransformMatchingShapes`, `FadeTransform` | `TransformMatchingStrings`/`…Tex` (longest-common-substring over symbols) | `TransformMatchingTex`/`…Shapes` | none (MorphSVG on outlines would be custom) | none (`interpolatePath` on outlines would be custom) | `Txt` swap; `Code` diff animation |
| **Wrapping / measuring** | no wrap width (`Text` wraps at the pixel width; `MarkupText` at a fixed 500); `Paragraph` alignment; `arrange`, `arrange_in_grid` | **`line_width=` wrap** with `justify`/`alignment`; `arrange_in_grid`, `arrange_to_fit_width` | no wrap; `Paragraph` on a baseline grid; exposes glyph advances | CSS flex/grid/wrap; `fitTextFontSize`, `pretext` measuring | CSS flex/grid/wrap; **`measureText`, `fitText`, `fillTextBox`, `fitTextOnNLines`** | flexbox via the browser (`layout` prop), `textWrap` |
| **Layout checks** | none built in (ours: geometry pass, `layout_check`) | none | **`manimgx inspect`**: cut, overlap, crossing, covered, small (< 20 px at 1080p), on 2D frames | linter: clipped, overflowing, occluded text; `text_below_floor` | none built in | none |
| **Math** | LaTeX + dvisvgm (`MathTex`, `{{ }}`, `substrings_to_isolate`, `t2c`); optional Typst | LaTeX + dvisvgm; **`tex["x"]` on any substring**, `t2c`, `isolate` | no TeX install: LaTeX → mitex → Typst inside Rust; no packages, no `\def`; open bugs (`\frac` + colour map crash) | none; load KaTeX/MathJax yourself | none; KaTeX/MathJax in React, per-term classes | **MathJax `<Latex>`** (Revideo: static image only) |
| **Equation morph** | `TransformMatchingTex` (by part tex string) | **best**: `TransformMatchingStrings` matching + `key_map`, `matched_keys` | `TransformMatchingTex` (by part) | custom build | custom build | **`tex().tex(new, dur)`**: matched parts move, others fade (Motion Canvas only) |
| **Speed / render** | Cairo CPU; slowest in the manimgx benchmark (278.8 s total) | OpenGL (1.7.2); wgpu on unreleased master; 35.3 s | Rust + wgpu; 3.08 s ("90.6× CE, 11.5× GL", vendor-run on an M4 Pro) | headless Chrome seek, 1–24 workers; deterministic on Linux | headless Chrome, `--concurrency`; GPU CSS effects slow on cloud CPUs | editor render button (MC); headless `renderVideo()` (Revideo) |
| **Licence, status** | MIT; 0.22.1 (2026-10-27), very active | MIT; PyPI 1.7.2 (2024-12-13), master active | MIT, but wheels with x264 are GPL-3.0+; 0.1.1 (2026-10-07), new | Apache-2.0, v0.9.77 (2026-11-21), daily; GSAP free incl. plugins | source-available; free ≤ 3 people, else paid; very active | MIT; MC dormant since 2025-02; Revideo slow |

**Strongest for** [inferred: from the table and the frames in §5–§6]:

- **(a) Typography motion: HyperFrames + GSAP.** Real fonts and kerning, SplitText masks per
  line/word/char, blur and springs, and a skill that already encodes timing rules (§4.2).
  Remotion has the same browser underneath with fewer text helpers.
- **(b) Automatic layout: the browser engines.** CSS flex/grid plus text measuring; Remotion's
  `layout-utils` is the most explicit measuring API, HyperFrames adds a layout linter. In the
  Manim family only manimgl wraps text to a width; manimgx's `inspect` is a check, not a layout
  engine.
- **(c) Math: manimgl**, then Manim CE. Substring indexing on any Tex plus
  longest-common-substring matching is exactly what 3b1b's term-by-term builds need. manimgx
  removes the TeX install but loses LaTeX packages and has open math bugs. Motion Canvas is the
  only non-Manim engine with native equation morphs, and it is dormant. In HyperFrames or
  Remotion, a 3b1b-style equation morph is a custom build (MathJax SVG + matched glyph tweens);
  Motion Canvas's `tweenTex` shows it is feasible.

No engine is strongest at all three. The two realistic shapes are a Manim-family engine with
browser-grade text rules imposed by the style pack, or a browser engine with a custom
equation-morph component [inferred].

### 4.1 Manim family (CE, manimgl, manimgx)

Researched by a sub-agent from source: `vendor/manim` (CE 0.21.0 fork), manimgl master
`fafa083` and the 1.7.2 wheel, manimgx `1fb4dd7`, all under `research_cache/motion/manim_family/`.
I re-checked the manimpango pin and runtime version, the ManimPango 0.7.0 release note, the
manimgx check thresholds, and CE's `Write`, `smooth` and `AddTextLetterByLetter` myself.

**Our word-spacing bug has an upstream fix we don't have.** CE issue #2844 (2022): `Text` is laid
out at `font_size / 4.8` pt and Pango rounds glyph positions to whole pixels, so small text
loses or squeezes spaces (ManimPango#130). ManimPango **0.7.0 (2026-10-01)** disables
`round_glyph_positions` by default ("fix: disable pango round glyph positions by default", PR
#131), and CE 0.22.0 requires it. **Our vendored fork pins `manimpango>=0.6.1` and locks 0.6.1,
and the `manim_env` runtime imports manimpango 0.6.1** [verified: `vendor/manim/pyproject.toml:32`,
`vendor/manim/uv.lock`, runtime import; release notes via `gh api`]. That is the most likely cause
of `thision` / `energy isspent` in §1; the old workaround is to build text at ≥ 48 and
`scale()` it down.

**Manim CE** (MIT; 0.22.1 released 2026-10-27; daily commits) [verified: source, PyPI, GitHub]

- Base defaults: 1 s, `smooth` (normalised logistic, §3.1), `lag_ratio` 0; `LaggedStart` and
  `LaggedStartMap` default `lag_ratio` 0.05; `LaggedStartMap` run time 2 s.
- `Write`: linear; 1 s under 15 glyph paths, else 2 s; `lag_ratio = min(4/max(1, n), 0.2)`
  (manimgl uses `4/(n+1)`). `Unwrite` reverses it. `DrawBorderThenFill`: 2 s, `double_smooth`.
- `AddTextLetterByLetter` / `RemoveTextLetterByLetter`: 0.1 s per character, linear.
  `TypeWithCursor` / `UntypeWithCursor`: 0.1 s per character with a cursor. `AddTextWordByWord`:
  its docstring says "currently broken" (it iterates glyphs, not words).
- `TransformMatchingTex` keys on each `MathTexPart`'s tex string; all parts sharing a key are
  transformed as one group (two source `x` can collapse into one target `x`); `key_map` pairs
  use `FadeTransformPieces`; unmatched parts fade out toward the unmatched targets. There is no
  `TransformMatchingStrings` in CE. `TransformMatchingShapes` keys on normalised point hashes.
- Emphasis defaults: `Indicate` ×1.2 yellow; `Circumscribe` rectangle, `time_width` 0.3;
  `ShowPassingFlash` `time_width` 0.1; `Flash` 12 lines; `Wiggle` 2 s.
- Rate functions include the full `ease_{in,out,in_out}_{sine,…,back,elastic,bounce}` family, so
  CSS-style eases and overshoot are available without custom code.
- Layout: `Text(width=…)` only rescales; `Text` wraps at the render's pixel width and
  `MarkupText` at a hard-coded Pango width of 500, so neither has a usable wrap width;
  `Paragraph` aligns lines; `arrange(buff=0.25)`, `arrange_in_grid(rows, cols, buff,
  cell_alignment, row/col alignments, row_heights, col_widths)`. No flex or auto-fit.
- Math: LaTeX + dvisvgm (`MathTex`, `{{ }}`, `substrings_to_isolate`, `tex_to_color_map`,
  `set_color_by_tex`); optional Typst (`Typst`, `MathTypst`) without TeX. CE's
  `TransformMatchingTex` asserts `MathTexPart`, so it won't key `MathTypst` parts [inferred: code].
- Speed: Cairo on CPU; 0.21.0 claims Cairo 2.2× faster on animation-heavy scenes.

**manimgl** (MIT; PyPI 1.7.2 of 2024-12-13; master active to 2026-09, ported to wgpu, unreleased)
[verified: source]

- `Write` as above (`4/(n+1)`); `ShowCreation` `lag_ratio` 1; no letter-by-letter typewriter or
  cursor; `AddTextWordByWord(time_per_word=0.2)` uses real word groups.
- **`TransformMatchingStrings`** (alias `TransformMatchingTex`), 2 s default. Matching order:
  your `key_map` / `matched_keys`; then repeated `SequenceMatcher.find_longest_match` over the
  symbol lists (a symbol is a `\command` or one character); then leftover pieces with the same
  shape; the rest fade out to the target's centre and in from the source's. This is why 3b1b's
  algebra steps move the right symbols without hand-isolated parts.
- **`tex["x"]`** selects any substring, isolated or not (regex plus symbol counting); `t2c` and
  `isolate`; multiple string arguments are auto-isolated; `Text` isolates words by default so
  `text["word"]` works.
- `FlashAround` (`time_width` 1, stroke 4, yellow), `FlashUnder`, `VShowPassingFlash`
  (`time_width` 0.3), `set_backstroke(BLACK, width=3)`.
- **Only Manim with real wrapping**: `Text`/`MarkupText(line_width=<units>, justify, indent,
  alignment)`; `arrange_to_fit_width/height`.
- Lays text out at full size (font_size × 1024 Pango units), so the CE rounding bug is about 5×
  smaller relative to the glyph [inferred: code]. Default `Text` font is Consolas: a pack must
  set fonts explicitly.

**manimgx** (academa-labs; own code MIT, but "native wheels include x264 and are GPL-3.0-or-later
as a whole"; 0.1.0/0.1.1 on 2026-10-07; Python ≥ 3.13) [verified: README, source, PyPI]

- **Mirrors Manim CE's API, not manimgl's**: same names, defaults, `Write` formula, logistic
  `smooth`, `ease_*` set; no `TransformMatchingStrings`, `FlashAround`, `set_backstroke` or
  `TexText`. A port from our CE code is cheap; a port of 3b1b or Welch idioms is not.
- Math without TeX: LaTeX → mitex 0.2.7 → Typst 0.15.1 inside the Rust engine; `{{ }}` parts
  anywhere; "LaTeX packages and `\def` don't" work; open bugs #60 (`\"`) and #74 (`\frac` +
  `tex_to_color_map` crash). Font fallback to New Computer Modern without warning (#33).
- No wrapping ("a newline breaks the line"); `Paragraph` on a shared baseline grid (1.3 em);
  glyph advances exposed, an em is `font_size/96` units.
- **`manimgx inspect` layout checks** (also run on `render`): samples the end of each play/wait on
  2D scenes and flags **cut** (> 0.02 units past a frame edge), **overlap** (two text boxes
  intersecting by > 5% of the smaller), **crossing** (a stroke within 0.03 units, about 4 px, of
  a glyph box), **covered** (a fill ≥ 0.5 opacity over > 30% of a text), **small** (text < 20 px
  tall at 1080p, i.e. 1.85% of frame height). Exit code 1 plus a red-numbered storyboard PNG.
  Bounding boxes, not ink; sampled moments only [verified: `src/manimgx/cli/diagnostics.py:283–459`].
  Its `small` floor (1.85%) is far below the 3.5% this doc proposes and HyperFrames' 2.6% of the
  short side.
- Speed: Rust + wgpu (lavapipe CPU fallback on Linux). The vendor's benchmark (2026-10-07, Apple
  M4 Pro) gives 3.08 s vs manimgl 35.3 s vs CE 278.8 s total, with caveats: CE got 1 run vs
  3-run means, manimgx encodes holds as one long frame, and CE beat manimgl on the 2D scenes
  [verified: `benchmarks/README.md`].
- Welch Labs has a `custom_gx/welch_style.py` but no video found made with manimgx.


### 4.2 Browser and vector engines

Researched by a sub-agent against current docs, repos and npm (raw copies of the skill files,
docs and licence pages in `research_cache/motion/browser_engines/`). I re-checked the HyperFrames
motion rules, the GSAP licence text, Motion Canvas's `Latex` tween and commit history, and the
HyperFrames release with `gh api`.

**HyperFrames** (HeyGen; HTML + CSS + a paused GSAP timeline, headless Chrome seeks each frame,
FFmpeg encodes) [verified: github.com/heygen-com/hyperframes, Apache-2.0, v0.9.77 released
2026-11-21, several releases a day]

- *Text animation*: no text primitives of its own; you write GSAP or CSS. Registry blocks:
  `typewriter`, `kinetic-type-swap`, `kinetic-center-build`, `caption-kinetic-slam`, and code
  blocks `code-typing`, `code-diff`, `code-morph` (Shiki tokens) [verified: repo, via sub-agent].
- *Layout*: the browser's CSS (flex, grid, wrapping). `window.__hyperframes.fitTextFontSize` and a
  `pretext` helper (on `@chenglou/pretext`) measure text without reflow; the linter flags
  clipped, overflowing or occluded text unless a `data-layout-allow-*` attribute opts out; the
  skill's `check` warns `text_below_floor` under 2.6% of the frame's short side [verified:
  `skills/hyperframes/references/runtimes.md`, `format.md`, `review.md`, via sub-agent].
- *Math*: none built in; no KaTeX or MathJax in the repo. Load KaTeX or MathJax in the page
  [verified: code search; loading inferred, it's plain HTML].
- *Morphing*: CSS, clip-path, SVG; GSAP MorphSVG works [inferred].
- *Rendering*: seek-deterministic (no `Date.now`, unseeded random or infinite repeats); full
  determinism needs Linux with chrome-headless-shell (Docker mode); 1–24 workers, 4 "usually the
  sweet spot"; `--chroma-subsampling 444` recommended for text-heavy masters [verified:
  `packages/cli/src/docs/rendering.md`, via sub-agent].
- **Its agent skill is the best numeric motion spec found anywhere in this research**
  [verified: `skills/hyperframes/references/motion.md`, `SKILL.md`, `story.md`]:
  - action-safe 90%, title-safe 80% (5% / 10% margins per side, stricter than EBU R95);
  - fast moves 0.3–0.6 s with 6–12 px motion blur on text-sized elements;
  - "arrive slow, leave clean": arrivals `expo.out` / `power4.out`, camera and colour floods
    `power2.inOut`, exits `power3.in`; linear only for rotation and progress;
  - "The same `power2.out` at 0.5 s on everything is the flat default that makes a film feel
    generated";
  - exits 40–50% shorter than entrances; the next element starts when the previous is 30–50%
    done; stagger: letters 1 frame apart, words 60–120 ms, list items 40–80 ms;
  - springs named by damping ratio: 0.7–0.85 "reads premium"; opacity and colour never bounce;
  - title entrances to vary between: per-word blur 6 px → 0 with opacity in 0.13 s, 0.067 s
    apart; per-word grey → ink 0.07–0.1 s apart; whole line blur 8 → 0 px in 0.13–0.2 s; per
    letter 0.1 s apart for a name;
  - holds: "about 0.5 s plus 0.3 s a word", the last line at least 2 s; exit with a blur-out
    and fade of 0.13–0.25 s;
  - title size 4–9% of frame height; quiet lines 2.5–4%; titles at most 6 words a line
    (explainer lines up to about 10), one line on screen at a time;
  - banned as "defaults that look generated": breathing, floating or pulsing loops; titles that
    keep moving after they land; every element fading and sliding up.

  These rules come from HeyGen's launch films (motion-design register, like Kurzgesagt), so
  their speeds are 2–4× faster than the 3b1b and Welch measurements in §2. The **shape** rules
  (ease by role, shorter exits, partial overlap, still after landing, no idle loops) agree with
  every reference style; the **durations** belong in a motion-design pack, not a lecture pack.

**GSAP** (Webflow) [verified: gsap.com docs and standard licence page]

- Default tween: 0.5 s, `"power1.out"`. CustomEase takes SVG path data or a cubic-bezier string.
- **SplitText** (rewritten in 3.13, 2025-04-29, "half the size, 14 new features"): splits into
  chars / words / lines; `mask` adds a clipping wrapper per line, word or char (the classic
  "text rises out of a slot" reveal); `autoSplit` re-splits after fonts load or the width changes
  (animations built in `onSplit()` keep their progress); `aria` handling, `propIndex` CSS
  variables such as `--word`, `smartWrap`. Split only after `document.fonts.ready`.
- **MorphSVG** morphs `<path>` data between shapes with different point counts (`shapeIndex`,
  `type: "rotational"`, `map`, `smooth` added in 3.14, 2025-12-08). Glyph morphing needs glyph
  outlines as paths, e.g. MathJax SVG output [inferred].
- **Licence**: the Standard "No Charge" License (effective 2025-04-30, modified 2025-05-30,
  © Webflow): "All of GSAP including the plugins that were formerly 'members-only' like SplitText
  and MorphSVG can be used in commercial projects at no charge." Prohibited: use "in tools that
  allow users to build visual animations without code" that compete with Webflow's visual
  animation builder. FAQ: "AI-generated code is not a 'Prohibited Use'." A code-first explainer
  generator is fine; a visual no-code animation editor built on GSAP would need Webflow's consent
  [verified: licence text, raw copy in `research_cache/motion/browser_engines/gsap_license/`;
  the conclusion is inferred]. Latest tag 3.15.1, 2026-11-04.

**Remotion** (React; every frame a pure function of the frame number) [verified: remotion.dev
docs, repo]

- *Text animation*: `spring()` (defaults mass 1, damping 10, stiffness 100: it bounces by
  default), `interpolate()` (extrapolation `extend` unless clamped), `Easing` incl.
  `Easing.spring()`. Official agent skills (`remotion-dev/skills`) say CSS transitions and
  Tailwind animation classes "will not render correctly", recommend `Easing.bezier(0.16,1,0.3,1)`
  or `Easing.spring({damping:200})` for "a nice push movement with no bounce", and
  `@remotion/rough-notation` for highlights, circles and strike-throughs. Typewriter rule:
  string slicing, never per-character opacity.
- *Captions*: `@remotion/captions` (`createTikTokStyleCaptions()`, SRT/VTT); the TikTok template
  fits text to 90% width (max 120 px), uppercase, 20 px black stroke, active word `#39E508`,
  pages every 1,200 ms, spring entry 0.8 → 1 over 5 frames.
- *Layout*: DOM/CSS, plus `@remotion/layout-utils` (MIT): `measureText`, `fitText`,
  `fillTextBox` (reports `newLine` / `exceedsBox`), `fitTextOnNLines`. The most explicit text
  measuring API of any engine here.
- *Math*: no official package or docs; use KaTeX or MathJax in React; per-term addressing via
  KaTeX `\htmlClass`/`\htmlId` (needs `trust: true`) or MathJax `\class`/`\cssId`. Equation morphing
  is custom code [verified: docs 404s, code search; KaTeX/MathJax docs].
- *Morphing*: `@remotion/paths` `interpolatePath()`; `@remotion/transitions` (fade, iris,
  clockWipe, blurSlide, cube, …).
- *Licence*: source-available Remotion License: free for individuals and companies of up to 3
  people; Company License from $25/seat/month (Creators) or $0.01/render with a $100/month minimum
  (Automators). v4.0.545, 2026-11-18, very active.

**Motion Canvas** (TypeScript generators + signals) and **Revideo** (its fork)
[verified: motion-canvas repo and docs; midrender/revideo repo]

- *Text*: `Txt` node; tweening its text does a left-to-right character swap while the box
  resizes. Property tweens default to `easeInOutCubic`; `spring()` with presets.
- *Layout*: opt-in `layout` prop, flexbox computed by hidden DOM elements
  (`getBoundingClientRect`), i.e. the browser's engine; `textWrap`, `lineHeight`, `letterSpacing`.
- *Math*: **the only engine besides the Manim family that morphs equations natively.** `<Latex>`
  renders MathJax (mathjax-full, AllPackages, SVG); `tex().tex(newTex, duration)` tweens between
  equations (v3.17.0, 2024-08-13): parts marked with `{{…}}` are matched by content; parts only
  in the source fade out, parts only in the target fade in, shared parts move. That is
  `TransformMatchingTex` semantics [verified: docs, `Latex.ts` `tweenTex`].
- *Code*: `Code` node with Lezer highlighting; tweening `code` animates a diff (`append`,
  `insert`, `replace`, `remove`, `selection`). Docs warn Chromium jitters code animations and
  recommend Firefox.
- *Maintenance*: Motion Canvas is MIT, latest stable v3.17.2 (2024-12-14); **last code commit
  2025-02-16**, only a docs-domain commit since (2026-07-02) [verified: gh api]. Effectively
  dormant. Community fork Canvas Commons (MIT, 0.4.0 on 2026-10-22). **Revideo** (MIT, now
  `midrender/revideo`, v0.11.0 2026-07-10) adds headless `renderVideo()` but its `Latex` is a
  static image with no tween, and it sends anonymous render telemetry unless
  `DISABLE_TELEMETRY=true`.

**Rive and Lottie** [verified: rive.app docs, lottie-web wiki, dotlottie-web repo]

- Rive text runs and text modifiers (ranges by character/word/line driving position, rotation,
  scale, opacity, follow-path, variable-font axes) are excellent typography motion, but authored
  in Rive's editor; runtime text changes go through Data Binding; video export needs Rive's paid
  cloud renderer, or render through Remotion/Revideo.
- Lottie supports After Effects text animators (range selectors, per-character transforms);
  lottie-web v5.13.0 (2024-11) is slow-moving; dotlottie-web (Rust/WASM, ThorVG) is active.
- Verdict: good for designer-made assets (characters, icons, a hand-animated title card), a poor
  fit for generated typography, because the motion lives in an editor, not in code
  [inferred].

## 5. Watch these: showcases per engine

What to look at is noted per link. Links marked (measured) are clips I stepped through for §2;
the rest come from official showcase pages and repos, with titles checked through YouTube
oEmbed or `gh api`. I did not watch the engine showcases end to end.

### 5.1 The target look (reference channels, timestamped)

| Link | Engine | Look at |
|---|---|---|
| 3Blue1Brown, *Bayes theorem*, 6:30–7:45 https://www.youtube.com/watch?v=HZGCoVF3YvM&t=390s (measured) | manimgl | terms flying from the diagram into the formula; strike-out + slide-together; box and title gliding to the compact form; formula row above, diagram below |
| 3Blue1Brown, *Reinventing Entropy* (2026), 14:10–15:50 https://www.youtube.com/watch?v=l6DKRf-fAAM&t=850s (measured) | manimgl | three algebra steps of 0.6–0.8 s each (grow-in, slide, sign arcing over `=`); the boxed result; live readout `Information := -log₂(p) = 2.03` on a plot |
| Welch Labs, *Can humans make AI any better?*, 12:05–12:45 https://www.youtube.com/watch?v=2hcsmtkSzIw&t=725s (measured) | manimgl | caps labels written letter by letter; a label re-parking to make room for an image; a 3 s camera pull-back that makes room for a new row |
| Welch Labs, *How DeepSeek Rewrote the Transformer*, ~3:45 and ~10:25 https://www.youtube.com/watch?v=0VLAoVGf_74&t=225s | manimgl + Illustrator | the three-slot caption row (CAPS name, equation, dims); angled leader lines from equation variables to labels |
| Kurzgesagt, *How Are Memories Stored Inside Your Brain?*, 2:50–3:03 https://www.youtube.com/watch?v=PqtggjVAi8M&t=170s and 1:04–1:15 (&t=64s) (measured) | After Effects | leader-line labels that draw, type, hold and reverse; pill tags expanding from their centre with a small overshoot |
| Veritasium, *Randomness is a lie*, 13:00–13:30 https://www.youtube.com/watch?v=uXuQF_PPg5U&t=780s (measured) | After Effects | an equation pill rising with a tilt and settling; colour-coded words; a plot building above a held equation |

### 5.2 HyperFrames

| Link | Look at |
|---|---|
| Launch-film sources, `heygen-com/hyperframes-launches` (Apache-2.0; `hyperframes-launch`, `figma-launch`, `claude-paper-launch`, `pr-to-video-launch`, …) https://github.com/heygen-com/hyperframes-launches | the films the motion rules were measured from; run `hyperframes preview` in a folder to watch one (needs Git LFS). Look at type entrances (blur-in per word), ease-by-role, transitions with a cause |
| Launch videos page https://hyperframes.heygen.com/launch-videos (did not load during this session: DNS error) | rendered versions of the above |
| Showcase https://hyperframes.heygen.com/showcase | two reference-vs-replica pairs (*THE OBLIST*, *Srinika × Mercury*); judge how closely code reproduces a designed film. Posters only on the page |
| Templates `kinetic-type`, `swiss-grid`, `nyt-graph`, `decision-tree`; blocks `flowchart`, `data-chart`, `code-typing`, `mk-callout-highlight` https://hyperframes.heygen.com/examples | type-led motion, grid layouts, editorial charts, diagrams: the closest to explainer frames. No math anywhere |

### 5.3 Remotion

| Link | Look at |
|---|---|
| Showcase https://www.remotion.dev/showcase | overall range (mostly product and social video) |
| William Candillon, *The Math behind Animations – Beautiful Trigonometry* https://www.youtube.com/watch?v=-lF7sSTelOg | math visuals in Remotion (title verified via oEmbed) |
| Ben Brophy, *The Eudaimonia Machine* https://www.youtube.com/watch?v=IyRB3SbGnaY (source https://github.com/brenjamin/eudaimonia-machine-video) | a full narrated explainer: layout and pacing |
| TikTok captions template https://github.com/remotion-dev/remotion/tree/main/packages/template-tiktok | word-highlight captions (a different genre: our reference styles never caption narration) |

### 5.4 Motion Canvas / Revideo

| Link | Look at |
|---|---|
| aarthificial (the author), *Could This Asset Be Code?* https://youtu.be/s1ZQnS_tOg0 ; *Smooth Parallax – Pixel Renderer Devlog #2* https://youtu.be/c_3TLN2gHow ; *Deferred Lights – Devlog #1* https://youtu.be/R6vQ9VmMz2w ; sources https://github.com/motion-canvas/examples | code-node diff transitions, diagram typesetting, voice-synced timing |
| Aurailus, *How do Games Load SO MANY Textures?* https://www.youtube.com/watch?v=YTfdBSjitd8 | a third-party technical explainer in Motion Canvas (title verified via oEmbed): layout and text motion |
| LaTeX tween docs https://motion-canvas.io/docs/latex | the equation morph (`tex().tex(...)`) the docs demo |

### 5.5 GSAP text effects

| Link | Look at |
|---|---|
| SplitText docs and demos https://gsap.com/docs/v3/Plugins/SplitText/ (demo collection https://codepen.io/collection/ExBwoK, not opened) | masked line/word reveals, char staggers: the raw vocabulary HyperFrames builds on |

### 5.6 Manim family

| Link | Engine | Look at |
|---|---|---|
| manimgl example clips: `TexTransformExample.mp4` https://cdn.jsdelivr.net/gh/manim-kindergarten/CDN@master/manimgl_assets/example_scenes/TexTransformExample.mp4 and `TextExample.mp4` (same folder) | manimgl | substring morphs with `TransformMatchingStrings`; `t2c` colour maps; source in `example_scenes.py` |
| 3Blue1Brown, *Transformers* https://www.youtube.com/watch?v=wjZofJX0v4M ; *Fourier* https://www.youtube.com/watch?v=spUNpyF58BY | manimgl | label choreography (Transformers); equation morphs (Fourier) |
| Welch Labs, *The Dark Matter of AI* https://www.youtube.com/watch?v=UGO_Ehywuxc | manimgl | description says "Most animations made with Manim: github.com/3b1b/manim"; caps labels, dimming, camera stops |
| Manim CE example gallery https://docs.manim.community/en/stable/examples.html (`#openingmanim`, `#movingframebox`, `#braceannotation`) | Manim CE | the defaults: `Write`, Text → MathTex transform, `SurroundingRectangle`. Plain; a floor, not a target |
| Reducible, *How PNG Works* https://www.youtube.com/watch?v=EFUYNoFRHQI (CE 0.11) ; *A\* Search* https://www.youtube.com/watch?v=88I6IidylGc (CE 0.18.1) | Manim CE | the best-known CE look: labelled grids and graphs, CMU Serif + SF Mono, `Write` + fades |
| manimgx gallery https://manimgx.academa.ai/gallery/ ; quadratic formula https://manimgx.academa.ai/gallery/quadratic-formula/ (GIF https://raw.githubusercontent.com/academa-labs/manimgx/main/docs/content/showcase/quadratic_formula.gif) | manimgx | 48 films, mostly 3D maths, few text-led; the quadratic formula shows `{{ }}` parts, colour-tied terms and matching transforms |
| manimgx same-scene comparison https://manimgx.academa.ai/images/benchmark-quality/manimgx-light.png (also `manim_ce-light.png`, `manimgl-light.png` in the same folder) | all | the vendor's side-by-side of identical scenes: compare text rendering directly |
| Academa backprop lecture (§5.7) | manimgx (likely) | automated output at lecture length |

### 5.7 Newer systems (from §6)

Claude Motion launch segment https://www.youtube.com/watch?v=en0GuyhieQk (0:39–1:15);
explainroo circle area https://www.explainroo.com/videos/why-a-circles-area-is-pi-r-squared/ ;
Academa backprop lecture https://academa.ai/lectures/backpropagation-is-the-chain-rule-on-a-graph ;
ManimGX skill sample https://github.com/manoletre/explainer-video/releases/download/v0.1.0/DataStructures.mp4 .

## 6. Newer explainer-generation systems (beyond agentic-systems.md)

Scope: systems released 2025-06 to 2026-11 that [agentic-systems.md](agentic-systems.md) does not
cover, judged only on frame polish (typography, text motion, layout, math). Found by a
sub-agent that watched the examples or pulled frames where an MP4 was available (frames in
`research_cache/motion/systems/`). I re-checked the repo facts with `gh api` and the Claude
Motion launch page myself.

**Verdict.** Nothing beats a well-made 3b1b or Welch frame on math (typeset equations,
term-by-term morphs, symbols colour-linked to the figure). On non-math typography, text motion
and layout, the browser-rendered systems look clearly better than default Manim CE: real fonts
and kerning, serif/sans pairing, springs, motion blur, grid layouts [inferred: frames compared
by the sub-agent]. None of them morphs equations.

| System | What / engine | Date, licence | Look (from frames) | Example |
|---|---|---|---|---|
| **Claude Motion** (Anthropic) | claude.ai artifact type; Claude writes HTML/CSS/JS scenes that "animate your text, charts, shapes, and images"; exports MP4; no video-generation model | beta 2026-10-08, Team and Enterprise only [verified: claude.com launch article] | Strongest typography and layout found: editorial serif titles, heavy rounded display sans, curved-path text, generous margins, animated charts. No math in any example | launch video https://www.youtube.com/watch?v=en0GuyhieQk (Motion segment 0:39–1:15); review https://www.youtube.com/watch?v=hbPvZvpu9KU |
| **explainroo** (`vincentsch/explainroo`) | agent writes `script.md` + `scenes.js`; headless-Chrome canvas with Rough.js, Lucide icons, **MathJax**; Kokoro TTS + Whisper word times; camera pushes to what the voice names; spring arrivals; motion blur; layout check for clipped/overlapping text | MIT, created 2026-09-25, 1,387★ [verified: gh api] | Chalkboard theme, crisp colour-coded MathJax (A = πr², boxed result), labels typed letter by letter; but a heading on every beat (slide-like) and small diagrams in large empty frames. About a good Manim CE video | https://www.explainroo.com/videos/why-a-circles-area-is-pi-r-squared/ ; gallery https://www.explainroo.com/videos/ |
| **Academa** lectures + Academa Studio | "Ask for something technical. Get a lecture video made for you in ~25 minutes"; Studio is an "AI-native Manim editor"; likely the ManimGX company [inferred: shared academa domain] | 2026 | Navy background, Computer Modern titles and LaTeX; sparse layouts, tiny graph nodes, oversized arrowheads, one glyph bug in a partial derivative. Clearly below 3b1b | https://academa.ai/lectures/backpropagation-is-the-chain-rule-on-a-graph |
| `manoletre/explainer-video` | ManimGX agent skill, Typst math | MIT, 2026-10-23, 6★ [verified: gh api] | Tidy sans, pill boxes, lots of dead space: useful as a sample of ManimGX's default look | https://github.com/manoletre/explainer-video/releases/download/v0.1.0/DataStructures.mp4 |
| OpenMontage | agentic studio: generative video (Veo, Kling) + Remotion + HyperFrames; Manim CE as one tool | AGPL-3.0, 2026-03-29, 82k★ [verified: gh api] | Showcase is cinematic trailers; not aimed at math explainers | https://github.com/OpenMontageInc/OpenMontage |
| Hera, Higgsfield Vibe Motion / AI Motion Designer | commercial AI motion-graphics tools (ads, launches; Higgsfield builds After Effects layers) | 2026 | Polished ad typography, no explainer or math examples verified | https://hera.video |
| bang-motion, iArt `motion-skills` / `explainer-video-skills` | agent skills, one HTML file per film | MIT / 2026 | Generic SaaS look (blurred colour blobs, rounded type, chips) or static stills only | https://github.com/bangtutorial/bang-motion |

**Claude Motion is available on Ben's account**: the artifact-type listing for this account
includes a core "Motion" type ("animated from a prompt … written by Claude as code … export MP4")
[verified: Artifact type listing, 2026-11-21]. It is a hosted player, not an engine our skill can
drive, and it has no math, but it is a cheap way to see one beat of ours rendered with web
typography before committing to a browser engine [inferred].

**A useful negative result.** A third-party test (agentskillshub, 2026-10-11) had 16 video skills
plus Claude Code with no skill make the same 15 s promo; 6 of 16 looked like the no-skill
default, mostly centred white sans over teal waves. HyperFrames and motion-video-kit produced the
most editorial layouts [verified by the sub-agent: repo README and opening-frame sheet
https://agentskillshub.top/best-runs/video/films.jpg]. Without a forced style brief, agent-made
video converges on one web-default look. That supports style packs with hard numbers (§3.8).

**Watch first:** Claude Motion's launch segment (typography bar), explainroo's circle-area video
(the only browser renderer seen with real math and word-synced camera), Academa's backprop
lecture (where automated ManimGX lands at lecture length, flaws included).

**Possibly stale doc, not edited:** Google's NotebookLM video help page now says "Gemini
Notebook" and lists Cinematic, Explainer and Short formats [verified by the sub-agent:
support.google.com/gemininotebook/answer/16454555]; agentic-systems.md still lists the older
format names. Flagging for Ben rather than editing.

## 7. Sources

**Local, measured** (all under `research_cache/motion/`, gitignored)

- Baseline: `baseline/` (19 frames + strip of `mn-07-nernst.mp4`), `demos/mn-07-nernst/out/timeline.json`,
  `demos/mn-07-nernst/scenes/nernst.py`, `skills/manim-explain/assets/style.py`,
  `vendor/manim/manim/mobject/text/text_mobject.py`.
- Clips (video files deleted after analysis, per the research README; frame strips kept in `frames/`): `dl/3b1b_v4/` (HZGCoVF3YvM
  6:30–7:45), `dl/3b1b_v8/` (l6DKRf-fAAM 14:10–15:50), `dl/welch_f/` (2hcsmtkSzIw 12:05–12:45),
  `dl/kurz/` (PqtggjVAi8M 0:52–1:22, 2:44–3:04), `dl/ver7_*.mp4` (cut from the cached
  `research_cache/veritasium/video/uXuQF_PPg5U.mp4`).
- Motion detector: `scripts/motion_segments.py` (320×180 greyscale, mean absolute frame
  difference > 0.1–0.15 grey levels, gaps < 0.2 s merged).
- Code: `research_cache/3b1b/repos/videos` (3b1b/videos at `31f8ffe`, 2024–26 folders),
  `research_cache/3b1b/repos/manim` (manimgl: `animation/creation.py`, `transform_matching_parts.py`,
  `animation.py`, `indication.py`, `utils/rate_functions.py`), `src/reducible`
  (nipunramk/Reducible at `88f4f8f`, 2022 folder), `vendor/manim` (Manim CE 0.21.0 fork:
  `animation/creation.py`, `utils/rate_functions.py`).

**Motion design and reading time**

- Material 3 motion tokens: https://github.com/material-components/material-components-android/blob/master/docs/theming/Motion.md
- IBM Carbon motion: https://carbondesignsystem.com/elements/motion/overview/
- Apple HIG, Motion (JSON of the page): https://developer.apple.com/design/human-interface-guidelines/motion
- EBU R95 v1.1, *Safe areas for 16:9 television production* (2017): https://tech.ebu.ch/docs/r/r095.pdf
- Netflix English (USA) Timed Text Style Guide: https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide
- Netflix subtitle timing guidelines: https://partnerhelp.netflixstudios.com/hc/en-us/articles/360051554394-Timed-Text-Style-Guide-Subtitle-Timing-Guidelines
- SSW rule, enough time to read text: https://www.ssw.com.au/rules/post-production-do-you-give-enough-time-to-read-texts-in-your-videos
- Text animation for readability (weak, practitioner): https://cursa.app/en/page/text-animation-for-readability-kinetic-type-without-overcomplication
- Ofcom/BBC 160–180 wpm (secondary only): https://clevercast.com/bbc-subtitling-guidelines
- HyperFrames motion rules: https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/motion.md
  and `SKILL.md`, `story.md`, `format.md`, `review.md`, `runtimes.md` in the same folder

**Browser engines** (verified by the sub-agent; raw copies in `browser_engines/`)

- HyperFrames: https://github.com/heygen-com/hyperframes , https://hyperframes.heygen.com/examples ,
  https://hyperframes.heygen.com/showcase , https://github.com/heygen-com/hyperframes-launches ,
  https://www.heygen.com/research/html-to-video
- GSAP: https://gsap.com/community/standard-license/ , https://gsap.com/docs/v3/Plugins/SplitText/ ,
  https://gsap.com/blog/3-13/ , https://gsap.com/docs/v3/Plugins/MorphSVGPlugin/ ,
  https://gsap.com/docs/v3/Eases/ , https://gsap.com/docs/v3/Eases/CustomEase/ , https://github.com/greensock/GSAP
- Remotion: https://www.remotion.dev/docs/spring , /docs/interpolate , /docs/easing ,
  /docs/layout-utils/ , /docs/captions/api , /docs/transitions , /docs/paths/interpolate-path ,
  /docs/license/pricing , /docs/performance , /docs/ai/skills , https://github.com/remotion-dev/skills ,
  https://github.com/remotion-dev/remotion/releases
- Motion Canvas: https://github.com/motion-canvas/motion-canvas , https://motion-canvas.io/docs/latex ,
  /docs/code , /docs/layouts , /docs/tweening , /docs/rendering , https://github.com/canvas-commons/canvas-commons
- Revideo: https://github.com/midrender/revideo
- Rive: https://rive.app/docs/editor/text/text-runs , /editor/text/text-modifiers , /runtimes/data-binding ,
  /editor/exporting/exporting-for-video-and-static-design ; Remotion Rive/Lottie: https://www.remotion.dev/docs/rive , /docs/lottie/lottie
- Lottie: https://github.com/airbnb/lottie-web/wiki/Text , https://github.com/LottieFiles/dotlottie-web
- KaTeX / MathJax per-term classes: https://katex.org/docs/supported.html , https://docs.mathjax.org/en/latest/input/tex/extensions/html.html

**Newer systems** (§6): https://claude.com/resources/articles/dashboards-and-motion ,
https://support.claude.com/en/articles/17454997-get-started-with-claude-motion ,
https://github.com/vincentsch/explainroo , https://www.explainroo.com/videos/ , https://academa.ai ,
https://studio.academa.ai , https://github.com/manoletre/explainer-video , https://github.com/OpenMontageInc/OpenMontage ,
https://hera.video , https://github.com/bangtutorial/bang-motion , https://github.com/zhuyansen/awesome-claude-video-skills ,
https://agentskillshub.top/best-runs/video/films.jpg , https://support.google.com/gemininotebook/answer/16454555

**Manim family** (verified by the sub-agent; local copies in `manim_family/`)

- Source: `manim_family/manimgx_git/` (academa-labs/manimgx `1fb4dd7`), `manim_family/manimgl_master_raw/`
  (3b1b/manim master `fafa083`), `manim_family/manimgl_src/` (1.7.2 wheel),
  `manim_family/manimpango_raw/cmanimpango.pyx` (v0.7.1); `vendor/manim/` with its `pyproject.toml`,
  `uv.lock` and `docs/source/changelog/0.21.0-changelog.md`.
- Issues: https://github.com/ManimCommunity/manim/issues/2844 , https://github.com/ManimCommunity/manim/issues/4690 ,
  https://github.com/ManimCommunity/ManimPango/issues/130 , https://github.com/academa-labs/manimgx/issues/33 ,
  /37 , /60 , /74 , /91
- Releases: https://github.com/ManimCommunity/ManimPango/releases (v0.7.0, 2026-10-01, PR #131),
  https://github.com/ManimCommunity/manim/releases (v0.21.0, v0.22.0, v0.22.1),
  https://pypi.org/pypi/manimgl/json , https://pypi.org/pypi/manimgx/json ,
  https://api.github.com/repos/3b1b/manim/compare/v1.7.2...master
- manimgx docs: https://github.com/academa-labs/manimgx (README, `benchmarks/README.md`,
  `docs/content/user-guide/{text-and-math,rendering,coming-from-manim-ce}.md`), https://manimgx.academa.ai/gallery/
- Showcase lists: https://github.com/ManimCommunity/awesome-manim , https://github.com/stephencwelch/manim_videos ,
  https://3b1b.github.io/manim/getting_started/example_scenes.html
