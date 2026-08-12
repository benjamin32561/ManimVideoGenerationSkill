# Layout craft (classic 3b1b)

Distilled from 3brown1blue production rules + Manim CE practice.

## Frame

- Frame ~14.2 × 8. Safe: x∈[-6.5,6.5], y∈[-3.5,3.5]. ~15% margin.
- Regions: title strip / main stage / bottom takeaway. One primary visual region.

## Layout templates (pick one per beat/scene)

- **FULL_CENTER** — equation or single diagram
- **DUAL_PANEL** — before/after, wrong/right, lowσ/highσ
- **BUILD_UP** — accumulate parts; formula grows at bottom
- **TOP_PERSISTENT_BOTTOM_CONTENT** — pipeline header + detail
- **GRID_CARDS** — comparison cards

Prefer `VGroup.arrange` / `arrange_in_grid` / `next_to` over absolute piles.

## Morph, don’t respawn

If on-screen A is *replaced by related* B (same idea, next form of the same object), use **`Transform` / `ReplacementTransform` / height morphs** — never `FadeOut(A)` then `FadeIn(B)`.

Fade-swap only when:
- there is a **long gap** with nothing connecting them, or
- they have **no identity link** (unrelated ideas).

Examples: dogs/cats chips → morph into `class c`; neurons → morph into bars; signed → morph into \(|\mu|\`; single skyline → morph into dual panels.

## Math & text

- **On-screen math:** `MathTex` / `Tex` (LaTeX required).
- **Labels / captions:** `Text` for English phrases; short spoken-phrase captions OK.
- Labels beside / above objects in a **reserved band**, not floating over them. Panel names use a fixed `PANEL_LABEL_Y` so growing bars never collide.
- Key sentences / final questions: live in **KEY_BAND** (or BOTTOM) while a figure
  owns the stage — **never** FadeIn prose at frame center over a live graph/net.
  Center-stage text is only OK after the figure is cleared, shrunk, or shifted away.
- Fade / `ReplacementTransform` bottom notes — never stack two full explanations.
- Prefer in-place morphs over spawning a second full copy.
- **Formula BUILD_UP:** derived equations morph term-by-term (`TransformMatchingTex`
  / staged `ReplacementTransform`) while VO explains each piece — never drop only
  the finished line unless it is a one-symbol label.

## Motion / pacing

- Motion during speech; hold ~0.5–1s after an aha.
- **~0.3s suspense between scenes** — bake into audio (`inter_chunk_silence`), soft-idle on screen.
- **Question moves its referent** — while VO asks about X, animate the mobjects that *are* X
  (`ask_about()` / Indicate / pulse), so the viewer sees what is changing.
- **Procedures are staged** — for any choose / rank / keep / build / compare sequence,
  show each verb as a step (quota → order → cut → lock), never one-shot recolor to the end state.
- **Picture matches the spoken noun** — if VO names a whole system, draw the whole system;
  when VO narrows to a part, focus that part, then morph it forward.
- **Never occlude the primary figure** — questions/captions go to KEY/BOTTOM bands
  (or clear/shift the figure first). `ask_about` / `key_sentence` default to bands,
  not ORIGIN-over-graph.
- Animate meaning changes, not every word.
- Bookmarks at visual-event words only.
- **Named object pops + settle** — when VO names a specific object, that mobject
  pops (Indicate/Flash/scale), then ~0.3s soft-idle before the next idea; nest
  container→member (layer then unit \(j\)).
- **Causal pairs move together** — if VO says A changes with B, animate both sides
  (e.g. inputs cycle *and* the neuron responds).
- Prefer **visual-only re-renders** when VO + timing are already good.

## Classic 3b1b look

- Dark background (Manim default black is fine).
- Semantic colors: gold/yellow = highlight / top-$k$; blue = structure; red sparingly for “wrong.”
- Sparse: empty space is a feature.
- Entity-color binding: one color for a concept across symbol and geometric avatar.

## Quality checklist (before final)

- No overlapping text; nothing past safe bounds
- Title not colliding with main content
- Previous bottom note cleared
- Dense formula readable (font size / split lines)
- Run layout tests: `pytest tests/test_layout.py` (AABB + per-beat snapshots)
- Scene uses `LayoutBoard.assert_clear()` at beat boundaries; reserved bands in `layout_check.py`
- **Pixel QA:** `qa_frames.py --contact-sheet` → read sheet + **every caption-near-figure
  still** (not a sparse cue list) + post-motion frames; verify spoken adjectives
  (spread/piled/…) match on-screen labels; fix figure gutters and text↔graph
  occlusion before shipping

## Persistent chips (counters, quotas, gain badges, readouts)

Long explainers accumulate small status pills. Give each one a **named x slot**
on a shared strip (e.g. just below the chart axis) and place from that constant —
never into a gap that merely looks free at the beat you add it. Two chips that
each fit alone still collide once a later beat makes them co-present.

Snapshot every chip that is alive at a beat, not only the one that beat adds.

## Reserved bands (do not overlap)

| Band | Y range | Owns |
|------|---------|------|
| TITLE | 3.05–3.95 | section titles |
| KEY | 2.25–2.95 | parked / banner key sentences (title must be gone) |
| PANEL_LABEL | 1.70–2.10 | "spread"/"piled" names |
| BOTTOM | −3.55–−2.75 | takeaway captions |

`key_sentence(..., park="left"|"right")` parks only in KEY_BAND — never `to_corner(UL)` into the title.