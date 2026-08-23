"""Named times and plays for a stills-only geometry walk.

The inner loop interpolates ``construct`` so occupancy can see motion. QA
sometimes needs the pixels at *one* instant — a collision midpoint, a cue, a
play end — without a movie and without the 50–80 auto stills. This module is
the request: which times, which plays, whether to abort after the last hit.

Nothing here imports Manim. The capture helper and the CLI both use it.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


def parse_floats(text: str) -> list[float]:
    """Parse a comma- or space-separated list of times.

    Args:
        text: Raw env/CLI string such as ``"93.6,367.8"``.

    Returns:
        Sorted unique times in seconds. Empty input yields an empty list.
    """
    if not text or not text.strip():
        return []
    parts = [p for chunk in text.split(",") for p in chunk.split()]
    times = [float(p) for p in parts if p]
    return sorted(set(times))


def parse_ints(text: str) -> list[int]:
    """Parse a comma- or space-separated list of play indices.

    Args:
        text: Raw env/CLI string such as ``"40,45"``.

    Returns:
        Sorted unique non-negative indices. Empty input yields an empty list.
    """
    if not text or not text.strip():
        return []
    parts = [p for chunk in text.split(",") for p in chunk.split()]
    return sorted({int(p) for p in parts if p})


def times_from_plays(
    plays: Sequence[Mapping[str, Any]],
    indices: Sequence[int],
    *,
    at: str = "end",
) -> list[float]:
    """Map play indices to scene times using a timeline play list.

    Args:
        plays: ``timeline.json`` ``plays`` records, in Manim ``num_plays`` order.
        indices: Play indices to resolve.
        at: ``"end"`` (motion at its extreme), ``"start"``, or ``"mid"``.

    Returns:
        Scene times in seconds, one per valid index.

    Raises:
        IndexError: If an index is outside the play list.
        ValueError: If ``at`` is not one of the allowed values.
    """
    out: list[float] = []
    for idx in indices:
        if idx < 0 or idx >= len(plays):
            raise IndexError(f"play {idx} is outside 0..{len(plays) - 1}")
        start = float(plays[idx].get("start") or 0.0)
        end = float(plays[idx].get("end") or start)
        if at == "end":
            out.append(end)
        elif at == "start":
            out.append(start)
        elif at == "mid":
            out.append(0.5 * (start + end))
        else:
            raise ValueError(f"at must be start, mid, or end, not {at!r}")
    return out


def times_from_violations(
    payload: Mapping[str, Any],
    *,
    min_duration: float = 1.0,
) -> list[float]:
    """Collision midpoints from a layout-violations report.

    Args:
        payload: Parsed ``layout_violations.json``.
        min_duration: Ignore shorter overlaps (morph crossings).

    Returns:
        Sorted unique midpoint times in seconds.
    """
    out: list[float] = []
    for viol in payload.get("violations") or []:
        if float(viol.get("duration") or 0.0) < min_duration:
            continue
        if "midpoint" in viol:
            out.append(float(viol["midpoint"]))
            continue
        start = float(viol.get("start") or 0.0)
        end = float(viol.get("end") or start)
        out.append(0.5 * (start + end))
    return sorted(set(out))


def times_from_cues(
    timeline: Mapping[str, Any],
    names: Sequence[str],
) -> list[float]:
    """Resolve cue / bookmark names to scene times.

    Args:
        timeline: Parsed ``timeline.json``.
        names: Bookmark or cue ids.

    Returns:
        Times in the same order as ``names``.

    Raises:
        KeyError: If a name is in neither bookmarks nor the cue log.
    """
    bookmarks = {
        str(k): float(v) for k, v in (timeline.get("bookmarks") or {}).items()
    }
    cues = {
        str(row.get("cue")): float(row.get("t") or 0.0)
        for row in timeline.get("cues") or []
    }
    out: list[float] = []
    for name in names:
        if name in bookmarks:
            out.append(bookmarks[name])
        elif name in cues:
            out.append(cues[name])
        else:
            known = sorted({*bookmarks, *cues})
            raise KeyError(f"cue {name!r} missing. Have: {known}")
    return out


@dataclass
class StillRequest:
    """Which instants a geometry walk should rasterize, and when to stop.

    Args:
        times: Absolute scene times in seconds.
        plays: Manim play indices to capture at play-end.
        still_only: Skip auto cue/overlap stills and do not rewrite occupancy.
        stop_after: Raise ``EndSceneEarlyException`` once every requested
            instant has been captured, so the rest of ``construct`` is not
            interpolated.
        out_rel: Directory under the demo for the PNGs, relative to demo root.
    """

    times: list[float] = field(default_factory=list)
    plays: list[int] = field(default_factory=list)
    still_only: bool = False
    stop_after: bool = True
    out_rel: str = "out/stills"

    @property
    def active(self) -> bool:
        """Whether this request names any instant.

        Returns:
            True when at least one time or play is requested.
        """
        return bool(self.times or self.plays)

    def due_times(self, now: float, pending: Sequence[float]) -> list[float]:
        """Pending times that have been reached at ``now``.

        Args:
            now: Current scene time in seconds.
            pending: Times not yet captured.

        Returns:
            Those pending times with ``t <= now``, in order.
        """
        return [t for t in pending if now + 1e-4 >= t]

    def next_time(self, now: float, until: float, pending: Sequence[float]) -> float | None:
        """Soonest pending time in ``(now, until]``.

        Used by frozen waits to snap the clock onto a requested instant
        instead of stepping past it in 0.1 s increments.

        Args:
            now: Current scene time.
            until: Exclusive-ish end of the hold (inclusive in practice).
            pending: Times not yet captured.

        Returns:
            The next hit, or ``None`` if the hold contains none.
        """
        hits = [t for t in pending if now < t <= until + 1e-9]
        return min(hits) if hits else None

    def to_env(self) -> dict[str, str]:
        """Serialize into environment variables the capture helper reads.

        Returns:
            Overlay for ``os.environ``.
        """
        return {
            "MANIM_STILL_TIMES": ",".join(f"{t:.4f}" for t in self.times),
            "MANIM_STILL_PLAYS": ",".join(str(i) for i in self.plays),
            "MANIM_STILL_ONLY": "1" if self.still_only else "0",
            "MANIM_STILL_STOP": "1" if self.stop_after else "0",
            "MANIM_STILL_DIR": self.out_rel,
        }

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> StillRequest:
        """Read a request from the process environment.

        Args:
            env: Mapping to read. Defaults to ``os.environ``.

        Returns:
            A request. Missing keys yield an inactive request.
        """
        src = env if env is not None else os.environ
        only = src.get("MANIM_STILL_ONLY", "0") == "1"
        stop = src.get("MANIM_STILL_STOP", "1") != "0"
        out_rel = src.get("MANIM_STILL_DIR") or "out/stills"
        return cls(
            times=parse_floats(src.get("MANIM_STILL_TIMES", "")),
            plays=parse_ints(src.get("MANIM_STILL_PLAYS", "")),
            still_only=only,
            stop_after=stop,
            out_rel=out_rel,
        )
