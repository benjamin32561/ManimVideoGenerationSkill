# Computer Engineering series — build progress

**Owner: the main session, working directly. No subagents.**
(User instruction, 2026-08-20.)

Videos 1–15 are delivered. Update this file at every state change.

## Pipeline per video

1. **complete** — scene waits on every cue in `timing.json` and calls
   `wait_until_end`
2. **runs** — `geometry_pass.py` exits 0. Layout assertions abort the walk, so
   this is a real gate, not a formality. No movie is encoded.
3. **audits** — `check_sync`: every cue window contains motion, no still stretch
   over 6 s. `check_layout`: zero lingering text-over-text. Occupancy leftovers
   are a checklist, not a verdict.
4. **pixels** — contact sheet read off `out/keyframes/`; full frames read for
   anything suspicious.
5. **delivered** — `output_videos/computer-engineering/<slug>.mp4` exists and has an audio stream.

## Status

| # | slug | narration | scene | state | notes |
|---|------|-----------|-------|-------|-------|
| 01 | ce-01-sequential-machines | 10:47 | 2377 | **delivered** |  |
| 02 | ce-02-programmable-computer | 6:58 | 1768 | **delivered** |  |
| 03 | ce-03-memory-devices | 8:49 | 2832 | **delivered** |  |
| 04 | ce-04-memory-hierarchy | 9:08 | 2160 | **delivered** |  |
| 05 | ce-05-virtual-memory | 8:58 | 1978 | **delivered** |  |
| 06 | ce-06-pipelines | 9:29 | 3005 | **delivered** |  |
| 07 | ce-07-out-of-order | 10:41 | 2663 | **delivered** |  |
| 08 | ce-08-interrupts-privilege | 9:48 | 2928 | **delivered** | 36 MB, 9:48, aac |
| 09 | ce-09-kernel-processes | 9:57 | 2544 | **delivered + reviewed** | 60 frames read, gate recorded |
| 10 | ce-10-scheduler | 15:12 | 3729 | **delivered** | 49 MB, 15:12, aac. irq riders and wait-bar buries fixed; review 62 frames. Geometry ~8.5 min; -qm ~97 min on a loaded box. |
| 11 | ce-11-synchronization | 7:50 | 2478 | **delivered** | 26 MB, 7:52, aac. Review already recorded. |
| 12 | ce-12-cache-coherence | 9:48 | 2224 | **delivered** | 27 MB, 9:49, aac. Review 52 frames. -qm ~2h10 on a loaded box. |
| 13 | ce-13-memory-consistency | 8:37 | 1292 | **delivered** | 25 MB, 8:38, aac. Re-encoded after acquire-band layout fix. |
| 14 | ce-14-multiprocessor-scheduling | 8:02 | 2515 | **delivered** | 29 MB, 8:02, aac. Encode finished 02:02. One 1s 6% ring graze accepted at review. |
| 15 | ce-15-dispatch-qos | 9:10 | 2428 | **delivered** | 26 MB, 9:11, aac. Deques/bound/not_this disposed; work tiles parked above worker labels. Review 48 frames. |

## Standing reminders — do not rediscover these

- `source skills/manim-explain/scripts/env.sh` first. Stay in the repo root; a
  stray `cd` into a demo folder broke `$MANIM_EXPLAIN_ROOT` paths once.
- Static gate first, it costs a second:
  `python $MANIM_EXPLAIN_ROOT/scripts/check_names.py demos/<slug>/scenes/<f>.py`
- Logic gate: `python $MANIM_EXPLAIN_ROOT/scripts/geometry_pass.py demos/<slug> scenes/<f>.py <Class>`
  — the WHOLE scene, no movie. **Never `-n 0,1`**: measured, it stops after
  animation 1 and exits 0. **Never `--dry_run`**: it still Cairo-rasterizes
  every frame.
- Geometry pass (inner loop):
  `python $MANIM_EXPLAIN_ROOT/scripts/geometry_pass.py demos/<slug> scenes/<f>.py <Class>`
- Deliver:
  `./skills/manim-explain/scripts/render_and_mux.sh demos/<slug>/scenes/<f>.py <Class> -qm --disable_caching`
  It uses a per-invocation media dir (so concurrent renders cannot collide) and
  writes `output_videos/computer-engineering/<slug>.mp4`.
- `script.yaml`, `timing.json` and `audio/` are **frozen**. Animate against the
  cue times that exist; never reshape the narration to suit the code.
- Five defects that pass both mechanical audits and only pixels catch:
  1. `set_opacity` on a group mixing a filled body with an outline — the outline's
     fill paints over the data. Use `cpu.dim_group`.
  2. A ring built inline inside `Indicate(...)` — it is added to the scene and no
     later `FadeOut` can reach it.
  3. A figure not disposed at its section boundary — it rides the rest of the video.
  4. `Indicate` on a `(frame, label)` group — recolours the label into its own fill.
  5. A caption that stops matching its picture after a morph.
