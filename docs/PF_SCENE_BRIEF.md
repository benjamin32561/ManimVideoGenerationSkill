# Brief for writing one Philosophical Foundations scene module

You are writing **one** Manim scene for one video of a thirteen-video series.
The script and the narration audio already exist and are **frozen** — you are
animating against real word timestamps that were measured from the recorded
voice. Do not edit `script.yaml`, `timing.json`, or anything in `audio/`.

Read first:

1. `demos/<slug>/script.yaml` — the beats. Every `show:` note is your spec.
2. `demos/<slug>/timing.json` — the real cue times. `bookmarks` maps cue word →
   seconds. **Print this sorted by time before you write anything**; it is the
   skeleton of your `construct`.
3. `skills/manim-explain/references/craft-laws.md` — non-negotiable.
4. `demos/<slug>/utils/mind.py` — the shared vocabulary. **Use it.** Do not
   reinvent a position card, a relation arrow, a price chip, a room, a Marr
   stack, or a Fodor sandwich. The series must look like one argument.
5. `demos/thermal-tnr/scenes/tnr.py` — a complete, audited reference scene in
   exactly the style expected. Copy its structure (attach, watch_layout,
   LayoutBoard, wait_until_end).
6. `docs/PF_SERIES_SPINE.md` § Visual vocabulary — roles and primitives.

Video 01 **creates** `utils/mind.py`. Later videos **copy** that file, the same
way CE copied `cpu.py`.

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

Import order for new files: path → blank → python-native → blank → third party
→ blank → current project. Detailed function docstrings (Args/Returns).

## The five bugs that will bite you

Every one of these was found by reading pixels on a previous series, after the
mechanical audits reported clean. They are not hypothetical.

1. **Never `set_opacity` a group that mixes a filled body with an outline.** It
   drives the outline's *fill* opacity up, so a `SurroundingRectangle` becomes a
   coloured pane painted over the data it framed. Use `mind.dim_group(grp, 0.5)`.
   Dim to ~0.5, never near zero — dimming is not deletion.
2. **Bind every emphasis ring.** `Indicate(ring_around(x), ...)` builds a
   rectangle inline, adds it to the scene, and no later `FadeOut` can reach it —
   it rides the rest of the video and lands on whatever comes next. Assign it a
   name, `Create` it, `FadeOut` it.
3. **Dispose of every figure at its section boundary, explicitly**, including
   the diagram from the *first* beat. A mobject you stop thinking about does not
   stop being on screen. FadeOut + `set_opacity(0)` + `self.remove` for riders.
4. **Emphasize the frame, not the group.** `Indicate` on a `VGroup(frame,label)`
   recolours the label into its own fill. Pulse `grp[0]` only.
5. **A label must die or change with its referent.** If the picture snaps back,
   the caption must too, or it contradicts the frame.

## Layout

`LayoutBoard.assert_clear()` raises and aborts the render on overlap, which is
the point — it is cheaper than a re-render. Reserved bands (y): title
`3.05..3.95`, key `2.25..2.95`, panel label `1.70..2.10`, bottom `-3.55..-2.75`.
`assert_clear` pad: leave **0.25**. Register **every text mobject** with
`board.add(mob, "name")` and `board.clear` it when it goes. Call
`board.assert_clear()` after each play that adds text.

Keep persistent chips (price chips, unpaid-bill stack) in the bottom band, not
floating just above it.

## Spoken numerals are a contract

Any number the narration says must be computed in the module from the same
constant that drives the drawing, and asserted at import. Video 01 speaks
**thirteen** steps — that count is `N_VIDEOS` in the scene, not a magic 13 in
a `Text`. The script's header comment lists which numerals it spoke. Honour
all of them.

## You own this video end to end

Do not hand back until `output_videos/philosophical-foundations/<slug>.mp4`
exists. The inner loop is **not** `-ql`. Use `finish_video.sh` then
`deliver_video.sh`.

```bash
source skills/manim-explain/scripts/env.sh
export PYTHONPATH="$MANIM_EXPLAIN_ROOT/scripts:$PWD/demos/<slug>:$PYTHONPATH"

python "$MANIM_EXPLAIN_ROOT/scripts/check_names.py" demos/<slug>/scenes/<file>.py
python "$MANIM_EXPLAIN_ROOT/scripts/find_leftovers.py" demos/<slug>/scenes/<file>.py

# WHOLE scene, no movie. Never -n 0,1. Never --dry_run.
python "$MANIM_EXPLAIN_ROOT/scripts/geometry_pass.py" \
    demos/<slug> scenes/<file>.py <SceneClass>

python "$MANIM_EXPLAIN_ROOT/scripts/check_sync.py" demos/<slug>
python "$MANIM_EXPLAIN_ROOT/scripts/check_layout.py" demos/<slug> --min-duration 1.0
```

Or: `./scripts/finish_video.sh <slug> <file.py> <Class> /tmp/<slug>_finish`

Read `demos/<slug>/out/keyframes/` (contact sheet + full frames). Then:

```bash
python "$MANIM_EXPLAIN_ROOT/scripts/review_gate.py" demos/<slug> \
    --record pass --frames N --notes '...'
./scripts/deliver_video.sh <slug> <file.py> <Class> /tmp/<slug>_deliver
```

`deliver_video.sh` is gated: it refuses `-qm` unless the review is recorded
against the current scene mtime. If the IDE touches the scene file after
review, the gate reopens — re-geometry and re-record.

Confirm delivery:

```bash
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type \
  -of default=noprint_wrappers=1 \
  "$(python3 skills/manim-explain/scripts/skill_paths.py demos/<slug>)"
```

### Rules while you work

- One geometry pass per slug at a time (`finish_video.sh` lock). One `-qm` of
  a given slug at a time. Two concurrent `-qm` of the **same** video is forbidden.
- The machine is shared. Load 40–60 is normal. Do not kill other people's
  processes.
- Morph, do not respawn. The picture is the argument: two cards and a labelled
  relation, not wallpaper quotes.
- Report: slug, scene class, line count, both audit results, what the pixel
  pass changed, the delivered MP4 path and its duration, and any deviation
  from the `show:` notes.
