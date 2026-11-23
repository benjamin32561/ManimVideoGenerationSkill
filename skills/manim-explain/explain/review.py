"""What the rendered video shows: motion against the narration, and frames for the review.

The render check decodes the finished video at a small size and compares every frame of an
event's window with the frame just before it. From that it checks each event against its
anchor: the picture must start changing within the style's sync window, and not before the
words. It then picks
the frames a reviewer must look at (the settled frame after every event, and the middle of
every long hold) and tiles them into captioned contact sheets.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from explain.media import extract_frame, small_gray_frames
from explain.plan import Timeline
from explain.problems import Problem
from explain.styles import Style

PROBE_SIZE = (384, 216)
PIXEL_LEVEL = 12
MIN_CHANGED_PIXELS = 2
LONG_HOLD_S = 4.0
SHEET_COLUMNS = 3
SHEET_ROWS = 3
THUMB_WIDTH = 640


@dataclass(frozen=True)
class Shot:
    """A frame to review.

    Attributes:
        t: Its time (s).
        name: File stem, e.g. ``e07_flow`` or ``hold_052.3``.
        caption: What the voice says there.
        event: Position of the event it shows (or holds after) in the timeline.
    """

    t: float
    name: str
    caption: str
    event: int

    @property
    def file(self) -> str:
        """The PNG's file name: time, then name."""
        return f"{self.t:07.2f}_{self.name}.png"


def changed(a: np.ndarray, b: np.ndarray) -> bool:
    """Whether two small grey frames differ visibly.

    A pixel counts when it differs by more than ``PIXEL_LEVEL`` grey levels (above encoder
    noise); the frames differ when at least ``MIN_CHANGED_PIXELS`` pixels count.

    Args:
        a: A frame.
        b: Another frame of the same size.

    Returns:
        True when the difference is visible.
    """
    return int((np.abs(a.astype(np.int16) - b.astype(np.int16)) > PIXEL_LEVEL).sum()) >= MIN_CHANGED_PIXELS


def runs(indices: list[int]) -> list[list[int]]:
    """Split sorted indices into runs of consecutive ones.

    Args:
        indices: Sorted, distinct indices.

    Returns:
        The runs, in order (``[1, 2, 5]`` → ``[[1, 2], [5]]``).
    """
    out: list[list[int]] = []
    for i in indices:
        if out and out[-1][-1] == i - 1:
            out[-1].append(i)
        else:
            out.append([i])
    return out


def measure_events(video: Path, timeline: Timeline, fps: int, only: set[int]) -> dict[int, dict]:
    """When some events' pictures start changing and when they settle.

    Every frame of an event's window (its anchor's first word to the next event's) is
    compared with the frame just before the window, not with its neighbour, so slow eased
    entrances register as soon as they have visibly changed anything. The event has settled
    once the picture stops differing from the window's last frame. Only the frames of the
    requested events' windows (and the frame before each run of them) are decoded.

    Args:
        video: The rendered video.
        timeline: The resolved events.
        fps: Frame rate.
        only: Positions in ``timeline.events`` to measure.

    Returns:
        Position → row: ``event``, ``anchor_s``, ``first_change_s`` and ``settled_s`` (both
        None when nothing visibly changed).
    """
    starts = [e.start for e in timeline.events] + [timeline.duration]
    windows = [(int(a * fps), int(b * fps)) for a, b in pairwise(starts)]
    rows: dict[int, dict] = {}
    for run in runs(sorted(only)):
        first = max(windows[run[0]][0] - 1, 0)
        frames = small_gray_frames(video, *PROBE_SIZE, first, windows[run[-1]][1] - first, fps)
        rows.update(measure_run(enumerate(frames, start=first), run, windows, timeline, fps))
    return rows


def measure_run(frames: Iterator[tuple[int, np.ndarray]], run: list[int], windows: list[tuple[int, int]],
                timeline: Timeline, fps: int) -> dict[int, dict]:
    """Measure a run of consecutive event windows from their decoded frames.

    Args:
        frames: ``(frame index, small grey frame)`` from the frame before the run to its end.
        run: Consecutive positions in ``timeline.events``.
        windows: ``(first frame, stop frame)`` of every event's window.
        timeline: The resolved events.
        fps: Frame rate.

    Returns:
        Position → row (see ``measure_events``).
    """
    rows: dict[int, dict] = {}
    buffer: list[np.ndarray] = []
    reference = previous = None

    def close(index: int) -> None:
        """Summarize one event's window from the buffered frames, then empty the buffer.

        The first change is the first buffered frame that differs from the frame just before the
        window; the event has settled after the last frame that differs from the window's final
        frame.

        Args:
            index: The event's position in ``timeline.events`` (and ``windows``).
        """
        event, (lo, _) = timeline.events[index], windows[index]
        moved = [i for i, f in enumerate(buffer) if reference is not None and changed(f, reference)]
        final = buffer[-1] if buffer else None
        unsettled = [i for i, f in enumerate(buffer) if changed(f, final)]
        rows[index] = {"event": event.id, "anchor_s": event.start,
                       "first_change_s": round((lo + moved[0]) / fps, 3) if moved else None,
                       "settled_s": round((lo + (unsettled[-1] + 1 if unsettled else 0)) / fps, 3) if moved else None}
        buffer.clear()

    w = 0
    for k, frame in frames:
        while w < len(run) and k >= windows[run[w]][1]:
            close(run[w])
            w += 1
        if w < len(run) and k == windows[run[w]][0]:
            reference = previous if previous is not None else frame
        if w < len(run) and k >= windows[run[w]][0]:
            buffer.append(frame)
        previous = frame
    while w < len(run):
        close(run[w])
        w += 1
    return rows


