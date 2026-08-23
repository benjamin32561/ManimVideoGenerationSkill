#!/usr/bin/env python3
"""Rasterize named scene times (or plays) without encoding a movie.

This is the QA stills tool. After a geometry pass, compact mobject snapshots
live in ``out/snapshots/``. This script Cairo-rasterizes the nearest dump — no
``construct``, no TeX. If no snapshot is close enough, it falls back to a
stills-only geometry walk that interpolates until those instants and aborts.

It does not rewrite ``occupancy.json``, ``layout_violations.json``,
``timeline.json``, or ``out/keyframes/``.

Usage::

    python render_stills.py demos/<slug> scenes/<file>.py <SceneClass> --t 93.6 367.8
    python render_stills.py demos/<slug> scenes/<file>.py <SceneClass> --play 40
    python render_stills.py demos/<slug> scenes/<file>.py <SceneClass> --from-violations
    python render_stills.py demos/<slug> scenes/<file>.py <SceneClass> --cue product
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from geometry_pass import _resolve_scene, run_geometry
from scene_snapshot import list_snapshot_times, rasterize_times
from still_request import (
    StillRequest,
    times_from_cues,
    times_from_plays,
    times_from_violations,
)


def _load_json(path: Path) -> dict:
    """Read a JSON object or fail with a short message.

    Args:
        path: File that must exist.

    Returns:
        The parsed object.

    Raises:
        SystemExit: If the file is missing or not a JSON object.
    """
    if not path.is_file():
        raise SystemExit(f"missing {path} — run geometry_pass.py first")
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise SystemExit(f"{path} is not a JSON object")
    return data


def build_request(demo: Path, args: argparse.Namespace) -> StillRequest:
    """Resolve CLI selectors into a :class:`StillRequest`.

    Args:
        demo: Demo directory holding ``out/``.
        args: Parsed CLI arguments.

    Returns:
        A request with ``still_only=True``.

    Raises:
        SystemExit: If nothing was selected, or a selector cannot be resolved.
    """
    times: list[float] = list(args.t or [])
    plays: list[int] = list(args.play or [])
    if args.from_violations:
        payload = _load_json(demo / "out" / "layout_violations.json")
        times.extend(
            times_from_violations(payload, min_duration=args.min_duration)
        )
    if args.cue:
        timeline = _load_json(demo / "out" / "timeline.json")
        try:
            times.extend(times_from_cues(timeline, args.cue))
        except KeyError as exc:
            raise SystemExit(str(exc)) from exc
    if plays and args.play_at != "play-end":
        timeline = _load_json(demo / "out" / "timeline.json")
        try:
            times.extend(
                times_from_plays(
                    timeline.get("plays") or [],
                    plays,
                    at=args.play_at,
                )
            )
        except IndexError as exc:
            raise SystemExit(str(exc)) from exc
        plays = []
    times = sorted(set(times))
    plays = sorted(set(plays))
    if not times and not plays:
        raise SystemExit("nothing to rasterize: pass --t, --play, --cue, or --from-violations")
    return StillRequest(
        times=times,
        plays=plays,
        still_only=True,
        stop_after=not args.keep_going,
        out_rel="out/stills",
    )


def main() -> int:
    """Parse arguments, walk until the requested instants, report the PNGs.

    Returns:
        0 when every requested still was written; 1 on a missing still or a
        failed Manim walk.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo_dir", type=Path)
    parser.add_argument("scene_file", type=Path)
    parser.add_argument("scene_class")
    parser.add_argument(
        "--t",
        nargs="+",
        type=float,
        metavar="SEC",
        help="Absolute scene times to rasterize.",
    )
    parser.add_argument(
        "--play",
        nargs="+",
        type=int,
        metavar="N",
        help="Play indices. Default captures at play-end during the walk.",
    )
    parser.add_argument(
        "--play-at",
        choices=("play-end", "start", "mid", "end"),
        default="play-end",
        help="Where in each --play to land. play-end needs no timeline.",
    )
    parser.add_argument(
        "--cue",
        nargs="+",
        metavar="NAME",
        help="Bookmark / cue names from out/timeline.json.",
    )
    parser.add_argument(
        "--from-violations",
        action="store_true",
        help="Rasterize midpoints of long layout violations.",
    )
    parser.add_argument("--min-duration", type=float, default=1.0)
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="Do not abort construct after the last still (for profiling).",
    )
    parser.add_argument(
        "--quality",
        default="qm",
        choices=("ql", "qm", "qh", "qk"),
        help="Manim quality without the dash. Default qm so QA stills are 720p.",
    )
    parser.add_argument(
        "--walk",
        action="store_true",
        help="Ignore snapshots and re-run construct (slow path).",
    )
    parser.add_argument(
        "--max-dt",
        type=float,
        default=0.35,
        help="Use a snapshot if |t - snap| is at most this many seconds.",
    )
    args = parser.parse_args()

    demo = args.demo_dir.resolve()
    if not demo.is_dir():
        print(f"no such demo: {demo}", file=sys.stderr)
        return 1
    scene_file = _resolve_scene(demo, args.scene_file)
    request = build_request(demo, args)
    print(
        f"stills: {len(request.times)} time(s) {request.times[:8]}"
        f"{'…' if len(request.times) > 8 else ''}  "
        f"{len(request.plays)} play(s) {request.plays[:8]}  "
        f"stop_after={request.stop_after}",
        flush=True,
    )
    started = time.perf_counter()
    stills_dir = demo / request.out_rel
    stills_dir.mkdir(parents=True, exist_ok=True)
    written: list = []
    if (
        not args.walk
        and request.times
        and not request.plays
        and list_snapshot_times(demo)
    ):
        written, missing = rasterize_times(
            demo,
            request.times,
            quality=args.quality,
            max_dt=args.max_dt,
            out_rel=request.out_rel,
        )
        print(
            f"snapshots: {len(written)} hit, {len(missing)} miss "
            f"(max_dt={args.max_dt}s)",
            flush=True,
        )
        if not missing:
            elapsed = time.perf_counter() - started
            manifest_path = stills_dir / "manifest.json"
            manifest_path.write_text(
                json.dumps({"stills": written, "missing": {"times": [], "plays": []}}, indent=2)
                + "\n"
            )
            for row in written:
                print(f"  {row.get('t')}s  {row.get('reason')}  {row.get('path')}")
            print(f"ok: {len(written)} PNG(s) from snapshots, {elapsed:.2f}s")
            return 0
        request.times = missing

    extra = request.to_env()
    if written:
        extra["MANIM_STILL_KEEP"] = "1"
    rc = run_geometry(
        demo,
        scene_file,
        args.scene_class,
        extra_env=extra,
        quality=f"-{args.quality}",
    )
    elapsed = time.perf_counter() - started
    stills_dir = demo / request.out_rel
    pngs = sorted(stills_dir.glob("*.png")) if stills_dir.is_dir() else []
    manifest_path = stills_dir / "manifest.json"
    missing: dict = {"times": list(request.times), "plays": list(request.plays)}
    if manifest_path.is_file():
        payload = json.loads(manifest_path.read_text())
        if isinstance(payload, dict):
            missing = payload.get("missing") or missing
            rows = payload.get("stills") or []
        else:
            rows = payload
            missing = {"times": [], "plays": []}
        print(f"manifest: {len(rows)} still(s) in {elapsed:.2f}s -> {stills_dir}")
        for row in rows:
            print(f"  {row.get('t', '?')}s  {row.get('reason')}  {row.get('path')}")
    else:
        print(f"no manifest in {stills_dir} after {elapsed:.2f}s", file=sys.stderr)
    if rc != 0:
        print(f"manim exited {rc}", file=sys.stderr)
        return rc
    missed_t = missing.get("times") or []
    missed_p = missing.get("plays") or []
    if missed_t or missed_p:
        print(
            f"missing stills: times={missed_t} plays={missed_p}",
            file=sys.stderr,
        )
        return 1
    if not pngs:
        print("no PNG stills written", file=sys.stderr)
        return 1
    print(f"ok: {len(pngs)} PNG(s), {elapsed:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
