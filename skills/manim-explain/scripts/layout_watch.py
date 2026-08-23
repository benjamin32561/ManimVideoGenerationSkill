"""Continuously watch a rendering scene for text that collides with text or a box.

Two kinds of collision are reported. Text over text is the obvious one. The
other, and by experience the more common, is a **box border cutting through
text**: an instruction chip whose rectangle runs into the label beside it, an
emphasis rectangle that starts mid-word, a table row whose edge crosses a
caption. Text-vs-text comparison cannot see any of those, because the two texts
never touch — only the stroke between them does.

The rule for boxes is a clean one: a box either fully contains a text or must
not touch it at all. A chip legitimately contains its own label; a partial
overlap is always a defect, and it also catches text overflowing the panel it
was meant to sit inside.

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
import os
from pathlib import Path
from typing import Any, Iterable

from occupancy import boundary_leftovers, leftover_records, motion_events
from scene_snapshot import DEFAULT_EVERY as SNAPSHOT_EVERY
from scene_snapshot import clear_snapshots, pack_scene, save_snapshot

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

# Mobject classes drawn as a bordered box, which must not cut through text
FRAME_CLASSES = {
    "Rectangle",
    "RoundedRectangle",
    "SurroundingRectangle",
    "Square",
}

DEFAULT_SAMPLE_EVERY = 0.10
DEFAULT_MIN_DURATION = 0.35
DEFAULT_MIN_OVERLAP_FRAC = 0.10
# A text is "inside" a box if this much of its area is within it; "outside" if
# less than 1 - this. Between the two it is being cut, which is the defect.
FRAME_INSIDE_FRAC = 0.97
FRAME_GRAZE_FRAC = 0.03


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


def _leaf_owner(scene: Any, want_frames: bool) -> list[tuple[Any, int]]:
    """Collect matching leaves paired with the id of their top-level ancestor.

    Full containment of a text inside a box is legitimate when the box owns the
    text — a chip and its own label. It is **occlusion** when they belong to
    different top-level mobjects: a wide chip laid over a small state node
    swallows that node's letter entirely, which the containment rule alone reads
    as "fine". One video shipped a whole state diagram buried under a later
    panel that way.

    Args:
        scene: The running Manim scene.
        want_frames: Collect box-like leaves when True, else text-like.

    Returns:
        ``(leaf, draw_index)`` pairs, deduplicated by leaf identity, where the
        index is the leaf's position in ``scene.mobjects`` — manim paints that
        list in order, so a larger index is drawn on top.
    """
    test = _is_frame if want_frames else _is_text
    found: list[tuple[Any, int]] = []
    seen: set[int] = set()
    for depth, top in enumerate(list(getattr(scene, "mobjects", []))):
        try:
            family = top.get_family()
        except Exception:  # noqa: BLE001
            continue
        for mob in family:
            if id(mob) in seen or not test(mob):
                continue
            if not want_frames and _opacity_of(mob) <= 0.06:
                continue
            seen.add(id(mob))
            found.append((mob, depth))
    return found


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
            family = top.get_family()
        except Exception:  # noqa: BLE001
            family = [top]
        for mob in [top, *family]:
            if _is_text(mob) and id(mob) not in found:
                if _opacity_of(mob) > 0.06:
                    found[id(mob)] = mob
    return list(found.values())


def _is_frame(mob: Any) -> bool:
    """Whether a mobject is a drawn box that could cut through text.

    Args:
        mob: Any Manim mobject.

    Returns:
        True when the class is box-like, it has a drawable extent, and it is
        actually painted (a zero-opacity hitbox occludes nothing).
    """
    if type(mob).__name__ not in FRAME_CLASSES:
        return False
    try:
        if not (mob.width > 0.02 and mob.height > 0.02):
            return False
        stroke = float(mob.get_stroke_opacity() or 0.0)
        fill = float(mob.get_fill_opacity() or 0.0)
        return max(stroke, fill) > 0.05
    except Exception:  # noqa: BLE001 - degenerate mobjects are simply skipped
        return False


def _frame_leaves(scene: Any) -> list[Any]:
    """Collect every visible box-like mobject currently in the scene.

    Args:
        scene: The running Manim scene.

    Returns:
        A list of box-like mobjects, deduplicated by identity.
    """
    found: list[Any] = []
    seen: set[int] = set()
    for top in list(getattr(scene, "mobjects", [])):
        try:
            family = top.get_family()
        except Exception:  # noqa: BLE001
            continue
        for mob in family:
            if id(mob) in seen or not _is_frame(mob):
                continue
            seen.add(id(mob))
            found.append(mob)
    return found


def _hides(box: Any, box_depth: int, text_depth: int) -> bool:
    """Whether a box can actually conceal a text it fully contains.

    Full containment alone is not occlusion. Three ways it is innocent:

    * the box and the text are the same figure (a chip and its own label);
    * the box is painted **under** the text, so the glyphs are still on top —
      this is the common case, because ``set_reg`` / ``set_readout`` swap a value
      with ``Transform``, which re-adds the new text above its own cell box;
    * the box has no fill, so it is an outline and hides nothing — a
      ``SurroundingRectangle`` ring is *meant* to enclose things.

    Args:
        box: The box mobject.
        box_depth: Its index in ``scene.mobjects``.
        text_depth: The contained text's index in the same list.

    Returns:
        True only when the box is drawn above the text and is opaque enough to
        conceal it.
    """
    if box_depth <= text_depth:
        return False
    try:
        return float(box.get_fill_opacity() or 0.0) > 0.30
    except Exception:  # noqa: BLE001
        return False


def _fill_of(mob: Any) -> float:
    """Fill opacity of a mobject, or 0 when it cannot be read.

    Args:
        mob: Any Manim mobject.

    Returns:
        Fill opacity in ``[0, 1]``.
    """
    try:
        return float(mob.get_fill_opacity() or 0.0)
    except Exception:  # noqa: BLE001
        return 0.0


def _item_record(mob: Any, depth: int, kind: str) -> dict[str, Any]:
    """One occupancy JSON item: geometry plus the paint attributes predicates use.

    Args:
        mob: The sampled mobject.
        depth: Index in ``scene.mobjects`` (draw order; larger is on top).
        kind: ``text`` or ``frame``.

    Returns:
        JSON-ready dict with ``id``, ``label``, ``kind``, ``box``, ``opacity``,
        ``fill``, and ``depth``.
    """
    return {
        "id": id(mob),
        "label": _label_of(mob),
        "kind": kind,
        "box": [round(c, 3) for c in _box(mob)],
        "opacity": round(_opacity_of(mob), 3),
        "fill": round(_fill_of(mob), 3),
        "depth": int(depth),
    }


def _contained_fraction(inner: tuple[float, ...], outer: tuple[float, ...]) -> float:
    """How much of ``inner``'s area lies within ``outer``.

    Args:
        inner: The box being tested, as ``(x0, y0, x1, y1)``.
        outer: The containing candidate, in the same form.

    Returns:
        0.0 when disjoint, 1.0 when fully inside.
    """
    dx = min(inner[2], outer[2]) - max(inner[0], outer[0])
    dy = min(inner[3], outer[3]) - max(inner[1], outer[1])
    if dx <= 0 or dy <= 0:
        return 0.0
    area = max((inner[2] - inner[0]) * (inner[3] - inner[1]), 1e-6)
    return (dx * dy) / area


def _opacity_of(mob: Any) -> float:
    """Best-effort visible opacity of a mobject.

    Invisible text cannot collide with anything, so faded-out mobjects that are
    still in the scene must not raise false alarms.

    Args:
        mob: Any Manim mobject.

    Returns:
        The larger of fill and stroke opacity, or 1.0 when unknown.
    """
    readable = False
    best = 0.0
    try:
        best = max(best, float(mob.get_fill_opacity() or 0.0))
        readable = True
    except Exception:  # noqa: BLE001
        pass
    try:
        best = max(best, float(mob.get_stroke_opacity() or 0.0))
        readable = True
    except Exception:  # noqa: BLE001
        pass
    try:
        kids = [k for k in mob.get_family() if k is not mob]
    except Exception:  # noqa: BLE001
        kids = []
    for k in kids:
        try:
            best = max(
                best,
                float(k.get_fill_opacity() or 0.0),
                float(k.get_stroke_opacity() or 0.0),
            )
            readable = True
        except Exception:  # noqa: BLE001
            continue
    if best > 0.0:
        return best
    # Fully transparent family: a ``set_opacity(0)`` address must not collide.
    # The previous fallback of 1.0 treated every hidden queue_card hex as
    # visible, which produced tens of box-cuts against labels nobody can see.
    # Unknown mobjects (nothing readable) stay visible so a MathTex we cannot
    # inspect is not dropped.
    if readable:
        return 0.0
    return 1.0


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
        self.occupancy: list[dict[str, Any]] = []
        self.samples = 0
        self._snap_every = float(os.environ.get("MANIM_SNAPSHOT_EVERY") or SNAPSHOT_EVERY)
        self._last_snap_t = -1.0
        if os.environ.get("MANIM_STILL_ONLY") != "1":
            clear_snapshots(self.demo_dir)

    def sample(self, dt: float) -> None:
        """Advance the timer and, when due, check the current frame.

        A stills-only walk does not need occupancy or overlap intervals — the
        requested instants are captured from the renderer clock — so this
        returns immediately and leaves the previous occupancy JSON in place.

        Args:
            dt: Seconds of scene time since the previous frame.
        """
        if os.environ.get("MANIM_STILL_ONLY") == "1":
            return
        self._accum += float(dt or 0.0)
        if self._accum < self.sample_every:
            return
        self._accum = 0.0
        now = float(getattr(self.scene, "time", 0.0))
        self.samples += 1

        text_owned = _leaf_owner(self.scene, want_frames=False)
        frames_owned = _leaf_owner(self.scene, want_frames=True)
        boxes = [(_label_of(m), _box(m)) for m, _ in text_owned]
        self.occupancy.append(
            {
                "t": round(now, 3),
                "items": [
                    *[_item_record(m, d, "text") for m, d in text_owned],
                    *[_item_record(m, d, "frame") for m, d in frames_owned],
                ],
            }
        )
        ids_now = {item["id"] for item in self.occupancy[-1]["items"]}
        prev = getattr(self, "_prev_ids", set())
        if prev:
            gone = prev - ids_now
            if (
                len(gone) >= 4
                and len(gone) / max(len(prev), 1) >= 0.35
            ):
                capture = getattr(self.scene, "_geometry_capture", None)
                if capture is not None:
                    capture.capture("section")
                self._maybe_snapshot(now, force=True)
        self._prev_ids = ids_now
        self._maybe_snapshot(now, force=False)
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
                        "kind": "text-over-text",
                    }
                    self._capture_overlap()
                else:
                    record["end"] = now
                    record["max_overlap_frac"] = max(record["max_overlap_frac"], frac)
        frames = [(_label_of(m), _box(m), owner, m)
                  for m, owner in frames_owned]
        for fl, fb, f_owner, fb_mob in frames:
            for (tl, tb), (_, t_owner) in zip(boxes, text_owned):
                inside = _contained_fraction(tb, fb)
                if inside <= FRAME_GRAZE_FRAC:
                    continue                       # not touching at all
                buried = inside >= FRAME_INSIDE_FRAC
                if buried and not _hides(fb_mob, f_owner, t_owner):
                    continue    # same group, drawn under the text, or unfilled
                kind = "box-buries-text" if buried else "box-cuts-text"
                # Class name alone cannot identify one of many rectangles, so
                # carry the centre — it is what makes the report actionable.
                cx, cy = (fb[0] + fb[2]) / 2.0, (fb[1] + fb[3]) / 2.0
                key = (f"box {fl}@({cx:.2f},{cy:.2f})", tl)
                seen_now.add(key)
                record = self._open.get(key)
                if record is None:
                    self._open[key] = {
                        "a": key[0],
                        "b": key[1],
                        "start": now,
                        "end": now,
                        "max_overlap_frac": inside,
                        "kind": kind,
                    }
                    self._capture_overlap()
                else:
                    record["end"] = now
                    record["max_overlap_frac"] = max(record["max_overlap_frac"], inside)

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
            capture = getattr(self.scene, "_geometry_capture", None)
            if capture is not None:
                capture.capture("overlap-end")
            self._maybe_snapshot(record["end"], force=True)

    def _capture_overlap(self) -> None:
        """Rasterize one still at the first sample of a new overlap.

        Collision midpoints are not known until the interval closes, so the
        one-pass walk captures the opening instead. Duplicate calls in the
        same tick are collapsed by GeometryCapture.min_gap.

        Returns:
            None. Missing capture helper is silent — a full encode has none.
        """
        capture = getattr(self.scene, "_geometry_capture", None)
        if capture is not None:
            capture.capture("overlap")
        self._maybe_snapshot(
            float(getattr(self.scene, "time", 0.0)), force=True
        )

    def _maybe_snapshot(self, now: float, *, force: bool = False) -> None:
        """Write a compact mobject dump if enough scene time has elapsed.

        Args:
            now: Scene time in seconds.
            force: Write even if the throttle has not elapsed (overlaps and
                section fades — those are the instants stills will request).
        """
        if os.environ.get("MANIM_STILL_ONLY") == "1":
            return
        if not force and self._last_snap_t >= 0.0:
            if now - self._last_snap_t < self._snap_every:
                return
        if abs(now - self._last_snap_t) < 1e-3:
            return
        try:
            records = pack_scene(self.scene)
        except Exception:  # noqa: BLE001
            return
        save_snapshot(self.demo_dir, round(now, 2), records)
        self._last_snap_t = now

    def flush(self) -> Path:
        """Close any open intervals and write the report.

        Returns:
            Path to the written ``out/layout_violations.json``, or the stills
            manifest when this walk is stills-only (occupancy is not rewritten).
        """
        if os.environ.get("MANIM_STILL_ONLY") == "1":
            capture = getattr(self.scene, "_geometry_capture", None)
            if capture is not None:
                return capture.flush()
            return self.demo_dir / "out" / "stills" / "manifest.json"
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
        duration = float(getattr(self.scene, "time", 0.0))
        occupancy_path = out_dir / "occupancy.json"
        occupancy_path.write_text(
            json.dumps(
                {
                    "duration": round(duration, 3),
                    "sample_every": self.sample_every,
                    "n_samples": len(self.occupancy),
                    "leftovers": leftover_records(self.occupancy, duration),
                    "boundary_leftovers": boundary_leftovers(self.occupancy),
                    "motion": motion_events(self.occupancy),
                    "samples": self.occupancy,
                }
            )
            + "\n"
        )
        capture = getattr(self.scene, "_geometry_capture", None)
        if capture is not None:
            capture.flush()
        return path


_ACTIVE_SCENE: Any = None


def active_scene() -> Any:
    """Return the scene most recently passed to :func:`watch_layout`.

    ``LayoutBoard.assert_clear`` uses this to tell a disposed figure from a live
    one. Manim's ``FadeOut`` *restores* a mobject's opacity and simply removes it
    from the scene, so opacity cannot answer the question — only membership can.

    Returns:
        The active scene, or ``None`` when no scene has attached a watcher.
    """
    return _ACTIVE_SCENE


def on_stage_ids(scene: Any) -> set[int]:
    """Collect the ids of every mobject currently drawn in a scene.

    Args:
        scene: The running Manim scene.

    Returns:
        A set of ``id()`` values covering each top-level mobject and its family.
    """
    ids: set[int] = set()
    for top in list(getattr(scene, "mobjects", [])):
        ids.add(id(top))
        try:
            for m in top.get_family():
                ids.add(id(m))
        except Exception:  # noqa: BLE001
            continue
    return ids


def watch_layout(scene: Any, demo_dir: Path, **kwargs: Any) -> LayoutWatcher:
    """Attach a layout watcher to a scene for the whole render.

    Args:
        scene: The running Manim scene, already set up.
        demo_dir: Demo directory; the report lands in ``out/``.
        **kwargs: Forwarded to :class:`LayoutWatcher`.

    Returns:
        The watcher, so callers can inspect or flush it early.
    """
    from manim import Mobject, config  # local import: keeps this module importable bare

    global _ACTIVE_SCENE
    _ACTIVE_SCENE = scene
    watcher = LayoutWatcher(scene, demo_dir, **kwargs)
    ticker = Mobject()
    ticker.add_updater(lambda _m, dt: watcher.sample(dt))
    scene.add(ticker)
    setattr(scene, "_layout_watcher", watcher)
    if getattr(config, "geometry_only", False):
        from keyframe_capture import GeometryCapture

        setattr(scene, "_geometry_capture", GeometryCapture(scene, Path(demo_dir)))

    orig_construct = scene.construct

    def _construct_and_flush() -> None:
        """Run construct, then always write occupancy even if it asserts.

        A layout assertion aborts the walk before ``scene_finished``, which is
        exactly when occupancy is most useful: it names what was on stage at
        the failing beat.

        Returns:
            None. The original construct's exceptions propagate after flush.
        """
        try:
            orig_construct()
        finally:
            watcher.flush()

    scene.construct = _construct_and_flush  # type: ignore[method-assign]
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
