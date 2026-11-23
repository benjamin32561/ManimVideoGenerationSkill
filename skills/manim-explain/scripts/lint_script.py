"""Lint a script against the narrative grammar and the style: ``lint_script.py demos/<series>/<slug>``.

Checks the chain of units under one central question (rules N1–N15 of
``docs/research/narrative-pattern.md``), the narration rules (no LaTeX, no narrated
dialogue, exact numbers per style) and the style's speaker profile. Before the narration is
voiced, beat times are estimated from word counts; once ``audio/words.json`` exists, real
times are used and pace and pauses are measured too.

Writes ``out/lint.json`` and exits 1 on errors. ``voice.py`` refuses to run without a
passing lint of the current script.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse

from explain.narrative import lint
from explain.paths import Video
from explain.plan import script_digest
from explain.report import print_problems, write_report
from explain.script import load_script
from explain.styles import load_style
from explain.timing import Transcript


def main() -> None:
    """Lint the script and write the report.

    Raises:
        SystemExit: 1 when the script has errors.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", help="demos/<series>/<slug>")
    args = parser.parse_args()
    video = Video.at(args.video)
    style = load_style(video.style_name)
    script = load_script(video.script)
    transcript = Transcript.load(video.words) if video.words.is_file() else None
    problems, summary = lint(script, style, transcript)
    write_report(video.lint_report, script_digest(video, style), problems, **summary)
    timing = "voiced" if summary["voiced"] else "estimated"
    print_problems(f"lint {video.series}/{video.slug} ({summary['seconds']:.0f} s {timing}, "
                   f"{summary['beats']} beats)", problems)
    print("  profile: " + ", ".join(f"{k} {v}" for k, v in summary["profile"].items()))
    if any(p.severity == "error" for p in problems):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
