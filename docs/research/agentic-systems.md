# Agentic video-creation systems

Researched 2026-11-21 for the multi-style redesign (see [README.md](README.md), decision 9).
Scope: systems that take an idea, topic or document and produce a finished explainer video with
LLM agents, with the emphasis on **code-rendered** output (Manim, Remotion, HTML/SVG, slides).
Generative-video agents appear only as contrast.

Every claim is marked **[verified: source]** (read in the paper, the code or an official page) or
**[inferred: basis]**. "Paper §3" or "Table 2" refers to the paper named in that system's Sources
line. Repos were shallow-cloned and read, never run. Numbers are quoted with their setup. Several
of these papers judge their own outputs with their own benchmark and their own VLM judge; that
caveat applies wherever it is not repeated.

---

## Findings in brief

1. **What reduces broken text and overlaps is less layout freedom for the model, not more critique.**
   The best evidence for fewer overlaps comes from fixing positions before code is written or
   handing them to an engine. OmniManim plans a box per object per keyframe before coding (human
   overlap score +16.4 vs plain GPT-5.4, +32.1 vs Code2Video). Code2Video makes the coder place
   objects on a named 6×6 grid (VLM-judged layout 45 → 83). Templates, Beamer and HTML reflow do
   the same job in other systems. Asking a VLM to critique rendered frames is the
   weakest-evidence layout fix: VLM layout scores disagree with humans in every study that
   checked, from 90.6 VLM vs 60.2 human (Code2Video) to r = −0.17 (ManimAgent).
2. **Deterministic geometry checks are the second lever, and the current skill is already strong
   there.** SGA (a code-level scene graph and computed shift vectors) beat both raw output and a
   VLM critic in human frame comparisons. PRISM measured a 41-point gap between "the code renders"
   and "the frames are spatially clean". The skill's geometry pass and live collision watch go
   beyond TEA, Code2Video and SGA. The gaps are elsewhere:
   - nothing plans layout before code;
   - violations name the problem but not the computed fix;
   - nothing measures text before it is placed, and nothing checks for text leaking out of a
     container or falling below a readable size;
   - the frame review spends the agent's vision on geometry, the job vision does worst.
3. **The field's typical architecture is plan → typed IR → constrained code → bounded, routed
   repair**, with programmatic checks first and an LLM only for meaning. The most reliable
   systems keep layout and timing out of the model's hands:
   - LASEV: templates plus an alignment spec; 0.90% compile failures over 20M videos.
   - DataMagic: a declarative spec; animations fire by narration-segment index.
   - ALGOGEN: a trace plus a style DSL rendered deterministically; 99.8% vs 82.5% success.

   A controlled study, though, found that making the model write a new declarative format does
   not cut cost and costs some reliability. The gain comes from the harness owning layout and
   timing, not from a shorter output language.
4. **On audio-visual sync the current skill is ahead of every system read.** Only it, manim-voiceover
   bookmarks, ManimGX's `say()`, Remotion's prompt-to-video template and the edge-tts skills
   anchor animation to individual words. Most systems sync per slide or per sentence, and several stretch audio to
   fit the video. Two improvements are worth taking:
   - Get word times from the TTS call when the provider returns them, and use Whisper to check
     the audio rather than as the timing source.
   - Bind each animation to a word in one place, so a rewording re-times itself (DataMagic,
     ManimGX).
5. **Render speed has three levers:**
   - **Parallelism.** Rendering scenes or sections in parallel gave 5.6× in Code2Video and 6× in
     PaperTalker.
   - **Faster or seekable engines.** ManimGX is 6–20× faster than Manim CE on 2D scenes in the
     vendor's own benchmark, unverified on Linux. Frame-seekable engines such as Remotion and
     HyperFrames make one QA still cost one frame.
   - **Never encoding inside the loop**, which the skill's geometry pass already does.

   ManimGX also ships most of the skill's QA tooling inside the engine; it deserves a spike under
   decision 4.

---

## The current skill, as the baseline

Read from `README.md` and `skills/manim-explain/SKILL.md` on 2026-11-21 [verified]:

- **Order:** viewer contract and causal spine → `script.yaml` (beats: `say`, `show` as free text,
  `bookmarks`, `tts_chunk`, `pause_after`) → `lint_script.py` → OpenRouter TTS (Grok Voice) →
  chunked Whisper word timestamps (`timing.json`) → the agent hand-writes Manim CE code timed with
  `TimedNarration.wait_until(cue)` / `play_before`.
- **Static gates:** `check_names.py` (undefined names, call signatures), `find_leftovers.py`.
- **Geometry pass:** interpolates the whole `construct` without encoding a movie, samples AABBs
  at about 10 Hz, writes occupancy, leftovers, overlap intervals and sparse Cairo stills.
- **Audits:** `check_sync.py` (silent and thin cues, frozen stretches), `check_layout.py` (live
  text collisions during motion), `qa_frames.py` (contact sheet).
- **Review loop:** the agent reads the frames itself; `review_gate.py` blocks the `-qm` delivery
  render until a review is recorded.
- **Memory:** user corrections become general rules in `craft-laws.md`.
- **Pains:** slow renders (a `-qm` render takes about 0.9× the video's runtime for line art and
  up to about 8× for heavy grids, per `build-loop.md`), and frames with overlapping, clipped or
  broken text.

---

## Overview

