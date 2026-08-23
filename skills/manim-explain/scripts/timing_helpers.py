"""Manim helpers: drive visuals from timing.json bookmark times.

Beyond waiting for cues, this records a **timeline** of what actually moved and
when. A cue whose window contains no animation is a beat where the narration
described something and the picture sat still — the single most common way these
videos go wrong, and impossible to see by reading 1000 lines of scene code.
The timeline lands in ``out/timeline.json``; ``check_sync.py`` turns it into a
verdict and ``qa_frames.py`` uses it to sample motion, not just cue times.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Union

from manim import Scene


class TimedNarration:
    """Attach narration audio and wait for absolute bookmark times."""

    def __init__(self, timing_path: Union[str, Path], audio_path: Union[str, Path, None] = None):
        self.timing_path = Path(timing_path)
        self.data = json.loads(self.timing_path.read_text())
        self.bookmarks: dict[str, float] = {
            str(k): float(v) for k, v in (self.data.get("bookmarks") or {}).items()
        }
        self.duration = float(self.data.get("duration") or 0.0)
        if audio_path is None:
            rel = self.data.get("audio") or "audio/narration.mp3"
            audio_path = self.timing_path.parent / rel
        self.audio_path = Path(audio_path)
        self.scene: Scene | None = None
        self._audio_added = False
        # instrumentation
        self.plays: list[dict[str, Any]] = []
        self.cue_log: list[dict[str, Any]] = []
        self._orig_play = None

    def attach(self, scene: Scene) -> None:
        """Add narration audio and start recording the motion timeline.

        Wraps ``scene.play`` so every animation's start and end time is logged.
        The wrapper is transparent: arguments and return value pass through.

        Args:
            scene: The scene about to be constructed.
        """
        self.scene = scene
        if not self._audio_added:
            from manim import config

            # Geometry-only walks still call attach(); converting the narration
            # mp3 to wav on every inner-loop pass was pure waste.
            if not getattr(config, "geometry_only", False):
                scene.add_sound(str(self.audio_path))
            self._audio_added = True
        if self._orig_play is None:
            self._orig_play = scene.play

            def _logged_play(*args: Any, **kwargs: Any) -> Any:
                start = float(scene.time)
                result = self._orig_play(*args, **kwargs)
                # Manim implements Scene.wait as play(Wait(...)); a wait is the
                # opposite of motion, so it must never count as one.
                kinds = [type(a).__name__ for a in args]
                is_wait = bool(kinds) and all(k == "Wait" for k in kinds)
                self.plays.append(
                    {
                        "start": round(start, 3),
                        "end": round(float(scene.time), 3),
                        "kind": "wait" if is_wait else "anim",
                        "anims": kinds[:6],
                    }
                )
                if not is_wait:
                    capture = getattr(scene, "_geometry_capture", None)
                    if capture is not None:
                        capture.capture("play-end")
                return result

            scene.play = _logged_play  # type: ignore[method-assign]

    def time_of(self, bookmark: str) -> float:
        if bookmark not in self.bookmarks:
            # allow bookmark#2 style already stored; also try base name
            raise KeyError(
                f"Bookmark {bookmark!r} missing. Have: {sorted(self.bookmarks)}"
            )
        return self.bookmarks[bookmark]

    def wait_until(self, bookmark: str, *, pad: float = 0.0) -> None:
        """Wait until scene clock reaches bookmark time (+ optional pad)."""
        if self.scene is None:
            raise RuntimeError("Call attach(scene) first")
        target = self.time_of(bookmark) + pad
        self.cue_log.append({"cue": bookmark, "t": round(target, 3)})
        remaining = target - float(self.scene.time)
        if remaining > 1e-3:
            self.scene.wait(remaining)
        capture = getattr(self.scene, "_geometry_capture", None)
        if capture is not None:
            capture.capture(f"cue:{bookmark}")

    def suspense(self, seconds: float = 0.3) -> None:
        """Thinking gap between beats.

        Only safe when the audio already contains matching silence (see
        ``tts.inter_chunk_silence``). Otherwise the picture lags the VO.
        """
        if self.scene is None:
            raise RuntimeError("Call attach(scene) first")
        if seconds > 1e-3:
            self.scene.wait(seconds)

    def play_until(self, bookmark: str, *animations, min_run: float = 0.2, **play_kwargs):
        """Play animations with run_time capped to land at/before the next bookmark."""
        if self.scene is None:
            raise RuntimeError("Call attach(scene) first")
        target = self.time_of(bookmark)
        remaining = target - float(self.scene.time)
        run = max(min_run, remaining)
        self.scene.play(*animations, run_time=run, **play_kwargs)

    def play_before(
        self,
        bookmark: str,
        *animations,
        settle: float = 0.35,
        min_run: float = 0.25,
        max_run: float | None = None,
        **play_kwargs,
    ):
        """Play so the motion *lands* before ``bookmark``, leaving ``settle`` free.

        Craft law: do not spill a morph into the next spoken idea. Prefer this over
        bare ``play`` when the next bookmark names a new concept.
        """
        if self.scene is None:
            raise RuntimeError("Call attach(scene) first")
        remaining = self.span_until(bookmark)
        run = max(min_run, remaining - float(settle))
        if max_run is not None:
            run = min(run, float(max_run))
        if animations:
            self.scene.play(*animations, run_time=run, **play_kwargs)
        # Natural wait_until(bookmark) later consumes the settle gap

    def span_until(self, bookmark: str) -> float:
        """Seconds from now until bookmark (clamped ≥0)."""
        if self.scene is None:
            raise RuntimeError("Call attach(scene) first")
        return max(0.0, self.time_of(bookmark) - float(self.scene.time))

    def wait_until_end(self, *, pad: float = 0.3) -> None:
        if self.scene is None:
            raise RuntimeError("Call attach(scene) first")
        target = max(self.duration, max(self.bookmarks.values(), default=0.0)) + pad
        remaining = target - float(self.scene.time)
        if remaining > 1e-3:
            self.scene.wait(remaining)
        self.write_timeline()

    def write_timeline(self) -> Path | None:
        """Write the motion timeline, and flush any attached layout watcher.

        Returns:
            Path to ``out/timeline.json``, or None when no demo directory can be
            inferred from the timing file location.
        """
        demo_dir = self.timing_path.parent
        if os.environ.get("MANIM_STILL_ONLY") == "1":
            capture = getattr(self.scene, "_geometry_capture", None)
            if capture is not None:
                capture.flush()
            return None
        out_dir = demo_dir / "out"
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            return None
        payload = {
            "duration": self.duration,
            "cues": sorted(self.cue_log, key=lambda c: c["t"]),
            "plays": self.plays,
            "bookmarks": self.bookmarks,
        }
        path = out_dir / "timeline.json"
        path.write_text(json.dumps(payload, indent=2) + "\n")
        watcher = getattr(self.scene, "_layout_watcher", None)
        if watcher is not None:
            watcher.flush()
        return path