- Any gap over ~6 s needs `breathe_until(self, tn, "<next cue>", *mobs)` before
  the `wait_until`.
- Every spoken numeral must be computed from a module constant and asserted at
  import, so narration and picture cannot drift.
- `LayoutBoard` bands (y): title 3.05–3.95, key 2.25–2.95, panel label 1.70–2.10,
  bottom −3.55…−2.75. Park persistent chips *inside* the bottom band, not just
  above it.

## Log

- 2026-08-20 — stopped all subagents, killed orphan renders, took inventory,
  wrote this file. Starting on video 08.

- 2026-08-20 — cue coverage re-measured properly: scenes use a local
  `hold_until(scene, t_abs, ...)` helper as well as `tn.wait_until`, so the first
  metric undercounted. Real state: **09, 10, 11, 14 are complete**; only 12, 13,
  15 need authoring. Fixed two syntax errors left by mid-edit agent kills
  (`run_time0.8` in v11, missing colon in v14) — both files were unrunnable.

- 2026-08-20 — wrote the last three scenes by hand: v13 from scratch (1292 ln),
  v12's remaining 13 beats (+606 ln), v15's remaining 13 beats including the
  series close (+492 ln). All three pass a full `-n 0,1` logic pass, which
  executes every beat without rendering frames — the fast way to catch crashes
  and layout assertions. **All 15 scenes now exist and execute.**
- 2026-08-20 — v11 and v13 renders had *died*, not stalled: v11 on a marginal
  overlap (`ctr_cap` vs the "overwritten" ghost chip, 0.10 apart against a 0.08
  pad), v13 on a caption pushed outside the safe frame at x = -7.45. Both fixed
  and restarted. Worth remembering: a render that stops advancing has usually
  asserted, not hung — check the log tail before assuming contention.

- 2026-08-20 — ce-08 delivered (8/15). Learned the concurrency lesson the hard
  way: four simultaneous renders each ran at ~13 animations/min instead of 62,
  so nothing finished for an hour. Two at a time from here — finishing beats
  advancing.
- 2026-08-20 — three more marginal overlaps, all the same shape: `assert_clear`
  pads **both** boxes by 0.08, so 0.16 of clearance is the real minimum, not
  0.08. v11's `cross_boundary()` also placed every crossing caption at one fixed
  point, so the second landed on the first — stacked by index now.
- 2026-08-20 — switched to iterating on the `-n 0,1` logic pass instead of full
  renders: it found and confirmed each fix in ~2 minutes rather than ~10. Both
  v11 and v13 now pass it. Skill updated with this loop
  (`references/build-loop.md`).

- 2026-08-21 — built `scripts/finish_video.sh`: carries one video from wherever
  it is to a delivered MP4 unattended — logic pass, full `-ql`, both audits, QA
  stills, `-qm`, then writes a one-line `<slug>.status`. On failure it records
  the reason and exits non-zero so the caller moves to the next video. Three
  lanes now run it over the remaining six. **This is the fix for the real
  problem: I was stepping each stage by hand and idling between turns.**
- 2026-08-21 — v11 hit the crossfade law a second time (`onecore` → `umode`),
  and v13 needed 16 breathe cycles. For v13 I added a `breathe_scene` helper
  that idles whatever is on stage rather than requiring the caller to name live
  mobjects — much less error-prone for a mid-beat cue several plays deep.

- 2026-08-21 — **split the pipeline at the review gate**, on Ben's point that
  looking at the renders is an integral step a shell script cannot hold.
  `finish_video.sh` now stops at review-ready; `deliver_video.sh` does the `-qm`
  and refuses to run without a recorded review (`review_gate.py --check`).
  Editing a scene after a pass reopens the gate, because a review describes one
  specific set of frames.
- 2026-08-21 — extended `check_layout` to catch **box-cuts-text**, the class that
  had been slipping through every audit. The rule: a drawn rectangle either fully
  contains a text or must not touch it. Validated immediately — it explains v11's
  `bnez` border through the `counter` label, v12's verdict landing on the bus
  chips, and v13's memory table painted across three captions. Root cause in all
  three: the figure was never registered with the board, so `assert_clear` could
  not see it either.
- 2026-08-21 — frame review found and fixed: v11 `s0_arrow` never disposed (rode
  130 s pointing at nothing), `bnez` strip shifted off the `counter` label, the
  `sc.w` cases block narrowed off the memory table. v13 memory table moved from
  the caption band to y=-0.35 and registered. v12 `bus_order`/`order_cap`
  disposed at their section boundary. v15 two marginal-clearance fixes.
