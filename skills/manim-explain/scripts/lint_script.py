#!/usr/bin/env python3
"""Pre-TTS lint for manim-explain script.yaml craft laws.

Checks (warnings by default; --strict → exit 1):
  - Question beats need pause_after ≥ 0.9
  - Beats with latex / formula show need BUILD_UP or MORPH in show
  - After-name / after-morph pause hints when pause_after is very short
  - Bookmarks appear in say (case-insensitive word match)
  - **Visual coverage**: every change-word the narration speaks (a verb like
    "grow", "spread", "cancel", or a state word like "peaky", "frozen",
    "identical") must appear in that beat's ``show:``. This is the cheapest
    place to catch the commonest defect in these videos — the VO describing
    something happening to an object while the frame holds still.
  - Each ``show:`` names at least one animation, not just a static arrangement.
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

# Words that promise the viewer something changes on screen. Spoken in `say`,
# each one is a contract: the matching motion must be described in `show:` (and
# then animated). Kept as stems so inflections match: "grow/grows/growing".
MOTION_STEMS = (
    "grow", "shrink", "rise", "ris", "fall", "climb", "drop", "slide", "shift",
    "spread", "crowd", "split", "merge", "fuse", "flip", "rotat", "cut", "strike",
    "cancel", "collaps", "expand", "stretch", "squeez", "fill", "empt", "sort",
    "rank", "stack", "scatter", "gather", "cross", "land", "peel", "hug", "turn",
    "swing", "sweep", "dim", "brighten", "freez", "frozen", "morph", "snap",
    "break", "shatter", "vanish", "appear", "pop", "pulse", "tilt", "slid",
    "widen", "narrow", "lift", "sink", "bend", "curve", "jump", "tick", "count",
    "divid", "multipl", "add", "subtract", "distribut", "arrang", "chop", "slice",
)
STATE_STEMS = (
    "taller", "shorter", "bigger", "smaller", "larger", "wider", "narrower",
    "steeper", "flatter", "brighter", "dimmer", "denser", "sparser", "finer",
    "coarser", "higher", "lower", "peak", "flat", "uniform", "piled", "crowded",
    "frozen", "identical", "equal", "louder", "quieter", "fine", "coarse",
    "continuous", "discret", "infinite", "finite", "empty", "full",
)
# Words that describe motion in `show:`; a beat with none is a static tableau.
SHOW_MOTION_RE = re.compile(
    r"\b(STAGED|MORPH|BUILD_UP|POP|grow|shrink|slide|fade|pulse|sweep|cascade|"
    r"animate|move|land|appear|light|flash|indicate|transform|rise|fall|spread|"
    r"crowd|collapse|shift|turn|draw|write|snap|strike|cancel|flip|stack|sort|"
    r"ask_about|soft.?idle|idle|tracer|shimmer|breathe|cycle|tick|swing|grow)\b",
    re.I,
)
# Spoken words that are about the argument, not the picture
VISUAL_EXEMPT = {"count", "add", "subtract", "curve", "turn", "fall"}

# Arithmetic the on-screen formula performs; satisfied by a formula-stage note
MATH_OP_STEMS = {"divid", "multipl"}
MATH_OP_EVIDENCE = ("mathtex", "build_up", "formula", "equation", "fraction", "morph", "×")

# A show: note satisfies a spoken stem if it names the stem *or* any of these.
# Without this the check fires on wording differences ("chop" vs "sliced") and
# an author learns to ignore it — which is worse than not checking at all.
SYNONYMS: dict[str, tuple[str, ...]] = {
    "chop": ("slice", "sliced", "cut", "divide", "element"),
    "slice": ("chop", "cut", "element"),
    "spread": ("distribute", "scatter", "fan", "apart", "widen", "crowd"),
    "distribut": ("distribution", "skyline", "histogram", "bars", "shape", "curve", "spectrum"),
    "collaps": ("fuse", "merge", "shrink", "fold", "reduce", "closed form"),
    "climb": ("rise", "grow", "ascend", "up", "extend"),
    "ris": ("rise", "grow", "climb", "extend", "up"),
    "grow": ("rise", "climb", "extend", "expand", "larger"),
    "shrink": ("smaller", "collapse", "reduce", "scale", "shrink"),
    "sort": ("rank", "order", "descending", "sorted"),
    "rank": ("sort", "order", "descending", "ranking"),
    "peak": ("peak", "peaky", "peakier", "hump", "maximum"),
    "infinite": ("endless", "ellipsis", "forever", "unbounded", "off the top", "· · ·", "..."),
    "identical": ("same", "equal", "match", "identical", "overlap"),
    "equal": ("same", "identical", "uniform", "flat"),
    "louder": ("gain", "scale", "amplify", "multiply", "taller"),
    "multipl": ("×", "times", "product", "multiply"),
    "frozen": ("freeze", "dim", "dark", "suppress", "fade"),
    "freez": ("frozen", "dim", "dark", "suppress"),
    "jump": ("jumps", "counter", "tick", "step"),
    "fine": ("crowd", "dense", "close together", "fine"),
    "continuous": ("slider", "dial", "smooth", "continuum", "crowd", "fine"),
    "land": ("onto", "hug", "settle", "arrive", "overlap", "lands"),
    "finite": ("finitely", "prefix", "bounded", "short", "element", "step", "rung"),
    "discret": ("ladder", "rung", "step", "lump", "element"),
    "cancel": ("strike", "cross out", "cancel"),
    "empt": ("empty", "clear", "vacate"),
    "flat": ("uniform", "level", "equal heights"),
    "vanish": ("fade", "disappear", "remove", "vanish"),
    "appear": ("fade in", "land", "arrive", "appear", "grow"),
    "arrang": ("arrangement", "distribute", "layout"),
    # comparatives: the motion that produces them counts as covering them
    "taller": ("grow", "rise", "height", "larger", "up", "climb"),
    "shorter": ("shrink", "smaller", "down", "fall", "height"),
    "bigger": ("grow", "expand", "scale", "larger"),
    "larger": ("grow", "expand", "scale", "bigger"),
    "smaller": ("shrink", "reduce", "scale", "shrink"),
    "wider": ("widen", "expand", "spread", "apart"),
    "narrower": ("narrow", "squeeze", "closer"),
    "higher": ("rise", "up", "above", "climb", "grow"),
    "lower": ("fall", "down", "below", "drop", "shrink"),
    "brighter": ("brighten", "light", "glow", "highlight"),
    "dimmer": ("dim", "fade", "darken"),
    "denser": ("crowd", "close together", "pack"),
    "sparser": ("spread", "apart", "thin"),
    "finer": ("crowd", "fine", "close together"),
    "coarser": ("spread", "coarse", "apart", "large"),
    "steeper": ("steep", "slope", "rise"),
    "flatter": ("flat", "level", "uniform"),
}


def _stem_present(stem: str, text: str) -> bool:
    """Whether a stem occurs as a word prefix in text.

    Args:
        stem: Lowercase stem, e.g. ``"collaps"``.
        text: Haystack, any case.

    Returns:
        True when some word in ``text`` starts with ``stem``.
    """
    return re.search(rf"\b{re.escape(stem)}", text, re.I) is not None


def visual_coverage(say: str, show: str) -> list[str]:
    """Change-words the narration promises that the show notes never mention.

    Args:
        say: The spoken line for this beat.
        show: The beat's staging notes.

    Returns:
        The stems found in ``say`` but absent from ``show``, in script order.
    """
    missing: list[str] = []
    for stem in (*MOTION_STEMS, *STATE_STEMS):
        if stem in VISUAL_EXEMPT:
            continue
        if not _stem_present(stem, say):
            continue
        covered = _stem_present(stem, show) or any(
            alt.lower() in show.lower() for alt in SYNONYMS.get(stem, ())
        )
        if not covered and stem in MATH_OP_STEMS:
            covered = any(ev in show.lower() for ev in MATH_OP_EVIDENCE)
        if not covered:
            word = re.search(rf"\b{re.escape(stem)}\w*", say, re.I)
            missing.append(word.group(0).lower() if word else stem)
    seen: set[str] = set()
    return [w for w in missing if not (w in seen or seen.add(w))]


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

        # Spoken change-words must have a matching motion in show:
        uncovered = visual_coverage(say, str(show))
        if uncovered:
            warnings.append(
                f"{bid}: VO says {', '.join(repr(w) for w in uncovered[:6])} but show: "
                "describes no matching motion — craft law: never narrate a change "
                "the picture does not make"
            )
        if show and not SHOW_MOTION_RE.search(str(show)):
            warnings.append(
                f"{bid}: show: names no animation (STAGED / MORPH / POP / grow / …) — "
                "a beat that only arranges objects will read as a frozen frame"
            )

        # Cues are matched forward-only, so a cue listed before an earlier-spoken
        # one can never be found — the alignment silently drops it.
        positions = []
        for bm in bookmarks:
            token = str(bm).split("#")[0].lower()
            hit = re.search(rf"\b{re.escape(token)}\b", say or "", re.I)
            positions.append((str(bm), hit.start() if hit else None))
        placed = [(b, i) for b, i in positions if i is not None]
        for (b1, i1), (b2, i2) in zip(placed, placed[1:]):
            if i2 < i1:
                warnings.append(
                    f"{bid}: bookmarks out of spoken order — {b2!r} is said before "
                    f"{b1!r}; cues are matched forward-only, so {b2!r} will be dropped"
                )
                break

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
