#!/usr/bin/env python3
"""Repair cues that did not survive transcription, without re-paying for STT.

Cues are matched forward-only, so the *earliest* failure is usually the only
real one: when a cue is missing the matcher hunts ahead for the next cue, binds
it to a later occurrence, and every cue after that fails as collateral. Fixing
the earliest failure and re-mapping therefore tends to recover a whole tail of
cues at once.

This tool loops: find the earliest unresolved cue, replace it in ``script.yaml``
with a word from the same beat that Whisper actually wrote and that occurs
exactly once in the transcript, re-map (free — no STT call), and repeat until
every cue resolves or no candidate remains.

Usage:
    python cue_repair.py demos/<slug> [--max-rounds 40] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

STOP = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "is",
    "it", "that", "this", "for", "with", "as", "by", "from", "you", "we", "so",
    "not", "are", "be", "has", "have", "had", "was", "were", "its", "into",
    "than", "then", "them", "they", "each", "every", "which", "what", "when",
    "where", "how", "why", "can", "will", "would", "there", "their", "about",
    "because", "while", "still", "only", "just", "does", "your", "over",
}


def words_of(text: str) -> list[str]:
    """Lowercase word tokens of a string.

    Args:
        text: Any prose.

    Returns:
        Lowercased word tokens.
    """
    return re.findall(r"[A-Za-z']+", (text or "").lower())


def remap(demo: Path) -> dict:
    """Re-map cues against the stored transcript and return the new timing.

    Args:
        demo: The demo directory.

    Returns:
        Parsed ``timing.json`` after remapping.
    """
    root = Path(__file__).resolve().parent
    subprocess.run([sys.executable, str(root / "align_words.py"), str(demo), "--remap"],
                   capture_output=True, text=True)
    return json.loads((demo / "timing.json").read_text())


def main() -> None:
    """Iteratively re-cue unresolved bookmarks, keeping only changes that help."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("demo_dir", type=Path)
    ap.add_argument("--max-rounds", type=int, default=60)
    args = ap.parse_args()
    demo = args.demo_dir.resolve()
    spath = demo / "script.yaml"

    tried: dict[str, set[str]] = {}
    changes: list[tuple[str, str, str]] = []

    for _ in range(args.max_rounds):
        timing = remap(demo)
        resolved = set(timing.get("bookmarks", {}))
        base = len(resolved)
        script = yaml.safe_load(spath.read_text())
        beats = script["beats"]

        tw = [w["word"].strip().lower().strip(".,!?;:") for w in timing["words"]]
        counts: dict[str, int] = {}
        for w in tw:
            counts[w] = counts.get(w, 0) + 1
        tset = set(tw)

        target = None
        for bi, b in enumerate(beats):
            for c in (b.get("bookmarks") or []):
                if str(c).split("#")[0] not in resolved:
                    target = (bi, str(c), b)
                    break
            if target:
                break
        if target is None:
            print(f"OK: every cue resolves ({base} cues)")
            break

        bi, bad, beat = target
        bid = beat.get("id", "?")
        say_words = words_of(beat.get("say"))
        try:
            pos = say_words.index(bad.lower())
        except ValueError:
            pos = len(say_words) // 2
        used = {str(x).split("#")[0].lower()
                for bb in beats for x in (bb.get("bookmarks") or [])}
        blocked = used | tried.get(bid, set())
        # Prefer a word that occurs exactly once in the transcript — it can only
        # bind where it belongs. Fall back to repeated words rather than giving
        # up, since the acceptance test below verifies the cue actually resolved
        # and a long technical narration repeats most of its vocabulary.
        cands = sorted(
            (counts.get(w, 0) > 1, abs(i - pos), w)
            for i, w in enumerate(say_words)
            if len(w) >= 5 and w not in STOP and w not in blocked and w in tset
        )
        seen: set[str] = set()
        ordered = [w for _, _, w in cands if not (w in seen or seen.add(w))]
        if not ordered:
            print(f"STUCK: {bid!r} cue {bad!r} — no unresolved-safe replacement left; "
                  "rewrite that beat by hand.")
            break

        before = spath.read_text()
        progressed = False
        for new in ordered:
            pat = re.compile(rf"(bookmarks:\s*\[[^\]]*?)\b{re.escape(bad)}\b")
            text2, n = pat.subn(rf"\g<1>{new}", before, count=1)
            if n != 1:
                continue
            spath.write_text(text2)
            after = remap(demo)
            got = len(after.get("bookmarks", {}))
            tried.setdefault(bid, set()).add(new)
            # Local test, not global: in a cascade the total cannot rise until
            # every cue in the broken tail is fixed, so accept any change that
            # makes *this* cue resolve and move on to the next one.
            if new in after.get("bookmarks", {}):
                print(f"  {bid:24s} {bad!r} -> {new!r}   (resolved; total {got})")
                changes.append((bid, bad, new))
                progressed = True
                break
            spath.write_text(before)
        if not progressed:
            tried.setdefault(bid, set()).add(bad)
            print(f"STUCK: {bid!r} cue {bad!r} — no candidate improved the count; "
                  "rewrite that beat by hand.")
            break

    if changes:
        print(f"\n{len(changes)} cue(s) re-cued in {demo.name}:")
        for bid, old_c, new_c in changes:
            print(f"  {bid}: {old_c} -> {new_c}")


if __name__ == "__main__":
    main()
