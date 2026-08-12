#!/usr/bin/env python3
"""Pre-TTS lint for manim-explain script.yaml craft laws.

Checks (warnings by default; --strict → exit 1):
  - Question beats need pause_after ≥ 0.9
  - Beats with latex / formula show need BUILD_UP or MORPH in show
  - After-name / after-morph pause hints when pause_after is very short
  - Bookmarks appear in say (case-insensitive word match)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

QUESTION_RE = re.compile(
    r"\?\s*$|\b(how|what|which|why|do they|would you)\b.*\?",
    re.I | re.M,
)
BUILD_RE = re.compile(r"\b(BUILD_UP|MORPH|TransformMatchingTex|staged|STAGED)\b", re.I)
MATH_HINT_RE = re.compile(
    r"\b(formula|MathTex|equation|HSIC|CKA|kernel|Gram|\\\\mathrm|\\\\frac)\b",
    re.I,
)


def _words(text: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[A-Za-z0-9']+", text or "")}


def lint(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text())
    beats = data.get("beats") or []
    warnings: list[str] = []

    for beat in beats:
        bid = beat.get("id", "?")
        say = beat.get("say") or ""
        show = beat.get("show") or ""
        latex = beat.get("latex")
        pause = beat.get("pause_after")
        bookmarks = beat.get("bookmarks") or []

        # Questions need a long baked pause
        if QUESTION_RE.search(say):
            if pause is None or float(pause) < 0.9:
                warnings.append(
                    f"{bid}: question-like beat needs pause_after ≥ 0.9 "
                    f"(got {pause!r}) — craft law: thinking beat after questions"
                )

        # Formula / latex beats need staged morph language in show
        has_math = bool(latex) or bool(MATH_HINT_RE.search(str(show)))
        if has_math and latex and not BUILD_RE.search(str(show)):
            warnings.append(
                f"{bid}: latex set but show: lacks BUILD_UP/MORPH/STAGED — "
                "math progress must morph, not flash the final equation"
            )

        # Very short pauses after naming / morph-heavy shows
        if pause is not None and float(pause) < 0.45:
            if BUILD_RE.search(str(show)) or "POP" in str(show).upper():
                warnings.append(
                    f"{bid}: pause_after={pause} is short for a morph/POP beat "
                    "(prefer ≥ 0.7 after heavy motion)"
                )

        # Bookmarks should appear in say
        say_words = _words(say)
        for bm in bookmarks:
            token = str(bm).split("#")[0]
            if token.lower() not in say_words:
                warnings.append(
                    f"{bid}: bookmark {bm!r} not found as a word in say "
                    "(Whisper alignment will fail)"
                )

    return warnings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path)
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any warnings")
    args = parser.parse_args()

    path = args.script.resolve()
    if not path.is_file():
        raise SystemExit(f"Missing script: {path}")

    warnings = lint(path)
    if not warnings:
        print(f"OK: {path} ({0} warnings)")
        return

    print(f"{len(warnings)} warning(s) in {path}:")
    for w in warnings:
        print(f"  - {w}")
    if args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
