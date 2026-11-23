"""The scene that plays a video's events against its narration.

The scene is the whole video: every object of the layout plan, every event at its time.
It is never rendered in one piece. Each beat's clip is a frame range of the same film: the
renderer runs the scene in several processes, and each process draws and encodes only its
own frames (``BeatRecorder``); frames outside the range are counted, not drawn, which costs
almost nothing. So beats render in parallel without any catch-up code, and the clips join
frame-exactly.
"""

import subprocess
from pathlib import Path
from typing import Protocol

import manimgx as m
from manimgx.mobject import flow
from manimgx.rendering.film import Cut, Frame

from explain.actions import Director
from explain.media import open_encoder
from explain.objects import Builder
from explain.paths import Video
from explain.plan import Timeline, code_digest, load_layout
from explain.styles import Style
from explain.windows import EDGE_FRAMES, Ledger


def configure(style: Style) -> None:
    """Set manimgx's global frame size, rate and background from the style.

    Args:
        style: The series' style pack.
    """
    m.config.pixel_width = style.canvas.width
    m.config.pixel_height = style.canvas.height
    m.config.frame_rate = style.canvas.fps
    m.config.background_color = style.canvas.background


@flow
def compute_every_frame(dt: float) -> None:
    """A scene updater that does nothing; its presence makes manimgx compute every frame.

    manimgx plays a play made only of tweens natively, from its start and end states, and the
    Python objects show the start state until the play ends. Any scene updater turns that
    off, so a geometry probe reads each frame's true state. A flow runs once per frame, not on
    the simulation clock.

    Args:
        dt: Seconds since the last frame (unused).
    """


class WindowObserver(Protocol):
    """Something that follows a scene window by window (the geometry probe)."""

    def begin_window(self, window: dict) -> bool:
        """Note that a window opens, and say whether to compute its every frame.

        Args:
            window: ``{"event", "start", "digest"}`` of the window opening now.

        Returns:
            True to compute every frame of the window in Python.
        """


class VideoScene(m.Scene):
    """Every object of the layout plan, every event at its resolved time.

    Each event starts ``motion.start_offset`` after its anchor's first word; between events
    the frame holds still. Each event opens a window (``explain.windows``); ``windows`` lists
    them with their digests, the blank canvas before the first event first.

    Args:
        video: The video.
        style: Its style pack.
    """

    def __init__(self, video: Video, style: Style) -> None:
        """Load the plan and prepare the builder; objects are built in ``construct``.

        Args:
            video: The video.
            style: Its style pack.
        """
        super().__init__()
        self.video = video
        self.style = style
        self.layout = load_layout(video.layout)
        self.timeline = Timeline.load(video.events)
        self.builder = Builder(style, self.layout, video.custom)
        self.registry: dict[str, m.Mobject] = {}
        self.director: Director | None = None
        self.current_event = ""
        self.windows: list[dict] = []
        self.observer: WindowObserver | None = None
        self.computing = False

    def construct(self) -> None:
        """Build every object, then play each event at its time and hold between events."""
        self.registry = self.builder.build_all()
        self.director = Director(self, self.style, self.layout, self.builder, self.registry)
        ledger = Ledger(self.layout, code_digest(self.video, self.style))
        offset = self.style.motion.start_offset
        events = self.timeline.events
        starts = [e.start + offset for e in events] + [self.timeline.duration]
        self.open_window("blank", ledger.blank(starts[0]))
        for event, t0, next_start in zip(events, starts[:-1], starts[1:], strict=True):
            self.hold_until(t0)
            self.open_window(event.id, ledger.window(event, float(self.time), next_start - t0))
            self.current_event = event.id
            self.play(*self.director.event(event, next_start - t0))
            self.director.after_event()
        self.hold_until(self.timeline.duration)

    def open_window(self, name: str, digest: str) -> None:
        """Record a window opening now, and compute its every frame if the observer asks.

        Args:
            name: The event's id (``blank`` before the first event).
            digest: The window's digest.
        """
        window = {"event": name, "start": round(float(self.time), 6), "digest": digest}
        self.windows.append(window)
        every = self.observer.begin_window(window) if self.observer else False
        if every != self.computing:
            (self.add_updater if every else self.remove_updater)(compute_every_frame)
            self.computing = every

    def hold_until(self, t: float) -> None:
        """Hold the frame still until scene time ``t``.

        Args:
            t: Target time (s); nothing happens if the scene is already there.
        """
        dt = t - self.time
        if dt > 1e-6:
            self.wait(dt, frozen_frame=True)


class BeatRecorder:
    """A frame sink that encodes frames ``[first, stop)`` of the film and cuts the film there.

    manimgx sends a held frame once with a repeat count; the recorder writes it as many
    times as it falls inside the range, so the clip has exactly ``stop - first`` frames at a
    constant rate. If the film ends early (its closing frame lands before ``stop``), the
    last frame is held to fill the range. The film is cut a little after ``stop``, once every
    window the beat's digest counts (``explain.windows.beat_digest``) has opened.

    Args:
        first: First frame index of the beat.
        stop: One past its last frame index.
        path: The clip to write.
        style: The series' style (frame size and rate).
    """

    def __init__(self, first: int, stop: int, path: Path, style: Style) -> None:
        """Start the encoder for the beat's clip.

        Args:
            first: First frame index of the beat.
            stop: One past its last frame index.
            path: The clip to write.
            style: The series' style (frame size and rate).
        """
        self.first = first
        self.stop = stop
        self.written = 0
        self.last: bytes | None = None
        self.encoder: subprocess.Popen = open_encoder(path, style.canvas.width, style.canvas.height,
                                                      style.canvas.fps)

    def __call__(self, frame: Frame) -> None:
        """Encode the part of one film frame that falls inside the beat.

        Args:
            frame: The frame manimgx sends (index, repeat, lazy pixels).

        Raises:
            Cut: Once the film is ``EDGE_FRAMES`` past the beat, to end it there.
        """
        lo, hi = frame.index, frame.index + frame.repeat
        if lo > self.stop + EDGE_FRAMES:
            raise Cut()
        if hi <= self.first or lo >= self.stop:
            return
        count = min(hi, self.stop) - max(lo, self.first)
        self.last = frame.pixels()
        self.encoder.stdin.write(self.last * count)
        self.written += count

    def close(self) -> int:
        """Pad a short film with its last frame, finish encoding, and check the frame count.

        Returns:
            How many frames were padded at the end (0 unless the film ended early).

        Raises:
            RuntimeError: If no frame was written, the encoder failed, or the clip would need
                more than one padded frame (the scene ended well before the narration).
        """
        missing = self.stop - self.first - self.written
        if self.last is None or missing > 1:
            self.encoder.kill()
            raise RuntimeError(f"Beat frames [{self.first}, {self.stop}) got only {self.written} frames")
        if missing:
            self.encoder.stdin.write(self.last * missing)
        self.encoder.stdin.close()
        if self.encoder.wait() != 0:
            raise RuntimeError(f"ffmpeg failed: {self.encoder.stderr.read().decode()[-800:]}")
        return missing
