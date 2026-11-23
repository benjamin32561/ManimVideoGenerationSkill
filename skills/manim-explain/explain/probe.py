"""Geometry sampled while a scene runs, with no pixels drawn.

``GeometryProbe`` is a manimgx frame sink that never asks for pixels, so the film is only
counted, not drawn. At every frame it records the canvas box of each visible leaf of the
layout, and of anything else on screen (copies in flight), together with what moved since
the previous frame. ``find_problems`` turns the samples into overlap, clipping and crossing
problems with the time intervals they last; holds are sampled once (manimgx sends a held
frame once), so long still stretches cost nothing.

Samples are kept per window (``explain.windows``) in ``out/probe/<digest>.npz``. A window
whose digest is already there is not computed frame by frame or sampled again: its frames
are the same as before, so its stored samples are loaded instead.
"""

from dataclasses import dataclass
from pathlib import Path

import manimgx as m
import numpy as np
from manimgx.rendering.film import Frame

from explain.plan import Layout
from explain.problems import Problem
from explain.scene import VideoScene

VISIBLE_OPACITY = 0.05
MOVED_PX = 0.5
OVERLAP_PX = 1.5
MOVER_SHARE = 0.25
CROSSING_GRACE_S = 0.15
SAFE_MARGIN = 0.05
TRANSIENT = "~copy"


@dataclass
class Sample:
    """What was on screen at one frame.

    Attributes:
        t: Time (s).
        ids: Leaf ids in sample order (``~copy`` marks one glyph of a copy in flight).
        boxes: ``(n, 4)`` canvas boxes ``x0, y0, x1, y1`` (px).
        moving: Which of them moved since the previous sample.
        event: Id of the event playing (or last played) at this frame.
    """

    t: float
    ids: list[str]
    boxes: np.ndarray
    moving: np.ndarray
    event: str


def save_samples(samples: list[Sample], path: Path) -> None:
    """Store one window's samples as plain arrays (no pickling).

    Args:
        samples: The window's samples, in time order.
        path: The ``.npz`` file to write.
    """
    counts = [len(s.ids) for s in samples]
    np.savez_compressed(
        path, t=np.array([s.t for s in samples], dtype=float), counts=np.array(counts, dtype=np.int64),
        events=np.array([s.event for s in samples], dtype=str),
        ids=np.array([i for s in samples for i in s.ids], dtype=str),
        boxes=np.concatenate([s.boxes for s in samples]) if samples else np.zeros((0, 4)),
        moving=np.concatenate([s.moving for s in samples]) if samples else np.zeros(0, dtype=bool))


def load_samples(path: Path) -> list[Sample]:
    """Read one window's samples back exactly as they were stored.

    Args:
        path: A file written by ``save_samples``.

    Returns:
        The samples, in time order.
    """
    with np.load(path, allow_pickle=False) as data:
        edges = np.concatenate([[0], np.cumsum(data["counts"])])
        ids, boxes, moving = data["ids"].tolist(), data["boxes"], data["moving"]
        return [Sample(float(t), ids[a:b], boxes[a:b].copy(), moving[a:b].copy(), str(event))
                for t, event, a, b in zip(data["t"], data["events"], edges[:-1], edges[1:], strict=True)]


