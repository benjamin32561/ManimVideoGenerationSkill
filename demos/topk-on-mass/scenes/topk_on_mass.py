"""Top-k on-mass explainer — Wrong→Right (fixed cutoff → ranked set → share of mass).

Story lane: layer responses → class means → magnitudes → threshold fails →
ranked top set S_c → mass share → on-mass, read against the uniform baseline f.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
from manim import *

DEMO_DIR = Path(__file__).resolve().parents[1]


def _skill_scripts() -> Path:
    """Find the manim-explain skill's ``scripts/`` directory.

    Honors ``MANIM_EXPLAIN_ROOT`` (exported by the skill's ``scripts/env.sh``),
    then searches the project and ``$HOME`` for an installed skill, so a demo
    keeps working wherever the skill is installed.

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


sys.path.insert(0, str(_skill_scripts()))
sys.path.insert(0, str(DEMO_DIR))

from timing_helpers import TimedNarration  # noqa: E402
from utils.style import (  # noqa: E402
    C,
    EQ_SIZE,
    PANEL_LABEL_Y,
    LayoutBoard,
    ask_about,
    bottom_note,
    key_sentence,
    panel_label,
    pop_named,
    safe_text,
    section_title,
    soft_idle,
)

# ── Toy class-response distribution (one signed class mean per unit) ──────────
# Display order is scrambled on purpose: the ranking step must be a real motion.
VALUES = [
    0.31, -0.22, 0.92, 0.13, 0.40, 0.07, 0.55, 0.17, -0.44, 0.25,
    0.11, 0.61, 0.05, 0.36, -0.78, 0.20, 0.48, 0.09, 0.28, 0.15,
]
F_UNITS = len(VALUES)
ABS = [abs(v) for v in VALUES]
TOTAL_MASS = sum(ABS)
ORDER = sorted(range(F_UNITS), key=lambda i: ABS[i], reverse=True)  # rank → unit
K_TOP = 2  # f = 10% of 20 units
ON_MASS = sum(ABS[i] for i in ORDER[:K_TOP]) / TOTAL_MASS  # ≈ 0.26

CUTOFF = 0.30
GAIN = 1.8  # chosen so exactly five more units cross the cutoff (9 → 14)
N_ABOVE = sum(1 for a in ABS if a > CUTOFF)  # 9
N_ABOVE_GAIN = sum(1 for a in ABS if a * GAIN > CUTOFF)  # 14

# ── Chart geometry (shared reference peak: louder ⇒ taller pixels) ────────────
AXIS_Y = -1.15
BAR_W = 0.34
PITCH = 0.45
VSCALE = 1.35 / max(ABS)  # manim units per unit of |mu| at gain 1
CHART_X = 0.0
CHART_X_SHIFTED = -0.9
COL_X = 5.35
COL_W = 0.85
COL_H = 1.5  # total-mass column height at gain 1
# Below-axis chip strip — one x slot per chip so co-present chips never collide
CHIP_Y = -1.85
COUNTER_X = -4.6
GAIN_X = -1.7
F_X = 1.4
CUT_CHIP_X = 5.5


def bar_heights(gain: float = 1.0, *, uniform: bool = False) -> list[float]:
    """Pixel heights for the bars, indexed by unit.

    Args:
        gain: Loudness multiplier applied to every response.
        uniform: If set, every unit carries the same share of the same total.

    Returns:
        One manim-unit height per unit, in display order.
    """
    if uniform:
        flat = TOTAL_MASS / F_UNITS
        return [flat * VSCALE * gain] * F_UNITS
    return [a * VSCALE * gain for a in ABS]


def make_bars(
    *,
    gain: float = 1.0,
    signed: bool = False,
    uniform: bool = False,
    x_center: float = CHART_X,
    rank_positions: bool = False,
    colors: list | None = None,
    opacities: list[float] | None = None,
) -> VGroup:
    """Build the response-distribution bars, indexed by unit.

    Args:
        gain: Loudness multiplier (shared reference peak — never renormalized).
        signed: Draw negative means below the axis instead of flipped up.
        uniform: Flatten the distribution while keeping the total mass.
        x_center: Chart centre on the x axis.
        rank_positions: Place unit ``j`` at its rank slot instead of its unit slot.
        colors: Per-unit fill/stroke colors (defaults to the structure blue).
        opacities: Per-unit fill opacities.

    Returns:
        A ``VGroup`` of one rectangle per unit, in unit order.
    """
    heights = bar_heights(gain, uniform=uniform)
    slot_of = {unit: rank for rank, unit in enumerate(ORDER)} if rank_positions else None
    bars = VGroup()
    for j in range(F_UNITS):
        h = max(heights[j], 0.03)
        col = (colors or [C["primary"]] * F_UNITS)[j]
        rect = Rectangle(
            width=BAR_W,
            height=h,
            fill_color=col,
            fill_opacity=(opacities or [0.85] * F_UNITS)[j],
            stroke_color=col,
            stroke_width=1.2,
        )
        slot = slot_of[j] if slot_of else j
        x = x_center + (slot - (F_UNITS - 1) / 2) * PITCH
        if signed and VALUES[j] < 0:
            rect.move_to([x, AXIS_Y - h / 2, 0])
        else:
            rect.move_to([x, AXIS_Y + h / 2, 0])
        bars.add(rect)
    return bars


def make_net() -> tuple[VGroup, list[VGroup], VGroup]:
    """Draw the whole network, with the studied layer wide enough to hold F units.

    Returns:
        ``(net, layers, edges)`` — the full group, the per-layer node groups, and
        the edge group (so the net can be dimmed without touching the layer).
    """
    sizes = [5, F_UNITS, 6, 3]
    radii = [0.10, 0.055, 0.10, 0.10]
    buffs = [0.16, 0.035, 0.16, 0.16]
    layers: list[VGroup] = []
    for n, r, b in zip(sizes, radii, buffs):
        layer = VGroup(
            *[
                Circle(
                    radius=r,
                    color=C["dim"],
                    fill_color=C["primary"],
                    fill_opacity=0.18,
                    stroke_width=1.6,
                    stroke_color=WHITE,
                )
                for _ in range(n)
            ]
        ).arrange(DOWN, buff=b)
        layers.append(layer)
    row = VGroup(*layers).arrange(RIGHT, buff=1.15).move_to(DOWN * 0.15 + RIGHT * 0.7)

    edges = VGroup()
    for left, right in zip(layers[:-1], layers[1:]):
        for i, a in enumerate(left):
            mid = int(round(i * (len(right) - 1) / max(len(left) - 1, 1)))
            for j in sorted({mid, max(0, mid - 1), min(len(right) - 1, mid + 1)}):
                edges.add(
                    Line(
                        a.get_right(),
                        right[j].get_left(),
                        stroke_width=1.0,
                        color=GREY_B,
                        stroke_opacity=0.22,
                    )
                )
    return VGroup(edges, row), layers, edges


def mass_column(
    *,
    gain: float = 1.0,
    share: float = ON_MASS,
    x: float = COL_X,
) -> tuple[VGroup, Rectangle, Rectangle]:
    """Total-mass column with the top-set share filled gold at the bottom.

    Args:
        gain: Loudness multiplier — the column grows with the bars.
        share: Fraction of the total mass held by the top set.
        x: Column centre on the x axis.

    Returns:
        ``(group, gold_segment, rest_segment)``.
    """
    total_h = COL_H * gain
    gold_h = max(total_h * share, 0.03)
    gold = Rectangle(
        width=COL_W,
        height=gold_h,
        fill_color=C["gold"],
        fill_opacity=0.9,
        stroke_width=0,
    ).move_to([x, AXIS_Y + gold_h / 2, 0])
    rest = Rectangle(
        width=COL_W,
        height=total_h - gold_h,
        fill_color=C["primary"],
        fill_opacity=0.45,
        stroke_width=0,
    ).move_to([x, AXIS_Y + gold_h + (total_h - gold_h) / 2, 0])
    border = Rectangle(
        width=COL_W,
        height=total_h,
        stroke_color=WHITE,
        stroke_width=1.6,
        fill_opacity=0,
    ).move_to([x, AXIS_Y + total_h / 2, 0])
    return VGroup(gold, rest, border), gold, rest


def chip(text: str, color=C["label"], font_size: int = 20) -> VGroup:
    """Small labelled pill used for counters, quotas and readouts.

    Args:
        text: Chip text.
        color: Stroke / text color.
        font_size: Text size.

    Returns:
        A ``VGroup`` of the rounded frame and its label.
    """
    label = safe_text(text, font_size=font_size, color=color)
    frame = RoundedRectangle(
        width=label.width + 0.34,
        height=label.height + 0.26,
        corner_radius=0.09,
        stroke_color=color,
        stroke_width=1.6,
        fill_color=BLACK,
        fill_opacity=0.55,
    )
    label.move_to(frame)
    return VGroup(frame, label)


def readout(value: float, *, x: float = COL_X, y: float = -1.75) -> VGroup:
    """The on-mass number parked under the mass column.

    Two lines, so the chip stays narrow enough to clear the quota chip that
    shares the below-axis strip.

    Args:
        value: Current on-mass value.
        x: Chip centre on the x axis.
        y: Chip centre on the y axis.

    Returns:
        The chip group, already positioned.
    """
    name = safe_text("on-mass", font_size=18, color=C["label"])
    val = safe_text(f"{value:.2f}", font_size=26, color=C["gold"])
    body = VGroup(name, val).arrange(DOWN, buff=0.08)
    frame = RoundedRectangle(
        width=body.width + 0.38,
        height=body.height + 0.26,
        corner_radius=0.09,
        stroke_color=C["gold"],
        stroke_width=1.6,
        fill_color=BLACK,
        fill_opacity=0.55,
    )
    body.move_to(frame)
    return VGroup(frame, body).move_to([x, y, 0])


def _soft_until(tn: TimedNarration, scene: Scene, bookmark: str, *mobs, max_t: float = 1.0) -> None:
    """Breathe through the baked audio pause until the next cue.

    Args:
        tn: Narration clock.
        scene: Active scene.
        bookmark: Cue to breathe up to.
        mobs: Mobjects to idle.
        max_t: Cap on the idle animation length.
    """
    rem = tn.span_until(bookmark)
    if rem > 0.28 and mobs:
        soft_idle(scene, *mobs, run_time=min(rem * 0.85, max_t))


class TopKOnMass(Scene):
    """Full explainer: hook → threshold trap → ranked set → on-mass → siblings."""

    def construct(self) -> None:  # noqa: PLR0915 - one linear storyboard
        tn = TimedNarration(DEMO_DIR / "timing.json", DEMO_DIR / "audio" / "narration.mp3")
        tn.attach(self)
        board = LayoutBoard()

        # ── 1. HOOK — whole net, then the studied layer ────────────────────
        title = board.set_title(section_title("Top-$k$ on-mass".replace("$k$", "k")))
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.7)
        tn.wait_until("layer")

        net, layers, edges = make_net()
        hidden = layers[1]
        tn.play_before(
            "class",
            LaggedStart(
                *[GrowFromCenter(n) for layer in layers for n in layer],
                lag_ratio=0.012,
            ),
            settle=0.35,
            max_run=1.5,
        )
        self.play(Create(edges), run_time=0.5)
        tn.wait_until("class")

        # Class-c inputs live on the INPUT side (labels follow the story)
        chips = VGroup(
            *[
                RoundedRectangle(
                    width=0.62,
                    height=0.42,
                    corner_radius=0.07,
                    color=C["accent"],
                    fill_opacity=0.25,
                    stroke_width=1.6,
                )
                for _ in range(3)
            ]
        ).arrange(DOWN, buff=0.22)
        chips.move_to([-5.55, -0.15, 0])
        chip_tag = safe_text("class c", font_size=20, color=C["accent"])
        chip_tag.next_to(chips, UP, buff=0.22)
        board.add(chip_tag, "chip_tag")
        feed_arrow = Arrow(
            chips.get_right(),
            layers[0].get_left(),
            buff=0.16,
            color=C["accent"],
            stroke_width=2.4,
            max_tip_length_to_length_ratio=0.18,
        )
        tn.play_before(
            "unit",
            LaggedStart(*[FadeIn(c, shift=RIGHT * 0.15) for c in chips], lag_ratio=0.12),
            FadeIn(chip_tag),
            GrowArrow(feed_arrow),
            settle=0.3,
            max_run=1.0,
        )

        # Causal pair: an example goes in, the layer's units answer
        rng = np.random.default_rng(3)
        for cyc in range(2):
            pattern = np.clip(
                np.array(ABS) / max(ABS) * (0.75 + 0.25 * cyc)
                + rng.normal(scale=0.06, size=F_UNITS),
                0.05,
                0.95,
            )
            travel = chips[cyc].copy()
            self.play(
                travel.animate.move_to(layers[0].get_center()).scale(0.4).set_opacity(0.0),
                *[
                    hidden[j].animate.set_fill(C["primary"], float(pattern[j]))
                    for j in range(F_UNITS)
                ],
                run_time=0.85,
                rate_func=smooth,
            )
            self.remove(travel)
        _soft_until(tn, self, "unit", hidden, max_t=0.8)

        # Container → member: the layer, then one unit inside it
        tn.wait_until("unit")
        focus = SurroundingRectangle(hidden, buff=0.14, color=C["secondary"], stroke_width=2.4)
        self.play(
            FadeIn(focus),
            edges.animate.set_stroke(opacity=0.08),
            VGroup(layers[0], layers[2], layers[3]).animate.set_opacity(0.3),
            run_time=0.6,
        )
        pop_named(self, focus, color=C["accent"], run_time=0.5, settle=0.2)
        pop_named(self, hidden[2], color=C["accent"], run_time=0.5, settle=0.2)
        tn.wait_until("strongly")

        pattern = np.clip(np.array(ABS) / max(ABS), 0.06, 0.95)
        travel = chips[2].copy()
        self.play(
            travel.animate.move_to(layers[0].get_center()).scale(0.4).set_opacity(0.0),
            *[hidden[j].animate.set_fill(C["primary"], float(pattern[j])) for j in range(F_UNITS)],
            run_time=0.9,
            rate_func=smooth,
        )
        self.remove(travel)
        _soft_until(tn, self, "carrying", focus, max_t=0.9)

        # ── 2. QUESTION — who carries the class? ───────────────────────────
        tn.wait_until("carrying")
        self.play(FadeOut(title), run_time=0.25)
        board.clear("title")
        q = ask_about(
            self,
            "who is carrying this class?",
            focus,
            hold=0.08,
            park="left",
            board=board,
            font_size=26,
            motion_time=0.8,
            color=C["highlight"],
        )
        tn.wait_until("handful")
        tall = VGroup(*[hidden[j] for j in ORDER[:3]])
        self.play(Indicate(tall, color=C["gold"], scale_factor=1.5), run_time=0.8)
        tn.wait_until("sharing")
        self.play(Indicate(focus, color=C["secondary"], scale_factor=1.03), run_time=0.8)
        _soft_until(tn, self, "Collapse", focus, q, max_t=1.0)

        # ── 3. CLASS MEANS — layer morphs into the response distribution ───
        tn.wait_until("Collapse")
        self.play(
            FadeOut(q),
            FadeOut(chips),
            FadeOut(chip_tag),
            FadeOut(feed_arrow),
            FadeOut(edges),
            FadeOut(layers[0]),
            FadeOut(layers[2]),
            FadeOut(layers[3]),
            FadeOut(focus),
            run_time=0.45,
        )
        board.clear()

        axis = Line([-5.6, AXIS_Y, 0], [5.6, AXIS_Y, 0], stroke_width=1.4, color=GREY_B)
        bars = make_bars(signed=True)
        tn.play_before(
            "average",
            FadeIn(axis),
            ReplacementTransform(hidden, bars),
            settle=0.4,
            max_run=1.4,
        )
        tn.wait_until("average")

        mu_eq = MathTex(
            r"\mu_{c,j}",
            r"=",
            r"\frac{1}{|\{m:\, y_m=c\}|}\sum_{m:\, y_m=c} a_j(m)",
            font_size=EQ_SIZE - 12,
        )
        board.set_bottom(mu_eq)
        tn.play_before("mean", Write(mu_eq), settle=0.4, max_run=1.4)
        self.play(Indicate(mu_eq[2], color=C["accent"], scale_factor=1.05), run_time=0.7)
        tn.wait_until("mean")

        pick = 6  # a mid-height positive unit
        mu_lab = MathTex(r"\mu_{c,j}", font_size=30, color=C["accent"])
        mu_lab.next_to(bars[pick], UP, buff=0.18)
        self.play(FadeIn(mu_lab, shift=UP * 0.1), run_time=0.4)
        pop_named(self, bars[pick], color=C["accent"], run_time=0.6, settle=0.25)
        _soft_until(tn, self, "distribution", bars, max_t=0.9)

        tn.wait_until("distribution")
        dist_lab = panel_label("class-c response distribution", C["secondary"])
        board.add(dist_lab, "dist_lab")
        self.play(FadeIn(dist_lab, shift=DOWN * 0.1), FadeOut(mu_lab), run_time=0.6)
        pop_named(self, dist_lab, color=C["secondary"], run_time=0.55, settle=0.25)
        board.assert_clear()
        _soft_until(tn, self, "down", bars, max_t=0.9)

        # ── 4. MAGNITUDES — sign carries no information here ───────────────
        tn.wait_until("down")
        neg_idx = [j for j, v in enumerate(VALUES) if v < 0]
        self.play(
            *[bars[j].animate.set_fill(C["wrong"], 0.85).set_stroke(C["wrong"]) for j in neg_idx],
            run_time=0.55,
        )
        tn.wait_until("direction")
        engaged = key_sentence(
            self,
            "direction is not engagement",
            color=C["wrong"],
            font_size=26,
            hold=0.1,
            park="left",
            board=board,
        )
        _soft_until(tn, self, "size", *[bars[j] for j in neg_idx], max_t=1.0)

        tn.wait_until("size")
        abs_eq = MathTex(r"|\mu_{c,j}|", font_size=EQ_SIZE - 4)
        board.set_bottom(abs_eq)
        tn.play_before(
            "flip",
            ReplacementTransform(mu_eq, abs_eq),
            FadeOut(engaged),
            settle=0.35,
            max_run=1.0,
        )
        board.clear("key")
        tn.wait_until("flip")

        flipped = make_bars(signed=False)
        self.play(
            LaggedStart(
                *[Transform(bars[j], flipped[j]) for j in neg_idx],
                lag_ratio=0.25,
            ),
            run_time=1.1,
            rate_func=smooth,
        )
        self.play(
            *[bars[j].animate.set_fill(C["primary"], 0.85).set_stroke(C["primary"]) for j in neg_idx],
            run_time=0.5,
        )
        _soft_until(tn, self, "fixed", bars, max_t=0.9)

        # ── 5. WRONG — a fixed cutoff ──────────────────────────────────────
        tn.wait_until("fixed")
        cut_y = AXIS_Y + CUTOFF * VSCALE
        cut_line = DashedLine(
            [-5.3, cut_y, 0], [4.6, cut_y, 0], color=C["wrong"], stroke_width=2.5, dash_length=0.14
        )
        cut_chip = chip("cutoff 0.30", color=C["wrong"])
        cut_chip.move_to([CUT_CHIP_X, cut_y, 0])  # right of the chart, on the line
        tn.play_before("line", FadeIn(cut_chip, scale=0.9), settle=0.3, max_run=0.7)
        tn.wait_until("line")
        self.play(Create(cut_line), run_time=0.7)

        tn.wait_until("Count")
        above = [j for j in ORDER if ABS[j] > CUTOFF]
        counter = chip(f"on: 0 / {F_UNITS}", color=C["wrong"], font_size=22)
        counter.move_to([COUNTER_X, CHIP_Y, 0])
        board.add(counter, "counter")
        self.play(FadeIn(counter, scale=0.9), run_time=0.4)
        step = min(0.28, max(0.14, tn.span_until("nine") / (len(above) + 1)))
        for n, j in enumerate(above, start=1):
            new_counter = chip(f"on: {n} / {F_UNITS}", color=C["wrong"], font_size=22)
            new_counter.move_to(counter.get_center())
            self.play(
                bars[j].animate.set_fill(C["gold"], 0.9).set_stroke(C["gold"]),
                Transform(counter, new_counter),
                run_time=step,
            )
        tn.wait_until("nine")
        pop_named(self, counter, color=C["wrong"], run_time=0.5, settle=0.2)
        _soft_until(tn, self, "gain", counter, max_t=0.7)

        # ── 6. THE TRAP — louder, same shape, bigger count ─────────────────
        tn.wait_until("gain")
        gain_chip = chip(f"gain x{GAIN}", color=C["highlight"], font_size=22)
        gain_chip.move_to([GAIN_X, CHIP_Y, 0])
        board.add(gain_chip, "gain_chip")
        self.play(FadeIn(gain_chip, scale=0.9), run_time=0.4)

        # Ghost of the quiet skyline proves the shape never changed
        ghost = VGroup(
            *[
                Line(
                    bars[j].get_corner(UL),
                    bars[j].get_corner(UR),
                    stroke_width=2.5,
                    color=WHITE,
                    stroke_opacity=0.75,
                )
                for j in range(F_UNITS)
            ]
        )
        gold_now = [j for j in range(F_UNITS) if ABS[j] > CUTOFF]
        cols = [C["gold"] if j in gold_now else C["primary"] for j in range(F_UNITS)]
        loud = make_bars(gain=GAIN, colors=cols)
        tn.play_before(
            "shape",
            FadeIn(ghost),
            *[Transform(bars[j], loud[j]) for j in range(F_UNITS)],
            settle=0.4,
            max_run=1.5,
        )
        tn.wait_until("shape")
        shape_note = board.set_bottom(bottom_note("same shape, louder", color=GREY_B))
        self.play(ReplacementTransform(abs_eq, shape_note), Indicate(ghost, color=WHITE), run_time=0.8)

        tn.wait_until("cross")
        newly = [j for j in ORDER if ABS[j] * GAIN > CUTOFF and ABS[j] <= CUTOFF]
        self.play(
            LaggedStart(
                *[
                    bars[j].animate.set_fill(C["gold"], 0.9).set_stroke(C["gold"])
                    for j in newly
                ],
                lag_ratio=0.18,
            ),
            run_time=1.0,
        )
        tn.wait_until("jumps")
        jumped = chip(f"on: {N_ABOVE_GAIN} / {F_UNITS}", color=C["wrong"], font_size=22)
        jumped.move_to(counter.get_center())
        self.play(Transform(counter, jumped), Flash(counter, color=C["wrong"]), run_time=0.7)
        tn.wait_until("loudness")

        loud_key = key_sentence(
            self,
            "loudness, not concentration",
            color=C["wrong"],
            font_size=28,
            hold=0.1,
            park="left",
            board=board,
        )
        _soft_until(tn, self, "stop", counter, max_t=0.9)

        # ── 7. RIGHT — rank instead of threshold ───────────────────────────
        tn.wait_until("stop")
        quiet = make_bars(gain=1.0)
        self.play(
            FadeOut(cut_line),
            FadeOut(cut_chip),
            FadeOut(gain_chip),
            FadeOut(ghost),
            FadeOut(shape_note),
            FadeOut(loud_key),
            *[Transform(bars[j], quiet[j]) for j in range(F_UNITS)],
            run_time=0.9,
        )
        board.clear("key", "bottom", "gain_chip")
        reset_counter = chip(f"on: ? / {F_UNITS}", color=C["dim"], font_size=22)
        reset_counter.move_to(counter.get_center())
        self.play(Transform(counter, reset_counter), run_time=0.4)
        tn.wait_until("Rank")

        ranked = make_bars(rank_positions=True)
        tn.play_before(
            "biggest",
            LaggedStart(
                *[Transform(bars[j], ranked[j]) for j in ORDER],
                lag_ratio=0.05,
            ),
            settle=0.35,
            max_run=1.9,
        )
        tn.wait_until("biggest")
        srt = [bars[j] for j in ORDER]  # left → right, tallest first
        pop_named(self, srt[0], color=C["accent"], run_time=0.55, settle=0.2)
        _soft_until(tn, self, "fraction", srt[0], srt[1], max_t=0.8)

        # ── 8. THE TOP SET S_c ─────────────────────────────────────────────
        tn.wait_until("fraction")
        f_chip = chip("f", color=C["highlight"], font_size=22)
        f_chip.move_to([F_X, CHIP_Y, 0])
        board.add(f_chip, "f_chip")
        self.play(FadeIn(f_chip, scale=0.9), run_time=0.35)
        tn.wait_until("percent")
        f_full = chip("f = 10%", color=C["highlight"], font_size=22)
        f_full.move_to(f_chip.get_center())
        self.play(Transform(f_chip, f_full), run_time=0.5)
        tn.wait_until("Keep")

        gold_bars = VGroup(*srt[:K_TOP])
        brace = Brace(gold_bars, direction=UP, buff=0.16, color=C["gold"])
        self.play(GrowFromCenter(brace), run_time=0.5)
        self.play(
            LaggedStart(
                *[b.animate.set_fill(C["gold"], 0.92).set_stroke(C["gold"]) for b in srt[:K_TOP]],
                lag_ratio=0.25,
            ),
            *[b.animate.set_fill(C["primary"], 0.35).set_stroke(opacity=0.5) for b in srt[K_TOP:]],
            run_time=0.9,
        )
        tn.wait_until("strongest")
        pop_named(self, gold_bars, color=C["gold"], run_time=0.6, settle=0.25)
        tn.wait_until("set")

        s_lab = MathTex(r"S_c", font_size=34, color=C["gold"])
        s_lab.next_to(brace, UP, buff=0.14)
        set_eq = MathTex(r"|S_c|", r"=", r"fF", font_size=EQ_SIZE - 6)
        board.set_bottom(set_eq)
        self.play(FadeIn(s_lab, shift=UP * 0.12), Write(set_eq), run_time=0.8)
        pop_named(self, s_lab, color=C["gold"], run_time=0.5, settle=0.2)
        _soft_until(tn, self, "died", gold_bars, s_lab, max_t=0.9)

        # ── 9. COUNTING IS DEAD ────────────────────────────────────────────
        tn.wait_until("died")
        self.play(
            Indicate(counter, color=C["wrong"], scale_factor=1.15),
            Indicate(gold_bars, color=C["gold"], scale_factor=1.06),
            run_time=0.8,
        )
        tn.wait_until("construction")
        fixed_counter = chip(f"on: {K_TOP} = fF, always", color=C["dim"], font_size=22)
        fixed_counter.move_to(counter.get_center())
        self.play(Transform(counter, fixed_counter), run_time=0.6)
        tn.wait_until("Counting")
        strike = Line(
            counter.get_left() + LEFT * 0.05,
            counter.get_right() + RIGHT * 0.05,
            color=C["wrong"],
            stroke_width=3,
        )
        self.play(Create(strike), run_time=0.5)
        self.play(FadeOut(counter), FadeOut(strike), run_time=0.6)
        board.clear("counter")
        _soft_until(tn, self, "mass", gold_bars, max_t=0.9)

        # ── 10. MASS, NOT MEMBERSHIP ───────────────────────────────────────
        tn.wait_until("mass")
        col, gold_seg, rest_seg = mass_column(gain=1.0)
        gold_seg.stretch_to_fit_height(0.03).move_to([COL_X, AXIS_Y + 0.015, 0])
        rest_seg.stretch_to_fit_height(0.03).move_to([COL_X, AXIS_Y + 0.045, 0])
        col[2].set_stroke(opacity=0.35)
        shift = CHART_X_SHIFTED - CHART_X
        col_lab = safe_text("total mass", font_size=18, color=C["label"])
        col_lab.move_to([COL_X, -1.75, 0])
        board.add(col_lab, "col_lab")
        tn.play_before(
            "heights",
            *[b.animate.shift(RIGHT * shift) for b in bars],
            brace.animate.shift(RIGHT * shift),
            s_lab.animate.shift(RIGHT * shift),
            axis.animate.put_start_and_end_on([-6.3, AXIS_Y, 0], [4.3, AXIS_Y, 0]),
            FadeIn(col[2]),
            FadeIn(col_lab),
            settle=0.3,
            max_run=1.0,
        )
        self.add(gold_seg, rest_seg)
        tn.wait_until("heights")

        # Gold heights accumulate first…
        gold_h = COL_H * ON_MASS
        gold_target = Rectangle(
            width=COL_W, height=gold_h, fill_color=C["gold"], fill_opacity=0.9, stroke_width=0
        ).move_to([COL_X, AXIS_Y + gold_h / 2, 0])
        ghosts = VGroup(*[b.copy() for b in srt[:K_TOP]])
        self.play(
            LaggedStart(
                *[
                    g.animate.move_to([COL_X, AXIS_Y + gold_h / 2, 0]).set_opacity(0.0)
                    for g in ghosts
                ],
                lag_ratio=0.3,
            ),
            Transform(gold_seg, gold_target),
            run_time=min(1.4, max(0.7, tn.span_until("every") - 0.5)),
        )
        self.remove(ghosts)
        tn.wait_until("every")

        # …then the rest of the layer stacks on top
        rest_h = COL_H - gold_h
        rest_target = Rectangle(
            width=COL_W, height=rest_h, fill_color=C["primary"], fill_opacity=0.45, stroke_width=0
        ).move_to([COL_X, AXIS_Y + gold_h + rest_h / 2, 0])
        ghosts2 = VGroup(*[b.copy() for b in srt[K_TOP:]])
        self.play(
            LaggedStart(
                *[
                    g.animate.move_to([COL_X, AXIS_Y + gold_h + rest_h / 2, 0]).set_opacity(0.0)
                    for g in ghosts2
                ],
                lag_ratio=0.05,
            ),
            Transform(rest_seg, rest_target),
            col[2].animate.set_stroke(opacity=1.0),
            run_time=min(1.6, max(0.8, tn.span_until("ratio") - 0.6)),
        )
        self.remove(ghosts2)
        _soft_until(tn, self, "ratio", gold_seg, max_t=0.7)

        # ── 11. FORMULA BUILD-UP ───────────────────────────────────────────
        tn.wait_until("ratio")
        num_eq = MathTex(r"\sum_{j\in S_c}|\mu_{c,j}|", font_size=EQ_SIZE - 6)
        board.set_bottom(num_eq)
        tn.play_before(
            "inside",
            ReplacementTransform(set_eq, num_eq),
            settle=0.3,
            max_run=1.0,
        )
        tn.wait_until("inside")
        self.play(
            Indicate(num_eq, color=C["gold"], scale_factor=1.06),
            Indicate(gold_seg, color=C["gold"], scale_factor=1.04),
            run_time=0.7,
        )
        tn.wait_until("total")

        frac_eq = MathTex(
            r"\frac{\sum_{j\in S_c}|\mu_{c,j}|}{\sum_{j=1}^{F}|\mu_{c,j}|}",
            font_size=EQ_SIZE - 8,
        )
        board.set_bottom(frac_eq)
        tn.play_before(
            "share",
            TransformMatchingTex(num_eq, frac_eq),
            Indicate(col[2], color=WHITE, scale_factor=1.03),
            settle=0.35,
            max_run=1.1,
        )
        tn.wait_until("share")

        on_eq = MathTex(
            r"\mathrm{on\text{-}mass}(c)",
            r"=",
            r"\frac{\sum_{j\in S_c}|\mu_{c,j}|}{\sum_{j=1}^{F}|\mu_{c,j}|}",
            font_size=EQ_SIZE - 10,
        )
        board.set_bottom(on_eq)
        self.play(TransformMatchingTex(frac_eq, on_eq), run_time=0.9)
        value_chip = readout(ON_MASS)
        board.clear("col_lab")
        self.play(ReplacementTransform(col_lab, value_chip), run_time=0.6)
        board.add(value_chip, "value_chip")
        pop_named(self, value_chip, gold_seg, color=C["gold"], run_time=0.6, settle=0.25)
        board.assert_clear()
        _soft_until(tn, self, "read", value_chip, max_t=0.9)

        # ── 12. READING IT — the uniform baseline is f ─────────────────────
        tn.wait_until("read")
        tn.wait_until("equal")
        flat = make_bars(uniform=True, x_center=CHART_X_SHIFTED, rank_positions=True)
        flat_gold = Rectangle(
            width=COL_W,
            height=COL_H * 0.10,
            fill_color=C["gold"],
            fill_opacity=0.9,
            stroke_width=0,
        ).move_to([COL_X, AXIS_Y + COL_H * 0.05, 0])
        flat_rest = Rectangle(
            width=COL_W,
            height=COL_H * 0.90,
            fill_color=C["primary"],
            fill_opacity=0.45,
            stroke_width=0,
        ).move_to([COL_X, AXIS_Y + COL_H * 0.10 + COL_H * 0.45, 0])
        flat_read = readout(0.10)
        self.play(
            *[Transform(bars[j], flat[j]) for j in range(F_UNITS)],
            *[
                b.animate.set_fill(C["gold"], 0.92).set_stroke(C["gold"])
                for b in srt[:K_TOP]
            ],
            Transform(gold_seg, flat_gold),
            Transform(rest_seg, flat_rest),
            Transform(value_chip, flat_read),
            FadeOut(brace),
            FadeOut(s_lab),
            run_time=1.2,
            rate_func=smooth,
        )
        tn.wait_until("baseline")

        base_y = AXIS_Y + COL_H * 0.10
        base_line = DashedLine(
            [COL_X - COL_W / 2 - 0.35, base_y, 0],
            [COL_X + COL_W / 2 + 0.35, base_y, 0],
            color=WHITE,
            stroke_width=2,
            dash_length=0.08,
        )
        base_lab = safe_text("uniform baseline = f", font_size=18, color=WHITE)
        base_lab.move_to([COL_X, AXIS_Y + COL_H + 0.42, 0])  # above the column, never across it
        self.play(Create(base_line), FadeIn(base_lab, shift=UP * 0.08), run_time=0.8)
        pop_named(self, base_line, color=WHITE, run_time=0.5, settle=0.2)
        _soft_until(tn, self, "Peakier", base_line, max_t=0.8)

        tn.wait_until("Peakier")
        real_cols = [C["gold"] if j in ORDER[:K_TOP] else C["primary"] for j in range(F_UNITS)]
        real_ops = [0.92 if j in ORDER[:K_TOP] else 0.35 for j in range(F_UNITS)]
        peaky = make_bars(
            x_center=CHART_X_SHIFTED,
            rank_positions=True,
            colors=real_cols,
            opacities=real_ops,
        )
        col_r, gold_r, rest_r = mass_column(gain=1.0)
        real_read = readout(ON_MASS)
        self.play(
            *[Transform(bars[j], peaky[j]) for j in range(F_UNITS)],
            Transform(gold_seg, gold_r),
            Transform(rest_seg, rest_r),
            Transform(value_chip, real_read),
            run_time=1.2,
            rate_func=smooth,
        )
        tn.wait_until("quarter")
        pop_named(self, value_chip, color=C["gold"], run_time=0.6, settle=0.25)
        _soft_until(tn, self, "volume", value_chip, max_t=0.9)

        # ── 13. SCALE INVARIANCE — the trap cannot touch a ratio ───────────
        tn.wait_until("volume")
        gain_chip2 = chip(f"gain x{GAIN}", color=C["highlight"], font_size=22)
        gain_chip2.move_to([GAIN_X, CHIP_Y, 0])
        board.add(gain_chip2, "gain_chip2")
        self.play(FadeIn(gain_chip2, scale=0.9), run_time=0.4)
        tn.wait_until("climbs")

        loud2 = make_bars(
            gain=GAIN,
            x_center=CHART_X_SHIFTED,
            rank_positions=True,
            colors=real_cols,
            opacities=real_ops,
        )
        col_l, gold_l, rest_l = mass_column(gain=GAIN)
        self.play(
            *[Transform(bars[j], loud2[j]) for j in range(F_UNITS)],
            Transform(gold_seg, gold_l),
            Transform(rest_seg, rest_l),
            Transform(col[2], col_l[2]),
            FadeOut(base_line),
            FadeOut(base_lab),
            run_time=1.3,
            rate_func=smooth,
        )
        tn.wait_until("budge")
        self.play(Indicate(value_chip, color=C["right"], scale_factor=1.12), run_time=0.8)
        tn.wait_until("trap")
        compare = VGroup(
            safe_text(f"count: {N_ABOVE} → {N_ABOVE_GAIN}", font_size=18, color=C["wrong"]),
            safe_text(f"on-mass: {ON_MASS:.2f} → {ON_MASS:.2f}", font_size=18, color=C["right"]),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        compare.move_to([COUNTER_X, CHIP_Y - 0.05, 0])
        board.add(compare, "compare")
        self.play(FadeIn(compare, shift=UP * 0.1), run_time=0.6)
        board.assert_clear()
        _soft_until(tn, self, "nearby", value_chip, max_t=0.9)

        # ── 14. SIBLING QUESTIONS ──────────────────────────────────────────
        tn.wait_until("nearby")
        chart_all = VGroup(
            *bars, axis, gold_seg, rest_seg, col[2], value_chip, gain_chip2, compare, f_chip
        )
        self.play(FadeOut(chart_all), FadeOut(dist_lab), run_time=0.6)
        board.clear("value_chip", "compare", "gain_chip2", "dist_lab", "f_chip")

        def card(head: str, sub: str, color) -> VGroup:
            """Comparison card: metric name over the question it answers.

            The frame keeps a dark fill so the label survives being highlighted
            (craft law: a highlight must never blank its own text).

            Args:
                head: Metric name.
                sub: The question that metric answers.
                color: Entity color bound to that metric.

            Returns:
                ``VGroup(frame, body)`` — frame and text stay separate so the
                two can be animated independently.
            """
            title_t = safe_text(head, font_size=24, color=color)
            sub_t = safe_text(sub, font_size=18, color=C["label"])
            body = VGroup(title_t, sub_t).arrange(DOWN, buff=0.18)
            frame = RoundedRectangle(
                width=3.6,
                height=1.5,
                corner_radius=0.12,
                stroke_color=color,
                stroke_width=2,
                fill_color=BLACK,
                fill_opacity=0.4,
            )
            body.move_to(frame)
            return VGroup(frame, body)

        def light(c: VGroup, color) -> list:
            """Raise a card: brighter stroke, faint tint, full-contrast label."""
            return [
                c[0].animate.set_stroke(color, width=4, opacity=1.0).set_fill(color, 0.18),
                c[1].animate.set_opacity(1.0),
            ]

        def dim(c: VGroup) -> list:
            """Push a card back without blanking it."""
            return [
                c[0].animate.set_stroke(width=2, opacity=0.4).set_fill(BLACK, 0.4),
                c[1].animate.set_opacity(0.35),
            ]

        def pulse(c: VGroup) -> None:
            """Stroke-only pop — never fills over the label."""
            self.play(
                c[0].animate.set_stroke(width=6),
                rate_func=there_and_back,
                run_time=0.6,
            )

        cards = VGroup(
            card("on-mass", "share of the mass", C["gold"]),
            card("top-set strength", "mean magnitude in S", C["primary"]),
            card("selectivity", "prefers this class?", C["secondary"]),
        ).arrange(RIGHT, buff=0.45)
        cards.move_to(UP * 0.15)
        self.play(
            LaggedStart(*[GrowFromCenter(c) for c in cards], lag_ratio=0.15),
            run_time=0.9,
        )
        self.play(*dim(cards[1]), *dim(cards[2]), run_time=0.4)
        tn.wait_until("magnitude")

        self.play(*light(cards[1], C["primary"]), *dim(cards[0]), run_time=0.6)
        pulse(cards[1])
        tn.wait_until("louder")
        up_arrow = Arrow(
            ORIGIN,
            UP * 0.7,
            buff=0.0,
            color=C["primary"],
            stroke_width=4,
            max_tip_length_to_length_ratio=0.3,
        )
        up_arrow.next_to(cards[1], DOWN, buff=0.25)
        self.play(GrowArrow(up_arrow), run_time=0.6)
        tn.wait_until("selectivity")

        self.play(
            *light(cards[2], C["secondary"]),
            *dim(cards[1]),
            up_arrow.animate.set_opacity(0.3),
            run_time=0.6,
        )
        pulse(cards[2])
        tn.wait_until("prefers")
        pulse(cards[2])
        tn.wait_until("opposite")

        down_gold = Arrow(
            ORIGIN, DOWN * 0.7, buff=0.0, color=C["gold"], stroke_width=4,
            max_tip_length_to_length_ratio=0.3,
        )
        down_gold.next_to(cards[0], DOWN, buff=0.25)
        up_teal = Arrow(
            ORIGIN, UP * 0.7, buff=0.0, color=C["secondary"], stroke_width=4,
            max_tip_length_to_length_ratio=0.3,
        )
        up_teal.next_to(cards[2], DOWN, buff=0.25)
        self.play(
            *light(cards[0], C["gold"]),
            *light(cards[2], C["secondary"]),
            FadeOut(up_arrow),
            GrowArrow(down_gold),
            GrowArrow(up_teal),
            run_time=0.9,
        )
        opp_note = board.set_bottom(
            bottom_note("concentration and preference can move opposite ways", color=C["label"])
        )
        self.play(ReplacementTransform(on_eq, opp_note), run_time=0.6)
        _soft_until(tn, self, "concentrated", cards[0], cards[2], max_t=0.9)

        # ── 15. SETTLE ─────────────────────────────────────────────────────
        tn.wait_until("concentrated")
        self.play(
            FadeOut(cards),
            FadeOut(down_gold),
            FadeOut(up_teal),
            FadeOut(opp_note),
            run_time=0.5,
        )
        board.clear()

        final_eq = MathTex(
            r"\mathrm{on\text{-}mass}(c)",
            r"=",
            r"\frac{\sum_{j\in S_c}|\mu_{c,j}|}{\sum_{j=1}^{F}|\mu_{c,j}|}",
            font_size=EQ_SIZE - 6,
        )
        final_eq.move_to(UP * 0.75)
        board.add(final_eq, "final_eq")
        tn.play_before("strength", Write(final_eq), settle=0.4, max_run=1.3)

        mini_scale = 0.42
        mini = VGroup(
            *[
                Rectangle(
                    width=BAR_W * 0.55,
                    height=max(ABS[j] * VSCALE * mini_scale, 0.03),
                    fill_color=C["gold"] if r < K_TOP else C["primary"],
                    fill_opacity=0.9 if r < K_TOP else 0.4,
                    stroke_width=0.8,
                    stroke_color=C["gold"] if r < K_TOP else C["primary"],
                )
                for r, j in enumerate(ORDER)
            ]
        )
        for r, rect in enumerate(mini):
            rect.move_to(
                [
                    (r - (F_UNITS - 1) / 2) * 0.26,
                    -1.75 + rect.height / 2,
                    0,
                ]
            )
        self.play(LaggedStart(*[GrowFromEdge(m, DOWN) for m in mini], lag_ratio=0.03), run_time=0.9)
        tn.wait_until("strength")

        share_key = key_sentence(
            self,
            "a share of the mass — at a stated fraction",
            color=C["highlight"],
            font_size=28,
            hold=0.1,
            park="left",
            board=board,
        )
        tn.wait_until("chose")
        pair = board.set_bottom(
            bottom_note(f"report the pair:  f = 10%,  on-mass = {ON_MASS:.2f}", color=C["gold"])
        )
        self.play(FadeIn(pair, shift=UP * 0.1), run_time=0.5)
        board.assert_clear()
        tn.wait_until("sweep")

        # Sweep the fraction: the number only means something next to f
        for frac, k in ((0.25, 5), (0.50, 10)):
            share = sum(ABS[i] for i in ORDER[:k]) / TOTAL_MASS
            new_pair = bottom_note(
                f"report the pair:  f = {int(frac * 100)}%,  on-mass = {share:.2f}",
                color=C["gold"],
            )
            self.play(
                *[
                    mini[r].animate.set_fill(C["gold"], 0.9).set_stroke(C["gold"])
                    for r in range(k)
                ],
                Transform(pair, new_pair),
                run_time=0.75,
            )
        soft_idle(self, final_eq, mini, run_time=0.7)

        tn.wait_until_end(pad=0.4)
