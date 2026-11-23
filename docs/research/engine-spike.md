# Engine comparison spike

Run 2026-11-21. The same 58 s segment was built in four engines from one shared spec, so the
only variable is the engine.

- **Watch:** `output_videos/engine-spike/compare_grid.mp4`, all four in sync with the
  narration.
- **Single renders:** `ce.mp4`, `gl.mp4`, `gx.mp4`, `hf.mp4` in the same folder.
- **Stills:** a 2×2 still just after every event in `output_videos/engine-spike/stills/`.
- **Spec, tools and code:** the spike lived in `spikes/engine-comparison/` and was removed on
  2026-11-22, after its manimgx scheduler, action vocabulary and GPU pinning were promoted into
  `skills/manim-explain/explain/` and `vulkan/`. The results below are the record.

## The segment

- **Narrative:** one full unit per `narrative-pattern.md` §7: setup → attempt ("you'd expect
  it to keep flowing out until both sides are equal") → wall (charge builds up) → revelation
  (the two pushes balance) → cash-out (naming, the Nernst equation built term by term, real
  numbers giving −89 mV) → link to the next question.
- **Voice:** decision 26 (Gemini 3.8 Flash TTS, Charon, brisk instruction). 181 words in
  58.04 s, 187 wpm. One request, cost under $0.01. Whisper word times.
- **Layout plan** (`spec/layout.json`): 103 objects with fixed pixel positions, colour tokens,
  sizes and draw order, plus the 3b1b style block (CMU Serif text, LaTeX math, black
  backstroke, one colour per concept).
- **Timing** (`spec/events.json`): 26 events, each bound to the phrase that describes it
  (decision 18). Frames hold still between events.

## Results

Render times are for the full 58 s at 1920×1080, 30 fps. "Measured" means I re-ran each
`render.sh` myself, one at a time, end to end including encode and mux. "Reported" is the
engine agent's own number.

| | Manim CE (current) | manimgl | manimgx | HyperFrames |
|---|---|---|---|---|
| Cold render | 86.3 s measured (90.7 reported) | 37.9 s reported (39.0 with mux) | 12.1 s engine + 8 s re-time/mux = 20.5 s reported | 37.9 s reported (38.5 with build) |
| Re-render (measured) | 34.4 s (partial-movie cache; 15 s render + 19 s encode) | 37.2 s | 20.0 s (about 12 s engine) | 36.4 s |
| Fastest feedback | 540p15 preview 36 s; only 2× faster, since the cost is Python | last frame 5.1 s; 480p15 10.6 s | dry run 2.2 s; chosen frames + layout check 6.9 s; 540p15 8 s | 9 stills 5.7 s; DOM geometry pass 1.8 s |
| Hardware | CPU | 1 GPU (EGL) + about 3 cores | 1 GPU (Vulkan); 44.7 s on the CPU fallback | CPU (software Chrome, 9 workers) |
| Setup | 12 min | 8 min | 14 min (11 of it pinning one GPU) | 42 min to first render |
| Scene code (no docs or comments) | 634 lines | 488 lines | 388 lines | 1,470 hand-written lines (a runtime emulating Manim write/morph) |
| Math | real LaTeX | real LaTeX; 1.7.2 strips spacing around isolated parts | Typst via mitex, near-identical to LaTeX, no TeX install | KaTeX, close; lighter scripts, softer edges |
| Built-in layout check | none (the skill's own tools) | none | `inspect`, at the end of each animation only | `check --json`, craft warnings |
| Engine problems | per-event re-encode makes text sharpness pop (worked around with lossless + one encode); unlike-glyph morphs go blobby | several 1.7.2 bugs (`--fps` flag, Tex spacing, outline spikes) | variable-frame-rate output needs re-timing; about 2 in 25 runs segfault after writing output; ignores `CUDA_VISIBLE_DEVICES` (needed a Vulkan layer); v0.1 | each glyph is a DOM span (1,295-line scene); the whole Manim look had to be rebuilt |
| Licence | MIT | MIT | MIT code; wheels GPL-3.0+ (videos unaffected) | Apache-2.0; GSAP free licence; KaTeX MIT |

## Findings

1. **With a fixed layout plan, the engine barely changes the look.** Held frames from all four
   are near-identical (compare any still in `stills/`). What made the frames clean was the plan
   and the phrase-bound timing, not the engine. Differences show only in motion: write-on
   style, morph quality, and KaTeX's softer edges.
2. **Speed:**
   - manimgx is the only clear outlier, at 3–7× faster than CE end to end. Its 2 s dry run and
     7 s chosen-frame check would make the edit → look loop short.
   - manimgl and HyperFrames match CE's warm time.
3. **HyperFrames' strength didn't apply here.** Its automatic text layout doesn't matter once
   the layout plan fixes positions, and reproducing 3b1b write-ons and morphs took a
   1,100-line custom runtime.
4. **Every agent hit the same problems with the spec, so these are rules for the redesign,
   whatever the engine:**
   - Thin glyphs at small sizes (± signs at 30 px CMU Serif, about 1 px strokes) read faint.
     The plan needs a minimum stroke or size per glyph role.
   - Copies flying in a straight line cross other objects for 0.2–0.3 s. Copy paths must
     route around occupied boxes.
   - Morphing unlike glyphs ([K⁺]ᵢₙ → 140 mM) goes blobby for about 0.4 s. Use a cross-fade
     when glyphs don't match.
   - Moving objects pass behind labels (ions behind "concentration push"). Plan motion paths
     against label boxes, not just rest positions.
   - A black backstroke over coloured fills shows as a dark halo. Apply it only over busy
     backgrounds.
   - Staggered starts through a narrow gap collide unless the stagger order is planned.
   - A dim must never brighten something already dimmer.
5. **Measured, not estimated:** every event's motion starts 0.05–0.24 s after its anchor word,
   and holds are pixel-identical (manimgl lossless check). The freeze-then-burst pattern from
   the old pipeline is gone in all four.
