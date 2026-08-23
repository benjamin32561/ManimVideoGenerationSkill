#!/usr/bin/env python3
"""Map occupancy / layout hits to Manim ``-n`` play windows.

A geometry pass cannot seek to t=337 s. After it names an overlap, a *repair*
encode of just those plays is ``manim -n START,END`` — not a logic gate (``-n
0,1`` still exits 0 after animation 1 and must not be used that way).

Play indices are taken from ``out/timeline.json``. Manim counts every
``scene.play``, including waits, so this uses the full play list, not only
``kind=anim``.

Usage::

    python play_window.py demos/<slug>
    python play_window.py demos/<slug> --t 114.7 178.8
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


def load_plays(demo: Path) -> list[dict[str, Any]]:
    """Read the ordered play list written by TimedNarration.

    Args:
        demo: Demo directory holding ``out/timeline.json``.

    Returns:
        Play records, empty if the timeline is missing.
    """
    path = demo / "out" / "timeline.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text())
    return list(data.get("plays") or [])


def window_for_interval(
    plays: Sequence[Mapping[str, Any]],
    t0: float,
    t1: float,
    *,
    pad: int = 1,
) -> tuple[int, int] | None:
    """Inclusive play-index window covering ``[t0, t1]``.

    Args:
        plays: Timeline plays, index = Manim ``num_plays`` order.
        t0: Interval start, seconds.
        t1: Interval end, seconds.
        pad: Extra plays on each side so a morph that *causes* the overlap is
            included.

    Returns:
        ``(from, upto)`` suitable for ``manim -n from,upto``, or ``None`` when
        no play overlaps the interval.
    """
    hits = [
        i
        for i, play in enumerate(plays)
        if float(play.get("end") or 0.0) >= t0
        and float(play.get("start") or 0.0) <= t1
    ]
    if not hits:
        return None
    start = max(0, min(hits) - pad)
    end = min(len(plays) - 1, max(hits) + pad)
    return start, end


def windows_from_violations(
    demo: Path,
    *,
    min_duration: float = 1.0,
    kinds: Sequence[str] | None = None,
) -> list[dict[str, Any]]:
    """One ``-n`` window per long layout violation.

    Args:
        demo: Demo directory.
        min_duration: Ignore shorter overlaps (morph crossings).
        kinds: Restriction, e.g. ``("text-over-text",)``. ``None`` means all.

    Returns:
        Dicts with ``start``, ``end``, ``kind``, ``from``, ``upto``.
    """
    plays = load_plays(demo)
    path = demo / "out" / "layout_violations.json"
    if not path.is_file() or not plays:
        return []
    report = json.loads(path.read_text())
    want = set(kinds) if kinds else None
    out: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for viol in report.get("violations") or []:
        if float(viol.get("duration") or 0.0) < min_duration:
            continue
        kind = str(viol.get("kind") or "text-over-text")
        if want is not None and kind not in want:
            continue
        span = window_for_interval(
            plays, float(viol["start"]), float(viol["end"])
        )
        if span is None or span in seen:
            continue
        seen.add(span)
        out.append(
            {
                "kind": kind,
                "t0": viol["start"],
                "t1": viol["end"],
                "from": span[0],
                "upto": span[1],
            }
        )
    return out


def main() -> int:
    """Print suggested ``-n`` windows and exit 0."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo_dir", type=Path)
    parser.add_argument("--t", nargs=2, type=float, metavar=("T0", "T1"))
    parser.add_argument("--min-duration", type=float, default=1.0)
    args = parser.parse_args()
    demo = args.demo_dir.resolve()
    plays = load_plays(demo)
    if not plays:
        print(f"no timeline at {demo / 'out' / 'timeline.json'}", file=sys.stderr)
        return 1
    if args.t:
        span = window_for_interval(plays, args.t[0], args.t[1])
        if span is None:
            print("no play covers that interval")
            return 1
        print(f"-n {span[0]},{span[1]}  ({args.t[0]:.2f}s–{args.t[1]:.2f}s)")
        return 0
    rows = windows_from_violations(demo, min_duration=args.min_duration)
    if not rows:
        print("no long violations to window")
        return 0
    for row in rows:
        print(
            f"-n {row['from']},{row['upto']}  "
            f"{row['t0']:.2f}s–{row['t1']:.2f}s  {row['kind']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
