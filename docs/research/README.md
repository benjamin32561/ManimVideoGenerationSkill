# Research: multi-style educational video generation

Started 2026-11-21. This folder holds everything we learned about how educational video
styles are made before the redesign. The shipped skill is `skills/manim-explain/`; install
it from the repository README. This file is the research hub: goal, decisions, method,
verified knowledge, and an index of the detailed docs. Per-channel findings live in
[`styles/`](styles/).

## Goal

A skill that turns an idea into a finished educational video (narration, animation,
on-screen text) in a chosen style. The style shapes everything from the script to the frames.
The first two styles are **3Blue1Brown** and **Welch Labs**.

Order of work:

1. **Styles:** how each creator goes from idea to script (words, timing, visuals) to finished
   video, what tools they use, and what their language and frames look like.
2. **Idea to script:** how our pipeline should write a script in a given style.
3. **Tools:** render engine (speed is a pain today) and frame quality (text that breaks,
   overlaps or clips).

## Decisions so far

| # | Topic | Decision |
|---|-------|----------|
| 1 | Packaging | Style packs inside the one `manim-explain` skill, not a skill per style |
| 2 | Pack scope | A style covers visuals **and** narrative tone, so the whole system becomes multi-style |
| 3 | 3D camera | Out of scope for now |
| 4 | Engine | Compare manimgl, manimgx and one browser renderer (HyperFrames or Remotion) against the vendored Manim Community. Ben picks from the rendered results by looks, with speed as the other driver (updated 2026-11-21). |
| 5 | Data in scenes | Analytic / synthetic shapes only. No precomputed real-data step. |
| 6 | Font for the Welch look | Source Sans 3, and fail clearly if it isn't installed (Myriad Pro is licensed) |
| 7 | Welch reference code | Gitignored read-only clone at `vendor/welch-labs-videos/`. Created when we implement, not yet. |
| 8 | Styles | 3Blue1Brown + Welch Labs. Floatheads Physics and other channels are research input. |
| 9 | Current implementation | Open to a complete redesign. Agentic video systems are researched for ideas (2026-11-21). |
| 10 | Inputs | Both existing course material (notes, slides, PDFs, papers) and bare topics the agent researches |
| 11 | Audience | Both Ben studying and other people (students, YouTube) |
| 12 | "With text" | Both: generated from text input, and on-screen text is a key part of the look |
| 13 | Autonomy | Optional storyboard checkpoint (script + rough frames before real rendering), off by default |
| 14 | Style scope | Chosen per series; every video in a series shares it |
| 15 | Narrative preference | Logical steps forward and a flow of data and information, as in 3b1b and Welch. No third-person dialogue device (FloatHeadPhysics' narrated mentor) (2026-11-21). |
| 16 | Underlying pattern | Ben's hypothesis to test: short intro → dig into the problem → hit a wall → revelation, repeated. Analysed in `narrative-pattern.md`. |
| 17 | Veritasium | Added as a research subject (2026-11-21) |
| 18 | Sync model | Each visual change runs across the phrase that describes it and lands near its key word. Still frames are allowed; breathing idles are removed. Styles set the tolerances. |
| 19 | Scene structure | One short scene per beat or shot, rendered in parallel and joined at the end |
| 20 | Layout planning | The script stage writes a layout plan per beat: each object gets a style slot or grid area with a text budget. Code places objects through the plan, and checks compare against it. |
| 21 | Rule ownership | The core keeps only rules that hold for every style. Style-dependent rules move into the style pack, which sets its own values. |
| 22 | Browser renderer | HyperFrames (my call: open licence, plain HTML/CSS, built-in checks for dead stretches and unreadable or overlapping text). Remotion dropped. |
| 23 | Current output quality | Ben: placement is poor, there's barely any text animation, the TTS is mid. So the engine comparison renders a newly designed segment (layout plan, text animation, best voice) in each engine, not a port of the old scene. TTS and motion typography researched first (2026-11-21). |
| 24 | Imported dev skills | `.cursor/skills/*` (except `manim-explain`) and `.cursor/settings.json` are gitignored |
| 25 | Video length | Length follows the content, aiming for at least 2–3 full units per video (roughly 6–12 min). Short neighbouring topics in a series are merged into one video. Replaces "no preset length" in `docs/DECISIONS.md` once the redesign lands. |
| 26 | Narration voice | Gemini 3.8 Flash TTS, voice Charon, with a brisk-pace instruction (sample `27`) through OpenRouter. Whisper stays for word timestamps: a provider that returns its own timings would be better, but Whisper is good enough. The "OpenRouter only" rule stands. |
| 27 | Local TTS weights | Only the two local models Ben liked are kept: Kokoro-82M (`61`) and Qwen3-TTS 1.7B CustomVoice (`64`) (4.6 GB of weights, plus their env). Everything else was deleted (35 GB → 4.6 GB). |
| 28 | Engine | manimgx. It's 3–7× faster than Manim CE end to end and has the same Python API, so switching back stays cheap. Chosen by Ben after watching the engine spike (2026-11-22). |
| 29 | Render device | The CPU by default, through manimgx's bundled lavapipe: the GPUs are shared with other people's jobs. A 23 s beat (695 frames) rendered in 24 s on one CPU worker. GPUs only when named (`--gpus`). Ben, 2026-11-22. |
| 30 | Fix rounds | Only what a fix changed is re-checked, re-rendered and re-measured, keyed by window and beat digests. A video took ~1.5–2 h, mostly 4–7 full check/render rounds of 10–15 min each. Ben, 2026-11-22. |

## Method

Every channel doc in `styles/` uses the same sections so the docs compare directly:

1. Snapshot
2. Production pipeline & tools
3. Script writing process & structure
4. Language profile (measured: words per minute, sentence length, question rate, pronouns, signposting)
5. Flow (timestamped beat sheets: what's said / shown / written on screen)
6. Visual system (background, palette, typography, on-screen text, equations, characters, imagery, density)
7. Motion & sync grammar
8. Polish (how frames stay clean and legible)
9. Reproducing it with a code-driven pipeline
10. Sources

Rules: claims about process or tools are marked **[verified: source]** or
**[inferred: from what]**. Language numbers are measured from caption timing, not estimated.
Quotes stay short.

Downloaded media stays out of git. Transcripts, frames, metrics and analysis scripts live in
`research_cache/` at the repo root, which is gitignored (moved there from the session
scratchpad on 2026-11-21). Video files are deleted after analysis. The freeze/burst
measurement script is `research_cache/diag/freeze_burst.py`.

Tooling: a Python 3.12 env with yt-dlp 2026.10.26.

```bash
Y=yt-dlp
# captions only (manual track preferred for punctuation, auto track carries timing)
$Y --ignore-no-formats-error --skip-download --write-subs --write-auto-subs \
   --sub-langs 'en.*' --sub-format vtt -o '%(id)s' URL
# 360p video for frame inspection (YouTube now needs a JS runtime; node is at /usr/bin/node)
$Y --js-runtimes node -f 'bv*[height<=360]' URL
```

## Index

| Doc | Covers | Status |
|-----|--------|--------|
| [styles/veritasium.md](styles/veritasium.md) | Veritasium, same sections as the other style docs, with the wall → revelation cycle explicit | done 2026-11-21. A web search confirms Gregor Čavlović is on the team and presents on camera. |
| [narrative-pattern.md](narrative-pattern.md) | Tests Ben's wall → revelation hypothesis across 3b1b, Welch and Veritasium; beat codebook, timelines, measurements, a template a script stage can follow and a lint can check | done 2026-11-21. 10 videos + 6 of our scripts hand-labelled, one labeller. |
| [tts.md](tts.md) | Better narration voice: hosted and open TTS options, native timestamps, cost; samples in `research_cache/tts-samples/` | done 2026-11-21. 37 voices × 2 texts (74 files), $0.70 on OpenRouter. Ranking from arena Elo + measurements; nobody has listened yet, so Ben's ears decide. |
| [motion-typography.md](motion-typography.md) | Text animation and layout craft, motion rules as numbers, engine capabilities, showcase links to watch | done 2026-11-21. Checked: `manim_env` has manimpango 0.6.1; `mn-07-nernst` scenes contain no `MathTex` and no `Write`. |
| [engine-spike.md](engine-spike.md) | Engine comparison: the same 58 s segment in Manim CE, manimgl, manimgx and HyperFrames. Videos in `output_videos/engine-spike/`; the spike code was promoted into the skill and removed (2026-11-22) | done 2026-11-21. Render times re-measured by me. Ben chose manimgx (decision 28). |
| [synthesis.md](synthesis.md) | The comparison: idea → video per style, scripts, language, timing, frame hygiene, what a style must specify, clashes with current rules, universal lessons | done 2026-11-21 |
| [styles/3blue1brown.md](styles/3blue1brown.md) | 3Blue1Brown + gap analysis against the current skill | done 2026-11-21. Checked: manimgl `yellow_c` is `#FFFF00` vs CE `YELLOW_C` `#F7D96F`; CMU Serif not installed here; ce-10 scene is 3,751 lines; `check_sync --max-gap` defaults to 6.0 s. |
| [styles/welch-labs.md](styles/welch-labs.md) | Welch Labs | done 2026-11-21. Repo-based claims spot-checked: `# Paragraph 83` in `sora/p78_85.py`, Claude in code comments, "3d sucks for this", the number-line tip bug. |
| [styles/floatheads-physics.md](styles/floatheads-physics.md) | FloatHeadPhysics (Mahesh Shenoy, @Mahesh_Shenoy) | done 2026-11-21. Channel identity and creator confirmed by an independent search. |
| [styles/landscape.md](styles/landscape.md) | 8 channels (Reducible, Artem Kirsanov, Primer, Sebastian Lague, Kurzgesagt, minutephysics, Branch Education, Core Dumped), the tools creators use, published script-writing guidance | done 2026-11-21. Mayer effect sizes checked against the source PDF. |
| [agentic-systems.md](agentic-systems.md) | Agentic video-creation systems (papers, repos, products): architecture, quality loops, sync, evaluation, what to borrow | done 2026-11-21. Spot-checked 9 papers and 6 repos: all exist and match. |

## Knowledge collected

### Welch Labs: code and tooling (verified 2026-11-21)

Source: [stephencwelch/manim_videos](https://github.com/stephencwelch/manim_videos), MIT,
default branch `master`, last push 2026-11-19, shallow clone at commit `7b8075fd`.

- **Engine:** 3Blue1Brown's manimgl (`manimgl>=1.7.2`), not Manim Community. The README
  says Manim is "not the only method used for the animations", so final videos also use
  other tools (which ones is still open).
- **No standalone package.** Nothing from Welch Labs is on PyPI (`welch-style`,
  `welch-labs-videos`, `welch-labs`, `welchlabs` all 404). The reusable code is small and
  lives inside the video repo:
  - `custom/welch_axes.py` (~330 lines): "nice" tick generation, custom axes.
  - `custom/welch_tools.py`: copies the current camera position as a `reorient(...)` call.
  - `custom/welch_tip_manimce.py`, `custom/welch_numberline_manimce.py`: Manim Community
    ports of the custom concave arrow tip and the brown number line.
  - `custom_gx/welch_style.py` (77 lines): palette, font, background, packaged as
    `welch-style` for **manimgx**, unpublished.
- **Scale:** 367 Python scene files under `_2025/` and `_2026/`, plus notebooks that compute
  the data the scenes load.
- **Process clues:** `_2025/tooling/notion_storyboard_to_pdf_1.ipynb` (storyboards kept in
  Notion). Scene files are named like `p14_18.py` (meaning of the p-numbers still open).
  `book_*` files belong to an AI book that shares figures with the videos.
- **Render config** (`custom_config.yml`): 3840×2160 at 30 fps, `file_writer.saturation: 1.5`,
  background currently `#031e1e` (older values in comments: `#063336`, `#EFE5D1`, black).
  The default text font there is CMU Serif, but scenes pass `font=` explicitly.

**Palette.** Names from `welch_style.py`. Counts are occurrences of the single-quoted hex
string across scene files, so they are a lower bound.

| Name | Hex | Count | Role (inferred from use) |
|------|-----|------:|--------------------------|
| CYAN | `#00FFFF` | 370 | signed values / highlights |
| MAGENTA | `#FF00FF` | 348 | signed values / highlights |
| CHILL_BROWN | `#948979` | 262 | axes, structure |
| FRESH_TAN | `#dfd0b9` | 235 | text |
| YELLOW | `#ffd35a` | 226 | accent |
| BLUE | `#65c8d0` | 221 | accent |
| (black) | `#000000` | 171 | background (`welch_style.BACKGROUND`) |
| CHILL_BLUE | `#3d5c6f` | 140 | muted fill |
| CHILL_GREEN | `#6c946f` | 139 | muted fill |
| YELLOW_FADE | `#7f6a2d` | 133 | dimmed accent |
| GREEN | `#00a14b` | 132 | accent |

**Fonts** (explicit `font=` across scenes): Myriad Pro about 239 times (including spellings
`myriad-pro` and `myraid-pro`), Georgia 20, Helvetica 13, American Typewriter 12, Minion Pro 4.

**Idioms**: the number of scene files (out of 367) that use each, from a text search that
skipped a few file names with spaces, so these are approximate.

| Idiom | Files | Note |
|-------|------:|------|
| `reorient(` (camera placement) | ~219 | 3D camera work. Out of scope (decision 3). |
| `self.embed` / interactive | ~235 | interactive authoring: tune the scene live, copy the camera state |
| data loading (`np.load` / `torch.load` / pickle) | ~192 | real data. Out of scope (decision 5). |
| `set_opacity` | ~208 | dimming / layering |
| `frame.animate` | ~156 | camera moves |
| `FadeIn` | ~150 | |
| `ImageMobject` | ~119 | raster images |
| `Surface` | ~114 | 3D surfaces |
| `ShowCreation` | ~105 | stroke draw-on |
| `Tex(` / `Text(` | ~102 / ~90 | |
| `SVGMobject` | ~84 | vector art made outside Manim |
| `ReplacementTransform` | ~62 | |
| `LaggedStart` | ~55 | |

### manimgx (lead for phase 3, not evaluated)

PyPI summary: "The animation engine for agents: blazingly fast math and 3D videos with
Manim's Python API, on a Rust GPU core." Repo
[academa-labs/manimgx](https://github.com/academa-labs/manimgx), docs at
manimgx.academa.ai. Welch Labs' `custom_gx/welch_style.py` targets it, so they appear to be
trying it out.

### Our skill today (verified 2026-11-21)

- Engine: vendored Manim Community fork at `vendor/manim` (Cairo renderer).
- The 3b1b look is hard-coded in three places: `SKILL.md` hard rule 3, `docs/DECISIONS.md`
  ("Visual style: Classic 3b1b"), and `skills/manim-explain/assets/style.py`. `style.py`
  mixes layout tooling (`LayoutBoard`, `ask_about`, `safe_text`) with the look (palette `C`,
  font sizes). A style pack has to split those two apart.
- All QA tooling (geometry pass, occupancy, `layout_check`, `wireframe`, snapshots) assumes
  a fixed 2D camera of 14.22 × 8 units. No demo uses 3D or images.

### Narration voice: headline findings

Detail in [tts.md](tts.md); files and per-voice notes in `research_cache/tts-samples/INDEX.md`.
`_t1` is the current choppy narration, `_t2` a flowing rewrite of the same content.

- **Current voice:** Grok `leo` sits at #31 on the Artificial Analysis TTS arena (Elo 1160).
  Its `speed: 0.95` setting has no effect through OpenRouter (0.75, 0.95 and 1.0 gave the
  same length).
- **Top picks (arena + measurements; not yet listened to):**
  1. ElevenLabs Eleven v4: ties for #1 (Elo 1340), about $0.084/min. Its direct API returns
     character timestamps, which would remove the Whisper step. No `speed` setting and no
     pause tag.
  2. Speechify Simba 3.5: #6, word timestamps in the same response as the audio, about
     $0.012–0.016/min, 164/187 wpm (near 3b1b pace).
  3. Gemini 3.8 Flash TTS: #7, the cheapest, and the only pick that stays inside "OpenRouter
     only". No timestamps, so Whisper stays. A "brisk" instruction raised it to 160/178 wpm.
  - Best local option: Kyutai TTS 1.6B (CC-BY-4.0). It runs on a V100 in fp32, and its native
    word timings match Whisper to about 0.06 s after a fixed ~0.2 s offset.
- **OpenRouter returns audio only,** so native timestamps need a direct key (ElevenLabs,
  Speechify, Cartesia or Inworld). That conflicts with the "OpenRouter only" TTS decision in
  `docs/DECISIONS.md` and `references/tts-stt.md`.
- **Local weights:** about 35 GB in the TTS bench cache.

### Ben's listening verdict (2026-11-21)

From `research_cache/tts-samples/`, in his words, condensed:
- **Best:** `27` Gemini 3.8 Flash + brisk instruction, Charon: "fucking amazing… immediately
  noticeably better". The same model without the instruction (`08`) is "really nice", so the
  pace and register instruction makes a big difference. A style pack should carry its own TTS
  instruction.
- **Very nice:** `08` Gemini 3.8 Flash, `11` Gemini 3.1 Flash preview, `10` Gemini 2.5 Pro
  (between 08 and 09), `21` HeyGen Lucian ("not as good as Google"), `09` Gemini 3.8
  Sadaltager.
- **Good:** `01` ElevenLabs v4 George ("a bit better, but pricier"), `02` ElevenLabs v4 Brian,
  `06` ElevenLabs Multilingual v2 Brian, `25` Qwen Audio 3.0 ("solid"), `61` Kokoro local,
  `64` Qwen3-TTS local (dislikes the voice). Fine: `00` Grok baseline, `14`, `16`.
- **Mid or worse:** `03`–`05` (ElevenLabs v3 and Multilingual v2 George), `07`, `15`, `17`–`20`,
  `22`, `23`, `26`, `65`, `66`, and all other local models.

### Veritasium: headline findings

Detail in [styles/veritasium.md](styles/veritasium.md); sample of 8 videos in
`research_cache/veritasium/SAMPLE.md`.

- **A team channel now.** Since Electrify's investment (April 2023) each video has its own
  writer/director. Other presenters front some videos (Gregor Čavlović, Emilia Gyles, Casper
  Mebius alongside Derek). Derek: 30+ people, and he won't appear in some videos.
- **The cycle, measured (2021–26):** a wall every 2–3.4 min, usually resolved 0.5–1.7 min
  later, so about 9–14 cycles per 30 min. Three patterns:
  - early videos: street interviewees guess, and each guess is refuted;
  - "chained why": each answer becomes the premise of the next "So if…, then how…?";
  - "ledger": 2–4 numbered problems announced early and closed out loud ("So that is problem
    two dealt with"), on screen as plaques or chapter cards.
- **How walls and revelations are built:** a wall states the expectation, then breaks it ("you
  might expect 100%, but that is not the case"), while the model just built is run until it
  visibly fails. A revelation comes through a named person, then one plain sentence, then a
  toy example with real numbers, then a scale-up. The payoff goes back to whoever held the
  wrong idea.
- **No naive character needed:** Muller's thesis found a single narrator who states and then
  refutes the misconception works about as well as a tutor–student dialogue (effect sizes .79
  vs .83). None of the 8 videos uses a scripted naive character.
- **Language:** short sentences (mean 15–17 words, reading grade about 8), 150–183 wpm, 0.5–1
  questions per minute. 11–19% of sentences open with "So" and 4–11% with "But".
- **Look and edit:** no house look; each video gets its own art direction. Physical props
  come first, then a matching motion graphic. 10–13 cuts per minute since 2023, and only
  13–25% of frames are still.
- **Gap for a code-only pipeline:** designed graphics fill only about 40–58% of runtime; the
  rest is filmed or found footage. A code-only version reads as an illustrated essay, not a
  documentary.

### Motion typography: headline findings

Detail and showcase links in [motion-typography.md](motion-typography.md).

- **What's wrong with the baseline (`mn-07-nernst`):**
  - Motion: no `Write` and no morphs. All 48 text entrances are 0.35 s `FadeIn`s with CE's
    `smooth` easing, which holds still for about 77 ms and then pops.
  - Layout: one title stays up for all 158 s, content fills a strip of about 8% of the frame,
    objects are parked at the edges, and every concept is a word in a box.
  - Content: the Nernst video never shows the Nernst equation (no `MathTex` in its scenes).
- **Words run together on screen** (for example "thision"). ManimPango 0.7.0 (2026-10-01)
  fixes this upstream; `manim_env` and the vendored CE are on 0.6.1. Separately, `style.py`
  sets no font, so text falls back to DejaVu Serif.
- **How the reference channels animate text:**
  - 3b1b: `Write` in 1–2 s (linear, per-glyph stagger); terms fly in from the diagram in about
    1 s; algebra steps morph matched symbols in 0.6–0.8 s; then holds.
  - Welch: caps labels write letter by letter at about 11 per second; prose fades in 0.6 s;
    labels re-park in 1.4 s; a 3 s camera move does the layout.
  - Kurzgesagt, Veritasium: 0.2–0.6 s entrances with overshoot.
  - None captions the narration. All of them give text a source (stroke, leader line,
    travel, mask) instead of fading it in from nowhere.
- **Motion rules as numbers:** §3.8 has a schema with 3b1b and Welch values. The HyperFrames
  agent skill is the most precise numeric spec found: eases by role, exits 40–50% shorter than
  entrances, word stagger 60–120 ms, hold of 0.5 s + 0.3 s per word.
- **Engines: no single winner.**
  - Typography motion: HyperFrames + GSAP (SplitText and MorphSVG are now free).
  - Automatic layout: browser engines (CSS, Remotion `layout-utils`, the HyperFrames text
    linter).
  - Math: manimgl (substring indexing and morphs on matching parts).
  - manimgx: CE's API with Typst math (no TeX install), a built-in layout checker, and a
    claimed 90× speed-up over CE (vendor's own benchmark).
- **Newer systems:** none beats 3b1b or Welch on math. "Claude Motion" (listed as an artifact
  type on Ben's account) has the strongest web typography but no math. explainroo is the only
  browser-based renderer seen with real math.

### Narrative pattern: headline findings

Detail in [narrative-pattern.md](narrative-pattern.md). 10 hand-labelled videos (3 by 3b1b,
3 by Welch, 4 by Veritasium) and 6 of our scripts; one labeller.

- **Ben's hypothesis holds for the repeating unit and misses two things:** the units chain
  under one central question that stays open, and every revelation is cashed out before the
  next unit starts.
  - **Short intro:** the central question arrives at a median of 60 s, within 90 s in 8 of 10
    videos.
  - **Dig → wall → revelation:** 2–9 turns per video. Of 64 units, 59% are wall → revelation,
    19% overturn a stated intuition, and 22% are plain builds. Walls are short pivots: median
    16 s, about 8% of runtime.
  - **"Over and over" is a chain, not a loop:** 81% of revelations directly cause the next
    question, often because the fix's own cost becomes the next wall.
  - **Missing from the hypothesis:**
    - the biggest revelation lands at a median of 67% of runtime;
    - 35–46% of runtime is setup, digging and attempts;
    - 16–26% is cashing out (naming, formula, a new test case, real numbers);
    - the ending returns to the opening.
- **Template:** `Video := Hook Q0 Unit+ Payoff`, where
  `Unit := question → work → turn → cash-out → link`. The turn is a wall then a revelation, an
  intuition then its refutation, or a plain build. Units nest up to depth 3. The doc also
  gives:
  - per-beat script fields (`unit`, `obstruction`, `resolves`, `link`, `climax`);
  - per-style parameters (turns per 10 min: 3b1b 2.5–4, Welch 1.2–2.5, Veritasium 1.8–3.5);
  - 15 lint rules, including "no narrated dialogue".
- **Our scripts:**
  - In 6 labelled scripts, only 9 of 47 `aha` beats are real revelations.
  - Setup and attempts take 4–28% of runtime (reference: 35–46%).
  - The biggest revelation lands at 14–24% in 5 of 6.
  - In pf and mn, 8 of 10 links between units are topic jumps.
  - The ce series already follows the target pattern.
  - None of the 52 scripts on disk carries a `narrative_role` field.

### 3Blue1Brown: headline findings

Detail and sources in [styles/3blue1brown.md](styles/3blue1brown.md). Based on 8 videos
(2016–2026), 4 process videos, and the `3b1b/videos` and `3b1b/manim` repos.

- **Process:** a full script built around one "aha" and a core visual; the wording changes
  while he animates. Animation is interactive in his own manimgl from Sublime Text. Clips are
  laid on a timeline, the VO is recorded over them, and he edits in Final Cut himself. Sync is
  by hand in the editor: scene code has no narration hooks, and 73–77% of waits are 1 s.
- **Clips, not one long scene:** a video is cut from 24–55 short scene classes, each starting
  on an empty stage. We render a whole demo from one class of up to 3,751 lines (ce-10). That
  is the root of our leftover, phantom-slot and section-boundary problems.
- **Clean frames come from attaching text, not avoiding it:**
  - labels sit next to their object, with a black stroke behind the glyphs;
  - median label is 2 words, and 74% are 3 words or fewer;
  - multi-line text is broken by hand at about 30 characters, never shrunk to fit;
  - inactive items are dimmed in place.

  OCR finds no fixed text band: 44–65% of text sits in the middle half of the frame.
- **Look:** black `#000000`, his own palette (manimgl `YELLOW` = `#FFFF00`; Manim CE
  `YELLOW_C` = `#F7D96F`, so our constants are the wrong hues). Text in CMU Serif to match
  LaTeX (our skill leaves the font unset, and CMU Serif isn't installed here). One concept, one
  colour, across prose, formulas and figures. Pi creatures, photos, footage and insets appear
  throughout.
- **Pacing:** 175–200 wpm with 0.45–1.8 pauses of 1 s or more per minute. Our 47 narrations:
  median 139 wpm and 4.6 such pauses per minute. Our post-question pause (0.9–1.3 s) is above
  his 90th percentile, and he asks only 0–0.75 questions per minute.
- **Motion:** 27–85% of frames are still. 90th-percentile holds are 4.4–9.5 s, and every
  video has 15–30 s holds. This contradicts our breathing idles and `check_sync`'s 6 s
  `--max-gap` default. Grant: "Avoid pointless animations." When animation starts line up
  with phrases, the picture follows the voice by 0–0.3 s. Emphasis is a colour change, a flash
  under the term, or dimming the rest; `Indicate` is almost never used.
- **Structure:** since 2019, a 1–3 minute cold open before the logo; a conversational voice
  that raises the viewer's objections ("I hear some of you asking…"); never a recap ending.
  Endings return to the opening, set a puzzle, or tease the next video.
- **Already matched by our skill:** concrete before abstract, one anchor example, a naive
  approach that fails before the real one, formula build-up, returning to the opening.

### Welch Labs: headline findings

Detail and sources in [styles/welch-labs.md](styles/welch-labs.md). Based on 8 videos (2015,
2024–2026), the 2017 process video, interviews, the site, and the repo.

- **Pipeline:** script in numbered paragraphs, then a Notion storyboard with 1920×1080
  Illustrator frames, then Welch's own VO, then manimgl scenes plus overhead desk shoots, then
  a Premiere edit. Scene files `pNN_MM.py` most likely map to script paragraphs (inferred from
  `# Paragraph 83` in `sora/p78_85.py`). Freelancers submit scenes as pull requests. Claude
  helps write scene code (code comments).
- **Sync is done in the edit, not in code.** No audio sync in the repo. Scenes are long takes
  with padding, cut to the VO in Premiere. 44–64% of hard cuts land in speech pauses (11–24% by
  chance). Sync is per clause, not per word.
- **Why frames stay clean:**
  - Layout is designed at final size in Illustrator, then imported as SVG or redrawn from the
    storyboard's pixel coordinates.
  - Positions are hand-tuned: 3,267 absolute placements vs 820 relative ones.
  - Each kind of text has a fixed slot (title, caption row, dimensions, footnote, legend).
  - Context is dimmed, not removed.
  - Graphic frames hold 5–22 short text items, the longest typically 9–22 characters, all
    about 4% of frame height.
- **Look:** about two thirds of runtime is Manim on black (late 2024 on); the rest is overhead
  walnut-desk shots (paper cutouts, printed papers, hands), a talking head, and clips.
  Uppercase Myriad Pro labels, LaTeX math, italic serif for example sentences. One colour per
  entity for the whole video, a recurring anchor diagram, real model weights as heatmaps.
- **Language:** about 170 words per minute while speaking, median sentence 20 words, "we" 34
  vs "you" 1.6 per 1,000 words. Questions are rare (0.19/min) and mark turning points. Exact
  numbers are part of the voice.
- **Recurring structure:** opens on a real artifact → one running real-model example →
  sponsor mid-roll → scale-up to production numbers → measured payoff → "it will be
  fascinating to see…" → callback to the opening → promo.
- **Conflicts with the current skill** (phase 2 decisions):
  - Hard rule 10 bans exact numbers and tables; Welch uses them centrally.
  - Rule 9 bans prose on graphs; Welch keeps small notes and footnotes in their own slots.
  - Our word-level sync is stricter than anything Welch does.
  - Decision 5 (no real data) excludes his real-weight heatmaps.
- **Worth porting (MIT):**
  - the storyboard-pixel layout layer in `world_models/p63_64.py`;
  - `welch_axes`;
  - the `WelchTip` arrow tip;
  - `format_number`.

  `welch_numberline_manimce.py` always draws its tips: it pops `include_tip` and then reads
  it back with a default of `True`.

### FloatHeadPhysics: headline findings

Detail and sources in [styles/floatheads-physics.md](styles/floatheads-physics.md). Based on 6
videos (2022–2026) plus his own Q&A and process videos.

- **Who:** Mahesh Shenoy, a former classroom teacher who now works at Khan Academy. The name
  comes from an old green-screen floating-head setup.
- **Signature device:** a Socratic dialogue with a dead scientist, voiced entirely by him
  ("Einstein says, 'Mahesh…'", "And I'm like, …"). The mentor poses the problem, lets him
  answer wrongly, then hints.
- **Fixed opening:** a common claim → "Or are they?" → a personal confession → his source →
  "rediscover" → "let's begin". It appears in 7 of 8 transcripts.
- **Format:** a live presenter beside a whiteboard-style canvas. He is on screen 55–98% of the
  time (median about 90%). Since 2024 his camera sits in a rounded card that moves and resizes
  per beat. A code-only version needs a stand-in, such as a portrait card of the mentor.
- **Look:** black (`#000000`) or dark navy grid (`#00001B`) backgrounds, colour-coded LaTeX
  built line by line, boxed results, red ✗ / green ✓ verdict stamps, checklists that build up,
  neon glow, archival photos. No mascot.
- **Sync is tight:** across about 15 measured events, each element appears between 0.8 s
  before and 0.4 s after its spoken noun. A finished board can then hold for minutes.
- **Frame hygiene:**
  - 1–5 words of designed text per frame (median), about 15–22 at most;
  - a keep-out zone for the camera card;
  - labels on leader lines;
  - old content dimmed, not deleted;
  - show the whole board, then zoom.

  Not to copy: equations running off the edge during zooms, labels overlapping while they
  fly in, a visible mouse pointer.
- **Pace slowed over time:** 187–203 wpm (2022–24) down to 142–154 wpm (2026). Sentences went
  from about 15–17 words to about 12, and runtimes from about 21 to 45 minutes. About one
  sentence in six is a question.
- **Process, from his own videos:** the Feynman Lectures as the main source; backward design
  (outcome → storyline → visuals); misconceptions written down before the storyline; early
  drafts shared on Patreon for feedback.
- **Unknown:** his animation and editing software. No public source names them.
- **Conflict with the current skill:** his opening ("So Feynman, where do we start?") breaks
  hard rule 5, so this style would need its own override.

### Channel landscape: headline findings

Detail and sources in [styles/landscape.md](styles/landscape.md). Samples are 2–3 videos per
channel, so these describe each style, not precise averages.

- **Voice first, visuals timed to it** is the norm: Kurzgesagt, minutephysics, Branch and
  Core Dumped. Artem Kirsanov renders long code animations and retimes them to his voice in
  After Effects. Sebastian Lague builds the project first and scripts from its history.
- **Core Dumped is the nearest existing match to our pipeline:** PowerPoint slides, an
  ElevenLabs voice, DaVinci Resolve. The voice runs fast (182–201 wpm), but the edit inserts
  8–10 pauses of 1 s or more per minute.
- **Pace differs about 2× between good channels:** 126 wpm (Branch) up to 212–234 wpm
  (minutephysics). A style needs its own words-per-minute and pause budget.
- **On-screen word count separates styles more than colour does:** Kurzgesagt about 0.8
  words per frame, Reducible 18, Primer 41, Core Dumped 46. 6 of 8 channels use a dark
  background.
- **Learning research backs word-level sync** (Mayer 2023, checked against the PDF):
  temporal contiguity (spoken words at the same time as the matching graphic) has the
  strongest effect, d = 1.31, 8 of 8 tests. Redundancy (don't caption the narration) has the
  weakest, d = 0.10, 8 of 12 tests.
- **Every code-driven creator built a house kit:**
  - Reducible: a public palette and font file on Manim CE.
  - Primer: from Blender to Unity to its own Godot toolkit.
  - Lague: Unity + the Shapes plugin + his own timing helpers.
  - Artem: After Effects + Manim + matplotlib + his own Blender add-ons.
- **Narrative mode shows in the numbers:** Kurzgesagt says "you" 34–74 times per 1,000 words.
  Lague narrates in first person. Primer has the most "but" turns, asking viewers to predict.
  Branch is an additive guided tour with the fewest turns.
- **Ease of reproducing each style with our pipeline:**
  - High: Core Dumped, Reducible.
  - Medium-high: Artem Kirsanov.
  - Medium: minutephysics, Primer's 2D parts.
  - Low: Lague, Branch, Kurzgesagt (they need a real project, 3D, or bespoke art).

### Agentic video systems: headline findings

Detail and sources in [agentic-systems.md](agentic-systems.md).

- **Layout fixed before code is the best-evidenced cure for overlapping text.** OmniManim
  plans a box for every object at each keyframe before writing code, and won a blinded human
  overlap comparison by +16.4 over a direct LLM and +32.1 over Code2Video. Code2Video's named
  6×6 placement grid raised its layout score from 48.8 (free placement) to 82.8, though a VLM
  did the judging. Our `show:` field is free text, so we do nothing of this kind.
- **VLM judges of layout disagree with humans** in every study that checked: Code2Video 90.6
  VLM vs 60.2 human, Manimator 0.853 vs 0.52, ManimAgent r = −0.17. The agent's eyes are better
  spent on "does the frame say what the voice says" than on geometry.
- **Deterministic geometry checks come second, and ours are already strong at detection.**
  Gaps: violations don't carry the computed fix (shift vector, variable, line); there are no
  checks for text leaking out of its container or text too small to read; text isn't measured
  and budgeted before placement.
- **Declarative formats vs code:** template / declarative systems are the most reliable,
  but a pre-registered 2026 study found that making Claude models write a new declarative
  format was neither cheaper nor more reliable than code. The suggested middle path:
  constrained code, where the model places objects through style-pack regions and times them
  through calls bound to the narration.
- **Sync:** our Whisper word-timestamp approach is ahead of every system read. Worth taking:
  bind each animation to its words in one place, and add a numeric tolerance check.
- **Speed:** rendering scenes in parallel gave 5.6× (Code2Video). ManimGX v0.1 claims 6–20×
  over Manim CE on 2D scenes (vendor's own Mac benchmark) and ships layout checks in the engine.
- **Projects new to us that matter:** HyperFrames (HeyGen, HTML/CSS/GSAP rendered in headless
  Chrome, with agent skills), anything2explainer (Remotion skill, noncommercial license),
  the SenseNova code-video skill (open 27B model), DataMagic (style packs + recipe library).

### Diagnosis: "the frame freezes, then everything happens at once" (measured 2026-11-21)

Ben's report: frames sometimes freeze, then all the animation happens at once, and things
end up on top of each other. Measured from the 47 `demos/*/out/timeline.json` files, which
log every `play` with its start and end.

**Mechanism.** The scene code waits for a cue word (`wait_until` / `breathe_until`) and then
plays the change with a run time computed from the time left before the next cue, with a
floor of 0.2–0.25 s (`play_until` / `play_before` `min_run` in `timing_helpers.py`). Between
cues, `breathe_until` loops 1.1 s "breaths" that scale the figure by 1.5%, which is
invisible on screen. The result is long stretches where nothing visibly changes, broken by
snaps of 0.2–0.4 s on the cue words, often several in under a second.

**Example**, `pf-10-mental-architecture`, 55–70 s: nine 1.1 s breaths in a row
(55.5–64.3 s), then FadeIn 0.30 s at "penetrate" (65.2), Indicate 0.20 s at "fins" (66.5),
then four FadeOuts plus a FadeIn within 0.7 s at "peripheral" (69.0).

**It got worse as the sync laws accumulated**, comparing series in the order they were made:

| Series | Median real animation | Real animations ≤ 0.4 s | Plays that are 1.1 s breaths |
|--------|----------------------:|------------------------:|-----------------------------:|
| ce-01…09 | 1.00 s | 5% | 2% |
| ce-10…15 | 0.90 s | 9% | 0% |
| thermal | 0.80 s | 9% | 13% |
| pf-01…07 | 0.80 s | 34% | 10% |
| il | 0.57 s | 29% | 9% |
| mn | 0.47 s | 44% | 8% |
| pf-08…09 | 0.37 s | 64% | 31% |
| pf-10…13 | 0.30 s | 72% | 41% |

Counting breath-only stretches of 4 s or more as frozen: pf-09 is still for 75 of 164 s,
pf-10 for 90 of 172 s, and pf-13 for 86 of 149 s. That's 8.4% across all 47 demos.
(Heuristic: a breath is a single `.animate` play of 1.1 s or less, next to another one.
Some short real moves may be miscounted.)

**Why the audits miss it.** `check_sync.py` counts any play as motion, so breaths satisfy
the "no frozen stretch" check. The laws "every spoken change has a visible one, on that
word" plus `play_before` push every real change into a short snap on the keyword. The sync
model is "event at a word", where real explainers tend to animate across the phrase that
describes the change. The 3b1b and Welch docs will measure how they actually do it.

## Open questions

- Welch Labs: which tools besides manimgl, what the `pNN` scene numbering means, how
  scripts and storyboards are written (research in progress).
- Floatheads Physics: confirm the channel, its tools and its process (in progress).
- Frame failures: Ben has no examples to hand. He describes freezes followed by bursts
  (measured above) and things stacked on top of each other (not yet measured; the
  `out/layout_violations.json` files are the next place to look).
