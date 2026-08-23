#!/usr/bin/env python3
"""Walk ``construct()`` without encoding a movie.

This is the inner video loop. It interpolates every play so occupancy sampling
sees motion, Cairo-rasterizes only the sparse stills requested by the capture
helper, then writes:

* ``out/timeline.json`` — cue and play times (TimedNarration)
* ``out/layout_violations.json`` — overlap intervals (layout_watch)
* ``out/occupancy.json`` — AABB samples + leftover checklist
* ``out/keyframes/*.png`` — cue / play-end / overlap stills
* ``out/keyframes/contact_sheet.png``
* ``out/wireframe.png`` — labelled boxes from occupancy, no Cairo

The Manim ``--media_dir`` for this pass is a throwaway directory. Geometry-only
mode still creates a writer object; that tree is deleted in ``finally`` so a
crash cannot leave a half-written movie next to the stills.

Usage::

    python geometry_pass.py demos/<slug> scenes/<file>.py <SceneClass>
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from occupancy import leftover_records, motion_events
from qa_frames import compose_contact_sheet, list_keyframes, select_sheet_frames
from skill_paths import scripts_dir
from wireframe import write_wireframe_sheet


def _resolve_scene(demo: Path, scene_file: Path) -> Path:
    """Resolve a scene path that may be relative to the demo or the cwd.

    Args:
        demo: Demo directory.
        scene_file: Path as passed on the command line.

    Returns:
        Absolute path to the scene file.

    Raises:
        SystemExit: If neither interpretation exists.
    """
    if scene_file.is_file():
        return scene_file.resolve()
    candidate = demo / scene_file
    if candidate.is_file():
        return candidate.resolve()
    candidate = demo / "scenes" / scene_file.name
    if candidate.is_file():
        return candidate.resolve()
    raise SystemExit(f"No scene file at {scene_file} or {demo / scene_file}")


def run_geometry(
    demo: Path,
    scene_file: Path,
    scene_class: str,
    *,
    extra_env: dict[str, str] | None = None,
    quality: str = "-ql",
) -> int:
    """Invoke Manim in geometry-only mode against a throwaway media dir.

    Args:
        demo: Demo directory. ``out/`` is written here by the scene helpers.
        scene_file: Absolute path to the scene module.
        scene_class: Scene class name.
        extra_env: Optional environment overlays (``PYTHONPATH`` is always
            extended with the skill scripts and the demo).
        quality: Manim quality flag. Occupancy walks use ``-ql`` (the AABB
            is in scene units, so pixel size does not matter). Named stills
            use ``-qm`` so the PNGs are 720p.

    Returns:
        The Manim process exit status.
    """
    skill_scripts = scripts_dir()
    pythonpath = os.pathsep.join(
        [
            str(skill_scripts),
            str(demo),
            os.environ.get("PYTHONPATH", ""),
        ]
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = pythonpath
    env.setdefault("MANIM_EXPLAIN_ROOT", str(skill_scripts.parent))
    if extra_env:
        env.update(extra_env)

    media = Path(tempfile.mkdtemp(prefix=f"geom_{demo.name}_"))
    cmd = [
        sys.executable,
        "-m",
        "manim",
        "--media_dir",
        str(media),
        "--geometry_only",
        quality,
        "--disable_caching",
        str(scene_file),
        scene_class,
    ]
    try:
        print(" ".join(cmd), flush=True)
        proc = subprocess.run(cmd, env=env, check=False)
        return int(proc.returncode)
    finally:
        shutil.rmtree(media, ignore_errors=True)


def write_sidecar_pictures(demo: Path) -> None:
    """Build the wireframe sheet and the keyframe contact sheet.

    Args:
        demo: Demo directory whose ``out/`` the geometry walk just wrote.
    """
    occ = demo / "out" / "occupancy.json"
    if occ.is_file():
        payload = json.loads(occ.read_text())
        leftovers = payload.get("leftovers") or leftover_records(
            payload.get("samples") or [],
            float(payload.get("duration") or 0.0),
        )
        movers = payload.get("motion")
        if movers is None:
            movers = motion_events(payload.get("samples") or [])
        print(
            f"occupancy: {payload.get('n_samples', len(payload.get('samples') or []))} "
            f"samples, {len(leftovers)} leftover candidate(s), "
            f"{len(movers)} motion event(s)"
        )
        for row in leftovers[:12]:
            print(
                f"  leftover {row['first']:7.2f}s–{row['last']:7.2f}s  "
                f"({row['duration']:.1f}s)  {row['kind']} {row['label']!r}"
            )
        if len(leftovers) > 12:
            print(f"  … {len(leftovers) - 12} more in {occ}")
        for row in movers[:8]:
            print(
                f"  moved {row['t0']:7.2f}s–{row['t1']:7.2f}s  "
                f"shift {row['shift']:.2f}  {row['label']!r}"
            )
        if len(movers) > 8:
            print(f"  … {len(movers) - 8} more motion events in {occ}")
        crossed = payload.get("boundary_leftovers") or []
        if crossed:
            print(f"  {len(crossed)} rode across a section fade:")
            for row in crossed[:8]:
                print(
                    f"    boundary {row.get('boundary', 0):7.2f}s  "
                    f"{row['kind']} {row['label']!r}"
                )
        sheet = write_wireframe_sheet(occ, demo / "out" / "wireframe.png")
        if sheet is not None:
            print(f"wireframe -> {sheet}")

    frames_dir = demo / "out" / "keyframes"
    frames = list_keyframes(frames_dir)
    if frames:
        dest = frames_dir / "contact_sheet.png"
        sheet_frames = select_sheet_frames(frames)
        compose_contact_sheet(sheet_frames, dest)
        print(
            f"contact sheet -> {dest}  "
            f"({len(sheet_frames)} of {len(frames)} stills)"
        )
    else:
        print(f"no keyframe PNGs in {frames_dir}")
    snaps = demo / "out" / "snapshots"
    if snaps.is_dir():
        n = len(list(snaps.glob("*.pkl")))
        if n:
            print(f"snapshots -> {snaps}  ({n} dumps, render_stills uses these)")


def main() -> int:
    """Parse arguments, walk the scene, write sidecar pictures.

    Returns:
        Process exit status: Manim's status, or 1 if the walk wrote no
        occupancy report (the scene probably never called ``watch_layout``).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo_dir", type=Path)
    parser.add_argument("scene_file", type=Path)
    parser.add_argument("scene_class")
    args = parser.parse_args()

    demo = args.demo_dir.resolve()
    if not demo.is_dir():
        print(f"no such demo: {demo}", file=sys.stderr)
        return 1
    scene_file = _resolve_scene(demo, args.scene_file)

    rc = run_geometry(demo, scene_file, args.scene_class)
    if rc != 0:
        return rc
    write_sidecar_pictures(demo)
    occ = demo / "out" / "occupancy.json"
    if not occ.is_file():
        print(
            f"no {occ} — the scene must call watch_layout(self, DEMO_DIR)",
            file=sys.stderr,
        )
        return 1
    for script in ("check_sync.py", "check_layout.py"):
        cmd = [sys.executable, str(scripts_dir() / script), str(demo)]
        if script == "check_layout.py":
            cmd.extend(["--min-duration", "1.0"])
        print(" ".join(cmd), flush=True)
        subprocess.run(cmd, check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