class GeometryProbe:
    """A frame sink that samples leaf boxes without drawing, window by window.

    Args:
        scene: The scene being run (its registry and director are read at every frame).
        fps: Frame rate of the film.
        cache: Directory of stored window samples (``out/probe``).
    """

    def __init__(self, scene: VideoScene, fps: int, cache: Path) -> None:
        """Follow the scene's windows and start with no samples.

        Args:
            scene: The scene being run; the probe becomes its window observer.
            fps: Frame rate of the film (converts frame indices to seconds).
            cache: Directory of stored window samples.
        """
        self.scene = scene
        self.fps = fps
        self.cache = cache
        cache.mkdir(parents=True, exist_ok=True)
        scene.observer = self
        self.windows: list[tuple[str, bool]] = []
        self.fresh: list[Sample] = []
        self.sampling = False
        self.previous: dict[str, np.ndarray] = {}

    def begin_window(self, window: dict) -> bool:
        """Close the window before, and decide whether to sample this one.

        A window is sampled when its digest has no stored samples. Sampling starts from the
        scene at rest, so what counts as moving is measured from the same state as in a run
        that sampled every window.

        Args:
            window: ``{"event", "start", "digest"}`` of the window opening now.

        Returns:
            True when the window is sampled (and must be computed frame by frame).
        """
        self.close_window()
        self.sampling = not (self.cache / f"{window['digest']}.npz").is_file()
        self.windows.append((window["digest"], self.sampling))
        if self.sampling:
            ids, boxes = self.visible()
            self.previous = {leaf: box for leaf, box in zip(ids, boxes, strict=True) if leaf != TRANSIENT}
        return self.sampling

    def close_window(self) -> None:
        """Store the samples of the window just finished, if it was sampled."""
        if self.windows and self.windows[-1][1]:
            save_samples(self.fresh, self.cache / f"{self.windows[-1][0]}.npz")
        self.fresh = []

    def samples(self) -> list[Sample]:
        """Every window's samples in time order: fresh ones as stored, the rest loaded.

        Call after the scene has finished.

        Returns:
            The samples of the whole film.
        """
        self.close_window()
        return [s for digest, _ in self.windows for s in load_samples(self.cache / f"{digest}.npz")]

    def prune(self) -> None:
        """Delete stored samples of windows the current plan no longer has."""
        keep = {f"{digest}.npz" for digest, _ in self.windows}
        for stale in self.cache.glob("*.npz"):
            if stale.name not in keep:
                stale.unlink()

    def __call__(self, frame: Frame) -> None:
        """Record the boxes of everything visible in the scene's current state.

        manimgx sends a frame when the next different frame is recorded, so the live scene
        already shows that next frame: index ``frame.index + frame.repeat``. The sample is
        labelled with its time, which keeps geometry and time in step through holds.
        Frames of windows that are not sampled are ignored.

        Args:
            frame: The frame manimgx sends (its pixels are never requested).
        """
        if not self.sampling:
            return
        ids, boxes = self.visible()
        array = np.array(boxes, dtype=float).reshape(-1, 4)
        moving = np.array([leaf == TRANSIENT or not np.allclose(self.previous.get(leaf, box), box, atol=MOVED_PX)
                           for leaf, box in zip(ids, array, strict=True)], dtype=bool)
        self.previous = {leaf: box for leaf, box in zip(ids, array, strict=True) if leaf != TRANSIENT}
        self.fresh.append(Sample((frame.index + frame.repeat) / self.fps, ids, array, moving,
                                 self.scene.current_event))

    def visible(self) -> tuple[list[str], list[list[float]]]:
        """The ids and canvas boxes of everything visible now.

        Returns:
            Leaf ids (``~copy`` for each glyph of anything that is not a layout leaf, such as a
            copy in flight) and their boxes; flash highlights are left out.
        """
        scene = self.scene
        on_screen = {id(mob) for mob in scene.get_mobject_family_members()}
        known: dict[int, str] = {}
        ids, boxes = [], []
        for leaf in scene.layout.leaves(list(scene.layout.objects)):
            mob = scene.registry[leaf]
            known[id(mob)] = leaf
            if id(mob) in on_screen and opacity(mob) > VISIBLE_OPACITY:
                ids.append(leaf)
                boxes.append(self.box(mob))
        highlights = {id(glow) for glow in scene.director.flashes}
        for mob in scene.mobjects:
            if id(mob) in highlights or any(id(part) in known for part in mob.get_family()):
                continue
            for glyph in mob.family_members_with_points():
                if opacity(glyph) > VISIBLE_OPACITY:
                    ids.append(TRANSIENT)
                    boxes.append(self.box(glyph))
        return ids, boxes

    def box(self, mob: m.Mobject) -> list[float]:
        """A mobject's bounding box in canvas pixels.

        Args:
            mob: Any mobject.

        Returns:
            ``[x0, y0, x1, y1]`` with y growing downward.
        """
        kit = self.scene.builder.kit
        x0, y1 = kit.to_px(mob.get_corner(m.DL))
        x1, y0 = kit.to_px(mob.get_corner(m.UR))
        return [x0, y0, x1, y1]