| System | Type | Input | Render target | QC loop | Eval | License |
|---|---|---|---|---|---|---|
| **Manim explainer agents** | | | | | | |
| [TheoremExplainAgent](#theoremexplainagent-tea) | paper (ACL 2025) + repo, frozen mid-2025 | theorem + one-line description | Manim CE 0.18 + plugins; Kokoro TTS via manim-voiceover | stderr → LLM fix ≤5; optional doc RAG; optional VLM reflection (broken in release) | TheoremExplainBench (240); 5 LLM/VLM dims; small human studies | MIT |
| [Code2Video](#code2video) | paper (ICML 2026) + repo, active | topic string | Manim CE 0.19, 480p15 sections; **no audio** | ScopeRefine line → block → full; Gemini 2.5 Pro critic on section video + 6×6 grid → line patches, 2 rounds | MMMC (3b1b); VLM AES; TeachQuiz; 40-person study | MIT |
| [OmniManim](#omnimanim-see-before-you-code) | paper (May 2026); planner not released | NL teaching requirement | Manim CE 0.19 | trained keyframe-box planner **before** code; CV diagnostics → 1 routed repair | EduRequire-500; CV metrics; 20-rater human study | no license file |
| [SGA](#sga-and-prism-deterministic-geometry) | paper (Jul 2026); code not public | LLM Manim code (plug-in) | Manim CE, executed without rendering | scene graph → AABB conflicts → min-separation vector → ±5-line patch | MMMC-Code; MVQS; 25-rater study | n/a |
| [PRISM](#sga-and-prism-deterministic-geometry) | benchmark + auditor | instruction | Manim CE 0.19 | eval only: overlap / out-of-bounds / container leak per `play` | 10,372 EN/ZH tasks, 7 LLMs | no license file |
| [LASEV](#lasev-beyond-end-to-end-video-models) | paper (KDD 2026) + Baidu production; no code | K-12 problem | template engine + Manim illustrations + TTS | semantic + tool + rule gate per stage, ≤3, then drop | 1,003 problems, teacher rubric; 20M-video log | paper CC BY-NC-ND |
| [ManimAgent (Jiang)](#manimagent-jiang-et-al) | paper (EMNLP 2026) + repo | paper section | Manim CE (sandboxed Cairo) | crash loop ≤2 (full regen); VLM keyframe loop ≤2; best-of-N; cross-task memory | 33 probe tasks, 54 raters | no license file |
| [VisualEDU](#brief-entries) | benchmark + repo (EMNLP Findings 2025) | math problem | Manim | code-error loop + VLM checks on one frame | 200 problems, 9 VLMs | no license file |
| [ManimTrainer (Silva)](#brief-entries) | paper + repo | NL description | Manim CE 0.19 | render-in-loop + docstrings of called APIs | ManimBench (100 test) | NOASSERTION |
| [PIVOT](#brief-entries) | paper (EMNLP 2026) + repo | STEM topic | Manim + TTS | public code: text-only LLM overlap review | 40 topics; VLM judge; 32 instructors | Apache-2.0 |
| [TeachMaster](#brief-entries) | paper + product | lecture outline | Manim + MiniMax TTS | debug loop, sync agent, heuristic layout agent, human edit | GPT-5.2 judge; deployment stats | not checked |
| [LLM2Manim](#brief-entries) | paper (Apr 2026) | concept brief | Manim + narration | pre-render checks; human fixes overlaps | 100-student A/B vs slides | not checked |
| [Manimator](#brief-entries) | paper + repo, stale since Feb 2025 | prompt / PDF / arXiv id | Manim CE, silent | blind regenerate (error not fed back) | TEB auto-judge + volunteers | MIT |
| [Generative Manim / Animo](#brief-entries) | repo + API + paid app | prompt / chat | Manim CE | `get_preview` tool returns frames to the chat, ≤4 rounds | 11-task render benchmark, no results | Apache-2.0 |
| [Math-To-Manim](#brief-entries) | repo, high churn | prompt / sketch photo | Manim CE (3D-heavy) | AST gate + bounded render repair; 12-frame sheet | none | MIT |
| [manim-generator](#brief-entries) | repo + leaderboard | prompt | Manim CE | writer / reviewer loop on logs + densest frame | Manim Bench leaderboard | MIT |
| **Declarative IR + deterministic renderer** | | | | | | |
| [DataMagic](#datamagic) | paper (IEEE VIS 2026) + repo + agent skill | table + query | Remotion (React, Vega-Lite / D3 / GSAP) + TTS | parallel candidates → global orchestration; execution retry | 109 samples; Gemini judge (r = 0.91 vs experts); user study | MIT |
| [ALGOGEN](#algogen-mover-logomotion-explainspec) | paper (ACL Findings 2026); code link 404 | LeetCode task | trace + style DSL → Manim / TikZ / Three.js | schema validation + error-guided repair ≤3 | 200 tasks; Code2Video AES rubric | n/a |
| [ExplainSpec study](#algogen-mover-logomotion-explainspec) | pre-registered controlled study | explanation request | SVG runtime vs free HTML/JS | one repair round | 20 tasks × 4 models | n/a |
| [MoVer](#algogen-mover-logomotion-explainspec) | paper (SIGGRAPH 2025) + repo | text prompt + SVG | GSAP / SVG | first-order-logic verification report → LLM fix | 5,600 synthetic prompts | Apache-2.0 |
| [LogoMotion](#algogen-mover-logomotion-explainspec) | paper (CHI 2025) | layered PDF logo | HTML + anime.js | programmatic last-frame diff + isolated VLM image pair, ≤4 | 276 animations; n = 16 | n/a |
| **Slide / paper / document to video** | | | | | | |
| [Paper2Video / PaperTalker](#paper2video--papertalker) | paper (NeurIPS 2025 workshop) + benchmark + repo | LaTeX paper + portrait + voice sample | Beamer → PNG; cursor; subtitles; talking head | compile repair ≤10; overfull → 4 scaled variants → VLM picks | 101 papers; 4 metrics; 10-person ranking | MIT |
| [Bespoke](#bespoke) | paper (Sep 2026); no code | lecture transcript + industry + length | HTML slides, progressive reveal, TTS | programmatic checks → cross-family VLM validator ≤3 | 25 experts, 92 videos | n/a |
| [EvoPresent](#brief-entries) | paper (ICLR 2026) + repo + trained critic | paper | HTML/CSS slides → video | checker sees DOM boxes + screenshot; accept ≥ 8.7; ≤3; revert on regression | 650 papers; PresAesth | MIT |
| [VideoAgent](#brief-entries) | paper (ICMR 2026); no code | paper PDF + intent | python-pptx + Manim clips | execution retry ≤3; VLM on sampled frames | SciVidEval (50); 16-person quiz | n/a |
| [PresentAgent](#brief-entries) | paper (EMNLP 2025 demo) + repo | document | PPTX → static slides + MegaTTS3 | API-execution retry ≤3 | 5 docs; 3B/7B judges | none declared |
| [NotebookLM Video Overviews](#notebooklm-video-overviews) | product (Google) | notebook sources + prompt | narrated slides + Nano Banana art; Cinematic adds Veo 3 | undisclosed | none published | proprietary |
| **Agent skills and engines** | | | | | | |
| [3brown1blue](#3brown1blue) | pip CLI + agent skill | topic / .pptx | Manim CE + Kokoro / VibeVoice | regex audit + 5 frames; no automatic repair | none | MIT |
| [manim-voiceover](#manim-voiceover) | Manim plugin (alpha) | `with self.voiceover(...)` blocks | Manim CE | none (library) | none | MIT |
| [SenseNova code-video](#sensenova-code-video-skill-and-model) | agent skill + open 27B model | dense prompt | Canvas / SVG / HTML / Three.js / Remotion / Manim via `seek(t)` | SPEC.md must-haves → stills, sheets, action strips → VERIFY.md; `check_video`, `sync_check` | none published | skill MIT; model Apache-2.0 |
| [anything2explainer](#anything2explainer-and-hyperframes) | Claude Code / Codex skill | topic / document | Remotion | static selfcheck + frame metrics + per-chapter QC agents | lessons log only | PolyForm Noncommercial |
| [HyperFrames](#anything2explainer-and-hyperframes) | framework + agent skills (HeyGen) | agent request | HTML / CSS / GSAP seeked in headless Chrome | `check --json` craft warnings; review sheets incl. phone width | none | Apache-2.0 |
| [Remotion AI tooling](#remotion-ai-tooling) | official skills + template | agent request / prompt | React → headless Chromium | single-frame stills; WebMCP inspection | none | Remotion License |
| [Motion Canvas](#brief-entries) | TS library (dormant) + fork + agent plugin | agent request | Canvas 2D | agent HTTP seek / screenshot | none | MIT / Apache-2.0 |
| [ManimGX](#manimgx) | engine (Rust + wgpu), Manim CE API | Python scene | own GPU renderer | `inspect`: storyboard + layout checks, exit 1 | vendor speed benchmark | MIT code; GPL-3.0+ wheels |
| **Contrast: generative video** | | | | | | |
| [MovieAgent, FilmAgent](#contrast-agents-on-generative-video) | papers + repos | script / idea | video models / Unity set | critique loops | human evals | various |

---

## Per-system notes: Manim explainer agents

### TheoremExplainAgent (TEA)

Sources: arXiv 2502.19400 v2; ACL 2025 main (oral); repo `TIGER-AI-Lab/TheoremExplainAgent`
(HEAD e9ece5d); dataset `TIGER-Lab/TheoremExplainBench`.

- **What.** The first well-known agentic Manim explainer. MIT, about 1.5k stars, last push
  2025-07-27, README says "research purposes only" [verified: gh api, README]. A research
  baseline, not maintained [verified: last push].
- **In → out.** Theorem plus short description → narrated video of 3–7 independently rendered
  scenes, joined with ffmpeg, plus an `.srt` [verified: §3.1; `prompt_scene_plan.txt`;
  `video_renderer.py`].
- **Architecture.** A fixed pipeline; the same model plays planner and coder in every paper run
  [verified: §4]:
  1. scene outline;
  2. per scene, run in parallel: storyboard plan → technical plan → animation-and-narration plan;
  3. optional plugin detection;
  4. coder writes one `Scene{n}(VoiceoverScene)`;
  5. render at `-qh` (1080p60); on failure, stderr goes to a fix prompt (`<THINKING>` Error Type /
     Location / Root Cause / Fixes), up to 5 retries;
  6. optional VLM check on one frame;
  7. concatenate.

  [verified: `src/core/*`, `generate_video.py`]. Each scene is told to be "entirely
  self-contained" [verified: `prompt_scene_vision_storyboard.txt`], so nothing carries across
  scene boundaries [inferred].
- **Script.** Narration is written *after* the storyboard and technical plan, as free text with
  "precise animation timing cues" [verified: `video_planner.py` order;
  `prompt_scene_animation_narration.txt`].
- **Visual IR.** Four free-text plans in XML tags per scene; no schema, no coordinates. Layout is
  prose repeated in four prompts: "Safe area margins: 0.5 units … Minimum spacing: 0.3 units … No
  absolute coordinates" [verified: prompt files]. The coder is asked to "implement explicit
  checks", but nothing in the harness measures a bounding box [verified: grep for
  `bbox|overlap|get_bounding_box` finds nothing].
- **Audio and sync.** Kokoro TTS wrapped as a manim-voiceover service. Block-level sync:
  `with self.voiceover(text=…) as tracker:` and `run_time=tracker.duration`; no bookmarks, no
  word times [verified: `src/utils/kokoro_voiceover.py`; code-generation prompt; grep].
- **QC.**
  - **Repair dominates success.** With o3-mini, scene-render success rises from 0–7% with no
    retries to 91–96% with 5 [verified: Table 3].
  - **Doc RAG hurt the strongest models.** Agentic RAG over the Manim docs (ChromaDB, k = 2):
    o3-mini 93.8 → 82.1%, GPT-4o 55.0 → 45.8%. It helped weak ones: Claude 3.5 Sonnet 2.1 →
    14.6% [verified: Table 1]. The authors call retrieved docs "often irrelevant or overly
    generic" [verified: §4].
  - **The VLM reflection path looks broken in the release.** The template has `{implementation}`
    and `{generated_code}` placeholders but is formatted with `code=` only [inferred: from
    reading the code, not run].
- **Eval.** TheoremExplainBench: 240 theorems across CS, chemistry, math and physics at three
  levels [verified: §3.3]. Five dimensions, 0–1, combined by geometric mean, judged by GPT-4o and
  Gemini 2.0 Flash [verified].
  - **Success (all 240):** o3-mini 93.8%, GPT-4o 55.0%, Gemini 2.0 Flash 14.6%, Claude 3.5 Sonnet
    2.1% [verified: Table 1].
  - **Quality (successful videos only):** o3-mini overall 0.77 with Element Layout 0.61; Claude
    3.5 0.79 with layout 0.57; human-made Manim videos 0.77 with layout 0.73. Layout is the
    weakest dimension for every model [verified: Table 2].
  - **Metric validity** (40 videos, 12 student raters): Spearman ρ with humans is 0.72 for Visual
    Relevance and 0.42 for Element Layout. The text-judged dimensions are near zero: Accuracy
    0.14, Logical Flow 0.16 [verified: Table 4].
  - **Human preference** reverses the success ranking: Gemini 2.0 Flash was top for clarity in
    70.6% of picks [verified: App. C].
- **Failure modes.** Render failures are mostly Manim API hallucination, then LaTeX errors, then
  general Python errors [verified: §4.3]. "Most of the generated videos exhibit minor element
  layout issues, such as overlapping texts, inconsistent sizes" [verified: §4.4]. Single-prompt
  generation "fails to generate videos longer than 20 seconds" [verified: §4].
- **Speed and cost.** Per video (7 scenes, 4 fixes): $0.10–$2.42 and 1,120–2,240 s; adding RAG
  takes Claude to $4.67 [verified: App. B, Table 5]. Every retry renders at 1080p60 [verified:
  `video_renderer.py`].
- **Borrow for Ben.**
  - Bounded compile repair is the single largest success lever; the skill's static gate already
    removes its biggest error class.
  - Use TEA's frame-based dimensions (Visual Relevance, Element Layout) if a VLM metric is needed:
    they are the only ones that tracked humans.
- **Avoid.** Prompt-only spatial rules. Generic doc RAG. High-quality renders inside the repair
  loop. Block-level sync. Self-contained scenes, which break morph-not-respawn across scenes.

### Code2Video

Sources: arXiv 2510.01174 v1; ICML 2026 camera-ready, PMLR 306:15370–15396; repo
`showlab/Code2Video` (HEAD 637509, 2026-11-17); dataset `YanzheChen/MMMC`.

- **What.** Show Lab (NUS). MIT, about 2.4k stars, actively maintained [verified: gh api].
- **In → out.** A topic → a **silent** video of about 2 minutes, built from slide-like sections:
  title on top, lecture lines on the left, animation on the right [verified:
  `prompts/base_class.py`; ICML Table 1; no TTS code in the repo].
- **Architecture.** Planner → Coder → Critic [verified: §4; `src/agent.py`]:
  1. JSON outline (audience, sections);
  2. per-section storyboard pairing lecture lines 1:1 with animation steps;
  3. asset step: icons from IconFinder, plus a reference image per topic;
  4. coder writes sections in parallel (`ThreadPoolExecutor(max_workers=6)`), each subclassing a
     fixed `TeachingScene`: "NEVER use .to_edge(), .move_to(), or manual positioning!";
  5. render at `-ql` with ScopeRefine repair;
  6. critic pass;
  7. ffmpeg concat.
- **Script.** No narration. The "script" is short on-screen lecture lines; line *i* changes
  colour while animation *i* plays [verified: App. A.2.5].
- **Visual IR.** JSON storyboard plus a **visual anchor grid**: 6×6 named cells (A1…F6) on the
  right half, fixed Manim coordinates, with `place_at_grid` / `place_in_area(obj, 'A1', 'C3')`
  [verified: `base_class.py`]. Two weaknesses [verified: `base_class.py`, `scope_refine.py`]:
  - The helper centres an object on its cell but never fits it to the cell.
  - The critic's "occupancy table" is regex-extracted from the code, not measured from rendered
    geometry.
- **QC.**
  - **ScopeRefine.** The error analyzer picks the smallest scope that can fix the error (line ±1,
    enclosing function, or a labelled `# === Animation for Lecture Line N ===` block). The LLM
    fixes only that block; the merge is AST-checked. Failing that, it escalates through a focused
    fix, a comprehensive review and a "COMPLETE REWRITE", then regenerates the section from its
    storyboard [verified: `scope_refine.py`].
  - **Critic.** Gemini 2.5 Pro watches each section MP4 next to a grid reference image. It checks
    obstruction of the lecture notes, overlap, off-screen long labels, grid violations and
    leftovers. It answers with JSON like `"Line X: self.place_at_grid(...)"`, which
    `GridCodeModifier` patches in without another LLM call; two rounds [verified:
    `prompts/stage4.py`; `scope_refine.py`].
- **Eval.** MMMC: 117 long-form 3Blue1Brown videos plus 339 clips, 13 categories [verified:
  §3.2]. Metrics: VLM "AES" on five axes, scored by Gemini 2.5 Pro on a 100-point scale; and
  **TeachQuiz**, quiz accuracy after watching minus accuracy under a prompt-based "unlearning"
  of the concept [verified: §3.3].
  - **Main results.** Direct code generation: AES 32.7–37.8, TeachQuiz 36.5–40.0. Code2Video
    with Claude Opus 4.1: AES 87.9 (layout 90.6), TeachQuiz 86.0. Human 3B1B: 99.7 / 97.1. Veo3:
    9.0 / 2.5 [verified: ICML Table 1].
  - **Ablation** (GPT-4.1, AES / TeachQuiz): full 79.0 / 82.0; without planner 38.1 / 40.5;
    without anchors 69.2 / 55.2; without critic 72.5 / 60.7 [verified: ICML Table 3].
  - **Anchor granularity** (layout score): none 45.2; free placement chosen by the model 48.8;
    4×4 76.1; **6×6 82.8**; 8×8 77.2 [verified: arXiv App. A.1.3 Table 7]. This is the cleanest
    controlled evidence that a discrete layout vocabulary beats free placement, though it is
    VLM-judged.
  - **TeachQuiz controls** (Opus 4.1): lecture text alone 24.0, animation alone 76.6, full video
    86.0, unrelated video 4.0 [verified: arXiv Table 5].
  - **Human study** (40 people): Code2Video layout **60.2** against the VLM's 90.6. The authors:
    "humans are highly sensitive to even brief occlusions, whereas VideoLLMs often miss such
    frame-level issues" [verified: §5, ICML Table 6].
- **Failure modes.** Brief occlusions the critic misses. Weak Attractiveness and Visual
  Consistency. Black or unusable retrieved assets. Without anchors the model falls back to
  "repeated vertical stacking" [verified: §5.2, App. A.1.3, App. A.1.6]. Overlap stays possible
  by construction, because cells don't size-fit and lecture text width is unbounded [inferred:
  from `base_class.py`].
- **Speed and cost.** 8.8–16.8 min and 19k–49k tokens per topic, or 4.9–6.9 compute-minutes per
  output minute [verified: ICML Tables 1–2]. Ablation (GPT-4.1): without parallelism 86.6 min vs
  15.4 (5.6×); naive retry instead of ScopeRefine 42.9 min and 49.8k tokens; full-code debugging
  39.2 min [verified: ICML Table 4]. A later paper reports agents like this spending "18–26 times
  the tokens of direct code generation" [verified: Huang 2026, §2].
- **Borrow for Ben.**
  - A named layout vocabulary shared by coder and critic, per style pack, with size-to-fit.
  - Critic output as a deterministic patch rather than prose.
  - Repair scoped to a labelled block (beat ids already exist).
  - Per-section parallel build and render.
  - TeachQuiz with its controls.
- **Avoid.** VLM as the final layout gate. The left-bullets / right-animation slide template.
  Silent output.

### OmniManim ("See Before You Code")

Sources: arXiv 2605.15585 v1 (Wuhan Univ., 15 May 2026); repo `AI4Learning-Club/OmniManim`
(6a6041f).

- **What.** The only paper with strong evidence for planning layout before code. The repo has no
  license and predates the paper: it lacks the layout model, whose release is "planned"
  [verified: GitHub API; App. C.3]. The headline method cannot be reproduced.
- **In → out.** A natural-language teaching requirement (about 22 words) → Manim code → video
  [verified: §3.1].
- **Architecture.** Four agents share a structured scene state [verified: §3.2]:
  - *Scene Agent*: objects, relations (`left_of`, `above`, `inside`), roles and a coarse timeline;
  - *Vision Agent*: a **trained** model that predicts a normalized box per object at sparse
    keyframes, coarse heatmap then a box denoiser;
  - *Code Agent*: "does not freely decide object positions"; it maps boxes to Manim coordinates
    and scale;
  - *Repair Agent*: routes each failure to the stage that owns it. Overlap, relation or overflow
    goes back to the Vision Agent; compile errors go to the Code Agent for that block only;
    ordering errors and leftovers go to the Scene Agent. At most one repair round.
- **Visual IR.** A scene graph plus boxes per keyframe. The training loss includes an
  **interpolation collision** term: boxes interpolated between keyframes at u = 0.25 / 0.5 / 0.75
  are penalized for IoU above a threshold. A layout is accepted only under collision, relation and
  boundary thresholds [verified: §3.2]. Training data: 1,000 Manim animations cut at create,
  transform and remove events, giving 22,579 (scene graph, layout) records [verified: App. B–C].
- **Audio.** Not in the paper. The public repo uses edge-tts with a `speak()` call that returns
  the clip duration, sentence-level and audio-first [verified: repo `code_gen.py`, `renderer.py`].
- **Eval.** EduRequire-500 (500 expert-written tasks, 120 subjects). CV metrics on frames sampled
  at 2 fps: pixel-level overlap detectors and a 6×8 density grid. Claude Opus 4.6 judges content
  [verified: §4.1, App. E].
  - **Main results (GPT-5.4).** Overlap / layout: direct generation 0.628 / 0.778, Code2Video
    0.598 / 0.742, OmniManim 0.763 / 0.931. Render@1: 0.812, 0.841, 0.907. Time: 108 s, 148 s,
    72 s [verified: Table 2].
  - **Ablation.** Without the Vision Agent: overlap 0.491. Without the interpolation loss: 0.734,
    with continuity −0.052 [verified: Table 4].
  - **Human study** (60 tasks, 4 blind raters each). Overlap: OmniManim 74.1 vs Code2Video 42.0
    (+32.1, p < 1e-5); +16.4 vs direct GPT-5.4 (p = 0.003) [verified: §5.2].
- **Caveats** [inferred: from the tables]:
  - The "no Vision Agent" ablation (0.491) is worse than one plain GPT-5.4 call (0.628), so part
    of the delta measures weak default heuristics.
  - The benchmark, metrics and judge are all the authors' own.
  - The public prompt tells the coder to prefer outline-only shapes because they "reduce false
    overlap detections": the metric is shaping the content [verified: `code_gen.py`].
- **Borrow for Ben.** Have the planner emit a box or region per object per beat, check it with
  the same clearance rules the geometry pass uses before any Manim is written, and make the coder
  honour it. Route failures to their owning stage. The public repo's helper layer (`fit_group`,
  `make_two_panel_page`, `limit_text_block`, a reserved subtitle band, "if group.width > 12:
  scale_to_fit_width(12)") is a usable starting vocabulary [verified: `code_gen.py`].

### SGA and PRISM: deterministic geometry

Sources: SGA arXiv 2607.18116 v2 (KAUST et al.); PRISM arXiv 2605.19382 (SJTU), repo
`positionprivacy/PRISM` (09ab747).

**SGA (Plug & Play Geometric Verification).** Code not public: the project page returned 404 on
2026-11-21, and the only repo is the human-evaluation site [verified].

- **What it does.** Wraps every statement of `construct()`, runs Manim without rendering and
  records per mobject: class, centroid, AABB, **Python variable name** and **creation line**
  [verified: §3.1].
- **Conflict handling** [verified: §3.2–3.5]:
  - Conflicts are found by exact AABB intersection and graded by coverage ratio.
  - It computes the **minimum separation vector**: the shortest axis-aligned shift that clears
    the overlap.
  - Five static patterns count as intentional overlap: enclosures, pointers, centering,
    containers, braces.
  - In motion it samples 11 times per animation, patches overlaps at t ∈ {0, 1} and **ignores
    mid-trajectory ones**.
  - The LLM gets ±5 source lines, the shift vector and target coordinates. The patch must parse
    or it is rolled back. One iteration.
- **Metric.** MVQS, deterministic: overlap, in-canvas fraction, a **legibility** floor (objects
  above a minimum scale), coverage band and grid occupancy [verified: §3.4].
- **Results** (117 topics × 4 backbones × TEA or Code2Video) [verified: Table 1, §4.3, App. 10]:
  - **Automatic.** Best case MVQS 62.97 raw → 64.54 with Code2Video's own VLM critic → **73.11
    with SGA**. SGA improves 7 of 8 configurations.
  - **VLM aesthetics scores** sit in an 85.9–96.4 band and correlate with MVQS at only
    ρ = 0.24 (n.s.).
  - **Humans, frame-level overlap.** SGA beat raw in 93.3% of comparisons and the VLM critic in
    56.7% (13.3% losses). The critic "frequently pushes elements beyond the canvas border".
  - **Intentional overlaps.** Readability raw 6.09, SGA 6.27, VLM critic 3.64: the critic
    "misinterprets valid overlap as a visual error".
  - **Whole-video preference** separates weakly (Krippendorff α = 0.208 vs 0.407 frame-level).
  - MVQS is computed on the same representation SGA optimizes [inferred]; the human frame study
    is the independent evidence.
- **Speed.** Scene-graph extraction takes under 5 s, against 30–90 s for a render; each iteration
  is 6–18× cheaper than render plus VLM [verified: §4.5].

**PRISM.**

- **What it is.** A benchmark of 10,372 EN/ZH instruction → Manim pairs with a deterministic
  auditor [verified].
- **The auditor** monkeypatches `Scene` to snapshot geometry after every `play()`, locking a
  snapshot just before removals ("the fullest moment") [verified: `scripts/audit_single.py`,
  `docs/spatial_audit.md`]. It flags three failures:
  - *out_of_bounds*;
  - *overlap*, measured as outline points inside the other object's outline polygon
    (point-in-polygon, not AABB);
  - *leak*, text escaping its container (ratio > 0.1).

  An AST pass injects `var.set(name="var")` after each assignment so reports name objects
  [verified].
- **Results.** The mean drop from execution success to spatial pass is **41.24 points**. Claude
  Sonnet 4.6, English: executes 0.803, passes spatially 0.263. GPT-5.4: 0.945 / 0.308. Gemini 3.1
  Pro: 0.778 / 0.572 [verified: Table 1].
- **Borrow for Ben** (detection is already at SGA's level; these add the fix and new classes):
  - Every violation carries a minimum separation vector, target coordinates, the variable name
    and the line.
  - Patch locally, AST-check, roll back on failure.
  - Add PRISM's container-leak and point-in-polygon checks.
  - Add a legibility floor.
  - Declare intentional-overlap patterns explicitly instead of judging them case by case.
  - Keep the live mid-motion check, which is stricter than SGA and PRISM and backed by
    OmniManim's interpolation result, but report rest-state and transient collisions as separate
    classes.

### LASEV ("Beyond End-to-End Video Models")

Sources: arXiv 2602.11790 v2 (Baidu), KDD 2026; project page `robitsg.github.io/LASEV`; repo
`RobitsG/LASEV` (demo videos only).

- **What.** A production system at Baidu: ">1M videos per day", logs from more than 20M videos.
  No source code is public [verified: abstract, §5.4, repo contents].
- **In → out.** A K-12 problem (Chinese language arts, middle-school maths) → about 2-min
  walkthrough with narration, an optional Manim illustration and an optional digital human
  [verified: §5.1].
- **Architecture.** Solve → (illustrate) → narrate, each stage conditioned on validated upstream
  output [verified: §4.1–4.3, Eq. 7–9]:
  - an Orchestrator plans the work and alone writes the alignment spec;
  - a Solution Agent produces step-by-step reasoning that is checked first;
  - an Illustration Agent writes Manim;
  - a Narration Agent writes segmentable narration.

  Backbone DeepSeek-R1, at most 3 refinements per stage [verified: §5.1].
- **Visual IR.** An *Executable Video Script* `S = (P, N, A)` [verified: §3.2, Eq. 2, §4.4]:
  - P: pedagogical content and assets;
  - N: narration segments;
  - A: step-to-time mapping, with style "mainly predefined in templates" and controllable slots.

  It is compiled deterministically: `V = Render_vis(P, A) ∥ Synth_audio(N)`. No example file is
  public.
- **Sync.** Segment-level. Each narration segment maps to a visual window; a computed
  `self.wait(T)` fills the gap between animation end and narration end [verified: §3.3
  footnote 3]. The TTS engine is not named.
- **QC.** Every artifact must pass three gates, `C_sem ∧ C_tool ∧ C_rule`: an LLM rubric with
  few-shot calibration examples, Python/Manim execution, and format and API rules. After 3 failed
  revisions the item is filtered, not shipped [verified: Eq. 5–6, §5.4].
- **Eval.** 1,003 problems, three certified teachers per video, 0–3 rubric [verified: §5.1,
  Tables 1–2, 5].
  - **Maths:** Usable / Publishable / Perfect 96.0 / 96.0 / 58.0 vs GPT-4o with improved
    prompting 94.0 / 86.0 / 52.0.
  - **Ablation (maths):** single agent 60.0 / 50.0 / 30.0; without few-shot examples 84.0 / 84.0
    / 30.0; without the tool (execution) gate 78.0 / 60.0 / 16.0.
  - **Production (>20M videos):** animation or LaTeX compile failures 0.90%; 96.42% shipped.
  - Baselines are single-model prompts only.
- **Failure modes.** "Presentation flaws" are the largest defect class (22% of maths videos)
  [verified: Table 4]. Strict rule critique lowers Perfect rate in Chinese [verified: §5.3]. In
  the demo frames, the worksheet template keeps text clear of collisions and the diagram slot is
  small [verified: inspection of 9 demo frames].
- **Cost.** At most $0.07 per 2-min video [verified: Table 3].
- **Borrow for Ben.**
  - A typed IR whose alignment and style parts belong to the harness and the style pack, not to
    the code-writing model.
  - Three kinds of gate per stage, each with a hard cap, then fail loudly.
  - Few-shot calibration examples for any LLM judge.
  - "Solve before you draw": check the reasoning chain and numbers before visuals.
- **Avoid.** The worksheet look; segment-level sync.

### ManimAgent (Jiang et al.)

Sources: arXiv 2606.30296 v3, EMNLP 2026; repo `jwj1342/Paper2Manim` (no license). "ManimAgent"
also names the inference pipeline in Silva et al. (2604.18364), a different work.

- **Architecture.** Storyboarder → memory retrieval → Coder → static check plus sandboxed render
  [verified: §3; `docs/architecture.md`]:
  - **Crash path.** A text reviewer gives a hint and the scene is **fully regenerated**, because
    "patching a broken script tends to inherit the same buggy structure". At most 2 tries; stop
    if the same error category repeats.
  - **Visual path.** Four keyframes go to a VLM that scores logic, layout and accuracy; a separate
    reviser rewrites; at most 2 rounds.
  - **Delivery.** It ships the **best-scoring** candidate, not the last one.
- **Memory.** A positive channel holds good scenes as soft references. A negative channel holds
  distilled "Known Pitfalls": trigger, root cause, fix recipe, anti-example, good example
  [verified]. 83.3% of retrieved positive memories concerned layout, pacing or formula rendering
  [verified: App. N].
- **Audio.** Narration is written to a word budget after the storyboard, then sped up or padded
  to fit the rendered video [verified: `prompts/narrator.md`, `voiceover/assembly.py`]. This is
  video-first.
- **Eval** (33 fixed probe tasks, GPT-5.5) [verified: Table 1, App. H–I]:
  - **Human Pass@1:** no memory about 62; VLM reflection only 68.5; a fixed Manim-code RAG library
    83.3; with 200 memory entries 84.9.
  - **Repair rounds:** 12.2 → 6.5.
  - **Reliability:** VLM vs human quality r = −0.17, and human raters barely agree with each other
    (Fleiss κ = −0.01).
- **Speed.** 19–31 min per task [verified: §4.5].
- **Borrow for Ben.**
  - Separate crash and visual budgets.
  - A "same error twice → stop" rule.
  - Keep-best delivery.
  - The Known-Pitfalls record shape for craft laws.
- **Avoid.** Duration-fitted narration. VLM scores as a gate.

---

## Per-system notes: declarative IR systems

### DataMagic

Sources: arXiv 2609.33403 (IEEE VIS 2026); repo `HKUSTDial/DataMagic` (MIT, 438 stars, commit
3a66365, 2026-10-02), including `skills/datamagic/`.

- **In → out.** Raw table plus query → narrated data video in Remotion (Vega-Lite / D3 / GSAP
  components) [verified: paper Fig. 1, §5.3].
- **IR: DVSpec.** A video is (meta, scenes); a scene is (id, type, content, narration, animation)
  [verified: §4.2–4.4]:
  - **narration** is an ordered list of sentence segments; after TTS each gets (text, start, end);
  - **animation** is (type, target_data, trigger, style);
  - **trigger** is the *index of the narration segment* that fires it, and the renderer converts
    it to a frame from the measured TTS duration;
  - **target_data** names data values (`{"sale_date": "2025-01-30"}`), not DOM ids, so references
    survive chart-type changes.
- **Architecture.** "Generate-then-Orchestrate". Story Planner, Data Manager and Visual Designer
  build candidate scenes in parallel; a Narration Director and Animation Coordinator select,
  order and synchronize them [verified: §5].
- **Eval** (109 samples, 60 datasets) [verified: Tables 1–2, §6]:
  - **Direct one-call Remotion generation:** execution 48.62% (DeepSeek-V3.2) to 86.24% (GPT-5);
    average quality 1.91–2.22 / 5.
  - **DataMagic:** execution 95.41–98.17%; quality 3.38–3.89 (Claude Sonnet 4 best).
  - **Animation score** 1.84 → 4.03, credited to narration-indexed triggering. It stays at 3.95
    even without the orchestration module, so the sync gain comes from the IR, not the planner.
  - **Judge:** Gemini 2.5 Pro, validated against three experts on 60 videos: Pearson r = 0.91,
    MAE 0.38.
  - **Time:** about 176 s vs 57 s for direct generation.
  - **User study:** task time 39.2 → 8.0 min vs a Claude Sonnet 4.5 + Remotion chat workflow.
- **Stated limitation.** Structured motion patterns "may suppress the more expressive animations
  an unconstrained model might attempt" [verified: discussion].
- **The repo today is an agent skill.** It is organised around a **recipe library**: "All 139
  cards include source, schemas and sample props"; the agent adapts a tested Remotion template
  instead of writing one [verified: `skills/datamagic/SKILL.md`]. Other parts of the skill
  [verified: `rules/styles/README.md`, `rules/self-review.md`, `rules/voiceover.md`]:
  - **Style packs** cover "visual, motion, narrative, and audio", in sections Key Characteristics
    / Tokens / **Banned** / Motion & Narration / Do-Don't.
  - **Self-review** sets numeric rules: "every label … sits above y≈840 (1080p)", "≤ 3 type sizes
    per frame", and audio "delayed with `<Sequence from>`, NOT trimmed with `<Audio startFrom>`".
  - **TTS:** edge-tts with WordBoundary events, one file per narration segment; word timing is
    used only "when an emphasis must land on a specific word".
- **Borrow for Ben.**
  - Animations bound to narration by reference and resolved to times by the harness. Ben's cue
    words already do this at word level; binding in one place would stop the scene code and
    `script.yaml` from duplicating it.
  - The style-pack shape with an explicit Banned list (matches decisions 1–2).
  - A library of tested scene recipes the agent adapts, rather than writing every scene from a
    blank file.
- **Avoid.** Its conservative motion vocabulary as a default for 3b1b / Welch.

### ALGOGEN, MoVer, LogoMotion, ExplainSpec

**ALGOGEN** (Xiamen Univ., Findings of ACL 2026, pp. 3168–3189).

- **Design.** It decouples algorithm execution from rendering [verified: §3.2–3.4]:
  - the LLM writes a Python *tracker* that runs the algorithm and emits schema-validated
    VTA-JSON (initial frame plus typed deltas, each tied to a pseudocode line);
  - the LLM writes one RSL instance, a JSON layout and style DSL;
  - deterministic renderers compile both to Manim, TikZ or Three.js.
- **Results** (200 LeetCode tasks, three open models) [verified: Tables 2–3, §5]:
  - Trace success 599/600 (99.8%) vs direct Manim render success 165/200 (82.5%).
  - Adding 12k tokens of Manim docs (RAG) **lowered** direct success to 79.0%; "over 80% of
    failures remain API misuse or logic drift".
  - Repair takes Pass@1 from 91.0% to 99.5% within 3 rounds; about $0.022 per task.
  - On Code2Video's AES rubric: 90.17 in 7.72 min vs Code2Video 74.90 in 68.10 min.
- **Code.** The paper's code URL returned 404 on 2026-11-21 [verified].

**MoVer** (Ma & Agrawala, Stanford; SIGGRAPH 2025 / ACM TOG; repo `jama1017/MoVer`, Apache-2.0).

- **What it is.** A first-order-logic DSL over an SVG motion program: motion type, direction and
  magnitude; Allen's 13 interval relations; rectangle-algebra spatial relations [verified: Table
  1, Fig. 2].
- **Pipeline.** GPT-4o writes both the animation (GSAP) and a MoVer program from the same prompt.
  The report of passing and failing predicates is fed back [verified: §4].
- **Results** (5,600 synthetic prompts) [verified: §5, Table 3]:
  - Correct on the first try for 58.8%; 93.6% within 50 rounds (mean 5.8).
  - Feedback ablation: additional prompts fixed with the full predicate report 34.8%; pass/fail
    only 19.2%; bare retry 12.1%. Specific, structured feedback roughly triples the repair rate.
  - Typical error: the LLM ignores object width and height when placing one object relative to
    another.
  - When the LLM writes a wrong verification program (4.9% of prompts), the pipeline would
    falsely report success for 75% of those.

**LogoMotion** (Columbia + Adobe, CHI 2025, arXiv 2405.07065) [verified: §4.3]:

- The canvas becomes HTML with per-layer ids and bounding boxes.
- *Visually-grounded repair* first diffs the last frame programmatically, layer by layer,
  against target boxes and opacity.
- Only on a mismatch does a VLM get the element id, a bug description and an **isolated** image
  pair, with other layers hidden: "Because VLMs often make mistakes when provided unnecessary
  visual context".
- It fixes 96% of detected errors within four attempts. It does not check intermediate frames.

**ExplainSpec / "Shorter Is Not Cheaper"** (Huang, Northeastern, arXiv 2610.32129, 2026-10-26).

- **Setup.** Pre-registered and controlled: a time-indexed declarative animation format played by
  a 600-line runtime, vs free-form HTML/JS, on 20 explanation tasks. Claude Opus, Sonnet and
  Haiku 5.5 at low effort (360 jobs), plus Qwen3-14B (240 jobs). Checkers read state through an
  observation contract (`seek(t)`, `getState()`), validated by mutation testing [verified:
  §3–4].
- **Results** [verified: Tables 2–8, §7]:
  - Specs were 25–48% shorter in answer tokens, but the Claude models reasoned far more before
    writing them. Total output fell significantly only for Opus, and latency fell for no model.
  - **Validity.** HTML/JS was 100% valid on the first try for all Claude models; specs 85–95%.
  - **Semantic pass after repair**, HTML vs spec: Opus 100 vs 95, Sonnet 95 vs 90, Haiku 93 vs 83.
  - **Qwen3-14B:** specs 33% valid vs 95%.
  - Lessons the authors draw: a format learned in context costs reliability, and runtimes should
    "surface runtime errors loudly instead of degrading gracefully".
- **Implication for Ben** [inferred]: do not make the model write a new DSL to save tokens. If a
  declarative layer helps, it should be the *harness's* representation (plan JSON, layout
  regions), with the model still writing the language it knows best, Python.

---

## Per-system notes: slide and document to video

### Paper2Video / PaperTalker

Sources: arXiv 2510.05096 v2 (Show Lab NUS; NeurIPS 2025 SEA workshop); repo `showlab/Paper2Video`
(MIT, 47beb50).

- **In → out.** LaTeX paper project, portrait and about 10 s of voice → static Beamer slides with
  cloned-voice narration, a red-dot cursor per sentence, burned-in subtitles and an optional
  talking head [verified: README, `src/pipeline_light.py`].
- **Architecture.** A scripted chain of four builders [verified: §4; code]:
  1. slides: one LLM call writes the whole Beamer deck, compiled with tectonic;
  2. subtitles: a VLM writes the narration *after* looking at the rendered slides;
  3. cursor: UI-TARS grounds each sentence's cursor description to a point; WhisperX gives the
     sentence spans;
  4. talker: F5-TTS voice clone, then Hallo2.
- **Layout idea: pick, don't tune** [verified: `slide_code_gen_select_improvement.py`,
  `prompts/select_proposal.txt`, §4.1]:
  - tectonic's `Overfull \hbox` warnings trigger the pass;
  - for frames containing figures, the harness renders scale variants 1 / 0.75 / 0.5 / 0.25 and
    tiles them in a labelled 2×2 grid;
  - the VLM must "Disqualify any option with overfull … choose the first slide in that order that
    is not overfull".

  The paper's rationale: models "are largely insensitive to small numeric changes". Text-only
  overfull frames are skipped in the released code.
- **Sync.** Per slide (audio length) and per sentence (cursor). Sentences are mapped to WhisperX
  words by *counting words*, so a tokenization mismatch shifts every later sentence. Subtitles
  are re-transcribed from the final video with Whisper base [verified: `cursor_gen.py`,
  `subtitle_render.py`].
- **Eval** (101 papers with author talks) [verified: Table 2, Fig. 6, Table 5]:
  - "+10% over humans" is a VideoLLM quiz score (0.842 vs 0.738). In the pairwise arena
    PaperTalker *wins* only 17.0% against the human videos.
  - Human ranking (10 people): human 4.6, PaperTalker 3.8.
  - The tree search adds **+0.12** to design on a 5-point VLM scale.
- **Speed.** 15.6 min without the talking head; per-slide parallelism is credited with 6×
  [verified: Table 3]. The printed $0.001 cost looks wrong [inferred: price arithmetic].
- **Borrow for Ben.**
  - Use the layout engine's own diagnostics as the trigger.
  - Generate deterministic variants (scale, band, wrap width) and let a VLM choose among rendered
    stills under a strict "disqualify clipped or overlapping, then maximise size" rule.
  - Reflowing layout for dense text.
  - Per-scene parallelism.
- **Avoid.** Narration written after the visuals. Word-count alignment. ASR-made subtitles.

### Bespoke

Sources: arXiv 2609.26540 v1 (MIT, Sep 2026); no code found.

- **In → out.** A seed lecture transcript, a target industry and a duration → a lecture of HTML
  slides with code-drawn charts and TTS narration; no talking head [verified: §3.1].
- **Architecture.** Five stages with one bounded loop [verified: §3.2, §4.4–4.5]:
  1. learning objectives (backward design);
  2. a timed plan;
  3. **the whole narration in one pass** "so the lecture has a single narrative arc", then a
     conversational-register pass;
  4. parallel visual subagents (ideation → execution → verification);
  5. progressive reveal and assembly with no LLM calls.
- **QC split.**
  - Programmatic first: "Duration arithmetic, schema checks, and detection of missing images or
    overflow run in ordinary code. The LLM is reserved for semantic judgments."
  - A cross-family validator: Claude Sonnet 4.6 generates, GPT-5.2 validates, "to reduce
    self-enhancement bias"; at most 3 rounds.
  - "On failure, only execution is retried; the ideation plan is kept."
  - Mayer's principles are named both as generation rules and as validator criteria.
- **Sync.** Slide elements are revealed "as the narrator introduces them"; timing is "derived
  from the narration and checked programmatically". The mechanism is not stated [verified:
  §4.5].
- **Eval** (25 domain experts, 92 videos, one rater each, anchored 5-point rubric whose midpoint
  is "comparable to a standard MOOC lecture") [verified: §5–6]:
  - 87% scored ≥ 3; mean 3.42.
  - Voice was rated lowest (3.16).
  - Cost about $0.22 per minute of video.
- **Reviewer complaints, usable as a regression list** [verified: §6.3]:
  - TTS reads "30" as "three zero";
  - no pause after questions;
  - "the narration dictates the formula before displaying it on the slide";
  - overlapping labels, cropped plots, text-heavy slides.
- **Borrow for Ben.**
  - Programmatic checks first.
  - A cross-family or fresh-context validator.
  - Freeze the plan and retry only execution.
  - Named pedagogy principles as lint and critic criteria.
  - The anchored expert rubric.
  - Its order (objectives → plan → whole narration → visuals) is direct support for Ben's
    audio-first order.

### NotebookLM Video Overviews

Sources: Google blog posts of 2025-07-29, 2025-08-25, 2025-10-13 and 2026-03-04; help page
`support.google.com/notebooklm/answer/16454555`.

- **What.** Narrated slides launched July 2025. Nano Banana illustrations in named styles
  (Classic, Whiteboard, Watercolor, Retro Print, Heritage, Paper-craft, Kawaii, Anime, plus Auto
  and a free-text **Custom**). A **Cinematic** format uses "Gemini 3, Nano Banana Pro and Veo 3",
  with Gemini acting "as a creative director" [verified: blog posts, help page].
- **Process.** Optional "producer notes" can be refined before rendering and freeze on Proceed.
  Generation "sometimes, more than 30 minutes". Videos "may contain inaccuracies or audio
  glitches" [verified: help page]. Google has published no pipeline, IR or sync details
  [verified: their absence].
- **Third-party eval** (VideoAgent's SciVidEval, 50 AI papers) [verified: VideoAgent Table 2]:
  - visual judge 3.16 / 10, the lowest of all systems;
  - asset match 31.99%: generated art does not reproduce technical figures;
  - human quiz 86.0% vs 90.0% for the authors' own videos.
- **Borrow for Ben.** Style as a named parameter with a Custom escape hatch. A reviewable plan
  artifact before the expensive render.
- **Avoid.** Image-model art for technical diagrams.

---

## Per-system notes: agent skills and engines

### 3brown1blue

Sources: repo `AmitSubhash/3brown1blue` (MIT, v0.3.1, fd9bf9c); PyPI `3brown1blue`.

- **What.** The current skill's inspiration: a Claude Code / Cursor skill (24 rule files,
  audience and domain profiles) plus a CLI [verified: README, `src/three_b1b/`].
- **Planning.** Research → **misconception analysis** ("show the misconception first …") →
  curriculum → scene plans → style contract → narration "timed to match the animation duration"
  [verified: `prompts.py`]. Inside an agent, it dispatches **one agent per scene**, each given
  context, 18 copy-paste rules and its scene plan [verified: `rules/scene-planning.md`].
- **Visual IR.** Six named layout templates (`FULL_CENTER`, `DUAL_PANEL`, `BUILD_UP`, …) and a
  fixed per-scene block (Template / LEFT / RIGHT / BOTTOM / anchors / cleanup), plus `safe_text()`
  and `labeled_box()` helpers [verified]. Its claim that "30-40% of scenes have spatial bugs"
  without the plan is unsourced [verified: no measurement in the repo].
- **Sync (video-first).** Each beat's duration is estimated by parsing `run_time` in the code;
  audio is then sped up 1.35× by default (2× maximum) or the last frame is frozen [verified:
  `voiceover.py`, `compose_voiceover.py`]. The current skill rightly dropped this.
- **QC.** Regex source audit plus frames at 10/25/50/75/90%; no automatic repair [verified:
  `audit_video.py`].
- **Still worth taking.**
  - The misconception step as an explicit planning field.
  - The template vocabulary as a *closed* list the planner must pick from. The current `show:` is
    free text [inferred: from the script contract].
  - One agent per scene.

### manim-voiceover

Sources: repo `ManimCommunity/manim-voiceover` (MIT, v0.4.0 of 2026-06-14, "Alpha").

- **Mechanism.** Audio-first per block: `with self.voiceover(text="… <bookmark mark='A'/> …") as
  tracker`. Bookmark times are linearly interpolated over character offsets between word
  boundaries [verified: `tracker.py`]:
  - Azure supplies the boundaries;
  - other services need Whisper (`stable-ts`);
  - with neither, it falls back to a straight line over the clip and warns.
- **Comparison.** The current skill already does the stronger version: script-level cues, real
  word times, cue repair. The one idea worth taking is the **block scope**: narration and its
  animations live together and the scene waits for the line to end, so drift can't accumulate.

### SenseNova code-video skill and model

Sources: repo `OpenSenseNova/SenseNova-Skills`, `skills/sn-code-video/` (MIT, 07e7ff8,
2026-11-13); model card `sensenova/SenseNova-6.8-Code2Video` (Apache-2.0, created 2026-10-24).

- **What.** SenseTime released an open 27B model, fine-tuned from Qwen3.8-27B, whose
  "recommended harness" is Claude Code with this skill [verified: model card]:
  - runs last "more than 10 hours and more than 2,000 turns";
  - a strong general model (Claude Opus 5.5) first expands the brief into `dense_prompt.md`;
  - output is `out/final.mp4` plus `SPEC.md` and `VERIFY.md`.

  The model card reports no benchmark [verified: model card, read 2026-11-21].
- **Core contract.** "A code video is a program `frame(t) → image`". Every renderer exposes
  `seek(t)`, with no wall clock and no unseeded randomness. Long films render in parallel chunks
  and are joined losslessly [verified: SKILL.md §3–4].
- **Spec and verification.** `SPEC.md` lists exact on-screen copy, facts and numbers, and one
  "must-have" per requirement. `VERIFY.md` records pass or fail per must-have with pixel evidence:
  "'drawn by `draw_pavilion()`' is not evidence" [verified: §2, §6].
- **Frame review.**
  - A **cold read first**: describe the still "as a stranger would" before comparing it to the
    brief.
  - Contact sheet, then **action strips** at 0.1–0.2 s spacing around each key action.
  - Measured minimums at 1080p: text at least about 28 px, subject at least about 1/3 of frame
    height.
  - Reading dwell of `letters / 15 + 1.5` s.

  [verified: §5; `references/explainer-diagrams.md`]
- **Sound** [verified: `references/sound-design-and-narration.md`, `scripts/sync_check.py`]:
  - edge-tts per line, with word timings shifted onto the measured speech onset ("edge-tts word
    offsets run about 40–55 ms early");
  - faster-whisper re-transcribes each line to **verify** the TTS said the script;
  - `sync_check.py` compares event times with audio onsets in the final file and fails if more
    than 10% are off by more than one frame.
- **Borrow for Ben.**
  - The SPEC must-have → VERIFY evidence pair, which formalizes the review gate.
  - Cold read before compare.
  - Action strips.
  - Numeric text and dwell minimums.
  - Whisper as a verifier of TTS rather than the timing source.
  - Chunked parallel renders.

### anything2explainer and HyperFrames

**anything2explainer.**

Sources: repo `Vincentwei1021/anything2explainer` (PolyForm Noncommercial, 3.5k stars,
dc21866).

- **What.** A Remotion explainer skill; the closest open analogue to Ben's skill.
- **Architecture.** Nine stages: research → narration + TTS timeline → storyboard (one line per
  shot) → **pilot** (the first 30 s for the user) → **parallel build** (5–7 shots per agent) →
  render + frame metrics → per-chapter QC agents → fix agents [verified: README].
- **Sync.** Audio-first. With edge-tts it requests `boundary='WordBoundary'`; without that it
  "silently degrades to interpolation", leaving subtitles off by up to half a second. Engines
  without timestamps synthesise per block, so block starts are exact. "Once the narration is
  voiced, the words are frozen — shot code hard-codes frame numbers" [verified: `tts_build.py`,
  README].
- **QC.**
  - **Static `selfcheck.py`:** shot coverage, plus every on-screen string checked against the
    fact list.
  - **Frame metrics:** hero size, empty stretches, stillness by changed-pixel count.
  - **Beat-timing rule:** a key element late by more than 3 frames or early by more than 6 is a
    medium defect; probe frames at −6, 0, +3 and +8 around each subtitle start.
  - **Text fitting:** from a per-font em-width table, shrinking to 78% at most; "beyond that,
    change the copy".

  [verified: `selfcheck.py`, `reference/agent-qc-rules.md`, `template/src/common/textfit.ts`]
- **Lessons log** [verified: `reference/lessons.md`]:
  - text left on screen 0.97–1.7 s was unreadable, so the rule became ≥ 2.5 s;
  - a group `scale` shrank text below the floor, so "multiply every font size by the group scale";
  - "don't copy the agent's self-assessment".

**HyperFrames.**

Sources: repo `heygen-com/hyperframes` (Apache-2.0, about 88k stars, e0d8440).

- **Render model.** HTML, CSS and paused GSAP timelines, seeked frame by frame in headless Chrome
  and encoded with FFmpeg [verified: README].
- **`check --json`** gives contract lint with `Fix:` lines and craft warnings [verified:
  `skills/hyperframes/SKILL.md`, `references/review.md`]:
  - `line_unread`: a line on screen too briefly to read;
  - `dead_stretch`: more than 3 s with nothing changing;
  - `text_below_floor`: text under 2.6% of the frame's short side;
  - `first_frame_empty`;
  - overlap and overflow must be *declared* with `data-layout-allow-overlap`.
- **Review sheets:** beats, a cut strip (−0.2 s to +0.2 s), and a 360 px phone-width sheet.
- **Review rules:** "Trust the numbers over your eye where they disagree: a clipped label or a
  0.6 s line looks fine on a contact sheet"; "Never score the film out of 10: a score finds
  nothing to fix"; an optional fresh sub-agent sees only the storyboard and sheets.
- **Explainer type sheet:** "the voice is the clock … Reveal each part when the voice names it",
  plus a list of tells (bullets sliding in, icons in circles, three cards in a row) [verified:
  `references/types/explainer.md`].

**Borrow for Ben (both).**

- Numeric sync tolerances against word times, which is sharper than `check_sync`'s silent-cue
  test.
- Reading-dwell and minimum-size checks.
- Declared intentional overlaps.
- Cut strips and a phone-width sheet.
- A per-style list of banned tells.
- Strings audited against the source notes.
- Pilot first, then parallel build.

### Remotion AI tooling

Sources: `remotion-dev/skills` (6f55706), `remotion-dev/template-prompt-to-video` (8f314ab),
remotion.dev/docs/ai; Remotion License (free for individuals and companies of up to 3 people).

- **Model.** Every frame is a pure function of `useCurrentFrame()`, so any single frame renders
  alone with `remotion still` [verified: `remotion-markup/timing.md`, render skill].
- **Text layout before render.** `@remotion/layout-utils` provides `measureText()`, `fitText()` and
  `fillTextBox()`, which detects overflow at a line limit. The skill sets margins (≥ 80 px from
  the sides at 1080p) and minimum sizes (headline ≥ 84 px) [verified: skills files].
- **The prompt-to-video template.** GPT-4.1 story → DALL·E images → ElevenLabs speech **with
  character-level timestamps** → a Zod-validated timeline JSON (`startMs`, `endMs` per element
  and caption), built deterministically from those timestamps, so there is no Whisper pass
  [verified: `cli/service.ts`, `cli/timeline.ts`, `src/lib/types.ts`].
- **Agent inspection.** WebMCP lets an agent seek and read Studio state (`seek_to_frame`,
  `get_outlines`), but it has no screenshot tool [verified: docs].
- **Cost of switching from Manim** [inferred: no equivalent in the skills docs]:
  - LaTeX would come through KaTeX or MathJax;
  - Manim's morph vocabulary (`TransformMatchingTex`) has no equivalent.
- **Borrow for Ben.** Seekable rendering for QA stills. Text measured before placement. TTS-native
  timestamps.

### ManimGX

Sources: repo `academa-labs/manimgx` (1fb4dd7, 2026-10-23), docs at manimgx.academa.ai, PyPI
`manimgx` 0.1.1.

- **What.** "The animation engine for agents": the Manim CE Python API on a Rust and wgpu core.
  MIT code, but the native wheels are GPL-3.0+ because they bundle x264. Python ≥ 3.13; v0.1;
  repo created 2026-10-05 [verified: README, pyproject, PyPI]. Welch Labs' `custom_gx/` already
  targets it (see [README.md](README.md)).
- **Agent features** [verified: `docs/content/user-guide/rendering.md`,
  `coming-from-manim-ce.md`, `sound-and-voice.md`, `cli/diagnostics.py`, `audio/sound.py`]:
  - **`manimgx inspect scene.py`** runs without encoding and draws only the inspected moments
    (default: the end of each play or wait; `-t 1.5,8,end` for chosen times). It writes a
    storyboard sheet and checks:
    - mobjects cut off by the frame;
    - text over text, a line through text, a fill over text;
    - text too small.

    Problems are named **by variable name and line**, outlined in red, and exit with code 1. "Checks
    cover the sampled moments, not every frame."
  - A fully typed API, so a type checker catches unknown names and wrong arguments before a
    render.
  - **`self.say("The derivative of [x squared] is [two x].", Indicate(square), Write(deriv))`**:
    each bracketed span starts its animation on its first word, and "If you change the words,
    the animations follow". Word times come from the voice's own timestamps (default ElevenLabs
    v3 via fal.ai) or are estimated by letter count.
- **Compatibility.** "Most Manim CE code runs" after renaming the import. `Tex` / `MathTex` are
  converted to **Typst**, and "LaTeX packages and `\def` don't convert" [verified:
  `coming-from-manim-ce.md`].
- **Speed (vendor benchmark, Apple M4 Pro, 2026-10-07).** 36.2 s of 1080p60 video across five
  scenes: ManimGX 3.08 s, ManimGL 35.28 s, ManimCE 278.83 s, which is "90.6×" overall. Per 2D
  scene the gap is much smaller: matrix 7.14 vs 0.36 s (about 20×), pendulums 4.75 vs 0.76 s
  (about 6×) [verified: `benchmarks/README.md`]. There are no Linux numbers, and without a GPU it
  falls back to Mesa lavapipe [verified: README; inferred: unbenchmarked].
- **Borrow for Ben.** A spike under decision 4: port one demo, time it on the DGX, compare
  `inspect` findings with `check_layout.py`, and test Typst output on the 3b1b `MathTex` set.

## Contrast: agents on generative video

- **MovieAgent** (Show Lab, arXiv 2503.07314). Director, screenwriter, storyboard-artist and
  location-manager agents plan shots for generative video models [verified: abstract].
- **FilmAgent** (arXiv 2501.12909). Agents act in a Unity set with a closed catalogue of
  locations, positions and shots, using Critique-Correct-Verify loops; human score 3.98 / 5 on
  15 ideas [verified: abstract; catalogue size from a search summary only].
- **What they show by contrast.** A wrong frame from a video model is a resample, not a code
  edit, and there is no text layout to verify. One survey puts it as: "slow dolly-in" "may be
  interpreted loosely by a generator, whereas a geometric trajectory or engine camera is executed
  exactly" [verified: arXiv 2610.40191 §3.1]. In Paper2Video's benchmark, Veo3 reached 8 s
  clips, "blurred text" and a 1.2% arena win rate; in Code2Video's, AES 9.0 [verified: both
  papers]. FilmAgent's closed action catalogue is the same idea as a closed layout and motion
  vocabulary.

## Brief entries

**Manim agents and benchmarks**

- **VisualEDU** (EMNLP Findings 2025, repo `UchihaIchigo/VisualEDU`) [verified: Table 4, §6.4,
  `feedback_visual.py`].
  - Its VLM looks at **one frame at 3/5 of the video** and answers yes/no on overlap, font
    uniformity and a fixed left/right layout.
  - Visual feedback added **+3%**, and it *lowered* executability (Claude 3.7 0.825 → 0.730).
- **ManimTrainer (Silva et al.)** (arXiv 2604.18364) [verified: §3–4].
  - SFT plus GRPO with a visual-similarity reward, and render-in-the-loop with docstrings of the
    APIs the code calls.
  - Best: 94% render success with 3 attempts. Code metrics stop predicting what renders once
    agentic repair is used.
- **PIVOT** (arXiv 2609.24083, EMNLP 2026, Apache-2.0) [verified: Tables 2, 4; repo
  `manim_generator.py`].
  - The paper claims a multimodal verification harness, with layout 9.10 vs 7.87 without it
    (VLM-judged).
  - The public code's overlap check is a **text-only LLM review of the code**, and narration is
    muxed by padding or freezing.
- **TeachMaster** (arXiv 2601.04204) [verified: PDF §2–3].
  - Narration is written from the page code. A sync agent injects waits at event anchors; a
    layout agent scans for coordinates heuristically.
  - About 2.46 min of production per minute of video. 75.2% of pages need no manual fix.
- **LLM2Manim** (arXiv 2604.05266) [verified: §II].
  - A slot-based plan with a symbol ledger and cue → event markers.
  - Overlaps are fixed "by a quick human edit".
  - 100 students: post-test 83% vs 78% for slides (p < .001), learning gain d = 0.67.
- **ManiBench** (arXiv 2603.13251) [verified]. Documents 145 ManimGL → CE incompatibilities;
  models mix the two APIs. Relevant if the engine changes (decision 4).
- **PhysicsSolutionAgent** (arXiv 2601.13453) [verified: §5–6]. One VLM screenshot pass moved
  layout **3.64 → 3.66**; "static screenshots miss temporal properties".
- **Manimator** (arXiv 2507.14306; repo stale since 2025-02-14) [verified: Tables 1–2,
  `gradio_app.py`].
  - Two LLM calls (plan, code). On failure it re-runs blind: the error is not fed back.
  - Auto-judged layout 0.853 vs **human 0.52**, the largest gap of any dimension.
- **Generative Manim / Animo** (Apache-2.0) [verified: `chat_generation.py`,
  `training/rendering/reward.py`].
  - A `get_preview` tool renders PNG frames back into the chat, "up to 4 times".
  - The GRPO reward pays 1.0 for rendering plus 0.1 per `self.play()`, with no layout term.
- **Math-To-Manim** (MIT, 2.9k stars, promotional README) [verified: `docs/ARCHITECTURE.md`,
  `src/neon/tools.py`, legacy pipeline guide].
  - A **reverse prerequisite tree** ("What must I understand BEFORE X?").
  - Typed JSON artifacts between stages (`storyboard.json → scene_spec.json →
    validation_report.json`).
  - Render repair against a frozen spec that never re-plans.
  - A `verify_math` tool that numerically checks constants.
- **manim-generator** (makefinks, MIT) [verified: README, `prompts/review_prompt_enhanced.txt`,
  `utils/rendering.py`].
  - A writer / reviewer loop over execution logs.
  - The reviewer sees the "highest density" frame: the most non-black pixels among 30 samples.
  - It drives the public Manim Bench leaderboard; scoring method not readable.

**Slide and document systems**

- **EvoPresent / PresAesth** (ICLR 2026, MIT) [verified: Table 3, `layout_checker.py`].
  - The checker sees HTML, **DOM bounding boxes** and a screenshot; it accepts at ≥ 8.7, makes
    at most 3 attempts, and reverts on regression.
  - Its trained critic and every general VLM score about **0.39 F1** at naming slide defects.
  - Pairwise "which is better": 0.88 for PresAesth, 0.77 for GPT-4o.
- **VideoAgent** (arXiv 2509.11253, ICMR 2026) [verified: §3.3–3.4, Tables 2–4].
  - Relative layout hints in the storyboard; style presets injected into code; a VLM check on
    sampled video frames.
  - Manim clips are **time-scaled** to the narration.
  - About $0.35 per video.
- **PresentAgent** (EMNLP 2025 demo; no license) [verified: `backend.py`, Table 3].
  - Slot schemas with **character budgets** keep text inside PPTX template slots.
  - Silent fallbacks: 3 s of silence on a TTS error, and "This is the N page" as narration.
  - Evaluated on 5 documents with 3B / 7B judges.

**Other**

- **ViviDoc** (arXiv 2603.27991): interactive documents. Its State / Render / Transition /
  Constraint spec is a compact IR for one animated beat [verified: §3].
- **Reels-RSI** (arXiv 2610.14495) [verified: abstract].
  - Lessons a static check can catch are compiled into rules, each with must-fail and must-pass
    examples.
  - For a weaker director: 30 violations unguarded vs 5 guarded.
  - Pairwise VLM judges picked the second-shown reel 62–81% of the time.
- **Motion Canvas** [verified: gh api, `VideoZero/skills`].
  - No upstream code commits since 2025-02-16; the active fork `canvas-commons` has 302 stars.
  - The only agent project of note is an HTTP plugin for seek and screenshot.
  - A risky base.
- **Surveys** (arXiv 2608.28122, 2609.06758, 2610.40191) [verified: §7.3, §4.4.1, Fig. 1]:
  - "A global score may support candidate selection or stopping, but it cannot by itself identify
    a local repair."
  - For expository video, "playback feedback must identify both the faulty interval and its
    upstream channel".

---

## Cross-system synthesis

### Recurring architecture patterns

1. **Plan, then code, then repair; one model, many prompts.** Most systems use the same model as
   planner and coder (TEA, Code2Video, OmniManim's LLM parts, ManimAgent). A distinct critic is
   rarer: Code2Video, ManimAgent, Bespoke, EvoPresent [verified: per section].
2. **Typed, persisted intermediate artifacts.** LASEV's `(P, N, A)`, DataMagic's DVSpec,
   Math-To-Manim's JSON chain, SenseNova's SPEC.md / VERIFY.md, anything2explainer's timeline and
   storyboard [verified]. They let a failure be traced to "the specification, the source
   material, or the generated candidate" [verified: arXiv 2610.40191 §3].
3. **Route repairs to the stage that owns the failure; freeze everything upstream.**
   - OmniManim: layout → planner, crash → that code block, order or leftovers → scene plan.
   - Bespoke: "only execution is retried; the ideation plan is kept".
   - Math-To-Manim: render repair never re-plans.
   - Code2Video: ScopeRefine.

   [verified]
4. **Programmatic checks first, LLM only for meaning** (Bespoke states it outright; LASEV's three
   gate types; SGA; HyperFrames: "Trust the numbers over your eye") [verified].
5. **Bounded loops that keep the best.** Typically ≤ 3 rounds (Bespoke, EvoPresent, VideoAgent,
   LASEV, ALGOGEN). Stop when the same error repeats (ManimAgent). Revert on regression
   (EvoPresent). Ship the best candidate, not the last (ManimAgent) [verified].
6. **Scene-level parallelism.** Code2Video 5.6×, PaperTalker 6×, anything2explainer (8 build
   agents), 3brown1blue (one agent per scene), Bespoke (parallel visual subagents), SenseNova
   (chunked renders). Each first freezes the timeline [verified].
7. **Closed vocabularies instead of free choice.**
   - Layout: Code2Video's grid, 3brown1blue's templates, LASEV's slots.
   - Motion and scene types: DataMagic's recipes and scene types, FilmAgent's catalogue.
   - Verification: MoVer's predicates.

   [verified]
8. **Experience memory.**
   - ManimAgent's pitfalls memory (fewer repair rounds; small quality gain over a fixed RAG
     library).
   - Reels-RSI: rules compiled with tests.
   - anything2explainer's lessons log.
   - Ben's craft laws.

   [verified]

### Intermediate representations compared

| IR | Who | Holds layout? | Holds timing? | Model writes | Evidence |
|---|---|---|---|---|---|
| Free-text plans → free code | TEA, Manimator, current skill's `show:` | prose only | narration cues / bookmarks | Manim code | layout weakest dimension (TEA 0.57–0.61; Manimator human 0.52) |
| JSON storyboard + anchor grid | Code2Video | named cells (centre only) | no audio | Manim code with `place_at_grid` | grid vs free placement: VLM-judged layout 48.8 → 82.8 |
| Scene graph + keyframe boxes | OmniManim | normalized boxes per keyframe, interpolation-checked | coarse temporal plan | relations; boxes come from a trained model | human overlap +16.4 vs direct, +32.1 vs Code2Video |
| Symbolic scene graph *from code* | SGA, PRISM, ManimGX `inspect`, current geometry pass | measured AABBs / outlines | sampled per play | n/a (extracted) | humans prefer SGA frames 93.3% vs raw |
| Typed executable script (P, N, A) + templates | LASEV | template slots | step-to-time alignment owned by the orchestrator | content and narration; Manim for illustrations | 0.90% compile failures over 20M videos |
| Declarative spec, narration-indexed triggers | DataMagic DVSpec | scene type + layout params | trigger = narration segment index | the spec, compiled to Remotion | execution 49–86% → 95–98%; animation 1.84 → 4.03 |
| Trace + style DSL → deterministic renderer | ALGOGEN | RSL templates | trace steps | a Python tracker + RSL JSON | 99.8% vs 82.5% success |
| Time-indexed declarative animation | ExplainSpec | objects with expressions | steps with durations | the spec | *not* cheaper; less reliable than HTML/JS |
| Reflowing document (Beamer / HTML / PPTX slots) | PaperTalker, EvoPresent, Bespoke, PresentAgent | the engine reflows; slots have character budgets | per slide / reveal | markup | no coordinates planned; overflow caught by the engine |
| Word-timestamped timeline | Remotion template, anything2explainer, ManimGX `say()` | n/a | from TTS timestamps | timeline or bracketed spans | rewording re-times automatically (ManimGX, DataMagic) |
| SPEC must-haves → VERIFY evidence | SenseNova | measured minimums | frame count, events | any renderer via `seek(t)` | none published |

[verified: per section; "Evidence" cells cite the numbers given above]

What the comparison shows [inferred: from the table and the ExplainSpec study]:

- **The reliability gains come from moving decisions out of the model.** Systems where the model
  writes free code and decides layout and timing itself (TEA, Manimator, direct baselines) have
  the worst layout. Systems where a template, a planner, a renderer or a reflow engine owns
  layout and timing have the best reliability (LASEV, ALGOGEN, DataMagic).
- **That costs expressiveness.** DataMagic names "conservative" motion, LASEV produces worksheet
  cards, and TEA's template flow scores high on Logical Flow "at the cost of expressiveness"
  [verified].
- **Changing what the model writes is not the source of the gain.** ExplainSpec found a new DSL
  does not make frontier models cheaper or more reliable.
- **The 3b1b / Welch target needs free motion,** so the design that follows is **constrained
  code**:
  - the model still writes Manim-style Python;
  - placement goes through style-pack regions with size-to-fit, checked before code;
  - timing goes through narration-bound calls;
  - verification goes through the harness.

### Visual and layout quality approaches, ranked by evidence

| Rank | Approach | Best evidence | Weak points |
|---|---|---|---|
| 1 | **Constrain layout before code**: box or region plan, anchor vocabulary, templates, reflow engines | OmniManim blinded human study (overlap +16.4 vs direct, p = 0.003; +32.1 vs Code2Video); Code2Video anchor ablation (48.8 → 82.8, VLM-judged); LASEV production (0.90% compile failures over 20M) | OmniManim's planner is unreleased and its ablation baseline is weak; Code2Video's grid doesn't size-fit; templates limit style |
| 2 | **Deterministic geometry verification with computed, code-attributed fixes** | SGA human frame study (93.3% vs raw, 56.7% vs VLM critic); PRISM's 41-point execution-vs-spatial gap; LogoMotion 96% of detected errors fixed within 4 tries; MoVer predicate feedback 34.8% vs 19.2% (pass/fail) vs 12.1% (retry) | MVQS is circular; SGA ignores mid-motion overlaps |
| 3 | **Measure text before placing it; enforce budgets** (`fitText`, a fit floor then rewrite, character budgets per slot, minimum size after transforms, reading dwell) | practitioner rules (Remotion, anything2explainer, PresentAgent, HyperFrames, SenseNova) and their lessons logs | no controlled study |
| 4 | **VLM picks among deterministic variants** | PaperTalker +0.12 / 5 design; EvoPresent pairwise accuracy 0.88 (trained) and 0.77 (GPT-4o) vs defect-naming F1 about 0.39 for all models | small measured gain |
| 5 | **VLM critic edits from rendered frames** | Code2Video critic −6.5 AES when removed (VLM-judged) | humans rate Code2Video layout 60.2 vs VLM 90.6; VisualEDU +3% with lower executability; PhysicsSolutionAgent 3.64 → 3.66; the SGA critic damages intentional overlaps and pushes objects off-canvas |
| 6 | **Prompt-only layout rules** | none positive | TEA layout stays the weakest dimension; Manimator human layout 0.52 |

[verified: per section]

**Where the current skill stands** [inferred: comparing the skill with the table]:

- **Already at the top of rank 2 for detection.** It extracts geometry without rendering
  (SGA-like), checks live collisions during motion (stricter than SGA and PRISM, and supported by
  OmniManim's interpolation result), and uses a static name and signature gate.
- **Missing rank 1:** no plan before code; `show:` is free text.
- **Missing the fix half of rank 2:** no shift vectors, targets or variable names in violations.
- **Missing rank 3.**
- **Its frame review spends vision on geometry**, which ranks 5. Meaning is where vision is
  irreplaceable: "does the frame say what the voice says", which TEA's Visual Relevance tracked
  humans on (ρ = 0.72).

**Mid-motion overlaps** [verified: per section]:

- SGA ignores transient overlaps; PRISM audits rest states only.
- OmniManim penalizes in-between collisions, and dropping that cost −0.029 overlap and −0.052
  continuity.
- Keep the live check, but report rest-state and transient collisions separately, with
  intentional overlaps declared.

### Audio-visual sync approaches

| Approach | Who | Anchor precision | Notes |
|---|---|---|---|
| Video-first fitting: stretch or pad audio, freeze frames, time-scale clips | 3brown1blue, ManimAgent, PIVOT, VideoAgent | poor | Ben already rejects it |
| One audio clip per slide | PresentAgent, PaperTalker, EvoPresent, NotebookLM (inferred) | slide | static frames |
| Segment windows + computed wait | LASEV | sentence | owned by the orchestrator, not the coder |
| Narration-indexed triggers resolved at render | DataMagic | sentence | animation 1.84 → 4.03; rewording re-times itself |
| Block-scoped audio-first | manim-voiceover, TEA, OmniManim repo | block, or word with Azure / Whisper | drift stays local |
| Word-level from TTS-native timestamps | Remotion template (ElevenLabs characters), ManimGX `say()`, anything2explainer and SenseNova (edge-tts WordBoundary) | word | no STT pass; edge-tts runs 40–55 ms early, so correct to measured onset |
| Word-level from STT after TTS | **current skill** (Whisper), PaperTalker (WhisperX for the cursor) | word | works with any TTS; needs `cue_doctor` / `cue_repair` when STT rewrites numbers |

[verified: per section]

What to take from this [inferred: from the table]:

- **Ben's granularity is the best in the field.** What others add is *where the binding lives*
  and *how sync is verified*:
  - **One binding.** In ManimGX `say("… [two x] …", anim)` and DataMagic triggers, the animation
    is attached to its words in one place. In the skill, cue words live in `script.yaml` and
    `wait_until("cue")` calls in the scene code.
  - **TTS timestamps as the source.** If the OpenRouter voice returns word or character timing,
    use it and turn Whisper into the check (SenseNova). Whether Grok Voice through OpenRouter
    returns timestamps was not checked.
  - **A numeric check.** Element appearance against cue time with tolerances (late by more than 3
    frames or early by more than 6 at 30 fps; anything2explainer), plus an onset check on the
    final mix (SenseNova `sync_check.py`). This is stricter than "is there motion in the cue
    window".
- **Bespoke's top complaint confirms the risk.** "Narration dictates the formula before
  displaying it" [verified]: reveal lag is the defect viewers notice.

### Evaluation methods worth adopting

1. **Treat VLM layout scores as uncalibrated.** Every study that checked found them off from
   humans [verified]:

   | Study | VLM / auto judge | Humans |
   |---|---|---|
   | Code2Video | layout 90.6 | layout 60.2 |
   | Manimator | layout 0.853 | layout 0.52 |
   | TEA | Element Layout metric | ρ = 0.42 with humans |
   | SGA | aesthetics score | ρ = 0.24 with geometry (n.s.) |
   | ManimAgent | quality score | r = −0.17 with humans |
2. **A deterministic spatial pass rate on a fixed topic set** (PRISM-style: every rest-state
   segment clean) as the regression metric for layout.
3. **TeachQuiz** with its controls (text only, animation only, unrelated video). It is cheap, but
   a VLM quiz saturates (VideoAgent ≥ 95%), so use hard questions or people.
4. **Blinded paired human comparisons on frames, not whole videos.** Agreement was α ≈ 0.41
   frame-level vs 0.21 video-level (SGA).
5. **An anchored expert rubric** with a "comparable to X" midpoint (Bespoke), and Usable /
   Publishable / Perfect rates (LASEV).
6. **For any pairwise judge:** randomize order (62–81% position bias, Reels-RSI), judge in both
   orders (PaperTalker), and never let the judge that gates revisions also report the headline
   number (ManimAgent).
7. **Cost per output minute** for comparing designs: Code2Video 4.9–6.9 compute-minutes, Bespoke
   $0.22, LASEV ≤ $0.035; ALGOGEN about $0.02 per task.
8. **Reviewer complaints as a regression checklist** (Bespoke's list; anything2explainer's
   lessons).

[verified: per section]

### Render-speed levers

[verified: per section]

- **Parallel per scene or chunk.** Code2Video 86.6 → 15.4 min; PaperTalker 6×; SenseNova chunked
  joins; Remotion Lambda.
- **No encoding inside the loop.** The current skill's geometry pass, ManimGX `inspect`,
  Code2Video's `-ql` debugging. Avoid TEA's 1080p60 retries.
- **Localized repair.** ScopeRefine: 15.4 min vs 39–43 min for full-code fixes.
- **Seekable frame functions.** Remotion, HyperFrames, SenseNova `seek(t)`, ManimGX `inspect -t`:
  one QA still costs one frame, not a replay of `construct()`.
- **A faster engine.** ManimGX: about 6–20× on 2D scenes (vendor benchmark, M4 Pro).
- **A deterministic renderer from an IR.** ALGOGEN 7.7 min vs Code2Video 68 min per task, but
  only for a narrow domain.

---

## Borrow / avoid, judged against the current skill

### Already ahead of the field (keep)

- Word-level, audio-first sync from real timestamps, with baked pauses. No system read does
  better; most sync per slide or stretch audio [verified: sync table].
- A geometry pass without encoding, plus live collision sampling during motion. This goes beyond
  TEA, Code2Video and SGA, and matches PRISM and ManimGX [verified: layout ranking].
- A static name and signature gate before render. TEA and ALGOGEN show API hallucination is the
  dominant failure, and doc RAG made it worse [verified].
- Narrative-first planning with a viewer contract. Bespoke, the only system here rated by domain
  experts, also writes the whole narration in one pass before any visuals (87% rated at or above
  the MOOC midpoint). Visual-first narration (PaperTalker) wins only 17% against human talks
  [verified: Bespoke §6; PaperTalker Table 2].
- Craft laws as experience memory. ManimAgent and Reels-RSI support the idea; see item 9 below for
  the upgrade.

### Borrow (ordered by expected impact on the two pains)

1. **Layout before code, per style pack.** [verified: OmniManim, Code2Video, LASEV, 3brown1blue]
   - Each style pack defines a closed set of named regions and bands, with size-to-fit.
   - Each beat in `script.yaml` names its region per object instead of free-text `show:`.
   - A deterministic check runs on the plan, including interpolated in-between states, before any
     Manim is written.
   - The coder places only through region helpers.
2. **Computed fixes in every violation**, carrying [verified: SGA, PRISM, ManimGX]:
   - variable name (inject names via AST as PRISM does);
   - creation line;
   - minimum separation vector and a target region;
   - then a local, AST-checked patch with rollback.
3. **Text measured and budgeted before render**: [verified: PresentAgent, anything2explainer,
   HyperFrames, SenseNova]
   - character and line budgets per region in `lint_script.py`;
   - fit with a floor, then "change the copy";
   - minimum rendered text size after group scaling (28 px at 1080p);
   - reading dwell `letters / 15 + 1.5` s, or HyperFrames' `line_unread`.
4. **New deterministic classes**: [verified: PRISM, ManimGX, HyperFrames, SGA]
   - container leak;
   - point-in-polygon overlap for curves and diagonals;
   - line-through-text and fill-over-text;
   - declared intentional overlaps;
   - rest-state vs transient collisions reported separately.
5. **Re-aim the frame review at meaning.** [verified: SenseNova, HyperFrames, LogoMotion,
   EvoPresent, PaperTalker, Bespoke]
   - Cold read before comparing with the script.
   - "Do the pictures tell the story with the words covered."
   - Crop or isolate the element in question.
   - Feed the geometry report alongside the pixels.
   - Ask the VLM to *choose* among deterministic variants rather than tune numbers.
   - Use a fresh-context or other-family reviewer for the final pass.
6. **One narration binding** (`say()`-style bracketed spans or narration-indexed triggers), so a
   rewording re-times itself; TTS-native word timestamps where the provider returns them, with
   Whisper as a transcript check [verified: ManimGX, DataMagic, SenseNova, Remotion template].
7. **A numeric sync check.** Element appearance against cue word with late and early tolerances,
   plus an audio-onset check on the final mix [verified: anything2explainer, SenseNova].
8. **Routed, bounded repair with frozen upstream.** Layout → re-plan regions; crash → the failing
   beat block; leftover or order → beat plan. Keep-best and "same error twice → stop" [verified:
   OmniManim, Code2Video, ManimAgent, Bespoke].
9. **Craft laws as executable rules.** Each law that a check can catch becomes a rule with a
   must-fail and a must-pass example. ManimAgent's Known-Pitfalls shape (trigger, root cause,
   fix, anti-example, good example) fits the rest [verified: Reels-RSI, ManimAgent].
10. **Scene-parallel build and render after a pilot.** Freeze timing, render the first scene for
    review, then fan out one agent per scene [verified: Code2Video, anything2explainer,
    3brown1blue].
11. **An engine spike on ManimGX** (decision 4). It bundles inspect, typed API, `say()` and a
    6–20× speed claim. Risks: v0.1, Typst instead of LaTeX, GPL wheels, no Linux numbers
    [verified: ManimGX docs].
12. **Style packs shaped like DataMagic's**: Tokens / Banned / Motion & Narration, plus
    HyperFrames-style "tells" per style; a library of tested scene recipes per pack [verified:
    DataMagic, HyperFrames].
13. **SPEC must-haves → VERIFY evidence** as the written form of the review gate (pixel evidence
    per must-have) [verified: SenseNova].
14. **Check facts and numbers before drawing**: LASEV's solve-first and Math-To-Manim's
    `verify_math`; on-screen strings audited against `SOURCE_NOTES.txt` (anything2explainer)
    [verified].
15. **Planning aids**: a misconception step (3brown1blue) and a reverse prerequisite tree for the
    knowledge ladder (Math-To-Manim) [verified].

### Avoid

1. A VLM as the geometry gate, or VLM scores as the success metric (every calibration study
   disagrees with humans).
2. Generic RAG over Manim docs (TEA: −11.7 points for o3-mini; ALGOGEN: 82.5 → 79.0%).
3. Video-first sync: `atempo`, padding, freeze frames, time-scaling clips.
4. Making the model write a new in-context DSL to save tokens (ExplainSpec: not cheaper, less
   reliable). Keep declarative structure in the harness.
5. High-quality renders inside the repair loop (TEA).
6. Rigid slide templates (left bullets / right animation, worksheet cards) for 3b1b and Welch;
   self-contained scenes that block morph-not-respawn across scenes (TEA).
7. Silent fallbacks (PresentAgent's 3 s of silence and placeholder narration); this matches Ben's
   rule.
8. Full regeneration as the default repair. Localized repair was about 2.5–2.8× faster (Code2Video:
   15.4 vs 39.2–42.9 min).
   ManimAgent's counter-claim for crashes is untested head to head.
9. Image-model art for technical figures (NotebookLM asset match 32%).
10. Narration written after the visuals (PaperTalker, TEA, TeachMaster).
11. Render success as a quality proxy, or rewards that pay for more `play()` calls (Generative
    Manim).
12. Hard-coded frame numbers from a frozen narration (anything2explainer's own stated limit): any
    rewording becomes a global retime.

---

## Could not verify / open items

- **Unreleased code:** SGA (page 404), OmniManim's Vision Agent and data, ALGOGEN (page 404),
  LASEV, Bespoke, VideoAgent.
- **PIVOT** claims a multimodal harness, but the public code only reviews code text.
- **NotebookLM** internals are undisclosed; the producer-notes workflow rests on the help page
  plus one third-party blog.
- **PaperTalker's** printed $0.001 cost and its below-chance 0.084 cursor-ablation accuracy look
  wrong.
- **ManimGX** has no Linux or GPU numbers and no quality study; all its speed numbers are the
  vendor's.
- **Manim Bench** (manim-bench.makefinks.dev) scoring method could not be read (JS-only page).
- **Whether OpenRouter's Grok Voice returns word timestamps** (needed for borrow item 6) was not
  checked.
- **SenseNova-6.8-Code2Video** publishes no benchmark; its quality claims are preliminary.

---

## Sources

Manim explainer agents

- TheoremExplainAgent: https://arxiv.org/abs/2502.19400 · https://aclanthology.org/2025.acl-long.332 · https://github.com/TIGER-AI-Lab/TheoremExplainAgent · https://huggingface.co/datasets/TIGER-Lab/TheoremExplainBench
- Code2Video: https://arxiv.org/abs/2510.01174 · https://proceedings.mlr.press/v306/chen26bx.html · https://github.com/showlab/Code2Video · https://huggingface.co/datasets/YanzheChen/MMMC
- OmniManim: https://arxiv.org/abs/2605.15585 · https://github.com/AI4Learning-Club/OmniManim
- SGA: https://arxiv.org/abs/2607.18116 · https://github.com/JhEdLp/SGA_Evaluation
- PRISM: https://arxiv.org/abs/2605.19382 · https://github.com/positionprivacy/PRISM
- LASEV: https://arxiv.org/abs/2602.11790 · https://doi.org/10.1145/3770855.3818323 · https://github.com/RobitsG/LASEV
- ManimAgent (Jiang): https://arxiv.org/abs/2606.30296 · https://github.com/jwj1342/Paper2Manim
- VisualEDU: https://aclanthology.org/2025.findings-emnlp.889 · https://github.com/UchihaIchigo/VisualEDU
- ManimTrainer (Silva): https://arxiv.org/abs/2604.18364 · https://github.com/SuienS/manim-trainer
- PIVOT: https://arxiv.org/abs/2609.24083 · https://github.com/Chloe-mxxxxc/Pedagogy-Guided-Generative-Video-Tutors-for-STEM-Learning
- TeachMaster: https://arxiv.org/abs/2601.04204
- LLM2Manim: https://arxiv.org/abs/2604.05266
- ManiBench: https://arxiv.org/abs/2603.13251 · https://github.com/nabin2004/ManiBench
- PhysicsSolutionAgent: https://arxiv.org/abs/2601.13453
- Manimator: https://arxiv.org/abs/2507.14306 · https://github.com/HyperCluster-Tech/manimator
- Generative Manim: https://github.com/marcelo-earth/generative-manim
- Math-To-Manim: https://github.com/HarleyCoops/Math-To-Manim
- manim-generator: https://github.com/makefinks/manim-generator · https://manim-bench.makefinks.dev

Declarative IR systems

- DataMagic: https://arxiv.org/abs/2609.33403 · https://github.com/HKUSTDial/DataMagic
- ALGOGEN: https://aclanthology.org/2026.findings-acl.156/
- MoVer: https://arxiv.org/abs/2502.13372 · https://github.com/jama1017/MoVer · https://mover-dsl.github.io
- LogoMotion: https://arxiv.org/abs/2405.07065
- Shorter Is Not Cheaper (ExplainSpec): https://arxiv.org/abs/2610.32129

Slide and document to video

- Paper2Video: https://arxiv.org/abs/2510.05096 · https://github.com/showlab/Paper2Video · https://huggingface.co/datasets/ZaynZhu/Paper2Video
- Bespoke: https://arxiv.org/abs/2609.26540
- EvoPresent: https://arxiv.org/abs/2510.05571 · https://github.com/UCSB-AI/EvoPresent
- VideoAgent: https://arxiv.org/abs/2509.11253
- PresentAgent: https://arxiv.org/abs/2507.04036 · https://github.com/AIGeeksGroup/PresentAgent · PresentAgent-2: https://arxiv.org/abs/2605.11363
- NotebookLM: https://blog.google/technology/google-labs/notebooklm-video-overviews-studio-upgrades/ · https://blog.google/technology/google-labs/notebook-lm-audio-video-overviews-more-languages-longer-content/ · https://blog.google/technology/google-labs/video-overviews-nano-banana/ · https://blog.google/innovation-and-ai/products/notebooklm/generate-your-own-cinematic-video-overviews-in-notebooklm/ · https://support.google.com/notebooklm/answer/16454555
- ViviDoc: https://arxiv.org/abs/2603.27991

Agent skills and engines

- 3brown1blue: https://github.com/AmitSubhash/3brown1blue · https://pypi.org/project/3brown1blue/
- manim-voiceover: https://github.com/ManimCommunity/manim-voiceover
- SenseNova: https://github.com/OpenSenseNova/SenseNova-Skills (skills/sn-code-video) · https://huggingface.co/sensenova/SenseNova-6.8-Code2Video
- anything2explainer: https://github.com/Vincentwei1021/anything2explainer
- HyperFrames: https://github.com/heygen-com/hyperframes
- Remotion: https://www.remotion.dev/docs/ai · https://github.com/remotion-dev/skills · https://github.com/remotion-dev/template-prompt-to-video · https://www.remotion.dev/docs/lambda
- Motion Canvas: https://github.com/motion-canvas/motion-canvas · https://github.com/canvas-commons/canvas-commons · https://github.com/VideoZero/skills
- ManimGX: https://github.com/academa-labs/manimgx · https://manimgx.academa.ai · https://pypi.org/project/manimgx/

Contrast and surveys

- MovieAgent: https://arxiv.org/abs/2503.07314 · https://github.com/showlab/MovieAgent
- FilmAgent: https://arxiv.org/abs/2501.12909
- Reels-RSI: https://arxiv.org/abs/2610.14495
- Agentic Artifact Creation: https://arxiv.org/abs/2608.28122
- Agentic Visual Generation: https://arxiv.org/abs/2609.06758
- Video Generation Meets Agent Harness: https://arxiv.org/abs/2610.40191
