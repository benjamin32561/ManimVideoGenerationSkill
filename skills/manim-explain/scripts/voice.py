"""Voice a script and time its words: ``voice.py demos/<series>/<slug>``.

Refuses to run unless ``lint_script.py`` passed for the current script. Sends the narration
to the series style's TTS voice through OpenRouter in as few requests as possible: one, or,
when the script is longer than the voice's ``max_chars``, one per run of whole units (never
mid-unit, so a unit's prosody is one arc), joined with a short paragraph pause. Then
transcribes each request's audio separately with word timestamps (Whisper drops stretches of
long files), and refuses to finish if a stretch of six or more script words is missing from
the transcript.

Writes ``audio/narration.wav``, ``audio/narration.mp3``, ``audio/words.json`` and
``audio/voice.json``. The last ties the audio to the spoken words and the voice it was made
from; ``plan_check.py`` refuses a narration older than the script. Re-run the lint afterwards:
it then measures the real pace and pauses.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import json
import tempfile

from explain.media import duration, encode_pcm
from explain.openrouter import speak, transcribe
from explain.paths import Video, load_dotenv
from explain.plan import narration_digest, script_digest
from explain.problems import Problem
from explain.report import require_passed, write_report
from explain.script import Script, ScriptBeat, load_script
from explain.styles import load_style
from explain.timing import Transcript, locate_beats, unheard_phrases

CHUNK_PAUSE_S = 0.35
DROPPED_RUN = 6


def chunks(script: Script, max_chars: int) -> list[str]:
    """Group the narration into request-sized texts, breaking only between units.

    A unit longer than ``max_chars`` on its own is split between beats instead.

    Args:
        script: The script.
        max_chars: The voice's longest request.

    Returns:
        The texts to voice, in order.
    """
    units: list[list[ScriptBeat]] = []
    for beat in script.beats:
        if units and units[-1][-1].unit == beat.unit:
            units[-1].append(beat)
        else:
            units.append([beat])
    pieces: list[str] = []
    for unit in units:
        text = " ".join(b.say for b in unit)
        pieces.extend([text] if len(text) <= max_chars else [b.say for b in unit])
    texts: list[str] = []
    for piece in pieces:
        if texts and len(texts[-1]) + 1 + len(piece) <= max_chars:
            texts[-1] += " " + piece
        else:
            texts.append(piece)
    return texts


def transcribe_pieces(pieces: list[bytes], rate: int, work_dir: Path) -> list[dict]:
    """Transcribe each voiced piece on its own and place its words on the joined timeline.

    Args:
        pieces: PCM of each TTS request, in order.
        rate: Sample rate (Hz).
        work_dir: Where the temporary per-piece MP3s are written (and removed).

    Returns:
        ``[{"word", "start", "end"}]`` for the whole narration.
    """
    words, offset = [], 0.0
    for piece in pieces:
        with tempfile.NamedTemporaryFile(suffix=".mp3", dir=work_dir) as handle:
            encode_pcm(piece, rate, Path(handle.name), "96k")
            for w in transcribe(Path(handle.name)):
                words.append({"word": w["word"], "start": round(w["start"] + offset, 3),
                              "end": round(w["end"] + offset, 3)})
        offset += len(piece) / 2 / rate + CHUNK_PAUSE_S
    return words


def main() -> None:
    """Voice the script, transcribe it, and check every beat is heard.

    Raises:
        SystemExit: If the lint has not passed, a request fails, or a stretch of the script is
            missing from the transcript.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", help="demos/<series>/<slug>")
    args = parser.parse_args()
    video = Video.at(args.video)
    load_dotenv(video.project)
    style = load_style(video.style_name)
    require_passed(video.lint_report, script_digest(video, style), "lint_script.py")
    video.voice_report.unlink(missing_ok=True)
    script = load_script(video.script)
    rate = style.voice.sample_rate
    texts = chunks(script, style.voice.max_chars)
    pieces = [speak(text, style.voice) for text in texts]
    pcm = (b"\x00\x00" * int(CHUNK_PAUSE_S * rate)).join(pieces)
    encode_pcm(pcm, rate, video.narration_wav)
    encode_pcm(pcm, rate, video.narration_mp3, "96k")
    words = transcribe_pieces(pieces, rate, video.audio_dir)
    video.words.write_text(json.dumps({"duration": duration(video.narration_wav), "words": words}, indent=1) + "\n")
    beat_texts = [(b.id, b.say) for b in script.beats]
    transcript = Transcript.load(video.words)
    dropped = [Problem("unheard_speech", "error", beat, detail=f'"{text}"')
               for beat, text in unheard_phrases(beat_texts, transcript, DROPPED_RUN)]
    write_report(video.voice_report, narration_digest(script, style.voice), dropped,
                 requests=len(texts), words=len(words))
    if dropped:
        raise SystemExit("The transcript is missing speech: " + "; ".join(f"{p.subject}: {p.detail}" for p in dropped)
                         + ". If audio/narration.wav has it, run voice.py again; if not, the voice skipped it.")
    beats = locate_beats(beat_texts, transcript)
    print(f"voice {video.series}/{video.slug}: {len(texts)} request(s), {len(words)} words, "
          f"{beats[-1].end:.1f} s, {style.voice.model} / {style.voice.voice}")


if __name__ == "__main__":
    main()
