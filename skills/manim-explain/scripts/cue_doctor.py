#!/usr/bin/env python3
"""Diagnose cues that did not survive transcription, and suggest replacements.

A cue is matched forward-only against one transcript of the whole narration, so
a single word Whisper wrote differently does more than lose its own cue: the
matcher skips ahead hunting for the *next* cue and can bind it to a much later
occurrence, after which every remaining cue in the script fails. One mangled
word can take thirty with it.

This tool finds, for every unresolved cue, the transcript window where that
beat actually is, and proposes replacement words from the same beat that (a)
appear in that window, (b) are unique in the whole transcript, and (c) are long
enough to be distinctive.

Usage:
    python cue_doctor.py demos/<slug>
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

STOP = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "is",
    "it", "that", "this", "for", "with", "as", "by", "from", "you", "we", "so",
    "not", "are", "be", "has", "have", "had", "was", "were", "its", "one", "two",
    "into", "than", "then", "them", "they", "each", "every", "which", "what",
    "when", "where", "how", "why", "can", "will", "would", "there", "their",
}


def words_of(text: str) -> list[str]:
    """Lowercase word tokens of a string.

    Args:
        text: Any prose.

    Returns:
        Word tokens, apostrophes preserved inside words.
    """
    return re.findall(r"[A-Za-z']+", (text or "").lower())


def main() -> None:
    """Report unresolved cues with concrete replacement candidates."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("demo_dir", type=Path)
    args = ap.parse_args()
    demo = args.demo_dir.resolve()

    timing = json.loads((demo / "timing.json").read_text())
    script = yaml.safe_load((demo / "script.yaml").read_text())
    beats = script["beats"]
    tw = [w["word"].strip().lower().strip(".,!?;:") for w in timing["words"]]
    tt = [w["start"] for w in timing["words"]]
    resolved = timing.get("bookmarks", {})

    counts: dict[str, int] = {}
    for w in tw:
        counts[w] = counts.get(w, 0) + 1

    # Anchor each beat in the transcript by its longest distinctive word.
    n_beats = len(beats)
    total = len(tw)
    print(f"{demo.name}: {len(resolved)} cues resolved, transcript {total} words, "
          f"{timing['duration']:.1f}s\n")

    any_bad = False
    for bi, b in enumerate(beats):
        bid = b.get("id", "?")
        cues = b.get("bookmarks") or []
        missing = [c for c in cues if str(c).split("#")[0] not in resolved]
        if not missing:
            continue
        any_bad = True
        # crude positional guess: beats are roughly proportional in length
        lo = max(0, int(total * (bi - 0.6) / n_beats))
        hi = min(total, int(total * (bi + 1.6) / n_beats))
        window = tw[lo:hi]
        say_words = words_of(b.get("say"))
        cands = []
        for w in say_words:
            if len(w) < 6 or w in STOP:
                continue
            if counts.get(w, 0) == 1 and w in window:
                cands.append(w)
        seen = set()
        cands = [c for c in cands if not (c in seen or seen.add(c))]
        print(f"── {bid}")
        print(f"   missing: {missing}")
        print(f"   transcript near this beat: ...{' '.join(window[:26])}...")
        print(f"   unique-in-transcript candidates from this beat: {cands[:10] or 'NONE'}")
        print()

    if not any_bad:
        print("All cues resolved. Nothing to repair.")


if __name__ == "__main__":
    main()
