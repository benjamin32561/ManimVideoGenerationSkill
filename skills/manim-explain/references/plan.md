# The plan: what is on screen, where, and when it changes

After the narration is voiced, turn each beat's `show:` into the video's plan:

- `plan/layout.json`: every object, placed in canvas pixels;
- `plan/events.yaml`: actions bound to the phrases that describe them.

The runtime builds and plays exactly this. Nothing is placed freehand by code, and nothing
moves between events.

## Coordinates

The canvas is 1920 × 1080 (the style's `canvas`), origin top-left, y downward. Sizes are px:
text sizes are CSS font sizes (the em), strokes are widths. Keep content inside the 5% safe
margin (96 px left and right, 54 px top and bottom).

## `plan/layout.json`

```json
{"objects": {"<id>": {"type": "...", ...}},
 "groups":  {"<name>": ["<id or part id or group>", ...]},
 "paths":   {"<name>": {"<object id>": [[x, y], [x, y], ...]}}}
```

Every object takes `z` (draw order; higher on top). Colours are palette tokens from the style.

| Type | Fields | Notes |
|---|---|---|
| `text` | `content`, `x`, `y`, `size`, `color`; `anchor` (`center` \| `left` \| `right`), `role`, `family`, `weight`, `slant`, `backstroke`, `inside`, `allow_overlap` | `y` is the vertical centre. `size` is px or a style role (`label`, `title`...). The role sets the word budget, and Welch roles need capitals. |
| `math` | `tex` or `parts`, `x`, `y`, `size`, `color`; `anchor`, `backstroke` | `parts`: `[{"id": "eq_num", "tex": "...", "color": "yellow"}, {"tex": "\\frac{"}, ...]`. Each named part is its own leaf: write it, copy into it, colour it separately. Unnamed parts are glue. A fraction's bar belongs to its closing `}` piece. |
| `circle` | `cx`, `cy`, `r`, `fill`; `fill_opacity`, `stroke`, `stroke_width` | |
| `rect` | `x0`, `y0`, `x1`, `y1`; `fill`, `fill_opacity`, `stroke`, `stroke_width`, `corner_radius`, `backdrop` | `backdrop: true` for large tints that text may sit on. |
| `line` | `points`, `stroke`, `stroke_width`; `dash: [on, off]`, `stroke_opacity` | Two or more points. |
| `arrow` | `points: [tail, head]`, `stroke`, `stroke_width`; `tip_length`, `fraction` | `fraction` draws part of the full length from the tail (grow it later with `change`). |
| `polygon` | `points`, `fill`; `fill_opacity`, `stroke`, `stroke_width` | |
| `symbol` | `glyph` (`+` \| `−` \| `×` \| `=`), `x`, `y`, `size`, `color`; `stroke_width` | a sign drawn as strokes (charges, operators on their own); `size` is its width in px |
| `box` | `around`, `padding`, `stroke`, `stroke_width`; `corner_radius` | An outline around another object, built after it. |
| `brace` | `around`, `side` (`down` \| `up` \| `left` \| `right`), `color` | |
| `component` | `name` + the component's fields | A style component (see the style's `STYLE.md`) or `custom:<name>` from the video's `custom.py`. Mark `text_like: true` if it is mostly text. |

**Placement rules:**

- **Every text has a home.** 3b1b attaches labels next to their object. Welch gives every
  kind of text a fixed slot (title top centre, caption under the object, dims lower right,
  footnotes bottom right, legend bottom left).
- **Labels are short:** the style's `max_words` per role (3b1b labels 3, Welch 4).
- **Lone signs are `symbol` objects.** A `+`, `−`, `×` or `=` set as text is a hairline at
  any label size; the plan check rejects it.
- **One primary figure, large.** Fill the frame with the idea, not with empty space.
- **One colour per concept** across the figure, its labels and every formula part.
- **Backstroke only over busy content**: it draws a dark halo on coloured fills.

## `plan/events.yaml`

```yaml
events:
  - id: e07_flow
    anchor: "keep flowing out until both sides are equal"   # a phrase from audio/words.json
    do:
      - {action: move, targets: [ions_flowing], along: flow_paths, lag: 0.12}
      - {action: change, targets: [bar_in], to: {y0: 270}}
```