def opacity(mob: m.Mobject) -> float:
    """The strongest fill or stroke opacity among a mobject's drawn parts.

    Args:
        mob: Any mobject.

    Returns:
        0 for an invisible mobject, up to 1.
    """
    parts = mob.family_members_with_points()
    if not parts:
        return 0.0
    return max(max(p.get_fill_opacity(), p.get_stroke_opacity()) for p in parts)


def box_area(box: np.ndarray) -> float:
    """Area of a box, never zero (degenerate boxes count as a hair).

    Args:
        box: ``[x0, y0, x1, y1]``.

    Returns:
        The area in px².
    """
    return max(box[2] - box[0], 1e-6) * max(box[3] - box[1], 1e-6)


def overlaps(boxes: np.ndarray) -> np.ndarray:
    """Pairwise overlap of boxes, by the shorter side of their intersection.

    Args:
        boxes: ``(n, 4)`` boxes.

    Returns:
        ``(n, n)`` matrix: the smaller of the intersection's width and height (px), 0 when
        the boxes do not overlap.
    """
    x0 = np.maximum(boxes[:, None, 0], boxes[None, :, 0])
    y0 = np.maximum(boxes[:, None, 1], boxes[None, :, 1])
    x1 = np.minimum(boxes[:, None, 2], boxes[None, :, 2])
    y1 = np.minimum(boxes[:, None, 3], boxes[None, :, 3])
    return np.clip(np.minimum(x1 - x0, y1 - y0), 0, None)


def allowed_pairs(layout: Layout) -> set[frozenset[str]]:
    """Pairs of leaves that may overlap by design.

    A box or brace may touch what it surrounds; parts of one formula touch each other; an
    object's ``allow_overlap`` list and ``inside`` container are deliberate.

    Args:
        layout: The layout plan.

    Returns:
        Unordered leaf-id pairs.
    """
    pairs: set[frozenset[str]] = set()
    for oid, spec in layout.objects.items():
        mine = layout.leaves([oid])
        others = list(spec.get("allow_overlap", [])) + ([spec["inside"]] if spec.get("inside") else [])
        if spec["type"] in ("box", "brace"):
            others.append(spec["around"])
        for other in others:
            pairs |= {frozenset((a, b)) for a in mine for b in layout.leaves([other])}
        pairs |= {frozenset((a, b)) for a in mine for b in mine if a != b}
    return pairs


