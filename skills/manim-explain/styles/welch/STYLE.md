# Welch Labs style

A measured documentary that works through real mechanisms, one running example, and real
numbers **where they prove a contradiction or land a payoff** — never as a spec-sheet dump.
Numbers in `style.yaml` are measured; the evidence is `docs/research/styles/welch-labs.md`,
`docs/research/narrative-pattern.md`, and `docs/research/intuitive-derivation.md`. Reference
code (MIT) is in `vendor/welch-labs-videos/`: a gitignored clone of
github.com/stephencwelch/manim_videos.

## Flow

- **Open on a real artifact, a historical moment, or a provocation.** State the driving "how
  exactly" or "why" question by about 75 s. A short historical prologue can itself be the
  first unit.
- **One running example from start to end.** A real input through a real mechanism, never an
  abstract x. Every symbol shown on screen is tied to a real object or dimension.
- **1.2–2.5 turns per 10 minutes, mostly walls.** Two deep units fit cleanly in 8–12
  minutes (three units belong in a 12+ minute video). Walls are a cost or a failure ("this
  shortcut comes at a cost"). The fix's cost becomes the next wall: links are causal, never
  jumps.
- **Work before every turn — derive the mechanism before quoting specs.** At least 40% of the
  video is setup, digging and attempts. Explain *why* a failure forces each architectural
  piece (test a plausible repair, state the constraint the fix must satisfy, walk through the
  easier case) before writing a loss formula or quoting a benchmark. Use one sharp contrast
  to prove a wall rather than chaining intermediate byte or arithmetic calculations in prose,
  and voice attempts as "we might expect…" (since "you" stays rare in Welch).
- **Scale up selectively after the logic clicks.** Real measurements are precision
  instruments: in Welch's own videos, spoken numbers average ~18 per 1,000 words (and only
  ~11/1k in his JEPA video, with ~2.5 exact specs/1k). Use a handful of sharp numbers to
  prove the wall and land the climax payoff ("a 57× reduction"), between 35% and 80% of the
  runtime; leave ablation tables, secondary benchmarks and hyperparameter lists in
  `SOURCE_NOTES.md`.
- **End on open questions, a hedged take, and a callback to the opening.**

## Voice

- Documentary "we" (15–75 per 1,000 words); "you" is rare.
- 150–185 wpm.
- Sentences around 20 words.
- Guiding questions sit at turning points and key `"why / what if"` derivation steps (up to
  ~1.5/min).
- Exact numbers earn their seat: keep total spoken numbers under ~35/1k and exact decimals,
  percentages or 3+-digit specs under ~12/1k — save them for the moments that actually prove a
  point.

## Look

- Black background.
- Colour roles:
  - `tan` is line art and body labels;
  - `brown` is axes, ticks, connectors, captions and anything de-emphasised;
  - `yellow` is the one thing to look at;
  - `blue`, `cyan`/`magenta` (signed or paired quantities) and `green` mark entities.
- One colour per entity for the whole video: in every diagram, equation and plot.
- Source Sans 3 (the free stand-in for Myriad Pro; install it to
  `~/.local/share/fonts/source-sans-3`, and rendering fails without it).
  - **Titles and component labels are UPPERCASE**: `weight: BOLD` for titles, `SEMIBOLD`
    for labels.
  - Explanatory phrases are sentence case (`caption` role).
  - Example sentences and quotes use `family: serif` with `slant: ITALIC`.
  - Math is LaTeX.
- **Every kind of text has a fixed slot**, never shared:
  - titles at top centre;
  - captions under or left of their object;
  - dimensions small at the lower right;
  - equations centred under the object;
  - footnotes bottom right, legend bottom left.
- Labels are 1–4 caps words. Text stays off busy areas instead of using a backstroke.
- **Dim, don't delete**: context drops to 0.2–0.5 opacity in place. Sizes stay in a narrow
  band; hierarchy comes from colour and caps, not size.

## Motion

- Caps labels type on letter by letter (`write_mode: letters`, about 11 per second); prose
  fades in over 0.6 s.
- Long smooth moves (1–3 s) do the layout: labels re-park in about 1.4 s.
- Emphasis:
  - `dim` everything else;
  - draw an outline `box` around the focus;
  - add a small yellow `arrow` component for one clause.
- `flash` is banned in this style.
- Numbers update in place with the `number` component (fixed width, right-aligned).
- Changes land per clause (sync window up to 0.6 s), not per syllable.

## Components (`components.py`)

- `arrow`: straight shaft with the notched Welch tip.
- `axes`: brown axes, outward ticks, nice 1-2-5 tick values, notched tips.
- `number`: fixed-width readout (`format_number`); an integer `value` shows as a count, without decimals.
- `heatmap`: cells from a grid of values; diverging cyan–black–magenta, or black-to-yellow.

The storyboard-pixel layer of `world_models/p63_64.py` is what `plan/layout.json` already is:
every object is placed in 1920×1080 pixel coordinates.

## Not reproduced

- Overhead desk shots and hands.
- Talking head and interview clips.
- 3D camera flights (decision 3).
- Real model data (decision 5): use analytic or synthetic values.