- **Anchors are phrases from the transcript.** Read `audio/words.json` and copy the words.
  Numbers match in words or digits. Anchors are matched in order, so a repeated phrase binds
  to its next occurrence.
- **Timing (decision 18):**
  - an event starts `motion.start_offset` after its anchor's first word;
  - each action runs for the time the style gives it, stretched toward the phrase's length;
  - nothing runs past the next event;
  - between events the frame holds still.
- **One object, one action per event.** Two animations of the same object in one event fight
  over it; the plan check rejects it. The one exception is `recolor` followed by `dim`.

| Action | Fields | Does |
|---|---|---|
| `draw` | `targets`; `lag` | strokes draw on; filled shapes draw their border, then fill |
| `write` | `targets` | text and math write on (in Welch, caps text types on letter by letter) |
| `grow` | `targets`; `from` (`center` \| `tail` \| `bottom` \| `top` \| `left` \| `right`), `lag` | grow in; `tail` grows from the first of the object's `points` (arrows, lines, arrow components) |
| `fade_in` | `targets`; `shift: [dx, dy]` px, `lag` | fade in, sliding by `shift` |
| `fade_out` | `targets` | short exit |
| `move` | `targets` + `to: [x, y]` or `along: <path>`; `lag`, `arc` | move to a point (the targets' joint centre) or along waypoints |
| `change` | `targets`, `to: {field: value}` | the object takes new layout fields (bar edges, arrow `fraction`, points, text...); it keeps its dim level and recolour |
| `recolor` | `targets`, `color` | take a palette colour (kept through later dims and changes) |
| `dim` | `targets`, `opacity` | opacity × own; a dim never brightens |
| `restore` | `targets` | back to own opacity |
| `flash` | `targets`, `color` | soft highlight behind, up and down (banned in Welch) |
| `copy_to` | `source`, `target`; `arc` | a copy flies into the target: glyph by glyph when the content matches, a cross-fade otherwise |
| `morph` | `source`, `target` | the source becomes the target in place; matching parts move |

Every action also takes `delay` (seconds after the event start).

**Before you write an event:**

- A target must enter (`draw`, `write`, `grow`, `fade_in`, `copy_to` or `morph` target)
  before anything else acts on it. It leaves by `fade_out` or as a `morph` source.
- **Route flights.** A copy flying straight across other labels is a defect: give it an `arc`
  (radians, ±0.8–1.4) or a `delay`.
- **Stagger crowds.** Objects squeezing through a gap together collide. Order the group and
  set `lag`.
- **Equations build on screen.** Write a part as the voice names it, and `copy_to` terms out
  of the figure into the formula. Never drop a finished formula in one go unless it is a
  one-symbol label.

## Plan checks

`scripts/plan_check.py demos/<series>/<slug>` first insists that the narration was voiced
from the current `say` text and voice (`audio/voice.json`). It then:

- resolves the anchors, writing `plan/events.json`;
- validates the plan;
- runs the scene without drawing, sampling every object's box at every frame.

It runs on the CPU. Only windows it has not seen are sampled: a window runs from one event to
the next, and its digest covers everything its frames depend on (what is on screen, the event,
the layout of the objects it touches). The samples of unchanged windows come from
`out/probe/`. An edit that only shapes motion (`arc`, `delay`, `lag`, `shift`, `from`,
`flash`) changes one window; a layout edit changes every window from the object's first use.

Errors block `render.py`.

| Problem | Level |
|---|---|
| invalid layout or events, unknown ids, lifecycle errors, two actions on one object | error |
| text under `min_px`, a lone sign set as text (use `symbol`), over the word budget, Welch labels not in capitals | error |
| `clipped` (outside the canvas), `text_overlap`, `outside_container` (`inside` set) | error |
| `crosses_label`: a moving shape or a copy in flight crosses a text for more than 0.15 s | error (shorter: warning) |
| `outside_safe_area`, `text_on_shape` at rest, `movers_collide` | warning |
| `short_dwell`: an unspoken text leaves before `max(1.5 s, 0.6 s × words)` | warning |
| `texts_enter_together`: two text entrances in one event | warning |
| `inspect`: `manimgx inspect` found problems (see `out/inspect.txt` and `out/inspect.png`) | warning |

Fix errors in the plan, not in code, and re-run until clean. Warnings go to the frame review.
