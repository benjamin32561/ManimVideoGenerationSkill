"""Capture sparse Cairo stills during a geometry-only walk of ``construct``.

The movie pipeline is skipped in geometry-only mode. Vision still needs pixels,
but only at the moments occupancy cannot speak for: a cue landing, the opening
and close of a lasting overlap, a section-scale fade, and a *few* play ends
where motion is at its extreme. A ten-minute video is ~18k frames at 30 fps;
this policy aims for on the order of 50–80 stills, not one per play.

Collision *midpoints* are not known until an interval closes, and a one-pass
walk cannot rewind. The close still is the one-pass stand-in.

The destination directory is cleared on construction so a previous pass cannot
leave stills the current code no longer produces.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from still_request import StillRequest


def slug_reason(reason: str) -> str:
    """Turn a capture reason into a filename fragment.

    Args:
        reason: Free-form tag such as ``cue:ready`` or ``overlap``.

    Returns:
        A short filesystem-safe string. Empty input becomes ``still``.
    """
    text = re.sub(r"[^A-Za-z0-9._:-]+", "_", reason).strip("._-")
    text = text[:48]
    return text or "still"


@dataclass
class CapturePolicy:
    """Decide whether a geometry-walk event is worth one Cairo still.

    Overlaps always win — those are the defects. Cues are next. Play-ends are
    capped so a 600-play scene does not rasterize 600 times.

    Args:
        max_stills: Hard cap on PNGs written in one walk.
        max_play_ends: Cap on ``play-end`` stills specifically.
        overlap_gap: Minimum seconds between overlap stills.
        play_end_gap: Minimum seconds since *any* still before a play-end.
        cue_gap: Minimum seconds between cue / section stills.
    """

    max_stills: int = 72
    max_play_ends: int = 16
    overlap_gap: float = 1.0
    play_end_gap: float = 2.5
    cue_gap: float = 0.15

    def allow(
        self,
        reason: str,
        now: float,
        *,
        n_stills: int,
        n_play_ends: int,
        last_t: float,
        last_overlap_t: float,
    ) -> bool:
        """Whether this event should rasterize.

        Args:
            reason: Tag such as ``overlap``, ``overlap-end``, ``cue:x``,
                ``section``, ``play-end``.
            now: Scene time in seconds.
            n_stills: Stills already written.
            n_play_ends: Play-end stills already written.
            last_t: Time of the last still of any kind, or -1.
            last_overlap_t: Time of the last overlap still, or -1.

        Returns:
            True when Cairo should run.
        """
        is_overlap = reason.startswith("overlap")
        if n_stills >= self.max_stills and not is_overlap:
            return False
        if is_overlap:
            if last_overlap_t < 0.0:
                return True
            return (now - last_overlap_t) >= self.overlap_gap
        if last_t < 0.0:
            return True
        dt = now - last_t
        if reason.startswith("cue") or reason.startswith("section"):
            return dt >= self.cue_gap
        if reason == "play-end":
            if n_play_ends >= self.max_play_ends:
                return False
            return dt >= self.play_end_gap
        return dt >= self.cue_gap


class GeometryCapture:
    """Write numbered PNG stills and a manifest into ``out/keyframes/``.

    A :class:`StillRequest` switches the helper into named-time mode: only the
    requested instants are rasterized, they land in ``out/stills/`` so a
    previous geometry-pass contact sheet is not wiped, and ``tick`` can ask
    the renderer to abort ``construct`` after the last hit.
    """

    def __init__(
        self,
        scene: Any,
        demo_dir: Path,
        policy: CapturePolicy | None = None,
        request: StillRequest | None = None,
    ) -> None:
        """Bind to a scene and empty the destination directory.

        Args:
            scene: The running Manim scene. Its renderer must expose
                ``capture_still``.
            demo_dir: Demo directory; stills land under ``out/``.
            policy: Capture budget for the auto geometry pass.
            request: Named times/plays. ``None`` reads the environment; an
                inactive request keeps the auto keyframe behaviour.
        """
        self.scene = scene
        self.demo_dir = Path(demo_dir)
        self.policy = policy or CapturePolicy()
        self.request = request if request is not None else StillRequest.from_env()
        if self.request.still_only or self.request.active:
            self.out_dir = self.demo_dir / self.request.out_rel
        else:
            self.out_dir = self.demo_dir / "out" / "keyframes"
        if self.out_dir.exists() and os.environ.get("MANIM_STILL_KEEP") != "1":
            shutil.rmtree(self.out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.manifest: list[dict[str, Any]] = []
        self._last_t = -1.0
        self._last_overlap_t = -1.0
        self._play_ends = 0
        self._pending_times = list(self.request.times)
        self._pending_plays = set(self.request.plays)

    def play_needs_ticks(self, now: float, duration: float, play_index: int) -> bool:
        """Whether this play must be interpolated frame-by-frame.

        Stills-only walks may jump a play to its final state when no requested
        instant falls inside it. Occupancy walks always tick.

        Args:
            now: Scene time at the start of the play.
            duration: Play duration in seconds.
            play_index: Manim ``num_plays`` for this play.

        Returns:
            True when the play must run ``play_internal``.
        """
        if not self.request.still_only:
            return True
        del play_index
        until = now + float(duration)
        return any(now < t <= until + 1e-9 for t in self._pending_times)
        """Soonest still-requested time inside a hold.

        Args:
            now: Current scene time in seconds.
            until: End of the hold.

        Returns:
            The next requested time, or ``None``.
        """
        return self.request.next_time(now, until, self._pending_times)

    def done(self) -> bool:
        """Whether every requested instant has been captured.

        Returns:
            True when no times or plays remain. Auto-pass captures never
            report done this way (they have nothing pending).
        """
        if not self.request.active:
            return False
        return not self._pending_times and not self._pending_plays

    def should_stop(self) -> bool:
        """Whether the renderer should abort the rest of ``construct``.

        Returns:
            True only in stills-only mode after the last requested still.
        """
        return bool(self.request.stop_after and self.request.still_only and self.done())

    def tick(self, now: float) -> bool:
        """Capture any requested time that has just been reached.

        Called from the geometry-only renderer on every clock advance.

        Args:
            now: Scene time after the increment, in seconds.

        Returns:
            True when the renderer should raise ``EndSceneEarlyException``.
        """
        due = self.request.due_times(now, self._pending_times)
        for t in due:
            self._pending_times.remove(t)
            self._write(f"t:{t:.2f}", now=now)
        return self.should_stop()

    def capture(self, reason: str, *, min_gap: float | None = None) -> Path | None:
        """Rasterize the current mobjects once, if the policy allows.

        ``min_gap`` is accepted for callers that used the old API; overlap
        spacing is owned by :class:`CapturePolicy`. In stills-only mode this
        ignores cue/overlap/section events and only honours requested plays.

        Args:
            reason: Short tag stored in the manifest and filename.
            min_gap: Ignored; kept so existing call sites do not break.

        Returns:
            The PNG path, or ``None`` when the capture was skipped.
        """
        del min_gap
        if self.request.still_only:
            if reason != "play-end":
                return None
            renderer = getattr(self.scene, "renderer", None)
            idx = int(getattr(renderer, "num_plays", 0)) - 1
            if idx not in self._pending_plays:
                return None
            self._pending_plays.discard(idx)
            path = self._write(f"play:{idx}")
            if self.should_stop():
                from manim.utils.exceptions import EndSceneEarlyException

                raise EndSceneEarlyException()
            return path
        renderer = getattr(self.scene, "renderer", None)
        still = getattr(renderer, "capture_still", None)
        if not callable(still):
            return None
        now = float(getattr(self.scene, "time", 0.0))
        if not self.policy.allow(
            reason,
            now,
            n_stills=len(self.manifest),
            n_play_ends=self._play_ends,
            last_t=self._last_t,
            last_overlap_t=self._last_overlap_t,
        ):
            return None
        path = self._write(reason, now=now)
        if reason.startswith("overlap"):
            self._last_overlap_t = now
        if reason == "play-end":
            self._play_ends += 1
        return path

    def _write(self, reason: str, *, now: float | None = None) -> Path | None:
        """Rasterize once and append a manifest row.

        Args:
            reason: Filename / manifest tag.
            now: Scene time to record. Defaults to ``scene.time``.

        Returns:
            The PNG path, or ``None`` when the renderer has no ``capture_still``.
        """
        renderer = getattr(self.scene, "renderer", None)
        still = getattr(renderer, "capture_still", None)
        if not callable(still):
            return None
        if now is None:
            now = float(getattr(self.scene, "time", 0.0))
        dest = self.out_dir / (
            f"{len(self.manifest):03d}_{slug_reason(reason)}_{now:.2f}s.png"
        )
        still(self.scene, dest, reason)
        self._last_t = now
        self.manifest.append(
            {
                "reason": reason,
                "t": round(now, 3),
                "path": str(dest.relative_to(self.demo_dir)),
            }
        )
        return dest

    def missing(self) -> dict[str, list]:
        """Requested instants that were never reached.

        Returns:
            ``{"times": [...], "plays": [...]}`` still pending after the walk.
        """
        return {
            "times": list(self._pending_times),
            "plays": sorted(self._pending_plays),
        }

    def flush(self) -> Path:
        """Write ``manifest.json`` next to the stills.

        Returns:
            Path to the written manifest.
        """
        path = self.out_dir / "manifest.json"
        if self.request.active:
            body = {"stills": list(self.manifest), "missing": self.missing()}
            path.write_text(json.dumps(body, indent=2) + "\n")
        else:
            path.write_text(json.dumps(list(self.manifest), indent=2) + "\n")
        return path
