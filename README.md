# manim-explain

An [Agent Skill](https://agentskills.io/specification) that turns course material or a topic
into a **narrated explainer video in a chosen style**: 3Blue1Brown or Welch Labs.

```
idea / course material
  → research   primary sources, thinking-process spine + verified values in SOURCE_NOTES.md; align if open
  → script     logic-first intuitive derivation in question → wall → revelation units under one central question
  → voice      OpenRouter TTS in the style's voice, Whisper word timings
  → plan       every object placed in pixels, every change bound to the phrase that describes it
  → render     one beat per worker, in parallel on the CPU (manimgx), joined frame-exactly
  → checks     lint (grammar + number-density guards), plan geometry at every frame, sync, frame review
  → MP4
```

Each step refuses to run until the check before it passed for the current files, and
delivery waits for a recorded frame review. After a fix, plan check, render and render check
redo only the stretches of the video the fix changed.

## Styles

| | 3Blue1Brown (`3b1b`) | Welch Labs (`welch`) |
|---|---|---|
| Narrative | 2.5–4 turns per 10 min; effortless toy numbers; geometric/logical derivation; ends on a principle or puzzle | 1.2–2.5 turns per 10 min; mechanism first + real numbers where they prove a wall or payoff; causal chain; ends on open questions |
| Voice | conversational, 170–205 wpm | measured documentary "we", 150–185 wpm |
| Look | black, ManimGL colours, CMU Serif, labels next to their objects | black, tan / brown / yellow, Source Sans 3 caps labels in fixed slots |
| Motion | write-ons, term-by-term equations, holds while explaining | letter-by-letter caps labels, long smooth moves, dim the rest |

Every number in the packs is measured from the channels' videos and code; see
`docs/research/`.

## Install

**Claude Code, as a plugin:**

```
/plugin marketplace add benjamin32561/ManimVideoGenerationSkill
/plugin install manim-explain@manim-video-generation
```

**Any agent that reads `SKILL.md`:** symlink `skills/manim-explain` into its skills folder
(for example `~/.claude/skills/manim-explain`). The skill locates itself, so projects can live
anywhere.

## Requirements

Linux. The default renderer is the CPU, through the lavapipe build bundled with manimgx, so
a GPU is not required. `render.py --gpus` is the Linux NVIDIA path: it needs `nvidia-smi`,
`gcc`, and the Vulkan headers.

| Need | Why |
|---|---|
| Python 3.13 and the packages in [`requirements.txt`](requirements.txt) | rendering and pipeline scripts |
| ffmpeg | encoding and the narration mux |
| CMU Serif in `~/.local/share/fonts/cmu` | both styles; rendering fails without it |
| Source Sans 3 in `~/.local/share/fonts/source-sans-3` | Welch labels; rendering fails without it |
| `OPENROUTER_API_KEY` | voice and word timings |

```bash
python -m pip install -r requirements.txt
mkdir -p ~/.local/share/fonts/cmu ~/.local/share/fonts/source-sans-3
# Computer Modern Unicode (OFL): https://sourceforge.net/projects/cm-unicode/
# Source Sans 3 (OFL): https://github.com/adobe-fonts/source-sans/releases
# Put the CMU .otf files in ~/.local/share/fonts/cmu
# and the Source Sans 3 .otf files in ~/.local/share/fonts/source-sans-3
```

Copy [`.env.example`](.env.example) to `.env` in your project, set the key and `MANIM_ENV`
(the Python environment whose `bin/` holds `manimgx`), then
`source skills/manim-explain/scripts/env.sh`.

## Use it

Ask the agent for an explainer video ("a Welch Labs-style video on caches from my course
notes"), or run the steps:

```bash
python skills/manim-explain/scripts/lint_script.py  demos/<series>/<slug>
python skills/manim-explain/scripts/voice.py        demos/<series>/<slug>
python skills/manim-explain/scripts/plan_check.py   demos/<series>/<slug>
python skills/manim-explain/scripts/render.py       demos/<series>/<slug>
python skills/manim-explain/scripts/check_render.py demos/<series>/<slug>
python skills/manim-explain/scripts/review.py record  demos/<series>/<slug> --notes "..."
python skills/manim-explain/scripts/review.py deliver demos/<series>/<slug>
```

Videos are worked on in `demos/<series>/<slug>/` and delivered to
`output_videos/<series>/<slug>.mp4`. Both folders are gitignored.

## Repository layout

```
skills/manim-explain/      the skill (this is what you install)
├── SKILL.md               entry point: hard rules and workflow
├── explain/               pipeline package: plan, timing, scene runtime, checks, rendering
├── scripts/               the pipeline steps
├── styles/3b1b, welch/    style packs: style.yaml, components.py, STYLE.md
├── references/            research, narrative grammar, plan format, voice, review, craft laws
├── vulkan/                GPU-selection layer, for rendering on named GPUs
└── assets/                script and series templates
docs/                      decisions and research
vendor/welch-labs-videos/  gitignored reference clone (MIT)
.claude-plugin/            plugin and marketplace manifests
```

## Credits

- Pedagogy and look from Grant Sanderson's [3Blue1Brown](https://www.3blue1brown.com/) and
  Stephen Welch's [Welch Labs](https://www.youtube.com/@WelchLabs), with intuitive-derivation
  principles distilled from Mahesh Shenoy's [FloatHeadPhysics](https://www.youtube.com/@Mahesh_Shenoy).
- The Welch pack ports helpers from
  [stephencwelch/manim_videos](https://github.com/stephencwelch/manim_videos) (MIT).
- Rendering by [manimgx](https://github.com/academa-labs/manimgx).
- Early inspiration from [AmitSubhash/3brown1blue](https://github.com/AmitSubhash/3brown1blue)
  (MIT).

## License

[MIT](LICENSE)
