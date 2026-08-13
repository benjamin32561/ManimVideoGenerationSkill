"""Continuously watch a rendering scene for text that collides with text.

Static snapshots only certify the frames an author thought to write down. Real
collisions happen *during* motion: while something grows, slides, or sits at its
maximum size. This module samples the live scene several times a second, records
every text-vs-text overlap that lasts long enough to be seen, and writes the
intervals out so `qa_frames.py` can grab exactly those moments.

Usage inside a scene::

    from layout_watch import watch_layout

    watch_layout(self, DEMO_DIR)          # right after tn.attach(self)
    ...
    tn.wait_until_end()                    # report is flushed automatically

Nothing here raises: a collision mid-render should not destroy a long render.
The report is the deliverable, and `check_layout.py` turns it into a verdict.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

# Mobject classes whose overlap is a genuine readability problem
TEXT_CLASSES = {
    "Text",
    "MarkupText",
    "Tex",
    "MathTex",
    "SingleStringMathTex",
    "DecimalNumber",
    "Integer",
    "Variable",
}

DEFAULT_SAMPLE_EVERY = 0.15
DEFAULT_MIN_DURATION = 0.35
DEFAULT_MIN_OVERLAP_FRAC = 0.10


def _is_text(mob: Any) -> bool:
    """Whether a mobject is a text-like leaf worth checking.

    Args:
        mob: Any Manim mobject.

    Returns:
        True when the mobject's class is text-like and it has a drawable extent.
    """
    if type(mob).__name__ not in TEXT_CLASSES:
        return False
    try:
        return bool(mob.width > 0.01 and mob.height > 0.01)
    except Exception:  # noqa: BLE001 - degenerate mobjects are simply skipped
        return False


def _text_leaves(scene: Any) -> list[Any]:
    """Collect every visible text-like mobject currently in the scene.

    Walks each top-level mobject's family so text nested inside groups (chips,
    cards, labelled boxes) is found without any registration discipline.

    Args:
        scene: The running Manim scene.

    Returns:
        A list of text-like mobjects, deduplicated by identity.
    """
    found: dict[int, Any] = {}
    for top in list(getattr(scene, "mobjects", [])):
        try:
            family = top.family_members_with_points()
        except Exception:  # noqa: BLE001
            family = [top]
        for mob in [top, *family]:
            if _is_text(mob) and id(mob) not in found:
                if _opacity_of(mob) > 0.06:
                    found[id(mob)] = mob
    return list(found.values())


def _opacity_of(mob: Any) -> float:
    """Best-effort visible opacity of a mobject.

    Invisible text cannot collide with anything, so faded-out mobjects that are
    still in the scene must not raise false alarms.

    Args:
        mob: Any Manim mobject.

    Returns:
        The larger of fill and stroke opacity, or 1.0 when unknown.
    """
    try:
        fill = float(mob.get_fill_opacity())
    except Exception:  # noqa: BLE001
        fill = 1.0
    try:
        stroke = float(mob.get_stroke_opacity())
    except Exception:  # noqa: BLE001
        stroke = 0.0
    return max(fill, stroke)


def _label_of(mob: Any) -> str:
    """A short human label for a text mobject, for the report.

    Args:
        mob: A text-like mobject.

    Returns:
        Its rendered string when available, else its class name.
    """
    for attr in ("text", "tex_string"):
        value = getattr(mob, attr, None)
        if isinstance(value, str) and value.strip():
            flat = " ".join(value.split())
            return flat[:48]
    return type(mob).__name__


def _box(mob: Any) -> tuple[float, float, float, float]:
    """Axis-aligned bounds of a mobject as ``(x0, y0, x1, y1)``.

    Args:
        mob: Any Manim mobject.

    Returns:
        Left, bottom, right and top coordinates.
    """
    return (
        float(mob.get_left()[0]),
        float(mob.get_bottom()[1]),
        float(mob.get_right()[0]),
        float(mob.get_top()[1]),
    )


def _overlap_fraction(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """Intersection area as a fraction of the smaller box.

    Args:
        a: First box as ``(x0, y0, x1, y1)``.
        b: Second box in the same form.

    Returns:
        0.0 when the boxes are disjoint, else the shared fraction of the smaller.
    """
    dx = min(a[2], b[2]) - max(a[0], b[0])
    dy = min(a[3], b[3]) - max(a[1], b[1])
    if dx <= 0 or dy <= 0:
        return 0.0
    inter = dx * dy
    area_a = max((a[2] - a[0]) * (a[3] - a[1]), 1e-6)
    area_b = max((b[2] - b[0]) * (b[3] - b[1]), 1e-6)
    return inter / min(area_a, area_b)


class LayoutWatcher:
    """Samples the scene on a timer and accumulates overlap intervals."""

    def __init__(
        self,
        scene: Any,
        demo_dir: Path,
        *,
        sample_every: float = DEFAULT_SAMPLE_EVERY,
        min_duration: float = DEFAULT_MIN_DURATION,
        min_overlap_frac: float = DEFAULT_MIN_OVERLAP_FRAC,
    ) -> None:
        """Create a watcher bound to a scene.

        Args:
            scene: The running Manim scene.
            demo_dir: Demo directory; the report lands in ``out/``.
            sample_every: Seconds of scene time between samples.
            min_duration: Shortest overlap worth reporting — brief crossings
                during a morph are legitimate and would otherwise dominate.
            min_overlap_frac: Shared area (as a fraction of the smaller box)
                below which a touch is treated as a graze.
        """
        self.scene = scene
        self.demo_dir = Path(demo_dir)
        self.sample_every = float(sample_every)
        self.min_duration = float(min_duration)
        self.min_overlap_frac = float(min_overlap_frac)
        self._accum = 0.0
        self._open: dict[tuple[str, str], dict[str, Any]] = {}
        self.violations: list[dict[str, Any]] = []
        self.samples = 0

    def sample(self, dt: float) -> None:
        """Advance the timer and, when due, check the current frame.

        Args:
            dt: Seconds of scene time since the previous frame.
        """
        self._accum += float(dt or 0.0)
        if self._accum < self.sample_every:
            return
        self._accum = 0.0
        now = float(getattr(self.scene, "time", 0.0))
        self.samples += 1

        texts = _text_leaves(self.scene)
        boxes = [(_label_of(m), _box(m)) for m in texts]
        seen_now: set[tuple[str, str]] = set()
        for i, (la, ba) in enumerate(boxes):
            for lb, bb in boxes[i + 1 :]:
                frac = _overlap_fraction(ba, bb)
                if frac < self.min_overlap_frac:
                    continue
                key = tuple(sorted((la, lb)))  # type: ignore[assignment]
                seen_now.add(key)  # type: ignore[arg-type]
                record = self._open.get(key)  # type: ignore[arg-type]
                if record is None:
                    self._open[key] = {  # type: ignore[index]
                        "a": key[0],
                        "b": key[1],
                        "start": now,
                        "end": now,
                        "max_overlap_frac": frac,
                    }
                else:
                    record["end"] = now
                    record["max_overlap_frac"] = max(record["max_overlap_frac"], frac)
        for key in list(self._open):
            if key not in seen_now:
                self._close(key)

    def _close(self, key: tuple[str, str]) -> None:
        """Close an overlap interval, keeping it only if it lasted.

        Args:
            key: The sorted label pair identifying the interval.
        """
        record = self._open.pop(key, None)
        if record is None:
            return
        record["duration"] = round(record["end"] - record["start"], 3)
        if record["duration"] >= self.min_duration:
            record["start"] = round(record["start"], 3)
            record["end"] = round(record["end"], 3)
            record["max_overlap_frac"] = round(record["max_overlap_frac"], 3)
            record["midpoint"] = round((record["start"] + record["end"]) / 2, 3)
            self.violations.append(record)

    def flush(self) -> Path:
        """Close any open intervals and write the report.

        Returns:
            Path to the written ``out/layout_violations.json``.
        """
        for key in list(self._open):
            self._close(key)
        out_dir = self.demo_dir / "out"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "layout_violations.json"
        payload = {
            "samples": self.samples,
            "sample_every": self.sample_every,
            "min_duration": self.min_duration,
            "min_overlap_frac": self.min_overlap_frac,
            "violations": sorted(self.violations, key=lambda v: -v["duration"]),
        }
        path.write_text(json.dumps(payload, indent=2) + "\n")
        return path


def watch_layout(scene: Any, demo_dir: Path, **kwargs: Any) -> LayoutWatcher:
    """Attach a layout watcher to a scene for the whole render.

    Args:
        scene: The running Manim scene, already set up.
        demo_dir: Demo directory; the report lands in ``out/``.
        **kwargs: Forwarded to :class:`LayoutWatcher`.

    Returns:
        The watcher, so callers can inspect or flush it early.
    """
    from manim import Mobject  # local import: keeps this module importable bare

    watcher = LayoutWatcher(scene, demo_dir, **kwargs)
    ticker = Mobject()
    ticker.add_updater(lambda _m, dt: watcher.sample(dt))
    scene.add(ticker)
    setattr(scene, "_layout_watcher", watcher)
    return watcher


def summarize(violations: Iterable[dict[str, Any]]) -> str:
    """Render violations as a human-readable report.

    Args:
        violations: Violation records from the JSON report.

    Returns:
        A multi-line string, one line per overlap interval.
    """
    lines = []
    for v in violations:
        lines.append(
            f"  {v['start']:7.2f}s–{v['end']:7.2f}s ({v['duration']:.2f}s, "
            f"{int(v['max_overlap_frac'] * 100):3d}% overlap)  "
            f"{v['a']!r} ↔ {v['b']!r}"
        )
    return "\n".join(lines)
