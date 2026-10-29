#!/usr/bin/env python3
"""Pre-TTS lint for manim-explain script.yaml craft laws.

Checks (warnings by default; --strict → exit 1):
  - A viewer contract defines the starting point, central question, initial
    intuition, recurring anchor, and ending insight
  - Beats carry narrative roles, causal bridges, and ``viewer_knows_after``
    so the outline forms a knowledge ladder rather than a topic list
  - The opening orients and poses an understandable question before formalism
  - Ordinary explainers keep run IDs and exact experimental result dumps out
    of narration and main visuals (``precision_mode: audit`` opts out)
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

NUMBER_WORD = (
    r"zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
    r"twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
    r"hundred|thousand|million"
)
NUMBER_TOKEN_RE = re.compile(rf"\b(?:\d+(?:\.\d+)?|{NUMBER_WORD})\b", re.I)
PRECISE_NUMBER_RE = re.compile(
    rf"\b(?:\d+\.\d+|(?:{NUMBER_WORD})\s+point\s+(?:{NUMBER_WORD}))\b",
    re.I,
)
RUN_ID_RE = re.compile(
    rf"\bP\s*(?:\d+|{NUMBER_WORD})\b|"
    r"\b(?:run|trial|experiment)\s+[A-Z]?\s*\d+\b",
    re.I,
)
RESULT_CONTEXT_RE = re.compile(
    r"\b(reached|scored|measured|achieved|reported|validation|evaluation|"
    r"benchmark|experiment|decibels?|percent(?:age)?|improvement|result)\b",
    re.I,
)
RESULT_TABLE_RE = re.compile(r"\b(table|rows?|scorecards?|benchmark)\b", re.I)
SPELLED_INITIALISM_RE = re.compile(r"\b(?:[A-Z]\s+){1,}[A-Z]\b")

CONTRACT_FIELDS = (
    "starting_point",
    "central_question",
    "initial_intuition",
    "anchor_example",
    "ending_insight",
)
ORIENT_ROLES = {"orient", "orientation", "setup", "hook"}
QUESTION_ROLES = {"question", "mystery", "contradiction"}
RESOLVE_ROLES = {"resolve", "resolution", "settle", "payoff"}

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


def evidence_load_warnings(beat: dict, precision_mode: str = "story") -> list[str]:
    """Flag lab-report detail that obscures an ordinary explanation.

    The check deliberately targets experimental reporting, not small teaching
    examples or integers used to develop a mathematical operation. Exact values
    remain available through ``precision_mode: audit`` when the user explicitly
    asks for a benchmark or report walkthrough.
    """
    if precision_mode.lower() in {"audit", "benchmark", "report", "report_walkthrough"}:
        return []

    bid = str(beat.get("id", "?"))
    say = str(beat.get("say") or "")
    show = str(beat.get("show") or "")
    out: list[str] = []

    if RUN_ID_RE.search(say):
        out.append(
            f"{bid}: narration includes a project/run identifier — keep run IDs "
            "in SOURCE_NOTES.txt and describe the experimental condition plainly"
        )

    has_result_number = bool(NUMBER_TOKEN_RE.search(say) and RESULT_CONTEXT_RE.search(say))
    if has_result_number:
        out.append(
            f"{bid}: narration reads out experimental quantities — show the "
            "qualitative relationship or one rounded, interpreted magnitude; "
            "keep exact scores and sample counts in SOURCE_NOTES.txt"
        )

    evidence_named = bool(
        RESULT_CONTEXT_RE.search(say)
        or re.search(r"(?:result|evidence|measurement|benchmark)", bid, re.I)
    )
    if evidence_named and RESULT_TABLE_RE.search(show):
        out.append(
            f"{bid}: main visual is a results table — replace it with the one "
            "comparison, trend, or reversal that advances the central question"
        )
    elif evidence_named and (
        re.search(r"\d", show) or PRECISE_NUMBER_RE.search(show) or RUN_ID_RE.search(show)
    ):
        out.append(
            f"{bid}: main visual foregrounds exact experimental labels or values — "
            "show the interpretable relationship and move the exact data to SOURCE_NOTES.txt"
        )
    return out


def story_structure_warnings(data: dict) -> list[str]:
    """Check that the outline declares and follows a viewer-centered story."""
    out: list[str] = []
    contract = data.get("viewer_contract") or {}
    missing_contract = [field for field in CONTRACT_FIELDS if not contract.get(field)]
    if missing_contract:
        out.append(
            "story: viewer_contract is missing " + ", ".join(missing_contract)
            + " — define the cold-viewer starting point and learning journey before beats"
        )

    beats = data.get("beats") or []
    missing_roles = [str(b.get("id", "?")) for b in beats if not b.get("narrative_role")]
    if missing_roles:
        out.append(
            "story: beats missing narrative_role: " + ", ".join(missing_roles)
            + " — roles expose whether the outline investigates or only lists topics"
        )

    missing_knowledge = [
        str(b.get("id", "?")) for b in beats if not b.get("viewer_knows_after")
    ]
    if missing_knowledge:
        out.append(
            "story: beats missing viewer_knows_after: " + ", ".join(missing_knowledge)
            + " — write the knowledge ladder before narration"
        )

    missing_bridges = [
        str(b.get("id", "?")) for b in beats[1:] if not b.get("bridge")
    ]
    if missing_bridges:
        out.append(
            "story: beats missing causal bridge: " + ", ".join(missing_bridges)
            + " — justify each transition with because, but, or therefore"
        )

    roles = [str(b.get("narrative_role", "")).lower() for b in beats]
    orient_at = next((i for i, role in enumerate(roles) if role in ORIENT_ROLES), None)
    question_at = next((i for i, role in enumerate(roles) if role in QUESTION_ROLES), None)
    if roles and orient_at is None:
        out.append("story: no beat orients a cold viewer")
    if roles and question_at is None:
        out.append("story: no beat establishes the central question")
    if orient_at is not None and question_at is not None and question_at <= orient_at:
        out.append("story: central question arrives before the viewer is oriented")
    formal_at = next(
        (i for i, role in enumerate(roles) if role in {"formalize", "definition", "evidence"}),
        None,
    )
    if question_at is not None and formal_at is not None and formal_at < question_at:
        out.append("story: formalism or evidence arrives before the central question")
    if roles and roles[-1] and roles[-1] not in RESOLVE_ROLES:
        out.append("story: final beat does not return to and resolve the opening question")

    for beat in beats[:2]:
        bid = str(beat.get("id", "?"))
        say = str(beat.get("say") or "")
        initialisms = SPELLED_INITIALISM_RE.findall(say)
        if initialisms or RUN_ID_RE.search(say):
            out.append(
                f"{bid}: opening uses an acronym or project identifier before "
                "orientation — rewrite the problem in ordinary language first"
            )

    evidence_flags = [
        bool(
            RESULT_CONTEXT_RE.search(str(b.get("say") or ""))
            or re.search(r"(?:result|evidence|measurement|benchmark)", str(b.get("id", "")), re.I)
        )
        for b in beats
    ]
    if any(a and b for a, b in zip(evidence_flags, evidence_flags[1:])):
        out.append(
            "story: consecutive evidence/result beats read as a lab report — keep "
            "only the comparison needed to choose between the competing explanations"
        )
    return out


def lint(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text())
    beats = data.get("beats") or []
    warnings: list[str] = story_structure_warnings(data)
    precision_mode = str(data.get("precision_mode") or "story")

    for beat in beats:
        bid = beat.get("id", "?")
        say = beat.get("say") or ""
        show = beat.get("show") or ""
        latex = beat.get("latex")
        pause = beat.get("pause_after")
        bookmarks = beat.get("bookmarks") or []

        warnings.extend(evidence_load_warnings(beat, precision_mode))

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

    warnings.extend(_check_global_first_occurrence(beats))
    return warnings


def _check_global_first_occurrence(beats: list) -> list[str]:
    """Flag cues that are not the first spoken occurrence of their word.

    Cues are matched forward-only against one transcript of the *whole*
    narration, so a cue on a word that was already spoken three beats earlier
    resolves to that earlier moment and fires the animation at the wrong time —
    or, if the earlier moment has already passed, fires it instantly. The
    per-beat order check cannot see this, because within its own beat the cue
    looks perfectly well placed.

    This is the single most common authoring error in a long script, and it is
    invisible until the render walks to a cue that already happened.

    Args:
        beats: The parsed ``beats`` list from the script.

    Returns:
        One warning per cue that is not a global first occurrence.
    """
    out: list[str] = []
    spoken: list[tuple[str, str]] = []   # (word, beat id) in narration order
    for b in beats:
        bid = b.get("id", "?")
        for w in _words(b.get("say") or ""):
            spoken.append((w, bid))

    first_beat: dict[str, str] = {}
    for w, bid in spoken:
        first_beat.setdefault(w, bid)

    for b in beats:
        bid = b.get("id", "?")
        for bm in (b.get("bookmarks") or []):
            token = str(bm).split("#")[0].lower()
            owner = first_beat.get(token)
            if owner is not None and owner != bid:
                out.append(
                    f"{bid}: cue {str(bm)!r} is not its first occurrence — "
                    f"{token!r} is already spoken in beat {owner!r}, so the cue "
                    "will resolve there and fire at the wrong time. Choose a "
                    "word unique to this beat."
                )
    return out


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
