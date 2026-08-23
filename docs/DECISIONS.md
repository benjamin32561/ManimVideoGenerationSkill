# Locked product decisions

Updated: 2026-08-21

| Decision | Choice |
|----------|--------|
| Inspiration | Distill from [3brown1blue](https://github.com/AmitSubhash/3brown1blue) (`pip install 3brown1blue`, MIT); do not ship its Kokoro/atempo sync. Optional read-only clone: `vendor/3brown1blue/` (gitignored) |
| Sync pipeline | Script+cues → OpenRouter TTS → Whisper word timestamps → timed Manim → mux |
| TTS | **OpenRouter only** — `x-ai/grok-voice-tts-1.0`, male voice **`leo`**, `chunk_by: tts_chunk`. No second provider (2026-08-11) |
| Autonomy | Skill runs **end to end** — no approval gate on script/arc/visuals; user reviews the finished MP4 |
| Craft laws | Living doc: `skills/manim-explain/references/craft-laws.md` — update from user feedback as **abstract** laws (not demo-only patches) |
| Morph rule | Related A→B transforms in place; soft idle on holds; first charts must move |
| Picture match | Spoken noun ↔ on-screen structure (whole system → focus part → morph) |
| Question motion | Referent mobjects move while the question is asked (`ask_about`) |
| Staged procedures | Multi-step VO (choose/rank/cut/lock/build) animates each verb, not one recolor |
| Beat suspense | ~0.3s via `tts.inter_chunk_silence` + soft-idle (not naked desync waits) |
| Visual QA | Geometry pass captures sparse stills; `qa_frames.py` tiles `out/keyframes/`; `render_stills.py` Cairo-rasterizes named times into `out/stills/` and aborts after the last hit. No MP4 seek in the inner loop (2026-08-21) |
| Build loop | Four gates, cheapest first: `--geometry_only` walk → occupancy/`check_sync`/`check_layout` → pixels read off captured stills → `-qm` once behind `review_gate.py`. `--dry_run` is not used: it still Cairo-rasterizes every frame. See `references/build-loop.md` (2026-08-21) |
| Render isolation | Every render passes `--media_dir`; `render_and_mux.sh` uses a per-invocation tree. Same-scene concurrency is safe by construction, not by coordination (2026-08-20) |
| Cue robustness | Cues must be transcript singletons. `align_words.py` rejects implausible forward jumps and joins split compounds; `cue_doctor.py` diagnoses, `cue_repair.py` re-cues and re-maps free. Unresolved cues now **fail** the align step instead of warning (2026-08-20) |
| Delivery path | Finished videos go to `<project>/output_videos/<series>/<slug>.mp4`, grouped by slug prefix (`ce-` → `computer-engineering/`, `pf-` → `philosophical-foundations/`, `thermal-` → `thermal/`, else `other/`). `demos/<slug>/` keeps the working tree only. Path is resolved by `skill_paths.final_video_path` (2026-08-22; was a flat directory 2026-08-19) |
| Figure gutters | Clear air between panels / bars / text (≥ ~0.35–0.5 units) |
| Terminology | Prefer precise domain nouns (e.g. **distribution** over “profile”) |

| Default STT | OpenRouter Whisper with `timestamp_granularities=["word"]` |
| Render quality | Prefer **`-qm` (720p30)**; avoid `-ql` (480p15 — looks choppy) |
| On-screen math | **LaTeX / MathTex** (classic 3b1b). Requires `dvisvgm` (local unpack under `.local/`) |
| Narration text | **Never** raw LaTeX/symbols that confuse TTS. Write spoken math; look up pronunciation when unsure (see skill `reference/spoken-math.md`) |
| Visual style | Classic 3b1b (dark frame, yellow/blue accents, sparse) |
| Narration tone | Calm curiosity (Grant-like), teaching-style rewrites (ellipses, questions, short beats) |
| On-screen text | Both: minimal labels **and** short spoken-phrase captions |
| Video length | No preset; script is as long as the teaching needs |
| Skill scope | Published Agent Skill: `skills/manim-explain/` (spec: agentskills.io). `.claude/skills/` and `.cursor/skills/` hold symlinks for dogfooding only (2026-08-12) |
| Distribution | Claude Code plugin marketplace (`.claude-plugin/`), or symlink/copy the skill dir into any agent's skills folder. Skill must never hard-code an install path — resolve via `MANIM_EXPLAIN_ROOT` / `scripts/skill_paths.py` (2026-08-12) |
| License | MIT (2026-08-12) |
| Third-party inspiration | `3brown1blue` is referenced by URL + pip name, never vendored into the repo (2026-08-12) |
| First demo topic | **Top-$k$ on-mass** (NTUDynamicRangeGCN neuron-on metric) |
| Manim env | `/raid/conda_envs/ben_envs/manim_env` |
| GPU rasterizer | Not for the inner loop (2026-08-21). Named stills after a geometry pass restore compact mobject snapshots (`out/snapshots/`, 0.5 s + overlaps) and Cairo once — no `construct`. CE-14: 2 stills at 93.6 + 367.8 in **2.0 s** vs construct walk **13.6 s** for 93.6 alone. First occupancy walk still pays construct (~8 min). Snapshot dump ~155 MB. `--walk` forces the slow path. |

## Source concept (first demo)

From `NTUDynamicRangeGCN/0docs/progress_tex/teaching.tex` §neuron-on:

\[
\mathrm{on\text{-}mass}(c)
= \frac{\sum_{j \in S_c} |\mu_{c,j}|}{\sum_{j=1}^{F} |\mu_{c,j}|}
\]

where \(S_c\) is the top \(fF\) units by \(|\mu_{c,j}|\). Uniform baseline = \(f\). Not the same as top-set strength or class selectivity.