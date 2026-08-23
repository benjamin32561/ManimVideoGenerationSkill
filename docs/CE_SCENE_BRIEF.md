# Brief for writing one Computer Engineering scene module

You are writing **one** Manim scene for one video of a fifteen-video series.
The script and the narration audio already exist and are **frozen** — you are
animating against real word timestamps that were measured from the recorded
voice. Do not edit `script.yaml`, `timing.json`, or anything in `audio/`.

Read first:

1. `demos/<slug>/script.yaml` — the beats. Every `show:` note is your spec.
2. `demos/<slug>/timing.json` — the real cue times. `bookmarks` maps cue word →
   seconds. **Print this sorted by time before you write anything**; it is the
   skeleton of your `construct`.
3. `skills/manim-explain/references/craft-laws.md` — non-negotiable.
4. `demos/<slug>/utils/cpu.py` — the shared vocabulary. **Use it.** Do not
   reinvent a register file or a bit field; the series must look like one machine.
5. `demos/thermal-tnr/scenes/tnr.py` — a complete, audited reference scene in
   exactly the style expected. Copy its structure.

## Shape

```python
class <CamelSlug>(Scene):
    def construct(self) -> None:
        tn = TimedNarration(DEMO_DIR / "timing.json", DEMO_DIR / "audio" / "narration.mp3")
        tn.attach(self)                 # first
        watch_layout(self, DEMO_DIR)    # second
        board = LayoutBoard()
        title = board.set_title(section_title("..."))
        ...
        tn.wait_until_end()             # last
```

Per beat: `tn.wait_until("<cue>")`, then `self.play(...)` for that cue's motion.
Where the next cue is far away, `breathe_until(self, tn, "<next cue>", *mobs)`
**before** the `wait_until`, or the frame freezes and the audit fails.

## The five bugs that will bite you

Every one of these was found by reading pixels on a previous series, after the
mechanical audits reported clean. They are not hypothetical.

1. **Never `set_opacity` a group that mixes a filled body with an outline.** It
   drives the outline's *fill* opacity up, so a `SurroundingRectangle` becomes a
   coloured pane painted over the data it framed. Use `cpu.dim_group(grp, 0.5)`.
   Dim to ~0.5, never near zero — dimming is not deletion.
2. **Bind every emphasis ring.** `Indicate(ring_around(x), ...)` builds a
   rectangle inline, adds it to the scene, and no later `FadeOut` can reach it —
   it rides the rest of the video and lands on whatever comes next. Assign it a
   name, `Create` it, `FadeOut` it.
3. **Dispose of every figure at its section boundary, explicitly**, including
   the equation or diagram from the *first* beat. A mobject you stop thinking
   about does not stop being on screen.
4. **Emphasize the frame, not the group.** `Indicate` on a `VGroup(frame,label)`
   recolours the label into its own fill. Pulse `grp[0]` only.
5. **A label must die or change with its referent.** If the picture snaps back,
   the caption must too, or it contradicts the frame.

## Layout

`LayoutBoard.assert_clear()` raises and aborts the render on overlap, which is
the point — it is cheaper than a re-render. Reserved bands (y): title
`3.05..3.95`, key `2.25..2.95`, panel label `1.70..2.10`, bottom `-3.55..-2.75`.
Register **every text mobject** with `board.add(mob, "name")` and `board.clear`
it when it goes. Call `board.assert_clear()` after each play that adds text.

Keep persistent chips (a pipeline strip, a running counter) in the bottom band,
not floating just above it — everything else you anchor to the bottom will
collide with them.

## Spoken numerals are a contract

Any number the narration says must be computed in the module from the same
constant that drives the drawing, and asserted at import:

```python
ALPHA = 0.9
assert abs(n_eff(ALPHA) - 19.0) < 1e-9, "VO says nine tenths behaves like nineteen frames"
```

The script's header comment lists which numerals it spoke. Honour all of them.

## You own this video end to end

You are responsible for the finished MP4, not for a scene file. Do not hand
back to the orchestrator until `output_videos/<series>/<slug>.mp4` exists.

### 1. Iterate: build and check, build and check

```bash
source skills/manim-explain/scripts/env.sh
export PYTHONPATH="$MANIM_EXPLAIN_ROOT/scripts:$PWD/demos/<slug>:$PYTHONPATH"
manim -ql --disable_caching demos/<slug>/scenes/<file>.py <SceneClass>
```

Loop until it exits 0. Layout assertions abort the render on purpose — fix them
by moving things, never by removing `assert_clear()`. Then:

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/check_sync.py"   demos/<slug>
python "$MANIM_EXPLAIN_ROOT/scripts/check_layout.py" demos/<slug>
```

`check_sync` must say **every cue window contains motion** with **no still
stretch over 6 s** (fix those with `breathe_until`). `check_layout` must report
**zero overlaps**. Keep looping until both are clean.

### 2. QA the pixels — on the cheap render

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/qa_frames.py" demos/<slug> \
  --video media/videos/<name>/480p15/<SceneClass>.mp4 --from-timeline --contact-sheet
```

**Read the contact sheet, and read full frames for anything suspicious.** Both
audits pass on defects only pixels reveal — a caption painted black on black, a
border filled over the data it framed, a label contradicting the picture. Fix
and re-loop. This step is not optional and it is where the quality comes from.

### 3. Render and deliver — this is yours too

Only once the audits are clean and the frames look right:

```bash
./skills/manim-explain/scripts/render_and_mux.sh \
  demos/<slug>/scenes/<file>.py <SceneClass> -qm --disable_caching
```

That writes `output_videos/<series>/<slug>.mp4` (via `skill_paths.py`). It takes
a while; wait for it. Then confirm the file exists and has audio:

```bash
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type \
  -of default=noprint_wrappers=1 "$(python3 skills/manim-explain/scripts/skill_paths.py demos/<slug>)"
```

If the pixel pass made you change the scene, re-render before reporting.

### Rules while you work

- **Give every `-ql` run its own media dir** so nothing can collide:
  `manim --media_dir demos/<slug>/media/qa -ql --disable_caching ...`
  Different scenes were always independent; this also makes two runs of *your*
  scene safe. `render_and_mux.sh` already does this for the final render.
- **The machine is shared** and two other agents are working. Do not run more
  than one render of your own at a time.
- Report: slug, scene class, line count, both audit results, what the pixel pass
  changed, the delivered MP4 path and its duration, and any deviation from the
  `show:` notes.
