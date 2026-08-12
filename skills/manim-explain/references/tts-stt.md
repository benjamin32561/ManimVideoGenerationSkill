# TTS / STT (OpenRouter)

## Auth

`OPENROUTER_API_KEY` from environment or repo-root `.env`.

## Defaults

| Role | Model | Notes |
|------|-------|-------|
| TTS | `x-ai/grok-voice-tts-1.0` | voice **`leo`** (calm lecturer) |
| TTS alt | `google/gemini-3.1-flash-tts-preview` | when style prompts help |
| STT | `openai/whisper-large-v3` | `verbose_json` + word timestamps |
| Draft TTS | `hexgrad/kokoro-82m` | cheap smoke only |

Endpoint TTS: `POST https://openrouter.ai/api/v1/audio/speech`  
Endpoint STT: `POST https://openrouter.ai/api/v1/audio/transcriptions`

## Teaching-style text (before TTS)

Matters more than voice choice:

- Ellipses for thinking pauses: `"Here is the rule... share, then divide."`
- Rhetorical questions: `"Why not a hard threshold?"`
- Quote key terms lightly in prose if it helps prosody
- 1–2 sentence beats aligned to visual phases
- **No raw LaTeX** — see spoken-math.md

## CLI

```bash
source skills/manim-explain/scripts/env.sh
python skills/manim-explain/scripts/tts_openrouter.py demos/<slug>/script.yaml
python skills/manim-explain/scripts/align_words.py demos/<slug>
```

## Grok voices

`eve`, `ara`, `rex`, `sal`, **`leo`** (default for this skill).

## No second provider

OpenRouter is the **only** TTS path in this skill. Do not add or restore another
vendor; fix narration text, chunking, and pauses instead (see [vo-tips.md](vo-tips.md)).