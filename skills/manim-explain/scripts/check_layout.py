#!/usr/bin/env python3
"""Turn the runtime layout report into a verdict.

Reads ``out/layout_violations.json`` (written by ``layout_watch``) and prints the
text-vs-text collisions that lasted long enough for a viewer to see them —
including the ones that only happen mid-motion, which static snapshots and
bookmark stills both miss.

Usage::

    python check_layout.py demos/<slug> [--min-duration 0.5] [--strict]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo_dir", type=Path)
    parser.add_argument("--min-duration", type=float, default=0.0,
                        help="Ignore overlaps shorter than this (seconds)")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any overlap survives")
    args = parser.parse_args()

    demo = args.demo_dir.resolve()
    path = demo / "out" / "layout_violations.json"
    if not path.is_file():
        raise SystemExit(
            f"No {path}. Call watch_layout(self, DEMO_DIR) in the scene and render once."
        )
    report = json.loads(path.read_text())
    violations = [v for v in report.get("violations", []) if v["duration"] >= args.min_duration]

    print(f"{report.get('samples', 0)} samples, {len(violations)} overlap interval(s)")
    if not violations:
        print("OK: no text overlapped text for longer than "
              f"{report.get('min_duration', 0)}s.")
        return

    print("\nTEXT COLLISIONS (grab these frames — they are not at bookmarks):")
    for v in violations:
        print(
            f"  {v['start']:7.2f}s–{v['end']:7.2f}s  ({v['duration']:5.2f}s, "
            f"{int(v['max_overlap_frac'] * 100):3d}% of the smaller box)\n"
            f"      {v['a']!r}\n      ↔ {v['b']!r}"
        )
    print(
        "\nExtract them with:\n"
        f"  python qa_frames.py {args.demo_dir} --from-timeline"
    )
    if args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
