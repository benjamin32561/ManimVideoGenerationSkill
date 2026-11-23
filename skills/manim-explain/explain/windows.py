"""Window digests: what each stretch of the film depends on, so unchanged stretches are reused.

A window runs from one event's play to the next event's. The scene is at rest when a window
opens (the previous play has finished), so the window's frames depend only on:

- the state at rest: every earlier event's lasting effect, and the layout of every object
  those events touched;
- its own event: its actions, its timing, and the layout of the objects it touches;
- the code, the style and the video's custom components (``plan.code_digest``).

``Ledger`` folds these into one digest per window, in order. A layout edit changes the windows
from the object's first use onward; a change with no lasting effect (an ``arc``, a ``delay``,
a ``flash``) changes only its own window. ``plan_check.py``, ``render.py`` and
``check_render.py`` reuse the work of every window (and beat) whose digest they have seen.
"""

import hashlib
import json

from explain.plan import Event, Layout

PASSING = ("delay", "lag", "arc", "shift", "from")
FLEETING = ("flash",)
EDGE_FRAMES = 1


def fold(*parts: object) -> str:
    """Hash values into one digest (JSON with sorted keys, so dict order never matters).

    Args:
        *parts: JSON-serializable values.

    Returns:
        A hex SHA-256.
    """
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()


class Ledger:
    """The running state digest of a scene, advanced one event at a time.

    Args:
        layout: The layout plan.
        base: ``plan.code_digest`` of the code, style and custom components.
    """

    def __init__(self, layout: Layout, base: str) -> None:
        """Start at the empty canvas.

        Args:
            layout: The layout plan.
            base: The digest of the code, style and custom components.
        """
        self.layout = layout
        self.state = fold("canvas", base)

    def blank(self, until: float) -> str:
        """The digest of the empty canvas before the first event.

        Args:
            until: When the first event's play starts (s).

        Returns:
            The window digest.
        """
        return fold(self.state, "blank", round(until, 6))

    def window(self, event: Event, start: float, limit: float) -> str:
        """The digest of one event's window; the ledger then moves past the event.

        Args:
            event: The event about to play.
            start: When its play starts (s), after any overrun of the previous play.
            limit: Seconds its actions may run (to the next event's scheduled start).

        Returns:
            The window digest.
        """
        specs = {oid: self.layout.objects[oid] for oid in sorted(self.touched(event))}
        digest = fold(self.state, self.view(event, lasting=False), specs, event.end - event.start,
                      round(start, 6), round(limit, 6))
        self.state = fold(self.state, self.view(event, lasting=True), specs)
        return digest

    def touched(self, event: Event) -> set[str]:
        """The objects an event acts on, and the objects those are built around.

        Args:
            event: The event.

        Returns:
            Object ids (a math part counts as its whole object).
        """
        layout = self.layout
        leaves = [leaf for action in event.actions for leaf in self.leaves(action)]
        objects = {layout.parts.get(leaf, leaf) for leaf in leaves}
        pending = list(objects)
        while pending:
            around = layout.objects[pending.pop()].get("around")
            for dep in {layout.parts.get(leaf, leaf) for leaf in layout.leaves([around])} if around else ():
                if dep not in objects:
                    objects.add(dep)
                    pending.append(dep)
        return objects

    def leaves(self, action: dict) -> list[str]:
        """The leaves one action names, groups expanded.

        Args:
            action: The action as written.

        Returns:
            Leaf ids.
        """
        named = list(action.get("targets", [])) + [action[k] for k in ("source", "target") if k in action]
        return self.layout.leaves(named)

    def view(self, event: Event, lasting: bool) -> list[dict]:
        """An event's actions as they bear on the frames.

        Args:
            event: The event.
            lasting: Keep only what outlives the event: fleeting actions are dropped,
                fields that only shape the motion are dropped, and a path keeps only its
                end points. Otherwise the actions in full, with their paths.

        Returns:
            One dict per action, with the leaves it names (so group membership counts).
        """
        out = []
        for action in event.actions:
            if lasting and action["action"] in FLEETING:
                continue
            kept = {k: v for k, v in action.items() if not (lasting and k in PASSING)}
            if "along" in action:
                path = self.layout.paths[action["along"]]
                kept["along"] = {leaf: points[-1] if lasting else points for leaf, points in path.items()}
            out.append({**kept, "leaves": self.leaves(action)})
        return out


def beat_digest(windows: list[dict], first: int, stop: int, fps: int) -> str:
    """The digest of one beat's clip: the windows its frames fall in, and its frame range.

    Windows within ``EDGE_FRAMES`` of the range count too, so rounding at a boundary can only
    cause a re-render, never a stale clip. A worker's film runs until all of them have opened
    (``scene.BeatRecorder``), so the worker and ``render.py`` count the same windows.

    Args:
        windows: ``{"start": s, "digest": d}`` in time order (the blank window first).
        first: The clip's first frame.
        stop: One past its last frame.
        fps: Frame rate.

    Returns:
        A hex SHA-256.
    """
    lo, hi = (first - EDGE_FRAMES) / fps, (stop + EDGE_FRAMES) / fps
    ends = [w["start"] for w in windows[1:]] + [float("inf")]
    inside = [w["digest"] for w, end in zip(windows, ends, strict=True) if w["start"] < hi and end > lo]
    return fold(inside, first, stop, fps)
