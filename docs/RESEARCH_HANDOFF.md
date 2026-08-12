# Manim Explainer Video Skill — Research Handoff

**Date:** 2026-08-10  
**Status:** Research complete enough to start building; skill not implemented yet in this repo.  
**Origin chat:** NTUDynamicRangeGCN workspace (Cursor), before moving development here.  
**This repo:** `/raid/ben/0Projects/ManimVideoGenerationSkill` → `git@github.com-personal:benjamin32561/ManimVideoGenerationSkill.git`

---

## 1. Goal

Build a **reusable Cursor skill** that turns any concept (math, ML metric, paper idea, code idea) into a short **3Blue1Brown-style Manim explainer video with voiceover** — not a doc/paper reader, but animated step-by-step teaching with narration.

### Why

Learn better when concepts are animated with synced narration. Prototype context existed in research work (`NTUDynamicRangeGCN`: teaching materials under `0docs/progress_tex/`, Manim env at `/raid/conda_envs/ben_envs/manim_env`). Generalize that into a skill developed in **this** dedicated repo.

### Non-goals (for now)

- Do not send emails or train models unless explicitly asked.
- Not a Remotion / talking-head / slide-deck product video tool.
- Not required to match Grant Sanderson’s ManimGL interactive Sublime workflow exactly (use Manim Community + scripted pipeline).

---

## 2. Desired end-to-end product

Given a concept, produce:

1. A **narrative script + visual beat sheet** (3b1b storytelling).
2. **Manim scene(s)** with clean layout (no overlapping text, progressive reveal).
3. **Voiceover audio** (high-quality TTS).
4. **Word-level timing** so visuals fire when the narrator says the relevant words.
5. A **final muxed MP4** watchable as a short lesson.

Preferred sync philosophy (user-stated):

```
script (+ what to show when)
  → TTS
  → extract word timestamps (STT / forced alignment)
  → implement visualizations on those timings
  → render + mux
```

Not: render video first and vaguely stretch audio to fit (except as a last-resort fit mode).

---

## 3. Constraints & environment

