#!/usr/bin/env python3
"""Report figures that are built, put on stage, and never taken off.

The single most damaging defect class in a long explainer is a figure that
outlives its section. It rides the rest of the video, drifts over whatever comes
next, and often points at nothing — and no audit catches it, because nothing
*collides* in a way a text-vs-text check can see and every frame it appears in
looks locally plausible. Three of them shipped into review in one series: an
arrow that rode 130 s pointing at empty space, and a bus-order strip plus two
snoop blocks that a later verdict chip landed on top of.

This is a static, deliberately over-eager reader. It lists every local bound to
a mobject-producing call whose name never reaches a disposal, then subtracts the
ones swept up in a ``VGroup`` that *is* disposed. Group sweeps it cannot follow
and mobjects reassigned through a transform will show up as false positives, so
the output is a review list, not a verdict: for each name, look at where it is
built and ask what section boundary should have removed it.

Usage::

    python find_leftovers.py demos/<slug>/scenes/<file>.py
    python find_leftovers.py demos/*/scenes/*.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# calls that put a new drawable on the stage
BUILDERS = re.compile(
    r"^\s*(\w+)\s*=\s*(?:cpu\.)?("
    r"Arrow|CurvedArrow|DoubleArrow|Line|DashedLine|Rectangle|RoundedRectangle"
    r"|SurroundingRectangle|Square|Circle|Dot|Brace|BraceLabel|Text|MarkupText"
    r"|Tex|MathTex|VGroup|Polygon|Arc|ArcBetweenPoints|Axes|NumberLine"
    r"|block|chip|instr|note|tile|event_chip|readout|reg_file|mem_column"
    r"|bitfield|program|lane|fifo|meter|core_tile|thread_card|key_line"
    r"|panel_label|safe_text|bottom_note|cost_bar|hbar|lamp|leg|strike"
    r")\("
)

# a name reaching any of these is considered disposed of
DISPOSERS = re.compile(
    r"(?:FadeOut|Uncreate|ShrinkToCenter|Unwrite|remove|ReplacementTransform"
    r"|TransformMatchingShapes|FadeTransform|_kill)\s*\(([^)]*)"
)


def _construct_body(lines: list[str]) -> tuple[int, int]:
    """Find the line range of the scene's ``construct`` method.

    Locals inside module-level helper builders are not stage figures, so
    scanning the whole file buries the real suspects in noise.

    Args:
        lines: The file's lines.

    Returns:
        ``(start, end)`` as 0-based indices, or ``(0, len(lines))`` if the
        method cannot be located.
    """
    start = None
    for i, line in enumerate(lines):
        if re.match(r"\s+def construct\(", line):
            start = i + 1
            break
    if start is None:
        return 0, len(lines)
    indent = len(lines[start]) - len(lines[start].lstrip()) if start < len(lines) else 8
    for j in range(start, len(lines)):
        stripped = lines[j].strip()
        if stripped and (len(lines[j]) - len(lines[j].lstrip())) < indent \
                and not stripped.startswith("#"):
            return start, j
    return start, len(lines)


def analyse(path: Path) -> list[tuple[str, int]]:
    """Find names built in ``construct`` that never reach a disposal.

    Args:
        path: Path to a scene ``.py`` file.

    Returns:
        A list of ``(name, line_number)`` for each suspect, in line order.
    """
    lines = path.read_text().split("\n")
    lo, hi = _construct_body(lines)
    body = "\n".join(lines[lo:hi])

    built: dict[str, int] = {}
    for i in range(lo, hi):
        m = BUILDERS.match(lines[i])
        if m and m.group(1) not in built:
            built[m.group(1)] = i + 1

    gone: set[str] = set()
    for m in DISPOSERS.finditer(body):
        gone.update(re.findall(r"\w+", m.group(1)))

    # A transform's *target* replaces something already on stage, so it is
    # consumed rather than left over; the source of a ReplacementTransform is
    # removed by the transform itself.
    for m in re.finditer(r"(?:Replacement)?Transform(?:MatchingShapes)?\s*\(([^)]*)\)", body):
        args = [a.strip() for a in m.group(1).split(",")]
        for a in args:
            name = re.findall(r"\w+", a)
            if name:
                gone.add(name[0])
    for m in re.finditer(r"\.become\(([^)]*)", body):
        gone.update(re.findall(r"\w+", m.group(1)))

    # a name added to a VGroup that is itself disposed is disposed too
    for _ in range(3):                      # groups of groups
        for m in re.finditer(r"(\w+)\s*=\s*VGroup\(([^)]*)\)", body):
            if m.group(1) in gone:
                gone |= set(re.findall(r"\w+", m.group(2)))
        for m in re.finditer(r"(\w+)\.add\(([^)]*)\)", body):
            if m.group(1) in gone:
                gone |= set(re.findall(r"\w+", m.group(2)))

    return sorted(((n, ln) for n, ln in built.items() if n not in gone),
                  key=lambda t: t[1])


def main() -> int:
    """Report suspects for every scene file named on the command line.

    Returns:
        0 always — this is an advisory reader, not a gate.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scenes", nargs="+", type=Path)
    args = ap.parse_args()

    for path in args.scenes:
        if not path.is_file():
            print(f"{path}: not a file", file=sys.stderr)
            continue
        suspects = analyse(path)
        print(f"\n{path}  —  {len(suspects)} never reach a disposal")
        for name, line in suspects:
            print(f"  {path.name}:{line:<5} {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
