# The review loop

The centre of this pipeline. Everything before it exists to produce frames worth
looking at; everything after it is just encoding.

```
write scene → geometry pass → LOOK AT THE FRAMES → fix → geometry pass → LOOK AGAIN → … → -qm
                                ↑_________________________________________________|
                          as many rounds as it takes, no budget
```

## Why it cannot be automated

`check_sync` and `check_layout` are mechanical, and they earn their place — they
catch narrated beats the picture ignored, and collisions that happen only mid
motion. But they are blind to the two questions that decide whether a video is
any good:

1. **Is anything obscured, clipped, invisible, or left over?**
2. **Does this frame say what the narration says over it?**

Both are judgements about a picture. Every defect that survived to a delivered
video in this project passed both audits and was visible the instant someone
looked at the frame. So the loop is: walk geometry, *look*, fix, look again.

## Doing a pass

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/qa_frames.py" demos/<slug>
```

Read the sheet off the **keyframes the geometry pass already captured**.
Composition, occlusion, invisible text and mislabelled figures are all legible
at that size, and catching them there saves the delivery encode. Then open full
frames for every beat you are not certain about — a sheet thumbnail is enough
to raise a doubt, never enough to settle one. To inspect one named instant
without a new auto-still walk:

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/render_stills.py" \
      demos/<slug> scenes/<file>.py <SceneClass> --t 367.8
```

For each frame, against the beat's `say:` line:

- **Occlusion** — anything on top of anything else; a label over a wire; a
  persistent chip drifted into a band it does not own.
- **Legibility** — text large enough at 480p, and actually a visible colour.
  A helper reading `.get_color()` off a `Text` gets black, and black on black
  renders as nothing at all.
- **Leftovers** — a figure from two sections ago still riding along; an
  emphasis ring that no `FadeOut` can reach because it was built inline inside
  `Indicate(...)`.
- **Truth** — the label still describes the picture *after* the morph, the
  register shows the value the voice just said, the arrow points the way the
  narration claims.
- **Frame bounds** — nothing past the safe area; nothing half off-screen.

## The gate

A clean pass gets recorded, and only a record opens `-qm`:

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/review_gate.py" demos/<slug> \
  --record pass --frames 34 --notes "read all 34 cue frames; ..."
```

`deliver_video.sh` runs `review_gate.py --check` first and exits 3 without a
current pass. **Editing the scene after a pass reopens the gate** — a review is
a statement about one specific set of frames, so changing the code that made
them voids it. Re-render, look again, re-record.

Record a `fail` too, with what was wrong. The history in `out/review.json` is
how a later round knows what the last one already caught.

## Division of labour

`finish_video.sh` carries a video from wherever it is to **review-ready** and
stops: logic pass, full `-ql`, both audits, QA stills. It deliberately cannot
deliver. `deliver_video.sh` does the `-qm` and the delivery, behind the gate.
The looking in between is not a stage a script can hold.
