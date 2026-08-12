#!/usr/bin/env python3
"""Generate narration audio from script.yaml via OpenRouter TTS.

This is the **only** TTS path in this skill: OpenRouter (Grok Voice, male voice
``leo`` by default). Chunking follows ``tts.chunk_by``; the per-chunk
``pause_after`` silences are baked into the concatenated mp3 so Manim can
soft-idle in real audio gaps (craft law: VO must breathe).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
import yaml

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from skill_paths import find_project_root, load_dotenv  # noqa: E402
from tts_chunking import chunk_plan  # noqa: E402

OPENROUTER_TTS = "https://openrouter.ai/api/v1/audio/speech"
DEFAULT_MODEL = os.environ.get("MANIM_EXPLAIN_TTS_MODEL", "x-ai/grok-voice-tts-1.0")
DEFAULT_VOICE = os.environ.get("MANIM_EXPLAIN_TTS_VOICE", "leo")

_LATEX_DANGER = re.compile(
    r"(\\mathrm|\\frac|\\sum|\\mu|\\sigma|\\text\{|\$\$|\\\(|\\\[)"
)




def prepare_openrouter(text: str) -> str:
    """Strip authoring tags so the TTS model never speaks them aloud.

    Emotion tags (``[curious]`` …) are dropped; ``[pause]`` becomes an ellipsis,
    which Grok Voice renders as a short breath. Real (longer) pauses come from
    ``pause_after`` silence, not from tags.

    Args:
        text: Raw ``say`` text from ``script.yaml``.

    Returns:
        Cleaned, single-spaced narration text.
    """
    text = re.sub(r"\[(?:curious|thoughtful|whisper|shout)\]", "", text, flags=re.I)
    text = re.sub(r"\[(?:long )?pause\]", "...", text, flags=re.I)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+\.\.\.", "...", text)
    return text.strip()


def assert_no_latex(text: str) -> None:
    """Refuse to synthesize narration that still contains LaTeX source.

    Args:
        text: Full narration text about to be sent to the TTS API.

    Raises:
        SystemExit: If LaTeX markup is detected (craft law: spoken math only).
    """
    stripped = re.sub(r"\[[^\]]+\]", " ", text)
    if _LATEX_DANGER.search(stripped) or "$" in stripped:
        raise SystemExit(
            "Refusing to TTS text that looks like LaTeX. "
            "Put display math in beat.latex / show only; rewrite say in spoken math."
        )


def synthesize(
    text: str,
    *,
    model: str,
    voice: str,
    response_format: str,
    api_key: str,
    speed: float | None = None,
) -> bytes:
    """Synthesize one chunk of narration through OpenRouter.

    Args:
        text: Narration text for this chunk (no LaTeX, no authoring tags).
        model: OpenRouter TTS model id.
        voice: Voice name (``leo`` by default — male, calm lecturer).
        response_format: Audio container, normally ``mp3``.
        api_key: OpenRouter API key.
        speed: Optional speaking-rate multiplier (~0.95 for explanations).

    Returns:
        Raw audio bytes for the chunk.

    Raises:
        SystemExit: If the API returns an error status or a JSON error body.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/benjamin32561/ManimVideoGenerationSkill",
        "X-Title": "ManimVideoGenerationSkill",
    }
    payload: dict = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": response_format,
    }
    if speed is not None:
        payload["speed"] = float(speed)
    resp = requests.post(OPENROUTER_TTS, headers=headers, json=payload, timeout=300)
    if resp.status_code >= 400:
        raise SystemExit(f"TTS failed {resp.status_code}: {resp.text[:800]}")
    ctype = resp.headers.get("Content-Type", "")
    if "json" in ctype and not resp.content[:4]:
        raise SystemExit(f"TTS returned JSON error: {resp.text[:800]}")
    return resp.content


def concat_mp3(
    chunks: list[Path],
    out: Path,
    *,
    silence_between: float = 0.0,
    silences: list[float] | None = None,
) -> None:
    """Concatenate chunk mp3s with baked silence gaps between them.

    Decodes to wav, splices generated silence, then re-encodes once, so the
    gaps are real audio (Manim can soft-idle inside them).

    Args:
        chunks: Ordered chunk mp3 paths.
        out: Destination mp3 path.
        silence_between: Uniform gap in seconds when ``silences`` is None.
        silences: Per-boundary gaps; length must be ``len(chunks) - 1``.

    Raises:
        ValueError: If ``silences`` does not match the number of boundaries.
    """
    gaps = silences
    if gaps is None:
        gaps = [float(silence_between)] * max(0, len(chunks) - 1)
    if len(gaps) != max(0, len(chunks) - 1):
        raise ValueError(f"silences length {len(gaps)} != {len(chunks) - 1}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        wavs: list[Path] = []
        for i, ch in enumerate(chunks):
            wav = tmp_path / f"c{i:03d}.wav"
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(ch), "-ar", "44100", "-ac", "1", str(wav)],
                check=True,
                capture_output=True,
            )
            wavs.append(wav)
            if i < len(chunks) - 1 and gaps[i] > 1e-4:
                sil = tmp_path / f"s{i:03d}.wav"
                subprocess.run(
                    [
                        "ffmpeg", "-y",
                        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                        "-t", str(gaps[i]),
                        str(sil),
                    ],
                    check=True,
                    capture_output=True,
                )
                wavs.append(sil)
        listing = tmp_path / "list.txt"
        listing.write_text("".join(f"file '{w}'\n" for w in wavs))
        merged = tmp_path / "merged.wav"
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(listing), "-c", "copy", str(merged),
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(merged),
                "-codec:a", "libmp3lame", "-qscale:a", "2", str(out),
            ],
            check=True,
            capture_output=True,
        )
    if gaps:
        print(f"Concatenated {len(chunks)} chunks; gaps={','.join(f'{g:.2f}' for g in gaps)}")
    else:
        print(f"Concatenated {len(chunks)} chunks (no gaps)")


