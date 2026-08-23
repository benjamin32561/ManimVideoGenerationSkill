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

# STT models transcribe in US spelling whatever the narration was written in, so
# a British cue word ("memorises") never matches its transcript ("memorizes").
_SPELLING_PAIRS = {
    "centre": "center", "metre": "meter", "litre": "liter", "fibre": "fiber",
    "theatre": "theater", "defence": "defense", "offence": "offense",
    "licence": "license", "practise": "practice", "grey": "gray",
    "catalogue": "catalog", "dialogue": "dialog", "colour": "color",
    "behaviour": "behavior", "favour": "favor", "honour": "honor",
    "labour": "labor", "neighbour": "neighbor", "humour": "humor",
    "rumour": "rumor", "odour": "odor", "vapour": "vapor", "armour": "armor",
    "harbour": "harbor", "valour": "valor", "savour": "savor",
    "endeavour": "endeavor", "splendour": "splendor",
}
_IS_TO_IZ_SUFFIXES = ("ise", "ises", "ised", "ising", "isation", "isations")


def _edit_distance(a: str, b: str, *, cap: int) -> int:
    """Levenshtein distance between two short tokens, giving up past ``cap``.

    Args:
        a: First token.
        b: Second token.
        cap: Stop early once the best possible distance exceeds this.

    Returns:
        The edit distance, or ``cap + 1`` when it provably exceeds ``cap``.
    """
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        if min(cur) > cap:
            return cap + 1
        prev = cur
    return prev[-1]


def near_homophone(expected: str, actual: str) -> bool:
    """Whether a long technical cue survived STT as a near-miss spelling.

    Transcribers mangle rare terms ("equipartition" → "equipetition"). Only long
    tokens sharing a prefix are compared, and the tolerance stays tight, so
    ordinary words are never conflated.

    Args:
        expected: Normalized cue token from the script.
        actual: Normalized transcript token.

    Returns:
        True when the two are within the allowed edit distance.
    """
    if len(expected) < 8 or len(actual) < 8:
        return False
    if expected[:3] != actual[:3]:
        return False
    tolerance = 1 + len(expected) // 10
    return _edit_distance(expected, actual, cap=tolerance) <= tolerance


def same_word_number(a: str, b: str) -> bool:
    """Whether two tokens differ only by a trailing plural/possessive ``s``.

    STT writes "nats" as "nat's", which normalization reduces to "nat"; the same
    fold rescues "modes"/"mode" and "elements"/"element".

    Args:
        a: First normalized token.
        b: Second normalized token.

    Returns:
        True when stripping one trailing ``s`` from each makes them equal.
    """
    sa, sb = a.rstrip("s"), b.rstrip("s")
    return len(sa) >= 3 and sa == sb


def partial_word_match(expected: str, actual: str) -> bool:
    """Whether a cue survived STT as a fragment of itself, or vice versa.

    Transcribers split rare words across tokens ("recovered" → "but covered")
    and add or drop inflections ("element" → "elements"). Either way one token
    is a prefix or suffix of the other; requiring a long, high-coverage overlap
    keeps unrelated words apart.

    Args:
        expected: Normalized cue token from the script.
        actual: Normalized transcript token.

    Returns:
        True when one token is a prefix or suffix of the other, sharing at least
        six characters and 60% of the longer token.
    """
    long, short = (expected, actual) if len(expected) >= len(actual) else (actual, expected)
    if len(short) < 6:
        return False
    if not (long.startswith(short) or long.endswith(short)):
        return False
    return len(short) / len(long) >= 0.6


def canonical_spelling(word: str) -> str:
    """Fold British spellings onto their US form for cue matching.

    Args:
        word: Already-normalized token (lowercase, punctuation stripped).

    Returns:
        The US-spelling equivalent when one is known, else ``word`` unchanged.
    """
    for brit, us in _SPELLING_PAIRS.items():
        if word == brit:
            return us
        if word.startswith(brit) and len(word) - len(brit) <= 2:
            return us + word[len(brit) :]
    for suffix in _IS_TO_IZ_SUFFIXES:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[: -len(suffix)] + suffix.replace("is", "iz", 1)
    return word


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
    # British cue vs US transcript ("memorises" → "memorizes")
    if canonical_spelling(expected) == canonical_spelling(actual):
        return True
    # rare technical term mangled by STT ("equipartition" → "equipetition")
    if near_homophone(expected, actual):
        return True
    # cue split or inflected by STT ("recovered" → "but covered", "element"/"elements")
    if partial_word_match(expected, actual):
        return True
    # singular vs plural / possessive-stripped ("nats" → "nat's" → "nat")
    if same_word_number(expected, actual):
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
    last_time: float | None = None
    # A cue should land within a beat or two of the previous one. Scale the
    # tolerance to the narration so short demos are not judged by a long one.
    duration = float(words[-1].get("start", 0.0)) if words else 0.0
    max_gap = max(45.0, 4.0 * duration / max(1, len(bookmarks)))

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
        if found is None and len(parts) == 1:
            # Whisper splits compound technical words: "wordline" comes back as
            # "word line", "lookaside" as "look aside", "dataflow" as "data
            # flow". Retry the cue against pairs of adjacent transcript tokens.
            target = parts[0]
            for i in range(cursor, len(norm_words) - 1):
                joined = norm_words[i][0] + norm_words[i + 1][0]
                if _token_matches(target, joined):
                    found = (i, float(norm_words[i][1]["start"]))
                    break
        if found is None:
            print(f"warn: bookmark not found in STT words: {mark!r}", file=sys.stderr)
            continue
        idx, start = found
        # Reject an implausible jump. When Whisper writes a cue differently
        # ("wordline" -> "word line"), the search runs past where that beat
        # actually is and binds the *next* cue to a much later occurrence of the
        # same word — after which every remaining cue is hunted for beyond that
        # point and fails. One mangled word can take thirty with it. A cue that
        # lands far past the previous one is almost always this failure, so drop
        # it and leave the cursor where it was rather than derailing the rest.
        if last_time is not None and start - last_time > max_gap:
            print(
                f"warn: bookmark {mark!r} only matches {start:.1f}s, "
                f"{start - last_time:.1f}s after the previous cue — treating as "
                "not found rather than binding it there",
                file=sys.stderr,
            )
            continue
        last_time = start
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
    _fail_on_missing(missing)


def _fail_on_missing(missing: list[str]) -> None:
    """Stop the pipeline when a cue did not survive transcription.

    An unresolved cue is not a warning: the scene will call ``wait_until`` on it
    and die mid-render, after the expensive part. It is also the one failure the
    three audits cannot reach, since they only run on a render that finished.
    Whisper writes what it *hears*, so the usual causes are a word it mangles
    ("guards" comes back "gods", "bench" comes back "bent"). The repair is to
    re-cue that beat on a word the transcript actually contains and re-run with
    ``--remap``, which costs nothing.

    Args:
        missing: Bookmark names absent from the resolved cue table.

    Raises:
        SystemExit: If anything is missing, with the repair instructions.
    """
    if not missing:
        return
    raise SystemExit(
        f"\nERROR: {len(missing)} cue(s) did not survive transcription: {missing}\n"
        "  Whisper transcribes what it hears, so pick a different, distinctive\n"
        "  word from the same sentence — check the transcript in timing.json for\n"
        "  what it actually wrote — then re-run with --remap (no STT cost)."
    )


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
    for k, v in bookmark_times.items():
        print(f"  @{k}: {v:.3f}s")
    _fail_on_missing(missing)


if __name__ == "__main__":
    main()
