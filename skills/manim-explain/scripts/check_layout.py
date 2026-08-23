#!/usr/bin/env python3
"""Turn the runtime layout report into a verdict.

Reads ``out/layout_violations.json`` (written by ``layout_watch``) and prints the
collisions that lasted long enough for a viewer to see them — including the ones
that only happen mid-motion, which static snapshots and bookmark stills both
miss. Two kinds are reported: text over text, and a box border cutting through
text (an chip rectangle running into the label beside it, an emphasis box
starting mid-word, a caption overflowing its panel).

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

    cuts = [v for v in violations if v.get("kind") == "box-cuts-text"]
    buried = [v for v in violations if v.get("kind") == "box-buries-text"]
    overs = [v for v in violations
             if v.get("kind") not in ("box-cuts-text", "box-buries-text")]
    print(f"{report.get('samples', 0)} samples, {len(violations)} overlap interval(s)"
          f" — {len(overs)} text-over-text, {len(cuts)} box-cuts-text,"
          f" {len(buried)} box-buries-text")
    if not violations:
        print("OK: nothing overlapped for longer than "
              f"{report.get('min_duration', 0)}s.")
        return

    print("\nCOLLISIONS (grab these frames — they are not at bookmarks):")
    for v in violations:
        kind = v.get("kind", "text-over-text")
        rel = {"box-cuts-text": "cuts",
               "box-buries-text": "completely covers"}.get(kind, "↔")
        print(
            f"  {v['start']:7.2f}s–{v['end']:7.2f}s  ({v['duration']:5.2f}s, "
            f"{int(v['max_overlap_frac'] * 100):3d}%, {kind})\n"
            f"      {v['a']!r}\n      {rel} {v['b']!r}"
        )
    print(
        "\nStills for these intervals were captured during the geometry walk:\n"
        f"  python qa_frames.py {args.demo_dir}"
    )
    if args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
