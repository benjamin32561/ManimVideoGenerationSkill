"""Manim helpers: drive visuals from timing.json bookmark times."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

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

    def attach(self, scene: Scene) -> None:
        self.scene = scene
        if not self._audio_added:
            # Manim CE: add_sound path relative to cwd or absolute
            scene.add_sound(str(self.audio_path))
            self._audio_added = True

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
        remaining = target - float(self.scene.time)
        if remaining > 1e-3:
            self.scene.wait(remaining)

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