def sync_problems(rows: list[dict], timeline: Timeline, style: Style) -> list[Problem]:
    """Check that each event's picture starts changing on its phrase.

    Args:
        rows: ``measure_events`` rows.
        timeline: The resolved events.
        style: The series' style (sync window, start offset, frame rate).

    Returns:
        ``out_of_sync`` errors for changes outside the window, ``no_visible_change`` warnings
        for events whose change could not be measured.
    """
    frame = 1 / style.canvas.fps
    early, late = style.motion.sync_window
    starts = [e.start for e in timeline.events[1:]] + [timeline.duration]
    problems = []
    for row, event, next_start in zip(rows, timeline.events, starts, strict=True):
        if row["first_change_s"] is None:
            problems.append(Problem("no_visible_change", "warning", event.id, detail=f"anchor {event.anchor!r}",
                                    intervals=[[event.start, next_start]]))
            continue
        offset = row["first_change_s"] - event.start
        if offset < early - frame or offset > late + style.motion.start_offset + frame:
            problems.append(Problem("out_of_sync", "error", event.id,
                                    detail=f"first change {offset:+.2f} s from its words; style allows {early}-{late} s",
                                    intervals=[[event.start, row["first_change_s"]]]))
    return problems


def review_shots(rows: list[dict], timeline: Timeline) -> list[Shot]:
    """The frames a reviewer must see: each event once settled, and the middle of long holds.

    Args:
        rows: ``measure_events`` rows (settled time per event).
        timeline: The resolved events.

    Returns:
        Shots in time order, captioned with the event's anchor phrase. An event whose change
        was too subtle to measure is shot at the end of its window.
    """
    shots = []
    starts = [e.start for e in timeline.events[1:]] + [timeline.duration]
    ends = [r["settled_s"] or next_start for r, next_start in zip(rows, starts, strict=True)]
    for i, (event, settled, next_start) in enumerate(zip(timeline.events, ends, starts, strict=True)):
        t = min(settled + 0.1, next_start - 0.05)
        shots.append(Shot(round(t, 2), event.id, f'"{event.anchor}"', i))
        if next_start - settled > LONG_HOLD_S:
            mid = (settled + next_start) / 2
            shots.append(Shot(round(mid, 2), f"hold_{mid:05.1f}", f"(hold after {event.id})", i))
    return shots


def capture(video: Path, shots: list[Shot], out_dir: Path, unchanged: set[int]) -> tuple[list[Path], list[bool]]:
    """Save every shot as a full-size PNG, keeping the ones of unchanged events.

    PNGs that no shot names any more are deleted (sheets are rebuilt by ``contact_sheets``).

    Args:
        video: The rendered video.
        shots: The frames to take.
        out_dir: Where the PNGs go.
        unchanged: Positions of events whose frames are the same as at the last check; their
            existing PNGs are kept.

    Returns:
        The PNG paths in shot order, and for each whether it was taken now.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = {shot.file for shot in shots}
    for old in out_dir.glob("*.png"):
        if old.name not in wanted:
            old.unlink()
    paths, fresh = [], []
    for shot in shots:
        path = out_dir / shot.file
        taken = shot.event not in unchanged or not path.is_file()
        if taken:
            extract_frame(video, shot.t, path)
        paths.append(path)
        fresh.append(taken)
    return paths, fresh


def contact_sheets(frames: list[Path], shots: list[Shot], out_dir: Path, font_file: Path) -> list[Path]:
    """Tile the review frames into captioned sheets of 3 × 3.

    Args:
        frames: Full-size PNGs.
        shots: Their shots (time, name, caption).
        out_dir: Where the sheets go.
        font_file: A TrueType/OpenType font for the captions.

    Returns:
        The sheet paths.
    """
    font = ImageFont.truetype(str(font_file), 22)
    per_sheet = SHEET_COLUMNS * SHEET_ROWS
    sheets = []
    for start in range(0, len(frames), per_sheet):
        batch = list(zip(frames, shots, strict=True))[start:start + per_sheet]
        thumbs = []
        for path, shot in batch:
            image = Image.open(path).convert("RGB")
            image.thumbnail((THUMB_WIDTH, THUMB_WIDTH))
            caption_h = 56
            tile = Image.new("RGB", (image.width, image.height + caption_h), "black")
            tile.paste(image, (0, 0))
            draw = ImageDraw.Draw(tile)
            draw.text((8, image.height + 4), f"{shot.t:.2f}s {shot.name}", fill="white", font=font)
            draw.text((8, image.height + 28), shot.caption[:70], fill="#bbbbbb", font=font)
            thumbs.append(tile)
        w, h = thumbs[0].size
        sheet = Image.new("RGB", (w * SHEET_COLUMNS, h * ((len(thumbs) - 1) // SHEET_COLUMNS + 1)), "#202020")
        for i, tile in enumerate(thumbs):
            sheet.paste(tile, ((i % SHEET_COLUMNS) * w, (i // SHEET_COLUMNS) * h))
        path = out_dir / f"sheet_{start // per_sheet + 1:02d}.png"
        sheet.save(path)
        sheets.append(path)
    return sheets