- 2026-08-21 — a full-res frame disproved one suspected collision that the 640px
  tile made look real. Thumbnails raise doubts; only full frames settle them.

- 2026-08-21 — built the layout **survey** (`MANIM_LAYOUT_COLLECT=1` on a full
  render): every failing `assert_clear` site with its line number, in one pass
  instead of one per render cycle. v12's 17 sites collapsed to 6 distinct
  problems; v14's 20 to 8; v15's 5 to 1. This is what turned the grind around.
- 2026-08-21 — found the phantom-box mechanism: a faded figure keeps its
  coordinates and its slot, so it collides with everything later placed there.
  `assert_clear` now ignores figures at zero opacity. Several "failures" chased
  earlier were phantoms.
- 2026-08-21 — `find_leftovers.py` added. Confirmed leftovers fixed: v11
  `s0_arrow`; v12 `bus_order`, `order_cap`, `sn0/sn1`, the `applied` strips, and
  `snoop_lab` (which claimed "snooping" over a directory picture); v13's drain
  chips under the producer beat.
- 2026-08-21 — **a wrong instruction encoding reached the review gate**: v13's
  `fence w,w` bit string was not the instruction, and the pred/succ brackets
  pointed at `rd` and `opcode`. Now computed from named fields and asserted
  against 0x0110000f. v11's `lw` strip was already correct because it was
  computed, not typed — the discipline works.
- 2026-08-21 — measured the real clearance threshold: pad is 0.08 per box and the
  test uses `<=`, so 0.16 still fails and 0.17 is the first clear value. Leave
  0.25.
- 2026-08-21 — v11 reviewed twice. First pass found 5 defects, all fixed and
  confirmed gone in the second render; the second pass found a sixth (a chip
  border through the "slot 0" label) that no audit reported. Frames caught what
  the tools missed.

- 2026-08-21 — **the logic pass was not a gate.** `-n 0,1` was used all session on
  the documented belief that it "executes every beat of construct". Measured with
  a six-animation scene that raises on its last line: `-n 0,1` runs animations 0
  and 1, never reaches the end, and **exits 0**. `--dry_run` runs all six and
  exits 1. That is why every fix kept revealing a new latent error deeper in the
  same file — those scenes had never been executed end to end. Skill corrected;
  `finish_video.sh` now uses `--dry_run`.
- 2026-08-21 — wrote `check_names.py` after finding that `from manim import *`
  disables ruff's F821, so an un-imported helper lints clean. It resolves names
  through the star import and checks calls against their callee's signature. On
  the six remaining scenes it found **20 latent crashes in under a second**: 18
  `note()` calls in v15 missing a required argument (the whole closing third of
  that video), plus `bottom_note` and `safe_multiline` used but never imported.
  The pipeline had been discovering these at one per full render. Static checks
  are now gate zero.
- 2026-08-21 — layout fixes are being batched per video from a `--dry_run` +
  `MANIM_LAYOUT_COLLECT=1` survey instead of one per render. Guessing a position
  twice for v14's `fail1` chips is what settled the policy: read the whole list,
  then move things once.

- 2026-08-21 — v12 frame review found the MOESI state diagram riding into the
  invalidate/update section: "your copy is wrong" printed over the S node and O
  over the core boxes. The detector had been silent because a wide panel fully
  contains a small node's letter, which the containment rule treated as a chip
  holding its own label. Fixed by tracking each leaf's top-level ancestor and
  reporting cross-owner containment as `box-buries-text`.
- 2026-08-21 — two further detector bugs found by testing it against that same
  case: `family_members_with_points()` never returns a `Text` (point-less
  parent), and `_opacity_of` reads zero for a `MathTex` parent. Both silently
  narrowed every layout audit run before this point.
- 2026-08-21 — v10 and v12 failed the *motion* audit, not layout: 5 and 15 frozen
  stretches, the worst 24.6 s. `check_sync` now names the cue each stretch runs
  into, and `breathe_scene` was promoted from one scene file into style.py, so
  the fix is a one-line insertion per stretch.
- 2026-08-21 — the text-over-text gate was blocking on a 0.40 s, 43 % crossing
  between a '?' glyph and 'core' during a transform. It now blocks only on
  intervals of 0.6 s or more and surfaces the brief ones for the frame review.
- 2026-08-21 — two self-inflicted pipeline faults, both of which looked like
  flaky renders rather than mistakes: (1) two lanes for the same video shared
  `media/qa`, manim pruned the shared partials, and the loser overwrote the
  winner's status — leaving v12 with frames from one render and a timeline from
  another; fixed with a per-slug lock and by clearing `out/qa_frames` each run.
  (2) Editing `finish_video.sh` while four lanes were executing it corrupted
  their control flow, because bash reads a script by byte offset as it runs.
  Stop the lanes before touching a driver.
