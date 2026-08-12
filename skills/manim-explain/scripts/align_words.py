#!/usr/bin/env python3
"""Align narration audio → word timestamps + bookmark absolute times."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

import requests
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skill_paths import find_project_root, load_dotenv  # noqa: E402

OPENROUTER_STT = "https://openrouter.ai/api/v1/audio/transcriptions"
DEFAULT_STT = os.environ.get("MANIM_EXPLAIN_STT_MODEL", "openai/whisper-large-v3")




def normalize_token(w: str) -> str:
    w = w.lower().strip()
    w = re.sub(r"[^a-z0-9']+", "", w)
    # strip possessive / trailing apostrophe-s so "unit's" matches "unit"
    if w.endswith("'s"):
        w = w[:-2]
    w = w.strip("'")
    return w


# Whisper writes numerals and symbols where the script spells them out
# ("ten percent" → "10%"). Cues stay spelled-out English in ``say``; matching
# happens on this shared vocabulary.
NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
    "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30",
    "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
    "eighty": "80", "ninety": "90", "hundred": "100",
}
_SYMBOL_WORDS = {"%": "percent", "$": "dollars", "&": "and", "+": "plus", "=": "equals"}


def expand_words(words: list[dict]) -> list[dict]:
    """Split symbol-glued STT tokens so spelled-out cues can match.

    Whisper emits ``10%`` as a single word; a script that says "ten percent"
    then has no ``percent`` token to bookmark. Each symbol is emitted as its own
    word sharing the source timestamps, so cue times stay exact.

    Args:
        words: STT words with ``word`` / ``start`` / ``end`` keys.

    Returns:
        A new word list with symbol tokens expanded into spoken equivalents.
    """
    out: list[dict] = []
    for w in words:
        raw = str(w.get("word", ""))
        out.append(w)
        for sym, spoken in _SYMBOL_WORDS.items():
            if sym in raw:
                out.append({**w, "word": spoken})
    return out


def collect_bookmarks(script: dict) -> list[str]:
    marks: list[str] = []
    for beat in script.get("beats") or []:
        for m in beat.get("bookmarks") or []:
            marks.append(str(m))
    return marks


def _token_matches(expected: str, actual: str) -> bool:
    """Fuzzy token match for Whisper quirks (hyphen splits, near-homophones)."""
    if expected == actual:
        return True
    # hyphenated cue may arrive as one token or as adjacent tokens handled by phrase match
    if expected.replace("-", "") == actual.replace("-", ""):
        return True
    # Whisper often hears "on-mass" as "masse" / "mass"
    aliases = {
        # Whisper often hears "on-mass" as French "en masse"
        "onmass": {"onmass", "masse", "mass", "enmasse", "en"},
        "on-mass": {"onmass", "masse", "mass", "enmasse"},
        "numerator": {"numerator", "numerators"},
        "denominator": {"denominator", "denominators"},
        "read": {"read", "reading"},
        "reading": {"read", "reading"},
        "peakier": {"peakier", "peekier", "peekierdistributions"},
        "Peakier": {"peakier", "peekier"},
        "eye": {"eye", "eyes", "i"},
    }
    for key, group in aliases.items():
        if expected in group or expected == key:
            if actual in group or actual == key:
                return True
    # spelled-out number cue vs numeral transcript (and back)
    if NUMBER_WORDS.get(expected) == actual or NUMBER_WORDS.get(actual) == expected:
        return True
    return False


def map_bookmarks(words: list[dict], bookmarks: list[str]) -> dict[str, float]:
    """Map bookmarks in order, searching only forward in the transcript.

    This keeps cue times monotonic with the script. Bookmark may be a single
    word or a short phrase.
    """
    norm_words = [(normalize_token(w.get("word", "")), w) for w in expand_words(words)]
    out: dict[str, float] = {}
    cursor = 0

    for mark in bookmarks:
        parts = [normalize_token(p) for p in mark.split() if normalize_token(p)]
        if not parts:
            continue
        found = None
        for i in range(cursor, len(norm_words)):
            tok, w = norm_words[i]
            if not _token_matches(parts[0], tok):
                # "on-mass" often arrives as "on mass", "en masse", or "masse"
                if parts[0] == "onmass":
                    if tok in {"masse", "mass", "onmass"}:
                        found = (i, float(w["start"]))
                        break
                    if tok in {"on", "en"} and i + 1 < len(norm_words):
                        nxt = norm_words[i + 1][0]
                        if nxt in {"mass", "masse", "onmass"}:
                            found = (i, float(w["start"]))
                            break
                continue
            ok = True
            for j, part in enumerate(parts[1:], start=1):
                if i + j >= len(norm_words) or not _token_matches(part, norm_words[i + j][0]):
                    ok = False
                    break
            if ok:
                found = (i, float(w["start"]))
                break
        if found is None:
            print(f"warn: bookmark not found in STT words: {mark!r}", file=sys.stderr)
            continue
        idx, start = found
        cursor = idx + 1
        key = mark
        n = 2
        while key in out:
            key = f"{mark}#{n}"
            n += 1
        out[key] = start
    return out

def transcribe(audio_path: Path, *, model: str, api_key: str) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/benjamin32561/ManimVideoGenerationSkill",
        "X-Title": "ManimVideoGenerationSkill",
    }
    # Prefer OpenAI-compatible multipart for word timestamps
    with audio_path.open("rb") as f:
        files = {"file": (audio_path.name, f, "application/octet-stream")}
        data = {
            "model": model,
            "response_format": "verbose_json",
            "timestamp_granularities[]": "word",
        }
        resp = requests.post(
            OPENROUTER_STT, headers=headers, files=files, data=data, timeout=300
        )
    if resp.status_code >= 400:
        # Fallback: base64 JSON body (may lack word timings on some providers)
        b64 = base64.b64encode(audio_path.read_bytes()).decode("ascii")
        fmt = audio_path.suffix.lstrip(".") or "mp3"
        resp = requests.post(
            OPENROUTER_STT,
            headers={**headers, "Content-Type": "application/json"},
            json={
                "model": model,
                "response_format": "verbose_json",
                "timestamp_granularities": ["word"],
                "input_audio": {"data": b64, "format": fmt},
            },
            timeout=300,
        )
    if resp.status_code >= 400:
        raise SystemExit(f"STT failed {resp.status_code}: {resp.text[:1000]}")
    return resp.json()


def probe_duration(path: Path) -> float:
    import subprocess

    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def transcribe_chunked(
    demo_dir: Path,
    script: dict,
    *,
    model: str,
    api_key: str,
) -> tuple[list[dict], float, str]:
    """STT each TTS chunk, offset by head silence + inter-chunk gaps.

    Full-file Whisper often drops middle sections when the VO has long gaps;
    per-chunk STT is more reliable.
    """
    tts_cfg = script.get("tts") or {}
    head = float(tts_cfg.get("head_silence", 0.0))
    default_gap = float(tts_cfg.get("inter_chunk_silence", 0.35))

    # Match TTS concatenation gaps (per-chunk pause_after)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from tts_chunking import chunk_plan  # noqa: WPS433

    plan = chunk_plan(script, chunk_by=tts_cfg.get("chunk_by"), default_gap=default_gap)
    gaps = [float(c["pause_after"]) for c in plan[:-1]]

    chunk_dir = demo_dir / "audio" / "chunks"
    if not (chunk_dir.is_dir() and any(chunk_dir.glob("chunk_*.mp3"))):
        raise FileNotFoundError(f"No {chunk_dir} with chunk_*.mp3 (run tts_openrouter.py first)")

    paths = sorted(chunk_dir.glob("chunk_*.mp3"))
    if gaps and len(gaps) != len(paths) - 1:
        print(
            f"  warn: plan gaps ({len(gaps)}) != chunk files-1 ({len(paths)-1}); "
            f"falling back to uniform {default_gap}s"
        )
        gaps = [default_gap] * (len(paths) - 1)

    words: list[dict] = []
    texts: list[str] = []
    t = head
    for i, path in enumerate(paths):
        gap_i = gaps[i] if i < len(gaps) else 0.0
        print(f"  STT chunk {i+1}/{len(paths)} {path.name} @ offset {t:.2f}s (next_gap={gap_i:.2f})")
        result = transcribe(path, model=model, api_key=api_key)
        chunk_words = result.get("words") or []
        if not chunk_words and result.get("segments"):
            for seg in result["segments"]:
                chunk_words.extend(seg.get("words") or [])
        for w in chunk_words:
            words.append(
                {
                    "word": w.get("word", ""),
                    "start": float(w.get("start", 0)) + t,
                    "end": float(w.get("end", w.get("start", 0))) + t,
                }
            )
        texts.append(result.get("text") or "")
        dur = probe_duration(path)
        t += dur
        if i < len(paths) - 1:
            t += gap_i
    return words, t, " ".join(texts).strip()


def remap(demo_dir: Path, script: dict) -> None:
    """Recompute bookmark times from the words already stored in timing.json.

    Cheap repair path for cue-word edits: the audio and the transcript are
    unchanged, only the bookmark list moved, so no STT request is needed.

    Args:
        demo_dir: Demo directory holding ``timing.json``.
        script: Parsed ``script.yaml`` providing the bookmark list.

    Raises:
        SystemExit: If ``timing.json`` is missing or holds no words.
    """
    timing_path = demo_dir / "timing.json"
    if not timing_path.is_file():
        raise SystemExit(f"No {timing_path} to remap — run alignment first")
    timing = json.loads(timing_path.read_text())
    words = timing.get("words") or []
    if not words:
        raise SystemExit(f"{timing_path} has no words to remap")

    bookmarks = collect_bookmarks(script)
    timing["bookmarks"] = map_bookmarks(words, bookmarks)
    timing_path.write_text(json.dumps(timing, indent=2) + "\n")
    print(f"Remapped {len(timing['bookmarks'])}/{len(bookmarks)} bookmarks in {timing_path}")
    found_bases = {k.split("#")[0] for k in timing["bookmarks"]}
    missing = [b for b in bookmarks if b not in found_bases]
    if missing:
        print(f"warn: still missing bookmarks: {missing}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo_dir", type=Path, help="Demo directory containing script.yaml")
    parser.add_argument("--audio", type=Path, default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument(
        "--no-chunk-stt",
        action="store_true",
        help="Force single-file STT (less reliable with silence gaps)",
    )
    parser.add_argument(
        "--remap",
        action="store_true",
        help="Re-map bookmarks from the words already in timing.json (no STT call). "
        "Use after editing cue words only — audio and words must be unchanged.",
    )
    args = parser.parse_args()

    demo_dir = args.demo_dir.resolve()
    load_dotenv(find_project_root(demo_dir))

    script_path = demo_dir / "script.yaml"
    script = yaml.safe_load(script_path.read_text())
    stt_cfg = script.get("stt") or {}
    model = args.model or stt_cfg.get("model") or DEFAULT_STT

    if args.remap:
        remap(demo_dir, script)
        return

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY not set")

    audio = args.audio or (demo_dir / "audio" / "narration.mp3")
    if not audio.exists():
        alt = demo_dir / "audio" / "narration.wav"
        if alt.exists():
            audio = alt
        else:
            raise SystemExit(f"Audio not found: {audio}")

    words: list[dict] = []
    duration = 0.0
    transcript = ""
    used_chunked = False
    if not args.no_chunk_stt:
        try:
            print(f"STT model={model} mode=chunked")
            words, duration, transcript = transcribe_chunked(
                demo_dir, script, model=model, api_key=api_key
            )
            used_chunked = True
        except Exception as exc:  # noqa: BLE001
            print(f"warn: chunked STT failed ({exc}); falling back to full file")

    if not used_chunked:
        print(f"STT model={model} audio={audio}")
        result = transcribe(audio, model=model, api_key=api_key)
        words = result.get("words") or []
        if not words and result.get("segments"):
            for seg in result["segments"]:
                words.extend(seg.get("words") or [])
        transcript = result.get("text", "")
        duration = float(result.get("duration") or (words[-1].get("end") if words else 0) or 0)

    if not words:
        raise SystemExit("No word timestamps in STT response.")

    # Prefer real full-file duration when available
    try:
        duration = max(duration, probe_duration(audio))
    except Exception:  # noqa: BLE001
        pass

    bookmarks = collect_bookmarks(script)
    bookmark_times = map_bookmarks(words, bookmarks)

    timing = {
        "audio": str(audio.relative_to(demo_dir)),
        "duration": duration,
        "stt_model": model,
        "stt_mode": "chunked" if used_chunked else "full",
        "transcript": transcript,
        "words": [
            {
                "word": w.get("word", ""),
                "start": float(w.get("start", 0)),
                "end": float(w.get("end", w.get("start", 0))),
            }
            for w in words
        ],
        "bookmarks": bookmark_times,
    }
    out = demo_dir / "timing.json"
    out.write_text(json.dumps(timing, indent=2) + "\n")
    print(f"Wrote {out} ({len(words)} words, {len(bookmark_times)} bookmarks)")
    missing = [b for b in bookmarks if b not in bookmark_times and f"{b}#2" not in bookmark_times]
    # account for #n duplicates in collect — map_bookmarks uses mark / mark#n
    found_bases = {k.split("#")[0] for k in bookmark_times}
    missing = [b for b in bookmarks if b not in found_bases]
    if missing:
        print(f"warn: still missing bookmarks: {missing}")
    for k, v in bookmark_times.items():
        print(f"  @{k}: {v:.3f}s")


if __name__ == "__main__":
    main()
