"""OpenRouter speech requests: text to speech (the style's voice) and word-timed transcription.

Both go through one OpenRouter key (``OPENROUTER_API_KEY`` in the environment or the
project's ``.env``). There is no second provider: a missing key or a failed request stops
the pipeline with the provider's message.
"""

import os
from pathlib import Path

import requests

from explain.styles import Voice

TTS_URL = "https://openrouter.ai/api/v1/audio/speech"
STT_URL = "https://openrouter.ai/api/v1/audio/transcriptions"
STT_MODEL = "openai/whisper-large-v3"
TIMEOUT_S = 900


def api_key() -> str:
    """The OpenRouter key from the environment (load the project ``.env`` first).

    Returns:
        The key.

    Raises:
        SystemExit: If no key is configured.
    """
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set (export it or put it in the project's .env).")
    return key


def speak(text: str, voice: Voice) -> bytes:
    """Synthesize narration as raw 16-bit mono PCM at the voice's sample rate.

    Args:
        text: The words to speak (no LaTeX).
        voice: The style's voice: model, voice name and delivery instruction.

    Returns:
        The PCM bytes.

    Raises:
        SystemExit: If the request fails or returns something other than audio.
    """
    resp = requests.post(TTS_URL, headers={"Authorization": f"Bearer {api_key()}"}, timeout=TIMEOUT_S, json={
        "model": voice.model, "voice": voice.voice, "input": text, "instructions": voice.instructions,
        "response_format": "pcm"})
    if resp.status_code >= 400 or "json" in (resp.headers.get("Content-Type") or ""):
        raise SystemExit(f"TTS failed ({resp.status_code}): {resp.text[:800]}")
    return resp.content


def transcribe(audio: Path) -> list[dict]:
    """Transcribe narration with word timestamps.

    Args:
        audio: An audio file under the provider's 25 MB limit (MP3 for long narrations).

    Returns:
        ``[{"word", "start", "end"}]`` in order.

    Raises:
        SystemExit: If the request fails or returns no word timings.
    """
    with Path(audio).open("rb") as handle:
        resp = requests.post(STT_URL, headers={"Authorization": f"Bearer {api_key()}"}, timeout=TIMEOUT_S,
                             files={"file": (Path(audio).name, handle, "audio/mpeg")},
                             data={"model": STT_MODEL, "response_format": "verbose_json",
                                   "timestamp_granularities[]": "word"})
    if resp.status_code >= 400:
        raise SystemExit(f"Transcription failed ({resp.status_code}): {resp.text[:800]}")
    data = resp.json()
    words = data.get("words") or [w for seg in data.get("segments", []) for w in seg.get("words", [])]
    if not words:
        raise SystemExit("Transcription returned no word timestamps.")
    return [{"word": w["word"].strip(), "start": round(float(w["start"]), 3), "end": round(float(w["end"]), 3)}
            for w in words]