| Item | Detail |
|------|--------|
| Manim env | `/raid/conda_envs/ben_envs/manim_env` (Manim Community **0.20.1** verified) |
| ffmpeg | Available (`/usr/bin/ffmpeg`) |
| LaTeX / `dvisvgm` | Prefer **no LaTeX dependency** by default; use `Text` / shapes when TeX stack is missing |
| API preference | Prefer **OpenRouter** if quality is close enough (user already has OpenRouter) |
| TTS interest | ElevenLabs (known strong), Grok TTS (interested), OpenRouter-hosted options |
| Development home | **This repo** (`ManimVideoGenerationSkill`), not the NTU research repo |
| Inspiration to adopt | Install / study **[3brown1blue](https://github.com/AmitSubhash/3brown1blue)** and take inspiration (not necessarily vendor-lock to its TTS) |

### Notes from exploration in NTU repo

- Mentioned paths `0docs/progress_tex/manim_explain/` and `figs_extra/` were **not present** at research time.
- A thin ECC-style skill already existed at `NTUDynamicRangeGCN/.opencode/skills/manim-video/` (basic Manim explainer; **no** VO sync).
- Shell at research time had **no** exported `OPENROUTER_API_KEY` / `XAI_API_KEY` / `ELEVENLABS_API_KEY` (keys may exist elsewhere; must be wired for demos).

---

## 4. 3Blue1Brown narrative research

### Core principles (Grant Sanderson)

Sources:

- [Dropbox interview with Grant Sanderson](https://blog.dropbox.com/topics/work-culture/grant-sanderson-channels-his-passion-for-math-into-marvelously-i)
- [Lessons from Grant Sanderson (summary)](https://www.antoinebuteau.com/lessons-from-grant-sanderson/)
- [How I animate 3Blue1Brown (Substack + demo)](https://3blue1brown.substack.com/p/how-i-animate-3blue1brown)
- [3b1b/videos README / workflow](https://github.com/3b1b/videos)
- Narrative patterns compiled in [adithya-s-k/manim_skill `narrative-patterns.md`](https://github.com/adithya-s-k/manim_skill/blob/HEAD/skills/manim-composer/references/narrative-patterns.md)

**Principles to encode in the skill:**

1. **Visual is the mystery** — striking picture/result first; narration explains what it is. Visual prompts the story.
2. **Specific before abstract** — concrete example → pattern → general rule (opposite of most textbooks/papers).
3. **Resist starting with the general formula** then “populating examples later.”
4. **One idea per beat** — progressive reveal; never dump a full dense diagram at once.
5. **Story, not lecture** — mystery to resolve, characters/care, emotion; not definition→properties→theorem.
6. **Emotional arc:** curiosity → productive confusion → partial clarity → aha → short settle.

### Narrative patterns (from manim_skill)

| Pattern | Skeleton |
|---------|----------|
| Mystery → Investigation → Resolution | Paradox → explore visually → principle → generalize |
| Build Up → Payoff | Simple blocks → combine → surprising result → reflect |
| Two Perspectives → Unity | View A → view B → same thing → implications |
| Wrong → Less Wrong → Right | Naive approach → fails → refine → correct |
| Specific → General | Concrete case → notice pattern → abstract → apply |
| History as Narrative | Historical problem → discovery journey → modern view |

Most good videos **combine** patterns (e.g. mystery hook + build-up).

### Suggested short-video skeleton (60–150s lessons)

| Phase | Time | Role |
|-------|------|------|
| Hook | 10–20s | Visual paradox / why care + one sentence |
| Concrete case | 20–40s | One worked example on screen |
| Mechanism | 30–60s | Build the idea piece by piece with VO |
| Payoff | 15–30s | Abstract view / why it matters |
| Settle | 5–10s | One-line takeaway (sparse on-screen text) |

Grant’s own craft uses **ManimGL** + interactive `checkpoint_paste` in Sublime. We target **Manim Community** + a reproducible scripted pipeline, while keeping his **story rules**.

---

## 5. Technical Manim craft (layout / production)

Encode rules so agents don’t produce overlapping text, cluttered frames, or dead pacing.

### Layout

- Prefer `VGroup.arrange` / `arrange_in_grid` over ad-hoc absolute positions.
- Keep ~**15% frame margin**; define stage regions: title strip / main stage / footer takeaway.
- One primary visual region; labels beside objects, not floating over them.
- Prefer in-place transforms (`Transform`, morph) over spawning a second full copy elsewhere.
- Fade/clear before the next dense beat; never stack two full explanations.
- Backstroke / background rect behind text on busy visuals.
- Prefer `Text` over `MathTex`/`Tex` unless LaTeX/`dvisvgm` is confirmed available.
- Be aware of Manim Pango kerning issues ([manim#2844](https://github.com/ManimCommunity/manim/issues/2844)); notes-to-video uses a `CText` workaround.

### Pacing / motion

- Motion during speech; hold ~0.5–1s after an aha.
- Animate **meaning changes**, not every word.
- Bookmarks/cues at visual-event words, not every noun.

### Validation ideas (steal from notes-to-video)

Pre-render or post-frame checks for: text overlap, out-of-bounds, overflow, line-through-text.

---

## 6. Sync pipeline research

### User-preferred pipeline (locked as design intent)

```
1. Concept brief
2. Narrative script + visual beat sheet (written together)
3. Bookmark / cue the script
4. TTS
5. STT / alignment → word timestamps → timing.json
6. Implement Manim using absolute times / bookmarks
7. Layout validate
8. Render + mux → final MP4
```

### Existing sync mechanisms

#### A. manim-voiceover (canonical bookmark model)

- Docs: https://voiceover.manim.community/
- Repo: https://github.com/ManimCommunity/manim-voiceover
- Pattern: inherit `VoiceoverScene`, wrap narration in `with self.voiceover(text="... <bookmark mark='A'/> ...")`, then `wait_until_bookmark("A")` / `tracker.time_until_bookmark("A")`.
- Word boundaries via Whisper (local or cloud PR); interpolates for finer timing.
- Gap for us: stock services don’t include **OpenRouter Grok**; older plugin surface; Whisper not installed in `manim_env` at research time.

#### B. notes-to-video cue system

- https://github.com/cymcymcymcym/notes-to-video
- `{CUE_NAME}` in narration → TTS per sentence → often **character-ratio** cue estimates → `until()` / `sync()` helpers.
- Strong: layout validator, project layout, Claude skill packaging.
- Weak vs our goal: ratio cues drift vs real word STT.

#### C. docgen-style timing.json

- https://github.com/jmjava/documentation-generator
- Offline local alignment (silence detect + interpolate) or Whisper → `timing.json`; layout budget rejection; AV sync checks.

### OpenRouter STT for word timestamps

OpenRouter has `/api/v1/audio/transcriptions` with:

- `response_format: "verbose_json"`
- `timestamp_granularities: ["word"]` (OpenAI-compatible providers: OpenAI, Groq, Together)

Docs:

- https://openrouter.ai/docs/guides/overview/multimodal/stt
- https://openrouter.ai/blog/tutorials/transcription-on-openrouter/

Recommended pairing with our TTS: e.g. `openai/whisper-large-v3` or `openai/whisper-1` via OpenRouter for word arrays → map bookmarks to absolute seconds.

**Recommended implementation stance for this repo:**

- Prefer **custom thin scripts**: OpenRouter TTS → OpenRouter Whisper words → `timing.json` → Manim helpers (`wait_until`, `play_until_bookmark`).
- Optionally later wrap as a manim-voiceover `SpeechService` if we want that API.

---

## 7. TTS research & recommendation

### OpenRouter TTS (important finding)

OpenRouter now has a dedicated **OpenAI-compatible** speech endpoint:

- Guide: https://openrouter.ai/docs/guides/overview/multimodal/tts
- Announcement: https://openrouter.ai/blog/announcements/announcing-audio-apis/
- Endpoint: `POST https://openrouter.ai/api/v1/audio/speech`
- Discover models: `GET /api/v1/models?output_modalities=speech`

Live list sampled 2026-08-10 included **19** speech models, notably:

| Model ID | Notes | Approx OR pricing (prompt $/char → $/1M chars) |
|----------|-------|-----------------------------------------------|
| `x-ai/grok-voice-tts-1.0` | Voices: eve, ara, rex, sal, leo; speech tags | ~$15 / 1M |
| `google/gemini-3.1-flash-tts-preview` | Style prompts + many tags; 30 voices; Elo ~1211 (Artificial Analysis via Google claims) | very cheap (dual prompt/completion pricing — verify on first call) |
| `hexgrad/kokoro-82m` | 54 voices; draft quality | ~$0.62 / 1M |
| Fish / MiniMax / Deepgram / MAI / Voxtral / etc. | Available | varies |

**OpenAI GPT TTS was not in that speech-modality list** at sample time (may still appear under other routes; use Models API to recheck).

### Grok / xAI direct

- Docs: https://docs.x.ai/developers/model-capabilities/audio/text-to-speech
- Endpoint: `POST https://api.x.ai/v1/tts`
- Features: speech tags, streaming WebSocket, timestamps option, 5 voices
- Also available **through OpenRouter** as `x-ai/grok-voice-tts-1.0` — preferred default path so one key (OpenRouter) covers TTS (+ STT)

Pricing notes conflict across sources (marketing pages vs third-party articles vs OR list ~$15/1M). **Treat OR Models API as source of truth at runtime.**

### ElevenLabs

- Strong natural narration; large voice library
- API pricing order-of-magnitude: ~$50–100 / 1M chars (Flash vs Multilingual)
- https://elevenlabs.io/pricing/api
- Keep as **premium fallback**, not default (cost + separate key)

### Gemini 3.1 Flash TTS

- Strong for *directed* educational narration (style prompts, audio tags)
- https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-flash-tts/
- Available on OpenRouter as `google/gemini-3.1-flash-tts-preview`

### Proposed defaults (from research chat)

1. **Default TTS:** OpenRouter `x-ai/grok-voice-tts-1.0`, voice `eve` (or `leo` for lecturer)
2. **Teaching alternate:** OpenRouter Gemini Flash TTS when we want style-directed delivery
3. **Premium fallback:** ElevenLabs Multilingual v2/v3
4. **Draft/smoke:** Kokoro via OR or local

**STT default for sync:** OpenRouter Whisper with word timestamps (`openai/whisper-large-v3` or `whisper-1`).

---

## 8. Existing skills / tools landscape (do we reinvent?)

Searched skills.sh (`npx skills find manim|3blue1brown|explainer video|voiceover`) and GitHub.

### Verdict

**Nothing already installed does the full ask.** Closest public options:

| Project | Strength | Gap vs our full ask |
|---------|----------|---------------------|
| **[3brown1blue](https://github.com/AmitSubhash/3brown1blue)** | Best Cursor-installable 3b1b Manim skill: planning, misconception engine, narration scripts, ~24 rule files, production rules, VO + compose | TTS = Kokoro/VibeVoice (not OR/Grok); sync = extend/atempo/hybrid (not word STT); expects LaTeX/texlive |
| **[notes-to-video](https://github.com/cymcymcymcym/notes-to-video)** | Full VO pipeline + layout validator + cue sync | Claude Code oriented; cue timing often character-ratio; TTS not OR/Grok |
| **[manim_skill](https://github.com/adithya-s-k/manim_skill)** | Narrative patterns + Manim CE/GL craft (~1.6–3K installs) | No full VO/TTS/STT pipeline |
| **ECC `manim-video`** (~4.5K on skills.sh; thin copy in NTU `.opencode/skills/manim-video/`) | Basic Manim explainer triggers | No narration sync; not real 3b1b storytelling |
| **[vumichien/manim-skill](https://github.com/vumichien/manim-skill)** | Multi-agent paper→Manim, optional OpenAI voice | Claude Code plugin; not OR word-sync |
| **manim-voiceover** | Bookmark sync gold standard | Library, not a Cursor skill; TTS plugins outdated vs OR |

### Decision from user (2026-08-10)

> Add **3brown1blue** and take inspiration from it; develop everything in **ManimVideoGenerationSkill**.

Interpretation for next work:

1. Install / vendor / study `3brown1blue` skill rules & planning structure.
2. Keep its strengths: curriculum/misconception planning, production rules, templates, audit tools.
3. Replace or extend voice path toward **OpenRouter Grok (+ Gemini alt)** and **word-timestamp sync**.
4. Prefer no-LaTeX defaults for environments missing `dvisvgm`.

Install hints from upstream README:

```bash
pip install 3brown1blue
3brown1blue install   # Claude Code | Cursor | Windsurf | Copilot
```

Also: `3brown1blue generate`, `voiceover`, `compose-voiceover`, audience/domain flags, paper/slides modes.

---

## 9. Proposed architecture for *this* repo

```
ManimVideoGenerationSkill/
├── docs/
│   └── RESEARCH_HANDOFF.md          # this file
├── skills/manim-explain/    # (to build)
│   ├── SKILL.md
│   ├── reference/
│   │   ├── narrative-patterns.md
│   │   ├── layout-craft.md
│   │   ├── sync-pipeline.md
│   │   └── tts-stt.md
│   ├── scripts/
│   │   ├── tts_openrouter.py
│   │   ├── align_words.py           # STT → timing.json + bookmark times
│   │   ├── validate_layout.py
│   │   └── render_and_mux.sh
│   └── templates/
│       ├── script_template.yaml
│       └── scene_template.py
├── vendor/ or third_party/          # optional: pin 3brown1blue rules for inspiration
├── demos/                           # first end-to-end demo project(s)
└── README.md
```

### Skill workflow to enforce

1. Concept brief → choose narrative pattern + emotional arc.
2. Write script + beat sheet with cues **before** Manim code.
3. TTS → word align → `timing.json`.
4. Implement Manim with Text-first, stage regions, progressive reveal.
5. Validate layout → smoke render (`-ql`) → quality render → mux.
6. Deliver: script, scene `.py`, audio/, timing.json, final MP4, short “what this teaches” blurb.

### Script artifact shape (draft)

Per video:

- `thesis` (one sentence visual thesis)
- `pattern` (from §4)
- `audience` (optional: high-school / undergrad / graduate / industry — steal from 3brown1blue)
- `beats[]`: `id`, `say`, `cue`/`bookmarks`, `show`, `emotional_beat`, `approx_sec` (approx only until TTS)

---

## 10. Open decisions (carry into next chat)

Still useful to confirm when implementing:

1. **Sync engine:** custom OR TTS→Whisper→`timing.json` (recommended) vs adapt manim-voiceover vs 3brown1blue compose-voiceover hybrid.
2. **Demo length:** ~90s micro-lessons vs 5–10 min mini-3b1b.
3. **Default research narrative pattern:** Wrong→Right vs Specific→General for ML metrics.
4. **First demo topic:** CKA layer similarity, top-k on-mass vs class selectivity, or a tiny classic (softmax) for pipeline validation.
5. **Skill scope:** project-only `skills/` vs also personal `~/.cursor/skills/`.
6. **LaTeX policy:** never in v1 vs auto-fallback if `dvisvgm` exists.
7. **API keys:** ensure `OPENROUTER_API_KEY` available for demos; ElevenLabs optional in v1?

User lean so far: 3b1b style; audio-first with word timestamps; OpenRouter-preferred; inspire from 3brown1blue; develop here.

---

## 11. Suggested immediate next steps (for agent in this repo)

1. Write a short `README.md` pointing at this handoff + intended product.
2. Install / inspect **3brown1blue** (`pip install` + `3brown1blue install` into Cursor skill dirs, or copy rule files into `vendor/3brown1blue/` for study).
3. Diff 3brown1blue’s planning/production rules vs gaps (OR TTS, word STT, no-LaTeX).
4. Scaffold `skills/manim-explain/SKILL.md` that:
   - Triggers on “make an explainer video / 3b1b / Manim with voiceover”
   - Mandates narrative plan before code
   - Mandates TTS→align→Manim timing contract
   - Points at scripts/templates
5. Implement minimal scripts: `tts_openrouter.py`, `align_words.py`, mux helper.
6. Ship one **smoke demo** (~60–90s) proving the pipeline.
7. Iterate craft rules after watching the demo (overlap, pacing, voice quality A/B Grok vs Gemini).

---

## 12. Key links (bookmark list)

### Narrative / 3b1b

- https://blog.dropbox.com/topics/work-culture/grant-sanderson-channels-his-passion-for-math-into-marvelously-i
- https://www.antoinebuteau.com/lessons-from-grant-sanderson/
- https://3blue1brown.substack.com/p/how-i-animate-3blue1brown
- https://github.com/3b1b/videos
- https://github.com/adithya-s-k/manim_skill

### Skills / pipelines

- https://github.com/AmitSubhash/3brown1blue ← **primary inspiration to add**
- https://github.com/cymcymcymcym/notes-to-video
- https://voiceover.manim.community/
- https://github.com/ManimCommunity/manim-voiceover
- https://github.com/vumichien/manim-skill
- https://skills.sh/

### TTS / STT

- https://openrouter.ai/docs/guides/overview/multimodal/tts
- https://openrouter.ai/docs/guides/overview/multimodal/stt
- https://openrouter.ai/collections/text-to-speech-models
- https://openrouter.ai/x-ai/grok-voice-tts-1.0
- https://docs.x.ai/developers/model-capabilities/audio/text-to-speech
- https://elevenlabs.io/pricing/api
- https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-flash-tts/

### Related local context

- Research teaching PDF/tex: `/raid/ben/0Projects/NTUDynamicRangeGCN/0docs/progress_tex/`
- Manim conda env: `/raid/conda_envs/ben_envs/manim_env`
- Thin prior skill: `NTUDynamicRangeGCN/.opencode/skills/manim-video/`

---

## 13. One-paragraph summary

We want a Cursor skill that teaches concepts like 3Blue1Brown: visual mystery first, specific-before-abstract, progressive Manim reveals, then high-quality narration. The best existing Cursor-oriented package is **3brown1blue** (planning + production rules + VO compose), but it doesn’t use OpenRouter/Grok or true word-timestamp sync and leans on LaTeX. Research recommends installing/studying 3brown1blue, then building our skill around **script+cues → OpenRouter TTS (Grok default) → OpenRouter Whisper word timestamps → timed Manim → mux**, with Text-first Manim craft and layout validation inspired by notes-to-video / 3brown1blue rules. Development continues in this empty git repo.

---

*End of handoff. Next conversation should start by reading this file, then installing/inspecting 3brown1blue and scaffolding the skill.*