def find_problems(samples: list[Sample], layout: Layout, width: int, height: int,
                  copy_endpoints: dict[str, set[str]]) -> list[Problem]:
    """Turn geometry samples into problems with the intervals they last.

    * ``clipped`` (error): a leaf reaches outside the canvas.
    * ``outside_safe_area`` (warning): inside the canvas but outside the 5% margin.
    * ``text_overlap`` (error): two texts overlap.
    * ``crosses_label`` (error): a moving shape or a copy in flight crosses a text for longer
      than ``CROSSING_GRACE_S`` (a brush of a few frames is a warning).
    * ``text_on_shape`` (warning): a text rests on a shape (the review judges it).
    * ``movers_collide`` (warning): two moving shapes overlap by more than a quarter.
    * ``outside_container`` (error): a text leaves its ``inside`` container.

    Backdrops (``backdrop: true``) never count; allowed pairs never count.

    Args:
        samples: The probe's samples.
        layout: The layout plan.
        width: Canvas width (px).
        height: Canvas height (px).
        copy_endpoints: Event id → the leaves its copies fly between (they may touch them).

    Returns:
        The problems, one per (kind, subject, other), with merged intervals.
    """
    allowed = allowed_pairs(layout)
    backdrop = {leaf for oid, s in layout.objects.items() if s.get("backdrop") for leaf in layout.leaves([oid])}
    containers = {leaf: s["inside"] for oid, s in layout.objects.items() if s.get("inside")
                  for leaf in layout.leaves([oid])}
    found: dict[tuple, Problem] = {}
    frame_dt = samples[1].t - samples[0].t if len(samples) > 1 else 0.0

    def note(kind: str, severity: str, a: str, b: str | None, t: float) -> None:
        """Record one occurrence of a problem, extending its last interval when contiguous.

        Args:
            kind: Problem kind.
            severity: ``error`` or ``warning``.
            a: The leaf at fault.
            b: The leaf it collides with, if any.
            t: Sample time (s).
        """
        key = (kind, a, b)
        problem = found.setdefault(key, Problem(kind, severity, a, b))
        if problem.intervals and t - problem.intervals[-1][1] <= max(frame_dt, 1 / 15) + 1e-6:
            problem.intervals[-1][1] = round(t, 3)
        else:
            problem.intervals.append([round(t, 3), round(t, 3)])

    margin_x, margin_y = width * SAFE_MARGIN, height * SAFE_MARGIN
    for s in samples:
        if not s.ids:
            continue
        is_text = np.array([i != TRANSIENT and layout.is_text(i) for i in s.ids])
        is_copy = np.array([i == TRANSIENT for i in s.ids])
        counts = np.array([i not in backdrop for i in s.ids])
        b = s.boxes
        for k, leaf in enumerate(s.ids):
            if leaf == TRANSIENT:
                continue
            x0, y0, x1, y1 = b[k]
            if x0 < -OVERLAP_PX or y0 < -OVERLAP_PX or x1 > width + OVERLAP_PX or y1 > height + OVERLAP_PX:
                note("clipped", "error", leaf, None, s.t)
            elif x0 < margin_x or y0 < margin_y or x1 > width - margin_x or y1 > height - margin_y:
                note("outside_safe_area", "warning", leaf, None, s.t)
            if leaf in containers and containers[leaf] in s.ids:
                c = b[s.ids.index(containers[leaf])]
                if x0 < c[0] or y0 < c[1] or x1 > c[2] or y1 > c[3]:
                    note("outside_container", "error", leaf, containers[leaf], s.t)
        depth = overlaps(b)
        n = len(s.ids)
        for i in range(n):
            for j in range(i + 1, n):
                if depth[i, j] <= OVERLAP_PX or not (counts[i] and counts[j]):
                    continue
                a_id, b_id = s.ids[i], s.ids[j]
                if frozenset((a_id, b_id)) in allowed:
                    continue
                if is_copy[i] or is_copy[j]:
                    text_id = b_id if is_copy[i] else a_id
                    if text_id != TRANSIENT and layout.is_text(text_id) \
                            and text_id not in copy_endpoints.get(s.event, set()):
                        note("crosses_label", "error", f"copy in {s.event}", text_id, s.t)
                    continue
                if is_text[i] and is_text[j]:
                    note("text_overlap", "error", a_id, b_id, s.t)
                elif is_text[i] or is_text[j]:
                    text_id, shape_id = (a_id, b_id) if is_text[i] else (b_id, a_id)
                    shape_moving = s.moving[j] if is_text[i] else s.moving[i]
                    if shape_moving:
                        note("crosses_label", "error", shape_id, text_id, s.t)
                    else:
                        note("text_on_shape", "warning", text_id, shape_id, s.t)
                elif s.moving[i] and s.moving[j]:
                    inter = max(0.0, min(b[i][2], b[j][2]) - max(b[i][0], b[j][0])) * \
                        max(0.0, min(b[i][3], b[j][3]) - max(b[i][1], b[j][1]))
                    if inter > MOVER_SHARE * min(box_area(b[i]), box_area(b[j])):
                        note("movers_collide", "warning", a_id, b_id, s.t)
    for problem in found.values():
        if problem.kind == "crosses_label" and all(b - a < CROSSING_GRACE_S for a, b in problem.intervals):
            problem.severity = "warning"
    return list(found.values())
