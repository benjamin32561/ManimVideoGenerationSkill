# Narration tips (less “dead” VO)

Single provider: **OpenRouter** (`x-ai/grok-voice-tts-1.0`, male voice **`leo`**).
There is no second TTS path — do not add one, and do not chase a different voice
before fixing the text.

## What usually makes it feel wrong

1. **Script cadence** — flat encyclopedia prose. Fix the text before touching knobs.
2. **Chunk seams** — one request per tiny beat resets energy. Group with `tts_chunk`.
3. **No breathing room** — continuous speech reads as *running*. Split the chunk and
   bake `pause_after` silence (see budgets below).
4. **Speed off** — explanations ~0.95; don't drag. Head silence **1.0–1.5s** or the
   first word is clipped.
5. **Tag spam** — `[curious]`-style tags are stripped before synthesis; `[pause]`
   becomes an ellipsis. Real pauses come from silence, never from tags.

## Pause budgets (baked into the audio)

| Moment | `pause_after` |
|--------|----------------|
| After naming an object | 0.55–0.75 |
| After a **question** | **0.9–1.3** |
| After a heavy morph / formula land | 0.7–1.0 |

Default `tts.inter_chunk_silence` ~0.4–0.5.

## Tone split (craft law)

| Beat type | Delivery |
|-----------|----------|
| Hook / mystery / dual worlds | Curious: questions, ellipses, short beats |
| Definitions / formula / traps | Documentary: clean sentences, steady |

## Defaults

| Knob | Value |
|------|--------|
| Model | `x-ai/grok-voice-tts-1.0` |
| Voice | `leo` (male; Ben prefers male narration) |
| Speed | 0.95 |
| Chunking | `chunk_by: tts_chunk` (A0, A1, B0 … groups) |
| Head silence | 1.5 |
| Inter-chunk silence | 0.45 |
| Format | `mp3` |

Other Grok voices if `leo` ever fails: `rex`, `sal`, `eve`, `ara`.

## Script writing

- Short beats. Rhetorical questions in hooks only.
- Ellipses for thinking pauses; end a question **in its own chunk**, then pause.
- Quote key terms lightly: the word "on".
- Never LaTeX in `say` — spoken math only (see [spoken-math.md](spoken-math.md)).
- Bookmarks must be distinctive words Whisper keeps.
