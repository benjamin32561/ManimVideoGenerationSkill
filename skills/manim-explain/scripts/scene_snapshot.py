"""Compact mobject snapshots so a later still does not re-run ``construct``.

A geometry walk already interpolates every play. The expensive part of a
second named-time still is executing ``construct`` again — creating Text /
MathTex, ``Transform.begin`` copies — not Cairo. These snapshots store the
drawable point arrays and colours at ~2 Hz plus overlap/section instants.
``render_stills`` rebuilds VMobjects from the nearest dump and Cairo-rasterizes
once. No movie, no ``construct``, no TeX.

The format is pickle of numpy arrays, not a pickled ``Scene``: cairo surfaces
and updaters do not round-trip, and we only need pixels.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

SNAPSHOT_DIR = Path("out") / "snapshots"
DEFAULT_EVERY = 0.5
DEFAULT_MAX_DT = 0.35
_MIN_OPACITY = 0.06


def snapshot_dir(demo: Path) -> Path:
    """Return the snapshot directory for a demo.

    Args:
        demo: Demo directory.

    Returns:
        ``<demo>/out/snapshots``.
    """
    return Path(demo) / SNAPSHOT_DIR


def clear_snapshots(demo: Path) -> None:
    """Delete previous snapshots so a re-walk cannot restore stale geometry.

    Args:
        demo: Demo directory.
    """
    import shutil

    dest = snapshot_dir(demo)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)


def pack_scene(scene: Any) -> list[dict[str, Any]]:
    """Capture drawable families as point arrays and colours.

    Args:
        scene: A live Manim scene. Updater tickers with no points are skipped.
            Mobjects whose fill and stroke opacity are both below
            :data:`_MIN_OPACITY` are skipped (hidden hex labels).

    Returns:
        Records in draw order, each with ``points``, ``fill``, ``stroke``,
        ``width``, and ``z``.
    """
    records: list[dict[str, Any]] = []
    for top in list(getattr(scene, "mobjects", [])):
        try:
            family = top.get_family()
        except Exception:  # noqa: BLE001
            family = [top]
        for mob in family:
            points = getattr(mob, "points", None)
            if points is None:
                continue
            arr = np.asarray(points, dtype=np.float32)
            if arr.ndim != 2 or arr.shape[0] < 2:
                continue
            fill = getattr(mob, "fill_rgbas", None)
            stroke = getattr(mob, "stroke_rgbas", None)
            fill_a = float(np.max(fill[:, 3])) if fill is not None and len(fill) else 0.0
            stroke_a = (
                float(np.max(stroke[:, 3])) if stroke is not None and len(stroke) else 0.0
            )
            if fill_a < _MIN_OPACITY and stroke_a < _MIN_OPACITY:
                continue
            width = getattr(mob, "stroke_width", None)
            if callable(getattr(mob, "get_stroke_width", None)):
                try:
                    width = float(mob.get_stroke_width())
                except Exception:  # noqa: BLE001
                    width = 0.0
            records.append(
                {
                    "points": arr,
                    "fill": None
                    if fill is None
                    else np.asarray(fill, dtype=np.float32),
                    "stroke": None
                    if stroke is None
                    else np.asarray(stroke, dtype=np.float32),
                    "width": float(width or 0.0),
                    "z": int(getattr(mob, "z_index", 0) or 0),
                }
            )
    return records


def save_snapshot(demo: Path, t: float, records: Sequence[dict[str, Any]]) -> Path:
    """Write one snapshot pickle named by scene time.

    Args:
        demo: Demo directory.
        t: Scene time in seconds.
        records: Output of :func:`pack_scene`.

    Returns:
        Path to the written pickle.
    """
    dest = snapshot_dir(demo)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"{t:.2f}.pkl"
    path.write_bytes(pickle.dumps({"t": float(t), "mobs": list(records)}, protocol=4))
    return path


def list_snapshot_times(demo: Path) -> list[float]:
    """Times for which a snapshot file exists.

    Args:
        demo: Demo directory.

    Returns:
        Sorted scene times in seconds.
    """
    dest = snapshot_dir(demo)
    if not dest.is_dir():
        return []
    times: list[float] = []
    for path in dest.glob("*.pkl"):
        try:
            times.append(float(path.stem))
        except ValueError:
            continue
    return sorted(times)


def nearest_snapshot(demo: Path, t: float, *, max_dt: float = DEFAULT_MAX_DT) -> Path | None:
    """Pick the snapshot closest to ``t`` if it is close enough.

    Args:
        demo: Demo directory.
        t: Requested scene time.
        max_dt: Maximum |snapshot − t| in seconds.

    Returns:
        The pickle path, or ``None`` when nothing is close enough.
    """
    times = list_snapshot_times(demo)
    if not times:
        return None
    best = min(times, key=lambda s: abs(s - t))
    if abs(best - t) > max_dt:
        return None
    return snapshot_dir(demo) / f"{best:.2f}.pkl"


def load_snapshot(path: Path) -> dict[str, Any]:
    """Read a snapshot pickle.

    Args:
        path: File written by :func:`save_snapshot`.

    Returns:
        Dict with ``t`` and ``mobs``.
    """
    payload = pickle.loads(path.read_bytes())
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a snapshot dict")
    return payload


def _quality_pixels(quality: str) -> tuple[int, int]:
    """Pixel size for a Manim quality letter.

    Args:
        quality: ``ql`` / ``qm`` / ``qh`` / ``qk``.

    Returns:
        ``(width, height)``.
    """
    table = {
        "ql": (854, 480),
        "qm": (1280, 720),
        "qh": (1920, 1080),
        "qk": (3840, 2160),
    }
    return table.get(quality, (1280, 720))


def records_to_mobjects(records: Sequence[Mapping]) -> list:
    """Rebuild VMobjects from snapshot records.

    Args:
        records: ``mobs`` list from a snapshot.

    Returns:
        VMobjects in draw order.
    """
    from manim.mobject.types.vectorized_mobject import VMobject

    mobs = []
    for rec in records:
        vm = VMobject()
        vm.set_points(np.asarray(rec["points"]))
        fill = rec.get("fill")
        if fill is not None:
            vm.fill_rgbas = np.asarray(fill, dtype=float)
        stroke = rec.get("stroke")
        if stroke is not None:
            vm.stroke_rgbas = np.asarray(stroke, dtype=float)
        vm.stroke_width = float(rec.get("width") or 0.0)
        vm.z_index = int(rec.get("z") or 0)
        mobs.append(vm)
    return mobs


def rasterize_snapshot(
    path: Path,
    dest: Path,
    *,
    quality: str = "qm",
) -> Path:
    """Cairo-rasterize one snapshot pickle to a PNG.

    Args:
        path: Snapshot pickle.
        dest: Destination PNG.
        quality: Manim quality letter; sets pixel size.

    Returns:
        ``dest`` after the image is written.
    """
    from manim import Camera, tempconfig

    payload = load_snapshot(path)
    width, height = _quality_pixels(quality)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempconfig(
        {
            "pixel_width": width,
            "pixel_height": height,
            "write_to_movie": False,
            "save_last_frame": False,
            "dry_run": False,
            "geometry_only": False,
        }
    ):
        camera = Camera()
        camera.reset()
        camera.capture_mobjects(records_to_mobjects(payload.get("mobs") or []))
        camera.get_image().save(dest)
    return dest


def rasterize_times(
    demo: Path,
    times: Sequence[float],
    *,
    quality: str = "qm",
    max_dt: float = DEFAULT_MAX_DT,
    out_rel: str = "out/stills",
) -> tuple[list[dict[str, Any]], list[float]]:
    """Rasterize requested times from snapshots when a close dump exists.

    Args:
        demo: Demo directory holding ``out/snapshots/``.
        times: Requested scene times.
        quality: Manim quality letter for PNG size.
        max_dt: Maximum distance to a snapshot.
        out_rel: Directory under the demo for the PNGs.

    Returns:
        ``(written, missing)``. ``written`` is manifest rows; ``missing`` is
        times that had no close snapshot and still need a construct walk.
    """
    out_dir = Path(demo) / out_rel
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[dict[str, Any]] = []
    missing: list[float] = []
    for t in times:
        snap = nearest_snapshot(demo, t, max_dt=max_dt)
        if snap is None:
            missing.append(t)
            continue
        dest = out_dir / f"{len(written):03d}_snap_{t:.2f}s.png"
        rasterize_snapshot(snap, dest, quality=quality)
        payload = load_snapshot(snap)
        written.append(
            {
                "reason": f"snap:{payload.get('t', t):.2f}",
                "t": round(float(t), 3),
                "snap_t": payload.get("t"),
                "path": str(dest.relative_to(demo)),
            }
        )
    return written, missing
