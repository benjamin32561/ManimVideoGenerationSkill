"""Check a rendered video and prepare its frame review: ``check_render.py demos/<series>/<slug>``.

Refuses to run unless ``out/video.mp4`` was rendered from the current plan. Then:

1. Checks the video's frame count against the narration.
2. Measures frame-to-frame change and checks every event against its words: the picture must
   start changing within the style's sync window (never before the words).
3. Saves the frames to review in ``out/review/`` (each event once settled, the middle of every
   long hold) and tiles them into captioned contact sheets (``out/review/sheet_NN.png``).

An event whose window and the window before it are unchanged since the last check
(``explain.windows``) keeps its measurement and its review frames; only the others are
decoded and captured. The summary names the sheets with new frames.

Writes ``out/render_check.json`` and exits 1 on errors. Then look at the sheets (all of them
the first time, the ones with new frames after a fix), and at the full frames for anything you
are unsure of, and record the review with ``review.py record``.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import json

from explain.media import frame_count
from explain.paths import Video
from explain.plan import Timeline, plan_digest
from explain.problems import Problem
from explain.report import print_problems, write_report
from explain.review import (
    SHEET_COLUMNS,
    SHEET_ROWS,
    capture,
    contact_sheets,
    measure_events,
    review_shots,
    sync_problems,
)
from explain.styles import load_style
from explain.windows import fold


def main() -> None:
    """Check the render and write the review frames.

    Raises:
        SystemExit: If the video is missing or stale; 1 when the check finds errors.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", help="demos/<series>/<slug>")
    args = parser.parse_args()
    video = Video.at(args.video)
    style = load_style(video.style_name)
    digest = plan_digest(video, style)
    rendered = video.out / "render.json"
    if not rendered.is_file() or json.loads(rendered.read_text())["digest"] != digest:
        raise SystemExit("out/video.mp4 is missing or was rendered from an older plan; run render.py.")
    timeline = Timeline.load(video.events)
    fps = style.canvas.fps
    problems: list[Problem] = []
    expected, frames = round(timeline.duration * fps), frame_count(video.rendered)
    if frames != expected:
        problems.append(Problem("frame_count", "error", "video", detail=f"{frames} frames, narration needs {expected}"))
    windows = json.loads(video.plan_report.read_text())["windows"]
    keys = [fold(before["digest"], window["digest"], event.id, event.anchor)
            for before, window, event in zip(windows[:-1], windows[1:], timeline.events, strict=True)]
    earlier = json.loads(video.render_report.read_text()) if video.render_report.is_file() else {"keys": [], "sync": []}
    known = dict(zip(earlier["keys"], earlier["sync"], strict=True))
    unchanged = {i for i, key in enumerate(keys) if key in known}
    measured = measure_events(video.rendered, timeline, fps, set(range(len(keys))) - unchanged)
    rows = [known[key] if i in unchanged else measured[i] for i, key in enumerate(keys)]
    problems += sync_problems(rows, timeline, style)
    shots = review_shots(rows, timeline)
    pngs, fresh = capture(video.rendered, shots, video.review_dir, unchanged)
    font = style.text.families["default"][1]
    font_file = next(p for p in sorted(font.glob("*")) if p.suffix.lower() in (".otf", ".ttf"))
    sheets = contact_sheets(pngs, shots, video.review_dir, font_file)
    per_sheet = SHEET_COLUMNS * SHEET_ROWS
    new_sheets = sorted({sheets[i // per_sheet].name for i, taken in enumerate(fresh) if taken})
    write_report(video.render_report, digest, problems, sync=rows, keys=keys, frames=[p.name for p in pngs],
                 sheets=[s.name for s in sheets], new_sheets=new_sheets)
    print_problems(f"check_render {video.series}/{video.slug}", problems)
    print(f"  measured {len(keys) - len(unchanged)} of {len(keys)} events; review: {len(pngs)} frames, "
          f"{len(sheets)} sheets in {video.review_dir}")
    print(f"  sheets with new frames: {', '.join(new_sheets) or 'none'}")
    if any(p.severity == "error" for p in problems):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
