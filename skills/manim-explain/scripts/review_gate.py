#!/usr/bin/env python3
"""Record and enforce the frame-review gate that stands between -ql and -qm.

The mechanical audits (``check_sync``, ``check_layout``) cannot see whether a
frame *means* what the narration says at that moment, and they cannot see a
caption painted black on black, a border filled over the grid it frames, or a
figure that was never disposed. Only someone reading the pixels can. That step
is therefore not optional and not automatable, so this module makes it a hard
gate: ``--check`` fails until a review has actually been recorded for the
current code, and the delivery script refuses to render final quality without
it.

A recorded pass is invalidated by editing the scene afterwards. That is
deliberate — a review describes one specific set of frames, and changing the
code that produced them makes it a statement about a video that no longer
exists.

Usage
-----
    review_gate.py demos/<slug> --check
    review_gate.py demos/<slug> --record pass --frames 34 --notes "..."
    review_gate.py demos/<slug> --record fail --frames 34 --notes "..."
    review_gate.py demos/<slug> --history
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

RECORD_NAME = "review.json"


def scene_files(demo_dir: Path) -> list[Path]:
    """List the scene sources whose content a review is a statement about.

    Args:
        demo_dir: Path to a demo folder (the parent of ``scenes/``).

    Returns:
        Every ``.py`` file under ``scenes/`` and ``utils/``, sorted by name.
        Empty if the demo has no scene sources yet.
    """
    found: list[Path] = []
    for sub in ("scenes", "utils"):
        d = demo_dir / sub
        if d.is_dir():
            found.extend(sorted(d.rglob("*.py")))
    return found


def newest_scene_mtime(demo_dir: Path) -> float:
    """Return the most recent modification time across all scene sources.

    Args:
        demo_dir: Path to a demo folder.

    Returns:
        The maximum mtime as a float epoch, or 0.0 if there are no sources.
    """
    stamps = [f.stat().st_mtime for f in scene_files(demo_dir)]
    return max(stamps) if stamps else 0.0


def contact_sheet(demo_dir: Path) -> Path:
    """Return the expected contact-sheet path for a demo.

    Args:
        demo_dir: Path to a demo folder.

    Returns:
        Path to ``out/qa_frames/contact_sheet.png``, whether or not it exists.
    """
    return demo_dir / "out" / "keyframes" / "contact_sheet.png"


def load(demo_dir: Path) -> list[dict]:
    """Read the review history for a demo.

    Args:
        demo_dir: Path to a demo folder.

    Returns:
        The list of recorded review entries, oldest first. Empty if no review
        has ever been recorded or the record is unreadable.
    """
    path = demo_dir / "out" / RECORD_NAME
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def record(demo_dir: Path, verdict: str, frames: int, notes: str) -> dict:
    """Append one review verdict to a demo's review history.

    Args:
        demo_dir: Path to a demo folder.
        verdict: Either ``"pass"`` or ``"fail"``.
        frames: How many frames were actually read, for accountability.
        notes: What was looked at and what was found. Required for a fail.

    Returns:
        The entry that was appended.

    Raises:
        SystemExit: If the contact sheet is missing, if the scene has been
            edited since the sheet was rendered (so the frames are stale), or
            if a pass is claimed without having read any frames.
    """
    sheet = contact_sheet(demo_dir)
    if not sheet.is_file():
        raise SystemExit(f"no contact sheet at {sheet} — run geometry_pass.py first")

    sheet_mtime = sheet.stat().st_mtime
    scene_mtime = newest_scene_mtime(demo_dir)
    if scene_mtime > sheet_mtime + 1.0:
        raise SystemExit(
            "scene edited after the contact sheet was made — those frames are "
            "stale. Re-run geometry_pass.py, then review again."
        )
    if verdict == "pass" and frames <= 0:
        raise SystemExit("a pass must state how many frames were read (--frames)")
    if verdict == "fail" and not notes.strip():
        raise SystemExit("a fail must say what is wrong (--notes)")

    entry = {
        "stamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "verdict": verdict,
        "frames_read": frames,
        "notes": notes.strip(),
        "scene_mtime": scene_mtime,
        "sheet_mtime": sheet_mtime,
    }
    history = load(demo_dir)
    history.append(entry)
    out = demo_dir / "out"
    out.mkdir(parents=True, exist_ok=True)
    (out / RECORD_NAME).write_text(json.dumps(history, indent=2) + "\n")
    return entry


def check(demo_dir: Path) -> tuple[bool, str]:
    """Decide whether this demo may be rendered at final quality.

    Args:
        demo_dir: Path to a demo folder.

    Returns:
        A ``(ok, reason)`` pair. ``ok`` is True only when the latest recorded
        verdict is a pass covering the current scene sources.
    """
    history = load(demo_dir)
    if not history:
        return False, "no frame review recorded — read the contact sheet first"

    last = history[-1]
    if last.get("verdict") != "pass":
        return False, f"last review failed: {last.get('notes', '')[:160]}"

    scene_mtime = newest_scene_mtime(demo_dir)
    if scene_mtime > float(last.get("scene_mtime", 0.0)) + 1.0:
        return False, "scene edited since the last passing review — re-run geometry_pass.py and review again"

    return True, f"reviewed {last['stamp']}, {last.get('frames_read', 0)} frames read"


def main() -> int:
    """Parse arguments and run the requested gate operation.

    Returns:
        Process exit status: 0 on success or a recorded verdict, 1 when the
        gate is closed.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("demo_dir", type=Path)
    ap.add_argument("--check", action="store_true", help="exit non-zero unless a current pass exists")
    ap.add_argument("--record", choices=("pass", "fail"), help="record a review verdict")
    ap.add_argument("--frames", type=int, default=0, help="how many frames were read")
    ap.add_argument("--notes", default="", help="what was looked at and found")
    ap.add_argument("--history", action="store_true", help="print the review history")
    args = ap.parse_args()

    demo = args.demo_dir
    if not demo.is_dir():
        print(f"no such demo: {demo}", file=sys.stderr)
        return 1

    if args.history:
        for e in load(demo):
            print(f"{e['stamp']}  {e['verdict']:4}  {e.get('frames_read', 0):3} frames  {e.get('notes','')}")
        return 0

    if args.record:
        entry = record(demo, args.record, args.frames, args.notes)
        print(f"recorded {entry['verdict']} for {demo.name} ({entry['frames_read']} frames read)")
        return 0

    ok, reason = check(demo)
    print(("REVIEW OK — " if ok else "REVIEW GATE CLOSED — ") + reason)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
