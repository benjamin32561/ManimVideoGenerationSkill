# Voice: narration and word timings

`scripts/voice.py demos/<series>/<slug>` runs after `lint_script.py` passes.

## What it does

1. Sends the narration to the series style's voice through OpenRouter (`voice` in
   `style.yaml`): Gemini 3.8 Flash TTS, voice Charon, with the style's delivery instruction
   (decision 26). The instruction sets pace and register: the 3b1b instruction asks for a
   brisk, conversational 180 wpm; the Welch one for a measured documentary voice at 155 wpm,
   because Gemini speaks faster than asked (it measured about 180).
2. Uses one request per video, so the whole narration is one prosodic arc. A script longer
   than the voice's `max_chars` is split between units, never mid-unit, with a 0.35 s pause
   at each seam.
3. Transcribes each request's audio on its own with Whisper (word timestamps). On a long
   file, Whisper drops whole stretches. It then refuses to finish if six or more consecutive
   script words are missing from the transcript, and quotes them. Listen to that spot: if the
   speech is there, run it again; if the voice skipped it, reword.

It writes `audio/narration.wav`, `audio/narration.mp3`, `audio/words.json` and
`audio/voice.json`. `voice.json` ties the audio to the exact spoken words and the style's
voice. `plan_check.py` refuses to run if any `say` or the voice changed since; `show` edits
don't count.

OpenRouter is the only provider. A failed request stops the step with the provider's
message: fix the account or key, not the pipeline. `402 ... exceeds your available credits`
means the account is out of credit; capping the request does not help.

## Writing for the voice

- **Spoken words only in `say`:** no LaTeX, no symbols (`references/spoken-math.md`).
- **The text sets the pace more than the voice does.** Long flowing sentences read faster and
  smoother than clipped ones, and the style's speaker profile gives the target sentence
  length.
- Pauses come from the writing: sentence ends, and the seams between units. There are no
  pause fields and no padding with silence.
- Prefer US spellings for words you will anchor events to (Whisper writes US spelling).

## After voicing

- **Re-run the lint.** It now uses real beat times, and measures words per minute and long
  pauses against the style.
- **Write the events from the transcript.** Anchors are phrases from `audio/words.json`.
  Numbers match in words or digits ("about one hundred forty millimolar" finds "about 140
  millimolar"). Whisper may split compounds, so copy those as it wrote them.
- **The lint checks numbers after voicing.**
  - `misheard_number`: the voice said a number the script never wrote, so the viewer hears it
    too.
  - `run_on_number`: a phrase like "seventy too" that sounds like one number, caught before
    voicing.

  Reword and voice again.
- If the narration must change, edit `say`, lint, voice again, then re-check the plan: the
  anchors move with the words.
