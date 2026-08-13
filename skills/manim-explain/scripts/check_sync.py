#!/usr/bin/env python3
"""Find cues the narration spoke and the picture ignored.

Reads ``out/timeline.json`` (written by ``TimedNarration.wait_until_end``) plus
``script.yaml``, and reports every cue window in which no animation ran. A cue
marks a visual event by definition, so a silent window means the VO named an
object, an action or a change while the frame sat still.

Also reports the reverse-lit failures worth knowing about:
  * windows whose only motion is shorter than ``--min-motion`` (a token pulse
    standing in for a described change);
  * long gaps between animations anywhere in the video.

Usage::

    python check_sync.py demos/<slug> [--min-motion 0.25] [--max-gap 6] [--strict]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


def load_beats(demo_dir: Path) -> dict[str, str]:
    """Map each cue word to the beat id that owns it.

    Args:
        demo_dir: Demo directory containing ``script.yaml``.

    Returns:
        Cue word → beat id. Empty when the script is missing.
    """
    script_path = demo_dir / "script.yaml"
    if not script_path.is_file():
        return {}
    script = yaml.safe_load(script_path.read_text()) or {}
    owner: dict[str, str] = {}
    for beat in script.get("beats") or []:
        for cue in beat.get("bookmarks") or []:
            owner.setdefault(str(cue), str(beat.get("id", "?")))
    return owner


def motion_in_window(plays: list[dict], start: float, end: float) -> list[dict]:
    """Animations overlapping a time window.

    Args:
        plays: Recorded animations with ``start`` / ``end``.
        start: Window start in seconds.
        end: Window end in seconds.

    Returns:
        The real animations intersecting the window. Waits are excluded — a
        ``Scene.wait`` is recorded as a play by Manim but is the absence of
        motion, which is precisely what this check looks for.
    """
    return [
        p
        for p in plays
        if p.get("kind", "anim") != "wait" and p["end"] > start and p["start"] < end
    ]


def analyse(timeline: dict, owner: dict[str, str], *, min_motion: float, max_gap: float) -> dict:
    """Compare cue windows against recorded motion.

    Args:
        timeline: Parsed ``timeline.json``.
        owner: Cue word → beat id.
        min_motion: Total animation seconds below which a window counts as thin.
        max_gap: Longest acceptable stretch with no animation at all.

    Returns:
        A dict with ``silent``, ``thin`` and ``gaps`` lists.
    """
    cues = sorted(timeline.get("cues") or [], key=lambda c: c["t"])
    plays = sorted(
        [p for p in (timeline.get("plays") or []) if p.get("kind", "anim") != "wait"],
        key=lambda p: p["start"],
    )
    duration = float(timeline.get("duration") or 0.0)

    silent, thin = [], []
    for i, cue in enumerate(cues):
        start = float(cue["t"]) - 0.25
        end = float(cues[i + 1]["t"]) if i + 1 < len(cues) else duration
        end = max(end, start + 0.3)
        overlapping = motion_in_window(plays, start, end)
        moving = sum(min(p["end"], end) - max(p["start"], start) for p in overlapping)
        entry = {
            "cue": cue["cue"],
            "beat": owner.get(cue["cue"], "?"),
            "t": round(float(cue["t"]), 2),
            "window": round(end - start, 2),
            "motion": round(max(moving, 0.0), 2),
        }
        if not overlapping or moving <= 1e-3:
            silent.append(entry)
        elif moving < min_motion:
            thin.append(entry)

    gaps = []
    cursor = 0.0
    for play in plays:
        if play["start"] - cursor > max_gap:
            gaps.append({"from": round(cursor, 2), "to": round(play["start"], 2),
                         "length": round(play["start"] - cursor, 2)})
        cursor = max(cursor, float(play["end"]))
    if duration - cursor > max_gap:
        gaps.append({"from": round(cursor, 2), "to": round(duration, 2),
                     "length": round(duration - cursor, 2)})

    return {"silent": silent, "thin": thin, "gaps": gaps,
            "n_cues": len(cues), "n_plays": len(plays)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo_dir", type=Path)
    parser.add_argument("--min-motion", type=float, default=0.25,
                        help="Animation seconds below which a cue window is 'thin'")
    parser.add_argument("--max-gap", type=float, default=6.0,
                        help="Longest stretch with no animation before it is reported")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when anything is silent")
    args = parser.parse_args()

    demo = args.demo_dir.resolve()
    timeline_path = demo / "out" / "timeline.json"
    if not timeline_path.is_file():
        raise SystemExit(
            f"No {timeline_path}. Render once with TimedNarration.wait_until_end() "
            "so the timeline is written."
        )
    timeline = json.loads(timeline_path.read_text())
    report = analyse(timeline, load_beats(demo), min_motion=args.min_motion, max_gap=args.max_gap)

    print(f"{report['n_cues']} cues, {report['n_plays']} animations")
    if report["silent"]:
        print(f"\nSILENT CUES — narration moved, picture did not ({len(report['silent'])}):")
        for e in report["silent"]:
            print(f"  {e['t']:7.2f}s  {e['beat']:<20s} cue {e['cue']!r}: no animation in {e['window']}s")
    if report["thin"]:
        print(f"\nTHIN CUES — under {args.min_motion}s of motion ({len(report['thin'])}):")
        for e in report["thin"]:
            print(f"  {e['t']:7.2f}s  {e['beat']:<20s} cue {e['cue']!r}: {e['motion']}s moving")
    if report["gaps"]:
        print(f"\nSTILL STRETCHES over {args.max_gap}s ({len(report['gaps'])}):")
        for g in report["gaps"]:
            print(f"  {g['from']:7.2f}s → {g['to']:7.2f}s  ({g['length']}s frozen)")
    if not (report["silent"] or report["thin"] or report["gaps"]):
        print("\nOK: every cue window contains motion.")

    (demo / "out" / "sync_report.json").write_text(json.dumps(report, indent=2) + "\n")
    if args.strict and report["silent"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
