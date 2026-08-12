# Sync pipeline

## Locked flow

```
script.yaml (say + bookmarks + show)
  → tts_openrouter.py  → audio/chunks/chunk_NN.mp3 + audio/narration.mp3
  → align_words.py     → timing.json  (words[] + bookmarks{})
  → Manim scene using absolute bookmark times
  → render_and_mux.sh  → out/final.mp4
```

TTS and STT both run through **OpenRouter** (single key). `align_words.py` uses
**chunked STT** over `audio/chunks/` — full-file Whisper drops middles when the
narration has baked silence gaps.

### Baking pauses (VO breathe)

When the viewer needs a beat after a name / grouping / **question** / finished morph:

1. End the current idea in its own `tts_chunk`
2. Set `pause_after` (names 0.55–0.75; **questions 0.9–1.3**; heavy morphs 0.7–1.0)
   — else `tts.inter_chunk_silence` (~0.4–0.5)
3. Soft-idle / pop the named object in Manim during that gap; **finish** the morph
   before the next bookmark (`TimedNarration.play_before`)

`scripts/tts_chunking.py` builds the plan; TTS concat and align must use the same gaps.
Run `scripts/lint_script.py` before TTS to catch short question pauses and empty formula beats.

### Visual-only iteration

If VO + bookmarks are already good, skip TTS/align:

```
edit scenes / style → render_and_mux.sh … -qm → out/final.mp4
```

Keep `timing.json` and `narration.mp3` unchanged. Still update `craft-laws.md` if
the visual fix teaches a reusable lesson.

## Bookmarks

In `script.yaml`, each beat lists `bookmarks` as cue words/phrases that appear in `say`:

```yaml
- id: formula
  say: >-
    On-mass is the share of the pie. Sum the gold heights, then divide by
    the sum of every height.
  bookmarks: [share, gold, divide]
  show: highlight numerator then denominator of on-mass formula
```

`align_words.py` finds the **first** matching word occurrence (case-insensitive) after the previous bookmark and records absolute start seconds.

Cue words must survive transcription. STT writes numbers and symbols in their
short form (`ten percent` → `10%`), so **cue the lexical word, not the number**.
The matcher normalizes digit↔word ("ten"↔"10") and splits symbol tokens
(`10%` → `10` + `percent`) before matching.

If only the cue list changed and the audio did not, repair the mapping for free:

```bash
python scripts/align_words.py demos/<slug> --remap   # re-maps from timing.json words, no STT call
```

## Manim timing helpers

```python
from timing_helpers import TimedNarration

tn = TimedNarration("timing.json", "audio/narration.mp3")
tn.attach(self)  # adds audio; tracks scene time

tn.wait_until("share")
self.play(...)
tn.play_before("gold", anim1, anim2, settle=0.35)  # lands before next cue
tn.wait_until("gold")
...
tn.wait_until_end()
```

`play_before` sizes `run_time` so the animation finishes with a settle gap before the
target bookmark — use it for formula morphs and other motions that must not spill
into the next spoken idea.

## timing.json shape

```json
{
  "audio": "audio/narration.mp3",
  "duration": 87.4,
  "words": [{"word": "On-mass", "start": 0.12, "end": 0.48}, ...],
  "bookmarks": {"share": 12.05, "gold": 18.40, "divide": 24.10}
}
```

## Anti-patterns

- Rendering silent video then `atempo`-stretching narration to match (3brown1blue hybrid) — last resort only
- Putting durations in the script before TTS
- Cueing every noun — only visual events