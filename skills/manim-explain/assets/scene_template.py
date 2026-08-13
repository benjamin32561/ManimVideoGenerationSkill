"""Timed Manim scene template — copy into demos/<slug>/scenes/.

Craft laws (every video): morph don't respawn; picture matches spoken noun;
question moves referent (ask_about); procedures staged; soft idle; LayoutBoard.
See the skill's references/craft-laws.md

Expects demos/<slug>/timing.json from align_words.py.
Visual-only iteration: keep timing.json + narration.mp3; edit this file; re-render -qm.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from manim import *

DEMO_DIR = Path(__file__).resolve().parents[1]


def _skill_scripts() -> Path:
    """Find the manim-explain skill's ``scripts/`` directory.

    Honors ``MANIM_EXPLAIN_ROOT`` (exported by the skill's ``scripts/env.sh``),
    then searches the project and ``$HOME`` for an installed skill.

    Returns:
        Absolute path to the skill's ``scripts`` directory.

    Raises:
        FileNotFoundError: If the skill cannot be located.
    """
    env_root = os.environ.get("MANIM_EXPLAIN_ROOT")
    if env_root and (Path(env_root) / "scripts" / "layout_check.py").is_file():
        return Path(env_root) / "scripts"
    here = Path(__file__).resolve()
    for base in [*here.parents, Path.home()]:
        for rel in ("skills", ".claude/skills", ".cursor/skills", ".agents/skills"):
            candidate = base / rel / "manim-explain" / "scripts"
            if (candidate / "layout_check.py").is_file():
                return candidate
    raise FileNotFoundError(
        "Cannot locate the manim-explain skill. Set MANIM_EXPLAIN_ROOT or source "
        "the skill's scripts/env.sh."
    )


# Skill helpers + this demo's utils/
sys.path.insert(0, str(_skill_scripts()))
sys.path.insert(0, str(DEMO_DIR))

from layout_watch import watch_layout  # noqa: E402
from timing_helpers import TimedNarration  # noqa: E402
from utils.style import (  # noqa: E402
    C,
    LayoutBoard,
    ask_about,
    bottom_note,
    breathe_until,
    section_title,
    soft_idle,
)


class ExplainerScene(Scene):
    def construct(self) -> None:
        demo_dir = DEMO_DIR
        tn = TimedNarration(demo_dir / "timing.json", demo_dir / "audio" / "narration.mp3")
        tn.attach(self)
        # Records every text collision that happens *during* motion, and flushes
        # out/layout_violations.json when tn.wait_until_end() runs.
        watch_layout(self, demo_dir)
        board = LayoutBoard()

        title = board.set_title(section_title("Title"))
        self.play(FadeIn(title))
        tn.wait_until("Watch")  # bookmark from script.yaml — must exist in timing.json

        # Example: when VO asks about X, move X while asking
        # q = ask_about(self, "What happens to X?", some_mobject, board=board)
        note = board.set_bottom(bottom_note("Short caption", color=C["highlight"]))
        self.play(FadeIn(note, shift=UP * 0.15))
        soft_idle(self, note, run_time=0.6)
        # At tts_chunk boundaries only (matches inter_chunk_silence in audio):
        # tn.suspense(0.35)
        board.assert_clear()

        tn.wait_until_end()
