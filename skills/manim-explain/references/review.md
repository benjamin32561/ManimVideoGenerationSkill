# Render, review, deliver

## Render

`scripts/render.py demos/<series>/<slug>` runs only after `plan_check.py` passed for the
current plan.

- Each beat's clip is a frame range of the same scene, rendered by its own worker.
- **Workers draw on the CPU** (manimgx's bundled lavapipe): `--workers 8` at a time with
  `--threads 8` cores each by default. The GPUs belong to other people's jobs. Name GPUs
  (`--gpus 2,3`) only when the user says you may.
- A worker checks where it landed: a CPU worker that finds a GPU, or a GPU worker that finds
  the CPU, fails.
- **Only changed beats are rendered.** Each beat has a digest of everything its frames depend
  on (`explain/windows.py`). A beat whose clip already has that digest is reused, and a new clip
  must come back with the digest the plan check predicted.
- Clips are checked frame by frame, then joined without re-encoding, and the narration is
  added.

The output is `out/video.mp4`, plus `out/render.json` with timings, the device, and the beats
rendered this time.

## Check the render

`scripts/check_render.py demos/<series>/<slug>`:

1. **Frame count:** the video has exactly as many frames as the narration needs.
2. **Sync.**
   - Every event's picture must start changing within the style's sync window after its first
     word, never before it (3b1b 0–0.25 s, Welch 0–0.6 s, plus the start offset).
   - Each frame is compared with the frame just before the event, so slow eased entrances
     count from their first visible change.
   - An event whose change is too subtle to measure (a faint tint, a thin glyph) is a warning.
     Look at it.
3. **Review frames.**
   - `out/review/` gets the settled frame after every event and the middle of every hold
     longer than 4 s.
   - `out/review/sheet_NN.png` tiles them 3 × 3, each captioned with its time, event and
     anchor phrase.
4. **Only changed events are redone.** An event whose window, and the window before it, are
   unchanged since the last check keeps its measurement and its frames. The summary lists the
   sheets with new frames.

## The frame review (the gate)

The checks see geometry and timing. They cannot see meaning. Read every sheet on the first
pass, and after a fix the sheets with new frames. Open the full frame for anything you are
unsure of. Judge each frame twice:

1. **Is anything clipped, covered, unreadable, or left over** from an earlier idea?
2. **Does the picture say what the voice says at that moment?** Check that the noun spoken is
   the thing shown, the emphasis is on it, and the formula matches the words.
3. **Does the frame advance the logic**, rather than showing an unmotivated formula or a wall
   of numbers? If a beat is mostly text or tables while explaining a mechanism, redesign the
   visual around the anchor diagram or thought experiment.

Fix problems in the plan (or the script), then re-run plan check → render → check. When a
whole pass is clean:

```bash
python scripts/review.py record demos/<series>/<slug> --notes "what you checked, what you fixed"
python scripts/review.py deliver demos/<series>/<slug>
```

- `record` needs a passing, current render check, and binds the review to that exact video
  file.
- `deliver` copies it to `output_videos/<series>/<slug>.mp4`, and refuses if the plan or the
  video changed after the review.

## Optional checkpoint (decision 13)

Off by default. When the user asks to see the direction first, stop after the first render
check. Send the script and `out/review/sheet_01.png`, wait for their answer, then continue.
