"""Record the frame review and deliver the video.

    review.py record demos/<series>/<slug> --notes "what you checked and fixed"
    review.py deliver demos/<series>/<slug>

``record`` is the reviewer's signature: run it only after reading every contact sheet in
``out/review/`` (and the full frames for anything unclear) and judging each frame twice: is
anything clipped, covered or left over, and does the picture say what the voice says at that
moment? It needs a passing, current ``check_render.py`` report, and ties the review to the
exact video file.

``deliver`` copies ``out/video.mp4`` to ``<project>/output_videos/<series>/<slug>.mp4``, and
only if the recorded review matches the current plan and that exact video.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import json
import shutil
from datetime import UTC, datetime

from explain.paths import Video
from explain.plan import plan_digest
from explain.report import digest_files, require_passed
from explain.styles import load_style


def record(video: Video, digest: str, notes: str) -> None:
    """Record a frame review of the current render.

    Args:
        video: The video.
        digest: The current plan digest.
        notes: What the reviewer checked and found.

    Raises:
        SystemExit: If the render check is missing, failed or stale, or the notes are empty.
    """
    report = require_passed(video.render_report, digest, "check_render.py")
    if not notes.strip():
        raise SystemExit("Write what you checked in --notes.")
    video.review_record.write_text(json.dumps({
        "digest": digest,
        "video": digest_files(video.rendered),
        "frames_reviewed": len(report["frames"]),
        "notes": notes.strip(),
        "recorded_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }, indent=1) + "\n")
    print(f"review recorded for {video.series}/{video.slug} ({len(report['frames'])} frames)")


def deliver(video: Video, digest: str) -> None:
    """Copy the reviewed video to the project's delivery folder.

    Args:
        video: The video.
        digest: The current plan digest.

    Raises:
        SystemExit: If there is no review, or it was made for another plan or another video.
    """
    if not video.review_record.is_file():
        raise SystemExit("No review recorded; look at out/review/ and run review.py record.")
    review = json.loads(video.review_record.read_text())
    if review["digest"] != digest or review["video"] != digest_files(video.rendered):
        raise SystemExit("The plan or the video changed after the review; check and review again.")
    video.delivery.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(video.rendered, video.delivery)
    print(f"delivered {video.delivery}")


def main() -> None:
    """Dispatch ``record`` or ``deliver``."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("record", "deliver"))
    parser.add_argument("video", help="demos/<series>/<slug>")
    parser.add_argument("--notes", default="", help="record: what was checked and fixed")
    args = parser.parse_args()
    video = Video.at(args.video)
    digest = plan_digest(video, load_style(video.style_name))
    if args.command == "record":
        record(video, digest, args.notes)
    else:
        deliver(video, digest)


if __name__ == "__main__":
    main()
