#!/usr/bin/env python3
"""Extract QA stills from a rendered explainer MP4 for visual inspection.

Craft: after render, the agent must look at real pixels — not only AABB tests.
Best signal: full-resolution frames *just after* a motion lands (bookmark time
+ a short settle), plus a contact sheet overview.

Bookmark stills are not enough on their own: a caption can be clear when a cue
fires and collide with something two seconds later, while a shape is still
growing. ``--from-timeline`` samples the moments that actually matter — the end
of every animation (where motion is at its extreme) and the midpoint of every
recorded text collision — using ``out/timeline.json`` and
``out/layout_violations.json``.

Usage:
  python qa_frames.py demos/<slug> [--video PATH] [--out DIR]
  python qa_frames.py demos/<slug> --bookmarks classifies,dogs,Pick,responding
  python qa_frames.py demos/<slug> --contact-sheet
  python qa_frames.py demos/<slug> --from-timeline        # motion ends + collisions
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


def timeline_moments(demo: Path, *, max_motion_frames: int = 60) -> list[tuple[str, float]]:
    """Moments worth a still, taken from the render's own record.

    Two sources, both invisible to a bookmark-driven sweep:
      * the end of each animation — where a growing shape is at its largest and
        a moving label has just landed;
      * the midpoint of each recorded text collision.

    Args:
        demo: Demo directory.
        max_motion_frames: Cap on motion-end samples, spread evenly across the
            video so a long render does not produce hundreds of stills.

    Returns:
        ``(label, time)`` pairs, sorted by time.
    """
    moments: list[tuple[str, float]] = []

    violations_path = demo / "out" / "layout_violations.json"
    if violations_path.is_file():
        report = json.loads(violations_path.read_text())
        for i, v in enumerate(report.get("violations", [])):
            moments.append((f"collision{i:02d}", float(v["midpoint"])))

    timeline_path = demo / "out" / "timeline.json"
    if timeline_path.is_file():
        timeline = json.loads(timeline_path.read_text())
        plays = sorted(timeline.get("plays") or [], key=lambda p: p["start"])
        ends = [
            float(p["end"])
            for p in plays
            if p.get("kind", "anim") != "wait" and p["end"] - p["start"] > 0.2
        ]
        if len(ends) > max_motion_frames:
            stride = len(ends) / max_motion_frames
            ends = [ends[int(i * stride)] for i in range(max_motion_frames)]
        for i, t in enumerate(ends):
            moments.append((f"motion{i:02d}", t))

    return sorted(moments, key=lambda m: m[1])


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
    parser.add_argument(
        "--from-timeline",
        action="store_true",
        help="Sample motion ends and recorded text collisions instead of bookmarks",
    )
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

    if args.from_timeline:
        moments = timeline_moments(demo)
        if not moments:
            raise SystemExit(
                "No timeline found. Render once with TimedNarration + watch_layout "
                "so out/timeline.json and out/layout_violations.json exist."
            )
        saved: list[Path] = []
        manifest: list[dict] = []
        for label, t in moments:
            t = min(max(t, 0.0), max(0.0, dur - 0.05))
            path = out_dir / f"{len(saved):03d}_{label}_{t:.2f}s.png"
            grab_frame(video, t, path)
            saved.append(path)
            manifest.append({"moment": label, "t": t, "path": str(path.relative_to(demo))})
            print(f"  {label} @ {t:.2f}s -> {path.name}")
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        if args.contact_sheet and saved:
            sheet = out_dir / "contact_sheet.png"
            contact_sheet(saved, sheet)
            print(f"Contact sheet -> {sheet}")
        print(f"Wrote {len(saved)} frames to {out_dir}")
        return

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
