#!/usr/bin/env python3
"""Wall-clock the geometry inner loop against --dry_run and named stills.

Prints a small table. Not a pytest: run it when changing the renderer so the
numbers stay attached to a real machine, not a CI average.

Usage::

    python profile_geometry.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def _write_scene(demo: Path, body: str) -> Path:
    """Write a tiny scene module that calls ``watch_layout``.

    Args:
        demo: Demo directory.
        body: Lines inside ``construct``, already indented.

    Returns:
        Path to the scene file.
    """
    (demo / "scenes").mkdir(parents=True, exist_ok=True)
    path = demo / "scenes" / "prof.py"
    path.write_text(
        "from pathlib import Path\n"
        "import sys\n"
        f"sys.path.insert(0, {str(SCRIPTS)!r})\n"
        "from manim import *\n"
        "from layout_watch import watch_layout\n"
        f"DEMO_DIR = Path({str(demo)!r})\n"
        "\n"
        "class Prof(Scene):\n"
        "    def construct(self):\n"
        "        watch_layout(self, DEMO_DIR, sample_every=0.1)\n"
        f"{body}"
    )
    return path


def _run(
    scene_path: Path,
    media: Path,
    extra_env: dict[str, str] | None = None,
    extra_args: list[str] | None = None,
) -> tuple[float, int]:
    """Run Manim and return (wall seconds, exit code).

    Args:
        scene_path: Scene module.
        media: Throwaway media dir.
        extra_env: Environment overlay.
        extra_args: Extra CLI flags (e.g. ``--dry_run``).

    Returns:
        Elapsed seconds and the process return code.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SCRIPTS)
    if extra_env:
        env.update(extra_env)
    cmd = [
        sys.executable,
        "-m",
        "manim",
        "--media_dir",
        str(media),
        "-ql",
        "--disable_caching",
        *(extra_args or ["--geometry_only"]),
        str(scene_path),
        "Prof",
    ]
    started = time.perf_counter()
    proc = subprocess.run(cmd, env=env, check=False, capture_output=True, text=True)
    elapsed = time.perf_counter() - started
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr[-1500:] + "\n")
    return elapsed, int(proc.returncode)


def main() -> int:
    """Run the comparisons and print a table.

    Returns:
        0 when every profiled command exited 0.
    """
    rows: list[tuple[str, float, int, str]] = []
    with tempfile.TemporaryDirectory(prefix="geom_prof_") as raw:
        root = Path(raw)

        wait_demo = root / "wait"
        wait_scene = _write_scene(
            wait_demo,
            "        self.add(Text('HOLD', font_size=48))\n"
            "        self.wait(8.0)\n",
        )
        t, rc = _run(wait_scene, root / "m1")
        rows.append(("geometry_only wait(8)", t, rc, "full interpolate"))
        t, rc = _run(
            wait_scene,
            root / "m2",
            extra_env={
                "MANIM_STILL_TIMES": "0.50",
                "MANIM_STILL_ONLY": "1",
                "MANIM_STILL_STOP": "1",
                "MANIM_STILL_DIR": "out/stills",
            },
        )
        pngs = list((wait_demo / "out" / "stills").glob("*.png"))
        rows.append(
            (
                "named still t=0.50 of wait(8)",
                t,
                rc,
                f"{len(pngs)} PNG, abort after hit",
            )
        )
        t, rc = _run(
            wait_scene,
            root / "m3",
            extra_args=["--dry_run"],
        )
        rows.append(("--dry_run wait(8)", t, rc, "Cairo every frame, no mux"))

        fade_demo = root / "fade"
        fade_scene = _write_scene(
            fade_demo,
            "        self.play(FadeIn(Text('MOVE', font_size=48)), run_time=4.0)\n"
            "        self.wait(4.0)\n",
        )
        t, rc = _run(fade_scene, root / "m4")
        rows.append(("geometry_only FadeIn(4)+wait(4)", t, rc, "full interpolate"))
        t, rc = _run(
            fade_scene,
            root / "m5",
            extra_env={
                "MANIM_STILL_TIMES": "0.30",
                "MANIM_STILL_ONLY": "1",
                "MANIM_STILL_STOP": "1",
                "MANIM_STILL_DIR": "out/stills",
            },
        )
        pngs = list((fade_demo / "out" / "stills").glob("*.png"))
        rows.append(
            (
                "named still t=0.30 of FadeIn(4)+wait(4)",
                t,
                rc,
                f"{len(pngs)} PNG, abort mid-play",
            )
        )

        many_demo = root / "many"
        many_lines = [
            "        self.add(Text('MANY', font_size=36))",
        ]
        many_lines.extend(
            f"        self.play(FadeIn(Dot().shift(RIGHT * 0.02 * {i})), run_time=0.12)"
            for i in range(40)
        )
        many_scene = _write_scene(many_demo, "\n".join(many_lines) + "\n")
        t, rc = _run(many_scene, root / "m8")
        rows.append(("geometry_only 40x FadeIn(0.12)", t, rc, "full interpolate"))
        t, rc = _run(
            many_scene,
            root / "m9",
            extra_env={
                "MANIM_STILL_TIMES": "0.20",
                "MANIM_STILL_ONLY": "1",
                "MANIM_STILL_STOP": "1",
                "MANIM_STILL_DIR": "out/stills",
            },
        )
        pngs = list((many_demo / "out" / "stills").glob("*.png"))
        rows.append(
            (
                "named still t=0.20 of 40x FadeIn",
                t,
                rc,
                f"{len(pngs)} PNG, abort after play 1",
            )
        )

        cairo_demo = root / "cairo"
        cairo_scene = _write_scene(
            cairo_demo,
            "        self.add(Text('STILL', font_size=48))\n"
            "        self.wait(1.0)\n",
        )
        t0, rc0 = _run(
            cairo_scene,
            root / "m6",
            extra_env={
                "MANIM_STILL_TIMES": "0.10",
                "MANIM_STILL_ONLY": "1",
                "MANIM_STILL_STOP": "0",
                "MANIM_STILL_DIR": "out/stills",
            },
        )
        times = ",".join(f"{0.05 * (i + 1):.2f}" for i in range(16))
        t16, rc16 = _run(
            cairo_scene,
            root / "m7",
            extra_env={
                "MANIM_STILL_TIMES": times,
                "MANIM_STILL_ONLY": "1",
                "MANIM_STILL_STOP": "0",
                "MANIM_STILL_DIR": "out/stills",
            },
        )
        n16 = len(list((cairo_demo / "out" / "stills").glob("*.png")))
        rows.append(("1 still on wait(1), no abort", t0, rc0, "Cairo once"))
        rows.append(
            (
                "16 stills on wait(1), no abort",
                t16,
                rc16,
                f"{n16} PNGs; delta vs 1 still = {t16 - t0:.3f}s",
            )
        )

    print(f"{'case':<44} {'sec':>8}  {'rc':>3}  note")
    print("-" * 90)
    failed = 0
    for name, elapsed, rc, note in rows:
        print(f"{name:<44} {elapsed:8.3f}  {rc:3d}  {note}")
        if rc != 0:
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
