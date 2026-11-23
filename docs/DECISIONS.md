# Locked product decisions

Updated: 2026-11-22 (multi-style redesign). The evidence behind each decision is in
`docs/research/`. The numbers in brackets refer to the decision table in
`docs/research/README.md`.

| Decision | Choice |
|----------|--------|
| Styles | Style packs inside the one skill: `skills/manim-explain/styles/<name>/` with `style.yaml`, `components.py` and `STYLE.md`. Shipped: `3b1b` and `welch` [1, 8] |
| What a style covers | Visuals **and** narrative: voice instruction, speaker profile, narrative parameters, palette, fonts, text policy, motion numbers, emphasis vocabulary, rule switches [2, 21] |
| Style scope | Chosen per series in `demos/<series>/series.yaml`; every video in a series shares it [14] |
| Core vs style rules | Core laws (`references/craft-laws.md`) hold for every style; anything style-dependent lives in the pack [21] |
| Narrative | Hook → central question → chain of units (question → work → turn → cash-out → link) → payoff; one climax; lint rules N1–N15 [15, 16] |
| No dialogue | No narrated dialogue with characters; the narrator voices the viewer's intuition [15] |
| Video length | Follows the content, at least 2–3 full units (roughly 6–12 min); short neighbouring topics merge [25] |
| Inputs | Course material, a bare topic the agent researches from primary sources, or both; always distilled into `SOURCE_NOTES.md` before scripting (`references/research.md`) [10] |
| Audience | Ben studying and other viewers [11] |
| Engine | manimgx (Manim CE API on a Rust/wgpu core). No Manim CE fork, no LaTeX install (math via Typst) [4, 28] |
| Rendering | One short scene per beat: each beat is a frame range of the same scene, rendered by its own worker, joined frame-exactly [19]. Workers draw on the CPU (manimgx's bundled lavapipe); GPUs only when named, pinned one per worker by a Vulkan layer. A worker on the wrong kind of device fails [29] |
| Fix rounds | Plan check, render and render check redo only what a fix changed: each window (event to event) and beat has a digest of everything its frames depend on, and unchanged work is reused [30] |
| Layout | A pixel layout plan per video (`plan/layout.json`); the runtime builds exactly it. No freehand placement [20] |
| Sync | Each visual change runs across the phrase that describes it, starting just after its first word; stills between events; no idle motion; tolerances per style [18] |
| Voice | Gemini 3.8 Flash TTS, voice Charon, with the style's delivery instruction, through OpenRouter. One request per video (split only between units). Whisper word timestamps. OpenRouter is the only provider [26] |
| Gates | lint → voice; plan check → render; render check → frame review → deliver. Each gate is tied to a digest of the files it judged |
| Autonomy | Research first and ask brief alignment questions when style, scope or background are open; once aligned, run end to end without approval stops (optional storyboard checkpoint, off by default) [13] |
| Real data | Analytic or synthetic values only; no precomputed real-model data [5] |
| 3D | Out of scope [3] |
| Welch font | Source Sans 3 (free stand-in for Myriad Pro); rendering fails if missing [6] |
| Welch reference | `vendor/welch-labs-videos/`, a gitignored read-only clone (MIT) [7] |
| Delivery path | `<project>/output_videos/<series>/<slug>.mp4`; the series is the folder the video sits in |
| Skill scope | Published Agent Skill: `skills/manim-explain/` (spec: agentskills.io). Local agent folders (`.cursor/`, `.claude`, `.opencode`) are gitignored and are not part of the repo (2026-11-23) |
| Distribution | Claude Code plugin marketplace (`.claude-plugin/`), or symlink/copy the skill dir into any agent's skills folder. The skill never hard-codes an install path: `explain/paths.py` resolves it from its own location |
| Inspiration | 3Blue1Brown, Welch Labs (helpers ported under MIT), and [3brown1blue](https://github.com/AmitSubhash/3brown1blue), referenced by URL, never vendored |
| License | MIT |
| Skill env | Any Python 3.13 environment with the packages in `requirements.txt`, named by `MANIM_ENV` in `.env` |
