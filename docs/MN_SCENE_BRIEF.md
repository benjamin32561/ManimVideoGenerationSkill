# Brief for writing one From Molecule to Neuron scene module

You are writing **one** Manim scene for one video of a thirteen-video series.
The script and the narration audio already exist and are **frozen**. Do not
edit `script.yaml`, `timing.json`, or anything in `audio/`.

Read first:

1. `demos/<slug>/script.yaml` — every `show:` note is your spec.
2. `demos/<slug>/timing.json` — print bookmarks sorted by time first.
3. `skills/manim-explain/references/craft-laws.md`
4. `demos/<slug>/utils/cell.py` — **use it.**
5. `demos/thermal-tnr/scenes/tnr.py` — structural reference.
6. `docs/MN_SERIES_SPINE.md` § Visual vocabulary.

Video 01 **creates** `utils/cell.py`. Later videos **copy** that file and
`style.py`.

## Shape

```python
class <CamelSlug>(Scene):
    def construct(self) -> None:
        tn = TimedNarration(DEMO_DIR / "timing.json", DEMO_DIR / "audio" / "narration.mp3")
        tn.attach(self)
        watch_layout(self, DEMO_DIR)
        board = LayoutBoard(pad=0.25)
        title = board.set_title(section_title("..."))
        ...
        tn.wait_until_end()
```

Per beat: `tn.wait_until("<cue>")`, then `self.play(...)`.
`breathe_until(self, tn, "<next cue>", *mobs)` before a long wait.
Helper `_kill` = FadeOut + `set_opacity(0)` + `self.remove`.

## The five bugs

1. Never `set_opacity` a group that mixes fill + outline. Use `cell.dim_group`.
2. Bind every emphasis ring. Never `Indicate(ring_around(x))` inline.
3. Dispose every figure at its section boundary.
4. Pulse `grp[0]` only on a `(frame, label)` card.
5. A label must die or change with its referent.

## Layout

Bands y: title `3.05..3.95`, key `2.25..2.95`, panel `1.70..2.10`,
bottom `-3.55..-2.75`. `assert_clear` pad **0.25**. Register every text
mobject with `board.add`. Park chips in the bottom band.

## Spoken numerals

Computed from the same constant that draws the picture, asserted at import.
`N_VIDEOS = 13`.

## Delivery

```bash
source skills/manim-explain/scripts/env.sh
export PYTHONPATH="$MANIM_EXPLAIN_ROOT/scripts:$PWD/demos/<slug>:$PYTHONPATH"
python "$MANIM_EXPLAIN_ROOT/scripts/check_names.py" demos/<slug>/scenes/<file>.py
python "$MANIM_EXPLAIN_ROOT/scripts/find_leftovers.py" demos/<slug>/scenes/<file>.py
python "$MANIM_EXPLAIN_ROOT/scripts/geometry_pass.py" \
    demos/<slug> scenes/<file>.py <SceneClass>
python "$MANIM_EXPLAIN_ROOT/scripts/check_sync.py" demos/<slug>
python "$MANIM_EXPLAIN_ROOT/scripts/check_layout.py" demos/<slug> --min-duration 1.0
python "$MANIM_EXPLAIN_ROOT/scripts/review_gate.py" demos/<slug> \
    --record pass --frames N --notes '...'
./scripts/deliver_video.sh <slug> <file.py> <Class> /tmp/<slug>_deliver
```

Finished file: `output_videos/molecule-to-neuron/<slug>.mp4`.

One geometry pass per slug at a time. One `-qm` of a given slug at a time.
Do not start `-qm` until review is recorded.
