# manim-explain

An [Agent Skill](https://agentskills.io/specification) that turns a concept into a
**3Blue1Brown-style Manim explainer video with word-synced voiceover** — narrative
script first, then TTS, then animation timed to the actual spoken words.

```
concept → script.yaml → OpenRouter TTS (Grok Voice)
        → Whisper word timestamps → timed Manim (LaTeX on screen)
        → pixel QA → MP4
```

The agent does not stop for approval between those stages: it writes the script,
records the voice, animates against the real word times, reads the rendered frames,
fixes what it sees, and hands you a finished MP4.

## Install

**Claude Code — as a plugin (recommended):**

```
/plugin marketplace add benjamin32561/ManimVideoGenerationSkill
/plugin install manim-explain@manim-video-generation
```

**Claude Code / Cursor / any agent that reads `SKILL.md`** — copy or symlink the
skill folder into a skills directory:

```bash
git clone https://github.com/benjamin32561/ManimVideoGenerationSkill.git
ln -s "$PWD/ManimVideoGenerationSkill/skills/manim-explain" ~/.claude/skills/manim-explain
# Cursor: ~/.cursor/skills/manim-explain   ·   project-scoped: .claude/skills/ or .cursor/skills/
```

The skill locates itself from wherever it is installed, so a project that uses it
can live anywhere on disk.

## Requirements

| Need | Why |
|------|-----|
| Vendored [Manim Community](https://docs.manim.community/) + ffmpeg | rendering and mux — source is `vendor/manim` |
| LaTeX with `dvisvgm` | `MathTex` on screen (classic 3b1b look) |
| Python `requests`, `PyYAML` | pipeline scripts |
| `OPENROUTER_API_KEY` | TTS **and** word alignment both go through OpenRouter |

Copy [`.env.example`](.env.example) to `.env` in *your* project and fill in the key.
Set `MANIM_ENV=/path/to/env` there if Manim lives in a dedicated interpreter.
After clone, install the in-tree engine (not the PyPI wheel):

```bash
git submodule update --init --recursive
pip install -e vendor/manim
```

Patches go in `vendor/manim`. Pull community updates with
[`scripts/sync_manim_upstream.sh`](scripts/sync_manim_upstream.sh).
No sudo for `dvisvgm`? [`scripts/setup_dvisvgm_local.sh`](scripts/setup_dvisvgm_local.sh)
unpacks it under `.local/` (Debian/Ubuntu).

## Use it

Ask the agent for an explainer video — "make me a 3b1b-style video explaining X" —
and it runs the whole pipeline. Or drive the scripts directly:

```bash
source skills/manim-explain/scripts/env.sh
python "$MANIM_EXPLAIN_ROOT/scripts/lint_script.py"     demos/<slug>/script.yaml --strict
python "$MANIM_EXPLAIN_ROOT/scripts/tts_openrouter.py"  demos/<slug>/script.yaml
python "$MANIM_EXPLAIN_ROOT/scripts/align_words.py"     demos/<slug>
"$MANIM_EXPLAIN_ROOT/scripts/render_and_mux.sh"         demos/<slug>/scenes/scene.py SceneName -qm
python "$MANIM_EXPLAIN_ROOT/scripts/qa_frames.py"       demos/<slug> --contact-sheet
```

## What makes it not look generated

The skill carries [`references/craft-laws.md`](skills/manim-explain/references/craft-laws.md)
— production laws accumulated from watching real output and fixing what was wrong:

- **Morph, don't respawn** — related A→B transforms in place; first appearance moves.
- **Orient before teaching** — define the cold viewer, central question, recurring
  anchor, and knowledge ladder before writing narration.
- **Evidence advances the idea** — exact run IDs and result tables stay in source
  notes unless the user asks for an audit or benchmark walkthrough.
- **The picture matches the spoken noun** — name a whole system, draw the whole system.
- **A question moves its referent** — while the VO asks about X, X animates.
- **Math develops on screen** — derived formulas morph term by term, never flash finished.
- **The VO breathes** — pauses are baked into the audio as real silence, not faked with `wait()`.
- **Spoken numerals are a contract** — if the narration says "five more", five more must move.
- **Pixel QA is mandatory** — the agent reads rendered frames before calling a render done.

Every law is written to apply to *any* topic. When you correct a video, the correction
goes into the laws first and the demo second, so the next video inherits the fix.

## Repository layout

```
skills/manim-explain/     the skill (this is what you install)
├── SKILL.md              entrypoint: hard rules + workflow
├── references/           craft laws, narrative patterns, layout, sync, TTS
├── scripts/              TTS, alignment, layout checks, QA stills, render
└── assets/               script + scene + style templates
vendor/manim/             our fork of Manim Community (editable install)
docs/                     locked decisions and research notes
tests/                    layout overlap tests
.claude-plugin/           plugin + marketplace manifests
```

The pipeline works inside `demos/<slug>/` (script, audio, `timing.json`, scenes,
renders, QA stills) and delivers the finished video to `output_videos/<series>/<slug>.mp4`
at your project root. Both directories are gitignored — they are your working
output and your deliverables, not part of the skill — so the layout tests skip
any demo that is not present.

## Credits

Pedagogy distilled from Grant Sanderson's [3Blue1Brown](https://www.3blue1brown.com/)
and from [AmitSubhash/3brown1blue](https://github.com/AmitSubhash/3brown1blue)
(`pip install 3brown1blue`, MIT). This skill keeps the storytelling rules and replaces
audio-stretch syncing with real word timestamps. No runtime dependency on either.

## License

[MIT](LICENSE)
