# The build loop

How to get from a frozen script to a delivered MP4 without wasting renders.
Written from a 15-video series; every step here exists because skipping it cost
real time.

## Gate zero: static checks, before any render

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/check_names.py"    demos/<slug>/scenes/<f>.py
python "$MANIM_EXPLAIN_ROOT/scripts/find_leftovers.py" demos/<slug>/scenes/<f>.py
```

`check_names.py` resolves names the way the interpreter will — through the star
import, the explicit imports, the file's own definitions — and checks each call
against its callee's signature. It is the cheapest gate by orders of magnitude
and it found 20 latent crashes in one series that renders were discovering one
per cycle. Run it after every edit; a render is never the right way to find a
typo.

## The four gates, cheapest first

Run them in this order. Each one catches a class of defect the next one cannot,
and each is more expensive than the last.

### 1. Geometry pass — interpolate, don't draw

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/geometry_pass.py" \
      demos/<slug> scenes/<file>.py <SceneClass>
```

This walks the whole of `construct`, samples AABBs ~10 Hz, writes occupancy /
leftovers / overlap intervals, and Cairo-rasterizes only cue, play-end, and
overlap stills. It is the logic gate *and* the QA-stills gate.

**Do not use `--dry_run` for this.** `--dry_run` still Cairo-rasterizes every
frame and only skips FFmpeg, so it costs about as much as `-ql`.

**Do not use `-n 0,1` for this.** It was used as the inner loop here for a long
time on the belief that it "executes every beat"; it does not. Measured, with a
six-animation scene that raises at the end of `construct`:

| command | animations executed | reached end | exit |
|---------|--------------------|-------------|------|
| `-n 0,1` | 0, 1 | no | **0** |
| `--geometry_only` | 0–5 | yes | 1 |

`-n 0,1` stops after the requested range and **exits 0**, so a scene that crashes
on its last beat looks clean.

Check the exit code, not just the log: under load the pass can hit its own
`timeout` and die silently, which looks identical to success through a grep.

### 2. Occupancy and stills — already written by gate 1

`TimedNarration` and `watch_layout` write `out/timeline.json`,
`out/layout_violations.json`, `out/occupancy.json`, and `out/keyframes/`
during the geometry walk. There is no second `-ql` movie for QA.

**Always pass `--media_dir` on a real encode.** Two renders of the same scene
otherwise share `media/videos/<name>/<quality>/partial_movie_files/<Scene>/`.
The geometry pass uses a throwaway media dir and deletes it.

### 3. The mechanical audits — seconds

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/check_sync.py"   demos/<slug>
python "$MANIM_EXPLAIN_ROOT/scripts/check_layout.py" demos/<slug>
```

`check_sync` names the cue that each frozen stretch runs into, which is exactly
the cue to breathe up to:

```
338.33s → 362.93s  (24.6s frozen)  → breathe up to 'workhorse'
```

Fix with `breathe_scene(self, tn, "workhorse")` immediately before that cue's
`wait_until`. It idles the scene's own top-level mobjects, so you do not have to
know what is alive at that instant — which is the part that goes wrong when a
stretch sits several plays deep inside a beat.

`check_sync` must report *every cue window contains motion* and no still stretch
over 6 s. `check_layout` must report zero overlaps.

### 4. Pixels — the only gate that catches the real defects

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/qa_frames.py" demos/<slug>
```

Read the sheet off the **keyframes the geometry pass already captured**.
Composition, occlusion, invisible text and mislabelled figures are all legible
at 480p, and catching them there saves the delivery encode. Then open full
frames for every beat you are not certain about — a sheet thumbnail is enough
to raise a doubt, never enough to settle one.

A collision named by occupancy does not need a new full walk of auto stills.
Rasterize *those* times only:

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/render_stills.py" \
      demos/<slug> scenes/<file>.py <SceneClass> --t 367.8
python "$MANIM_EXPLAIN_ROOT/scripts/render_stills.py" \
      demos/<slug> scenes/<file>.py <SceneClass> --from-violations
```

PNGs land in `out/stills/`. The walk interpolates until the last requested
time and then aborts `construct`, so a still at 10 s of an 8-minute scene does
not replay the other seven minutes. Occupancy / keyframes from the geometry
pass are left alone.

Then read full frames for anything suspicious. Defects that pass gates 1–3 and
only show up here, all observed in production:

- a caption painted black on black, because a helper read `.get_color()` off a
  `Text` (a `VGroup` of glyphs, whose group colour is unset)
- a `SurroundingRectangle` whose *fill* opacity was raised, painting over the
  grid it was framing
- an emphasis ring built inline inside `Indicate(...)`, which is added to the
  scene and can never be faded
- a figure never disposed at its section boundary, riding 150 s of video
- a caption still asserting the opposite of what the picture now shows

## Reading a stalled render

**A render that stops advancing has usually asserted, not hung.** Read the log
tail before blaming load:

```bash
sed 's/\x1b\[[0-9;]*m//g' <log> | grep -E "^  (overlap|oob):" | head -3
```

Layout assertions abort the process, so the last `Animation N` line just sits
there looking like a stall. Two of these were misdiagnosed as contention before
the pattern became obvious.

## Marginal overlaps

`assert_clear()` pads boxes by ~0.08, so figures that look separated by a tenth
of a unit still fail. Both real cases were of the form "label A ends at 3.05,
label B starts at 3.15". Fix by moving one of them a clear distance, not by
shaving the pad. When placing something *between* two existing objects, move
**both** neighbours apart — moving only one leaves the gap on the other side.

## Concurrency

Renders are CPU-bound and mostly single-threaded per process. Aggregate
throughput improves up to roughly three concurrent renders and then flattens: a
single render measured ~62 animations/min, four concurrent dropped to ~13 each.
On a shared machine, check `uptime` first and leave headroom.

Prefer **finishing** videos to advancing all of them. Four renders at 60 % each
delivers nothing; two at 100 % delivers two.

## Cost model

For line-art scenes (schematics, timing diagrams, block diagrams) a `-qm` render
costs roughly **0.9× the video's runtime** — a ten-minute video renders in about
ten minutes, alone on the box. Scenes that re-tint large grids every frame are
far slower; a thermal-imaging series with 140-cell grids ran closer to 8×. Time
your own first render before promising a schedule.

## One lane per video, and clear the frames each run

Two concurrent runs of the same scene share `demos/<slug>/media/qa`. Manim prunes
that directory when it exceeds `max_files_cached`, so the second render deletes
the first's partial files and dies with `FileNotFoundError` — then overwrites the
winner's status. The result is worse than a crash: the frames come from one
render and `out/timeline.json` from the other, so the contact sheet and the audit
describe different videos. `finish_video.sh` now takes a per-slug lock.

`qa_frames.py` only writes a sheet from already-captured stills. The geometry
pass clears `out/keyframes/` at the start of each walk, so a re-run cannot
leave pictures the current code no longer produces.

## Never edit a driver script while instances of it are running

Bash reads a script **incrementally, by byte offset**, so editing a running
`.sh` file makes every live instance jump to the wrong place in the new text.
Editing `finish_video.sh` while four lanes were executing it produced:

- `line 62: skips: command not found` — a comment body executed as a command,
  because the offset landed mid-line
- a lane started at 14:03 suddenly re-running an earlier stage at 14:30
- statuses written by control flow that never legitimately ran

None of it looks like corruption from the outside; it looks like flaky renders.
The file on disk was correct the whole time. If a driver needs changing, stop the
lanes, edit, verify with `bash -n`, then relaunch. Python scripts are safe to edit
mid-run — the interpreter loads them once — but the shell drivers are not.
