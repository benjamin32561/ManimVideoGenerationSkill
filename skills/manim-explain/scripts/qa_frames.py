#!/usr/bin/env python3
"""Extract QA stills from a rendered explainer MP4 for visual inspection.

Craft: after render, the agent must look at real pixels — not only AABB tests.
Best signal: full-resolution frames *just after* a motion lands (bookmark time
+ a short settle), plus a contact sheet overview.

Usage:
  python qa_frames.py demos/<slug> [--video PATH] [--out DIR]
  python qa_frames.py demos/<slug> --bookmarks classifies,dogs,Pick,responding
  python qa_frames.py demos/<slug> --contact-sheet
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path


# Prefer every bookmark in timing.json when the caller does not pass --bookmarks.
# Demo-specific hard-coded cue lists miss caption-near-figure beats on new topics.
DEFAULT_CUES: list[str] = []  # empty → use all keys from timing.json



def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def grab_frame(video: Path, t: float, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    # -ss before -i is fast; accurate enough for QA stills
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{max(0.0, t):.3f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(out),
        ],
        check=True,
        capture_output=True,
    )


def contact_sheet(frames: list[Path], out: Path, cols: int = 4) -> None:
    if not frames:
        return
    rows = math.ceil(len(frames) / cols)
    # tile with ffmpeg
    inputs: list[str] = []
    for f in frames:
        inputs.extend(["-i", str(f)])
    # scale each to 320 wide then xstack
    filters = []
    for i in range(len(frames)):
        filters.append(f"[{i}:v]scale=320:-1:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}]")
    layout_parts = []
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            if idx < len(frames):
                layout_parts.append(f"{c * 320}_{r * 180}")
    # pad missing cells with black
    n = rows * cols
    while len(frames) < n:
        # reuse last frame faded — simpler: just fewer in xstack with layout of existing
        break
    used = min(len(frames), n)
    layout = "|".join(f"{(i % cols) * 320}_{(i // cols) * 180}" for i in range(used))
    stack_in = "".join(f"[v{i}]" for i in range(used))
    filters.append(f"{stack_in}xstack=inputs={used}:layout={layout}[out]")
    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        ";".join(filters),
        "-map",
        "[out]",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo_dir", type=Path)
    parser.add_argument("--video", type=Path, default=None)
    parser.add_argument("--timing", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--bookmarks",
        default="",
        help="Comma-separated bookmark names from timing.json (default: all)",
    )
    parser.add_argument(
        "--settle",
        type=float,
        default=1.0,
        help="Seconds after bookmark to capture (after FadeIn/pop lands; avoid mid-tween)",
    )
    parser.add_argument("--contact-sheet", action="store_true")
    args = parser.parse_args()

    demo = args.demo_dir.resolve()
    video = args.video or (demo / "out" / "final.mp4")
    timing_path = args.timing or (demo / "timing.json")
    out_dir = args.out or (demo / "out" / "qa_frames")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not video.is_file():
        raise SystemExit(f"Missing video: {video}")
    timing = json.loads(timing_path.read_text())
    bookmarks = timing.get("bookmarks") or {}
    dur = probe_duration(video)

    names = [n.strip() for n in args.bookmarks.split(",") if n.strip()]
    if not names:
        # Stable order by time
        names = sorted(bookmarks.keys(), key=lambda k: float(bookmarks[k]))
        print(f"  using all {len(names)} bookmarks from timing.json")
    saved: list[Path] = []
    manifest: list[dict] = []
    for name in names:
        if name not in bookmarks:
            print(f"  skip missing bookmark: {name}")
            continue
        t = float(bookmarks[name]) + float(args.settle)
        t = min(t, max(0.0, dur - 0.05))
        path = out_dir / f"{len(saved):02d}_{name}_{t:.2f}s.png"
        grab_frame(video, t, path)
        saved.append(path)
        manifest.append({"bookmark": name, "t": t, "path": str(path.relative_to(demo))})
        print(f"  {name} @ {t:.2f}s -> {path.name}")

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if args.contact_sheet and saved:
        sheet = out_dir / "contact_sheet.png"
        contact_sheet(saved, sheet)
        print(f"Contact sheet -> {sheet}")
    print(f"Wrote {len(saved)} frames to {out_dir}")


if __name__ == "__main__":
    main()