def prepend_silence(audio_path: Path, seconds: float) -> None:
    """Pad the start of an mp3 with silence so the first word is not clipped.

    Args:
        audio_path: Narration mp3 to pad in place.
        seconds: Head silence in seconds (craft law: ≥ 1.0–1.5).
    """
    if seconds <= 0:
        return
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        padded = tmp_path / "padded.mp3"
        silence = tmp_path / "silence.wav"
        narration = tmp_path / "narration.wav"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", str(seconds),
                str(silence),
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(audio_path), "-ar", "44100", "-ac", "1", str(narration)],
            check=True,
            capture_output=True,
        )
        listing = tmp_path / "list.txt"
        listing.write_text(f"file '{silence}'\nfile '{narration}'\n")
        merged = tmp_path / "merged.wav"
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(listing), "-c", "copy", str(merged),
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(merged),
                "-codec:a", "libmp3lame", "-qscale:a", "2", str(padded),
            ],
            check=True,
            capture_output=True,
        )
        audio_path.write_bytes(padded.read_bytes())
    print(f"Prepended {seconds:.2f}s silence -> {audio_path}")


def main() -> None:
    """CLI: read a demo ``script.yaml`` and write ``audio/narration.mp3``.

    Raises:
        SystemExit: If ``OPENROUTER_API_KEY`` is missing or the script has no
            spoken text.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path, help="Path to script.yaml")
    parser.add_argument("-o", "--output", type=Path, default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--voice", default=None)
    parser.add_argument("--speed", type=float, default=None)
    args = parser.parse_args()

    script_path = args.script.resolve()
    demo_dir = script_path.parent
    load_dotenv(find_project_root(demo_dir))

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY not set (export or put in repo .env)")

    script = yaml.safe_load(script_path.read_text())
    tts_cfg = script.get("tts") or {}
    model = args.model or tts_cfg.get("model") or DEFAULT_MODEL
    voice = args.voice or tts_cfg.get("voice") or DEFAULT_VOICE
    fmt = tts_cfg.get("response_format") or "mp3"
    speed = args.speed if args.speed is not None else tts_cfg.get("speed")
    if speed is not None:
        speed = float(speed)
    head = float(tts_cfg.get("head_silence", 1.5))
    gap = float(tts_cfg.get("inter_chunk_silence", 0.45))
    chunk_by = tts_cfg.get("chunk_by")

    plan = chunk_plan(
        script,
        prepare=prepare_openrouter,
        chunk_by=chunk_by,
        default_gap=gap,
    )
    chunks = [c["text"] for c in plan]
    gaps = [float(c["pause_after"]) for c in plan[:-1]]
    if not chunks:
        raise SystemExit("No beat.say text found in script")
    full = " ".join(chunks)
    assert_no_latex(full)

    out = args.output or (demo_dir / "audio" / f"narration.{fmt}")
    out.parent.mkdir(parents=True, exist_ok=True)
    chunk_dir = demo_dir / "audio" / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"TTS model={model} voice={voice} speed={speed} "
        f"chunks={len(chunks)} gaps={[round(g,2) for g in gaps]} head={head} chars={len(full)}"
    )

    paths: list[Path] = []
    for i, text in enumerate(chunks):
        audio = synthesize(
            text,
            model=model,
            voice=voice,
            response_format=fmt,
            api_key=api_key,
            speed=speed,
        )
        path = chunk_dir / f"chunk_{i:02d}.{fmt}"
        path.write_bytes(audio)
        paths.append(path)
        print(f"  chunk {i+1}/{len(chunks)} -> {path.name} ({len(audio)} bytes)")

    if len(paths) == 1:
        out.write_bytes(paths[0].read_bytes())
    else:
        concat_mp3(paths, out, silences=gaps)

    prepend_silence(out, head)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")
    (demo_dir / "audio" / "narration.txt").write_text(full + "\n")


if __name__ == "__main__":
    main()
