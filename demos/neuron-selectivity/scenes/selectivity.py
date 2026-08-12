"""Neuron selectivity explainer — Wrong→Right.

Top-9 gallery (cherry-picked) → whole response distribution → split by label →
selective vs mixed → class-mean bars → selectivity index BUILD_UP → loudness
trap → ablation / label-axis caveats → settle.

Craft laws: morph don't respawn; picture matches the spoken noun; questions move
their referent; named objects pop then settle in the baked audio pause; spoken
state-words play on the word; prose only in reserved bands.
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
    LayoutBoard,
    ask_about,
    bottom_note,
    key_sentence,
    labeled_box,
    panel_label,
    pop_named,
    safe_text,
    section_title,
    soft_idle,
)

# ── Toy data: one unit's response over a labelled dataset ─────────────
RNG = np.random.default_rng(11)
CLASSES = ["dog", "cat", "car", "tree"]
TEXTURES = ["striped", "smooth", "spotted", "plain"]
N_PER = 12
N_TOTAL = N_PER * len(CLASSES)
CLASS_COLORS = [C["gold"], C["primary"], C["secondary"], GREEN_C]

_SEL_MEAN = [0.84, 0.30, 0.20, 0.16]
_SEL_SD = [0.055, 0.13, 0.075, 0.06]
_SEL_CLIP = [(0.70, 0.98), (0.05, 0.62), (0.03, 0.42), (0.02, 0.34)]


def _selective_values() -> np.ndarray:
    """Sample the selective unit's activation for every dataset example.

    Returns:
        Array of ``N_TOTAL`` activations in [0, 1], grouped class by class.
    """
    out = []
    for c in range(len(CLASSES)):
        v = RNG.normal(_SEL_MEAN[c], _SEL_SD[c], N_PER)
        out.append(np.clip(v, *_SEL_CLIP[c]))
    return np.concatenate(out)


def _texture_ids() -> np.ndarray:
    """Assign a texture to every example, balanced inside each class.

    Returns:
        Texture index per example (0 = striped), length ``N_TOTAL``.
    """
    per_class = np.repeat(np.arange(len(TEXTURES)), N_PER // len(TEXTURES))
    return np.concatenate([RNG.permutation(per_class) for _ in CLASSES])


def _mixed_values(tex: np.ndarray) -> np.ndarray:
    """Sample a second unit whose response tracks texture, not class.

    Args:
        tex: Texture index per example.

    Returns:
        Activations that look piled across classes but separate by texture.
    """
    high = RNG.normal(0.78, 0.05, N_TOTAL)
    low = RNG.normal(0.24, 0.08, N_TOTAL)
    return np.clip(np.where(tex == 0, high, low), 0.02, 0.98)


CLASS_ID = np.repeat(np.arange(len(CLASSES)), N_PER)
SEL_VALUES = _selective_values()
TEX_ID = _texture_ids()
MIX_VALUES = _mixed_values(TEX_ID)
JITTER = RNG.uniform(-1.0, 1.0, N_TOTAL)
CLOUD_XY = np.stack(
    [RNG.uniform(-3.0, 3.0, N_TOTAL), RNG.uniform(-1.45, 1.15, N_TOTAL)], axis=1
)


def group_means(values: np.ndarray, group: np.ndarray, n_groups: int) -> np.ndarray:
    """Mean response per group.

    Args:
        values: Per-example activations.
        group: Per-example group index.
        n_groups: Number of groups.

    Returns:
        Array of group means.
    """
    return np.array([float(values[group == g].mean()) for g in range(n_groups)])


def selectivity_index(means: np.ndarray) -> float:
    """Class selectivity index from group means (Morcos et al., ICLR 2018).

    ``(mu_max - mu_-max) / (mu_max + mu_-max)``.

    Args:
        means: Per-group mean activations (non-negative).

    Returns:
        Index in [0, 1]; 1 = only the favourite group drives the unit.
    """
    top = float(np.max(means))
    rest = float(np.mean(np.delete(means, int(np.argmax(means)))))
    return float((top - rest) / (top + rest + 1e-9))


SEL_MEANS = group_means(SEL_VALUES, CLASS_ID, len(CLASSES))
MIX_CLASS_MEANS = group_means(MIX_VALUES, CLASS_ID, len(CLASSES))
MIX_TEX_MEANS = group_means(MIX_VALUES, TEX_ID, len(TEXTURES))
SI_SEL = selectivity_index(SEL_MEANS)
SI_MIX = selectivity_index(MIX_CLASS_MEANS)
SI_TEX = selectivity_index(MIX_TEX_MEANS)
REST_VAL = float(np.mean(SEL_MEANS[1:]))

# ── Stage geometry ────────────────────────────────────────────────────
AX_X0, AX_SPAN = -2.35, 5.0
ROW_Y = [1.15, 0.42, -0.31, -1.04]
AXIS_Y = -1.72
BAR_FLOOR = -1.70
H_SCALE = 1.35  # value → height; never re-normalized, so loudness shows in pixels
BAR_W = 0.62


def ax_x(value):
    """Map activation in [0, 1] to a stage x coordinate."""
    return AX_X0 + np.asarray(value, dtype=float) * AX_SPAN


def pos_rows(values: np.ndarray, groups: np.ndarray) -> np.ndarray:
    """Dot positions split into one row per group."""
    return np.stack(
        [
            ax_x(values),
            np.array([ROW_Y[int(g)] for g in groups]) + JITTER * 0.13,
            np.zeros(N_TOTAL),
        ],
        axis=1,
    )


def pos_strip(values: np.ndarray) -> np.ndarray:
    """Dot positions in one response strip along the activation axis."""
    return np.stack([ax_x(values), -0.15 + JITTER * 0.62, np.zeros(N_TOTAL)], axis=1)


def pos_cloud() -> np.ndarray:
    """Unordered dataset cloud positions."""
    return np.stack([CLOUD_XY[:, 0], CLOUD_XY[:, 1], np.zeros(N_TOTAL)], axis=1)


def pos_rank_grid(values: np.ndarray, cols: int = 8) -> np.ndarray:
    """Grid positions ordered by activation, highest first (reading order)."""
    order = np.argsort(-values)
    pts = np.zeros((N_TOTAL, 3))
    for rank, idx in enumerate(order):
        r, c = divmod(rank, cols)
        pts[idx] = [(c - (cols - 1) / 2) * 0.52, 1.30 - r * 0.46, 0.0]
    return pts


def make_dots(groups: np.ndarray, *, radius: float = 0.075) -> VGroup:
    """One dot per dataset example, coloured by group (index-stable)."""
    return VGroup(
        *[
            Dot(radius=radius, color=CLASS_COLORS[int(g)], fill_opacity=0.85, stroke_width=0)
            for g in groups
        ]
    )


def move_dots(dots: VGroup, points: np.ndarray, *, lag: float = 0.0) -> Animation:
    """Animation moving every dot to its target point (morph, never respawn)."""
    anims = [d.animate.move_to(p) for d, p in zip(dots, points)]
    return LaggedStart(*anims, lag_ratio=lag) if lag else AnimationGroup(*anims)


def make_axis() -> VGroup:
    """Activation axis with end ticks — the response scale for the dot rows."""
    line = Arrow(
        [AX_X0 - 0.25, AXIS_Y, 0],
        [AX_X0 + AX_SPAN + 0.35, AXIS_Y, 0],
        buff=0,
        stroke_width=2.5,
        color=C["dim"],
        max_tip_length_to_length_ratio=0.03,
    )
    lo = safe_text("0", font_size=16, color=C["dim"]).move_to([AX_X0, AXIS_Y - 0.26, 0])
    hi = safe_text("1", font_size=16, color=C["dim"]).move_to([AX_X0 + AX_SPAN, AXIS_Y - 0.26, 0])
    return VGroup(line, lo, hi)


def make_net(sizes=(4, 7, 5, 3), *, radius=0.15, layer_buff=1.05, node_buff=0.26):
    """Feedforward schematic: ``(net, layers, edges)`` with sparse edges."""
    layers: list[VGroup] = []
    for n in sizes:
        layers.append(
            VGroup(
                *[
                    Circle(
                        radius=radius,
                        color=C["dim"],
                        fill_opacity=0.35,
                        stroke_width=2,
                        stroke_color=WHITE,
                    )
                    for _ in range(n)
                ]
            ).arrange(DOWN, buff=node_buff)
        )
    VGroup(*layers).arrange(RIGHT, buff=layer_buff)
    edges = VGroup()
    for left, right in zip(layers[:-1], layers[1:]):
        for i, a in enumerate(left):
            mid = int(round(i * (len(right) - 1) / max(len(left) - 1, 1)))
            for j in sorted({mid, max(0, mid - 1), min(len(right) - 1, mid + 1)}):
                edges.add(
                    Line(
                        a.get_right(),
                        right[j].get_left(),
                        stroke_width=1.3,
                        color=GREY_B,
                        stroke_opacity=0.28,
                    )
                )
    return VGroup(edges, *layers), layers, edges


def make_bar(value: float, x: float, color, *, width: float = BAR_W) -> Rectangle:
    """One value bar standing on the shared floor (no per-bar normalization)."""
    rect = Rectangle(
        width=width,
        height=max(float(value) * H_SCALE, 0.04),
        fill_color=color,
        fill_opacity=0.9,
        stroke_width=1.5,
        stroke_color=WHITE,
    )
    rect.move_to([x, BAR_FLOOR, 0], aligned_edge=DOWN)
    return rect


def morph_bar(bar: Rectangle, value: float, *, color=None) -> Animation:
    """Animation morphing a bar to a new value at the same x (height changes)."""
    target = Rectangle(
        width=bar.width,
        height=max(float(value) * H_SCALE, 0.04),
        fill_color=color or bar.get_fill_color(),
        fill_opacity=0.9,
        stroke_width=1.5,
        stroke_color=WHITE,
    )
    target.move_to([bar.get_center()[0], BAR_FLOOR, 0], aligned_edge=DOWN)
    return Transform(bar, target)


def bar_top(value: float) -> float:
    """Y coordinate of a bar top for a given value."""
    return BAR_FLOOR + max(float(value) * H_SCALE, 0.04)


class Dial(VGroup):
    """Half-circle [0, 1] readout whose needle morphs in place."""

    def __init__(self, value: float, label: str = "selectivity", color=C["accent"], radius=0.8):
        super().__init__()
        self.color_ = color
        self.arc = Arc(radius=radius, start_angle=PI, angle=-PI, color=C["dim"], stroke_width=6)
        self.needle = self._needle(value)
        self.tip = Dot(self.needle.get_end(), radius=0.055, color=color)
        self.label = safe_text(label, font_size=18, color=C["label"])
        self.value_text = safe_text(f"{value:.2f}", font_size=24, color=color)
        self.label.next_to(self.arc, DOWN, buff=0.16)
        self.value_text.next_to(self.label, DOWN, buff=0.08)
        self.add(self.arc, self.needle, self.tip, self.label, self.value_text)

    def _needle(self, value: float) -> Line:
        """Build the needle for ``value``, sized to the arc's current radius."""
        pivot = self.arc.get_arc_center()
        radius = float(self.arc.width) / 2.0
        end = pivot + rotate_vector(LEFT * (radius * 0.88), -float(value) * PI)
        return Line(pivot, end, color=self.color_, stroke_width=4)

    def value_anims(self, value: float, *, color=None) -> list[Animation]:
        """Animations morphing needle and readout to a new value.

        Returned rather than played so the dial can move *in the same beat* as
        the figure it reports on — a dial that lags its bars reads as a bug.

        Args:
            value: New index value in [0, 1].
            color: Optional new accent colour.

        Returns:
            List of animations to include in a ``Scene.play`` call.
        """
        if color is not None:
            self.color_ = color
        needle = self._needle(value)
        tip = Dot(needle.get_end(), radius=float(self.tip.width) / 2.0, color=self.color_)
        val = safe_text(f"{value:.2f}", font_size=24, color=self.color_)
        if self.value_text.height > 0.02:
            val.scale_to_fit_height(self.value_text.height)
        val.move_to(self.value_text)
        return [
            Transform(self.needle, needle),
            Transform(self.tip, tip),
            Transform(self.value_text, val),
        ]

    def set_value(self, value: float, *, scene: Scene, run_time: float = 0.8, color=None) -> None:
        """Morph needle and readout to a new value on its own.

        Args:
            value: New index value in [0, 1].
            scene: Scene used to play the morph.
            run_time: Animation duration.
            color: Optional new accent colour.
        """
        scene.play(*self.value_anims(value, color=color), run_time=run_time, rate_func=smooth)


def _soft_until(tn: TimedNarration, scene: Scene, bookmark: str, *mobs, max_t: float = 1.0) -> None:
    """Breathe through the baked audio pause until the next bookmark."""
    rem = tn.span_until(bookmark)
    if rem > 0.28 and mobs:
        soft_idle(scene, *mobs, run_time=min(rem * 0.85, max_t))


class SelectivityScene(Scene):
    def construct(self) -> None:
        tn = TimedNarration(DEMO_DIR / "timing.json", DEMO_DIR / "audio" / "narration.mp3")
        tn.attach(self)
        board = LayoutBoard()

        # ══ 1. HOOK — whole net, then one unit answering to inputs ══
        title = board.set_title(section_title("Neuron Selectivity"))
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.7)
        tn.wait_until("network")

        net, layers, edges = make_net()
        net.scale(0.92).move_to(LEFT * 1.5 + DOWN * 0.2)
        tn.play_before(
            "unit",
            LaggedStart(*[GrowFromCenter(n) for L in layers for n in L], lag_ratio=0.02),
            settle=0.3,
            max_run=0.8,
        )
        self.play(Create(edges), run_time=0.35)
        tn.wait_until("unit")

        hidden = layers[1]
        unit = hidden[3]
        focus = SurroundingRectangle(hidden, buff=0.11, color=C["primary"], stroke_width=2.5)
        self.play(FadeIn(focus), run_time=0.28)
        pop_named(self, focus, color=C["primary"], run_time=0.4, settle=0.1)
        self.play(
            unit.animate.set_fill(C["gold"], 0.95).set_stroke(C["gold"], 3),
            edges.animate.set_stroke(opacity=0.14),
            run_time=0.35,
        )
        pop_named(self, unit, color=C["gold"], run_time=0.45, settle=0.1)

        meter_x = 3.9
        meter_track = Rectangle(
            width=0.62, height=2.45, stroke_color=C["dim"], stroke_width=1.6, fill_opacity=0
        ).move_to([meter_x, BAR_FLOOR + 2.45 / 2, 0])
        meter_bar = make_bar(0.05, meter_x, C["gold"], width=0.62)
        meter_lab = panel_label("response", C["gold"], x=meter_x)
        board.add(meter_lab, "meter_lab")
        chips = VGroup(
            *[
                labeled_box(name, width=1.15, height=0.42, color=CLASS_COLORS[i], font_size=20)
                for i, name in enumerate(CLASSES[:3])
            ]
        ).arrange(DOWN, buff=0.3).move_to([-5.3, -0.2, 0])
        feed = Arrow(
            chips.get_right() + RIGHT * 0.05,
            net.get_left() + LEFT * 0.05,
            buff=0.12,
            stroke_width=2.5,
            color=C["dim"],
            max_tip_length_to_length_ratio=0.12,
        )
        tn.play_before(
            "dog",
            LaggedStart(*[FadeIn(c, shift=RIGHT * 0.12) for c in chips], lag_ratio=0.1),
            GrowArrow(feed),
            FadeIn(meter_track),
            FadeIn(meter_bar),
            FadeIn(meter_lab),
            settle=0.2,
            max_run=0.7,
        )
        tn.wait_until("dog")

        def show_input(i: int, value: float, run_time: float = 0.55) -> None:
            """Cycle one input class and let the unit respond in lockstep.

            The active chip brightens its box *and* keeps a readable label —
            never fill a chip opaque in its own text colour.
            """
            chip_anims = []
            for k, chip in enumerate(chips):
                box, text = chip[0], chip[1]
                if k == i:
                    chip_anims += [
                        box.animate.set_fill(CLASS_COLORS[k], 0.45).set_stroke(
                            CLASS_COLORS[k], 3, opacity=1.0
                        ),
                        text.animate.set_color(WHITE).set_opacity(1.0),
                    ]
                else:
                    chip_anims += [
                        box.animate.set_fill(CLASS_COLORS[k], 0.1).set_stroke(
                            CLASS_COLORS[k], 2, opacity=0.4
                        ),
                        text.animate.set_color(CLASS_COLORS[k]).set_opacity(0.45),
                    ]
            self.play(
                *chip_anims,
                morph_bar(meter_bar, value),
                Indicate(unit, color=C["gold"], scale_factor=1.0 + 0.35 * value),
                run_time=run_time,
                rate_func=smooth,
            )

        show_input(0, 0.86, run_time=0.7)  # dog → it lights up
        pop_named(self, meter_bar, color=C["gold"], run_time=0.45, settle=0.12)
        show_input(1, 0.24)
        show_input(2, 0.16)
        show_input(0, 0.88)
        _soft_until(tn, self, "neuron", unit, meter_bar, max_t=0.7)

        # ══ 2. The question ══
        tn.wait_until("neuron")
        self.play(FadeOut(title), run_time=0.25)
        board.clear("title")
        q1 = ask_about(
            self,
            "a dog neuron?",
            unit,
            meter_bar,
            chips[0],
            hold=0.06,
            park="left",
            board=board,
            font_size=28,
            motion_time=0.7,
            color=C["highlight"],
        )
        tn.wait_until("claim")
        show_input(0, 0.9, run_time=0.5)
        _soft_until(tn, self, "gallery", unit, q1, max_t=1.0)

        # ══ 3. WRONG — the cherry-picked top-9 gallery ══
        tn.wait_until("gallery")
        dots = make_dots(CLASS_ID)
        cloud_left = pos_cloud() * np.array([0.55, 0.82, 1.0]) + np.array([-3.1, 0.0, 0.0])
        for d, p in zip(dots, cloud_left):
            d.move_to(p)
        data_lab = panel_label("the dataset", C["dim"], x=-3.1)
        board.add(data_lab, "data_lab")
        self.play(
            FadeOut(q1),
            FadeOut(net),
            FadeOut(focus),
            FadeOut(feed),
            FadeOut(meter_track),
            FadeOut(meter_bar),
            FadeOut(meter_lab),
            FadeOut(chips),
            run_time=0.45,
        )
        board.clear("key", "meter_lab")
        tn.play_before(
            "nine",
            LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.008),
            FadeIn(data_lab),
            settle=0.25,
            max_run=0.85,
        )
        tn.wait_until("nine")

        top9 = [int(i) for i in np.argsort(-SEL_VALUES)[:9]]
        gallery = VGroup(
            *[
                VGroup(
                    RoundedRectangle(
                        width=0.66,
                        height=0.66,
                        corner_radius=0.07,
                        color=C["gold"],
                        fill_opacity=0.28,
                        stroke_width=2,
                    ),
                    safe_text("dog", font_size=14, color=C["gold"]),
                )
                for _ in range(9)
            ]
        )
        for cell in gallery:
            cell[1].move_to(cell[0])
        gallery.arrange_in_grid(3, 3, buff=0.13).move_to([3.15, 0.1, 0])
        gal_lab = panel_label("top 9", C["gold"], x=3.15)
        board.add(gal_lab, "gal_lab")
        self.play(
            LaggedStart(
                *[
                    ReplacementTransform(dots[idx].copy(), gallery[k])
                    for k, idx in enumerate(top9)
                ],
                lag_ratio=0.06,
            ),
            *[dots[idx].animate.set_color(C["gold"]).scale(1.3) for idx in top9],
            FadeIn(gal_lab),
            run_time=1.5,
        )
        rest_idx = [i for i in range(N_TOTAL) if i not in top9]
        self.play(
            *[dots[i].animate.set_opacity(0.2) for i in rest_idx],
            run_time=0.5,
        )
        _soft_until(tn, self, "closed", gallery, max_t=0.9)

        tn.wait_until("closed")
        q2 = ask_about(
            self,
            "case closed?",
            gallery,
            hold=0.06,
            park="left",
            board=board,
            font_size=28,
            motion_time=0.7,
            color=C["highlight"],
        )
        _soft_until(tn, self, "ranking", gallery, q2, max_t=1.1)

        # ══ 4. That gallery is only the top of a ranking ══
        tn.wait_until("ranking")
        self.play(FadeOut(q2), FadeOut(gal_lab), FadeOut(data_lab), run_time=0.3)
        board.clear("key", "gal_lab", "data_lab")
        rank_arrow = Arrow(
            [-2.95, 1.4, 0], [-2.95, -1.35, 0], buff=0, stroke_width=3, color=C["dim"]
        )
        rank_lab = safe_text("rank", font_size=20, color=C["dim"]).next_to(
            rank_arrow, LEFT, buff=0.16
        )
        board.add(rank_lab, "rank_lab")
        tn.play_before(
            "rest",
            FadeOut(gallery, shift=LEFT * 0.8, scale=0.6),
            move_dots(dots, pos_rank_grid(SEL_VALUES), lag=0.004),
            GrowArrow(rank_arrow),
            FadeIn(rank_lab),
            settle=0.3,
            max_run=1.2,
        )
        tn.wait_until("rest")

        self.play(
            LaggedStart(
                *[dots[i].animate.set_opacity(0.9).scale(1.18) for i in rest_idx],
                lag_ratio=0.008,
            ),
            run_time=1.3,
        )
        mid_high = [i for i in rest_idx if SEL_VALUES[i] > 0.42]
        self.play(
            *[
                Flash(dots[i], color=C["primary"], line_length=0.13, flash_radius=0.22)
                for i in mid_high
            ],
            run_time=0.8,
        )
        key_rank = key_sentence(
            self,
            "the top of a ranking hides the rest",
            color=C["wrong"],
            font_size=26,
            hold=0.08,
            park="left",
            board=board,
        )
        _soft_until(tn, self, "picture", dots, max_t=0.9)

        # ══ 5. One picture → the whole distribution ══
        tn.wait_until("picture")
        one = dots[top9[0]]
        ring = SurroundingRectangle(one, buff=0.07, color=C["highlight"], stroke_width=2.5)
        self.play(Create(ring), run_time=0.4)
        pop_named(self, one, color=C["highlight"], run_time=0.45, settle=0.1)

        axis = make_axis()
        ax_lab = safe_text("activation", font_size=20, color=C["dim"]).move_to(
            [AX_X0 + AX_SPAN / 2, AXIS_Y - 0.6, 0]
        )
        board.add(ax_lab, "ax_lab")
        tn.play_before(
            "distribution",
            FadeOut(ring),
            FadeOut(rank_arrow),
            FadeOut(rank_lab),
            FadeOut(key_rank),
            move_dots(dots, pos_strip(SEL_VALUES), lag=0.004),
            FadeIn(axis),
            FadeIn(ax_lab),
            settle=0.35,
            max_run=1.4,
        )
        board.clear("key", "rank_lab")
        tn.wait_until("distribution")
        soft_idle(self, dots, run_time=0.7, scale=1.04)
        _soft_until(tn, self, "dataset", dots, max_t=0.7)

        # ══ 6. Split the responses by label ══
        tn.wait_until("dataset")
        self.play(
            LaggedStart(
                *[Flash(d, color=d.get_color(), line_length=0.08, flash_radius=0.15) for d in dots],
                lag_ratio=0.006,
            ),
            run_time=1.2,
        )
        tn.wait_until("activation")
        self.play(Indicate(axis, color=C["accent"], scale_factor=1.02), run_time=0.6)
        _soft_until(tn, self, "label", dots, max_t=0.6)

        tn.wait_until("label")
        row_chips = VGroup(
            *[
                labeled_box(name, width=1.05, height=0.38, color=CLASS_COLORS[i], font_size=19)
                for i, name in enumerate(CLASSES)
            ]
        )
        for i, chip in enumerate(row_chips):
            chip.move_to([AX_X0 - 0.95, ROW_Y[i], 0])
        in_lab = safe_text("input label", font_size=18, color=C["label"]).move_to(
            [AX_X0 - 0.95, ROW_Y[0] + 0.5, 0]
        )
        board.add(in_lab, "in_lab")
        tn.play_before(
            "selective",
            move_dots(dots, pos_rows(SEL_VALUES, CLASS_ID), lag=0.004),
            LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in row_chips], lag_ratio=0.1),
            FadeIn(in_lab),
            settle=0.35,
            max_run=1.5,
        )

        # ══ 7. What should selective look like? ══
        tn.wait_until("selective")
        q3 = ask_about(
            self,
            "what should selective look like?",
            *row_chips,
            hold=0.06,
            park="left",
            board=board,
            font_size=26,
            motion_time=0.8,
            color=C["highlight"],
        )
        soft_idle(self, dots, run_time=0.7, scale=1.05)
        _soft_until(tn, self, "high", q3, max_t=1.0)

        # ══ 8. Dual panel — selective vs mixed ══
        tn.wait_until("high")
        self.play(FadeOut(q3), FadeOut(ax_lab), FadeOut(in_lab), run_time=0.3)
        board.clear("key", "ax_lab", "in_lab")

        panel_l = VGroup(dots, row_chips, axis)
        tn.play_before(
            "piled",
            panel_l.animate.scale(0.6).move_to([-3.3, -0.15, 0]),
            settle=0.3,
            max_run=1.1,
        )
        lab_sel = panel_label("selective", C["gold"], x=-3.3)
        board.add(lab_sel, "lab_sel")
        self.play(FadeIn(lab_sel, shift=DOWN * 0.1), run_time=0.4)
        tn.wait_until("piled")

        mix_dots = make_dots(CLASS_ID)
        for d, p in zip(mix_dots, pos_rows(MIX_VALUES, CLASS_ID)):
            d.move_to(p)
        mix_chips = VGroup(
            *[
                labeled_box(name, width=1.05, height=0.38, color=CLASS_COLORS[i], font_size=19)
                for i, name in enumerate(CLASSES)
            ]
        )
        for i, chip in enumerate(mix_chips):
            chip.move_to([AX_X0 - 0.95, ROW_Y[i], 0])
        panel_r = VGroup(mix_dots, mix_chips, make_axis())
        panel_r.scale(0.6).move_to([3.3, -0.15, 0])
        self.play(FadeIn(panel_r, shift=LEFT * 0.2), run_time=0.6)
        self.play(
            LaggedStart(
                *[
                    Flash(d, color=d.get_color(), line_length=0.06, flash_radius=0.11)
                    for d in mix_dots
                ],
                lag_ratio=0.006,
            ),
            run_time=1.0,
        )
        tn.wait_until("everything")
        lab_mix = panel_label("mixed", C["wrong"], x=3.3)
        board.add(lab_mix, "lab_mix")
        note_units = board.set_bottom(bottom_note("two units — same dataset", color=C["label"]))
        self.play(FadeIn(lab_mix, shift=DOWN * 0.1), FadeIn(note_units), run_time=0.45)
        board.assert_clear()
        _soft_until(tn, self, "collapse", lab_sel, lab_mix, max_t=0.9)

        # ══ 9. Collapse to class means → mu_max and the rest ══
        tn.wait_until("collapse")
        self.play(FadeOut(panel_r), FadeOut(lab_mix), FadeOut(note_units), run_time=0.4)
        board.clear("lab_mix", "bottom")

        bar_x = [-1.41, -0.47, 0.47, 1.41]
        bars = [make_bar(SEL_MEANS[c], bar_x[c], CLASS_COLORS[c]) for c in range(4)]
        bar_chips = VGroup(
            *[
                safe_text(CLASSES[c], font_size=17, color=CLASS_COLORS[c]).move_to(
                    [bar_x[c], BAR_FLOOR - 0.28, 0]
                )
                for c in range(4)
            ]
        )
        subs = [VGroup(*[dots[i] for i in range(N_TOTAL) if CLASS_ID[i] == c]) for c in range(4)]
        self.remove(dots)
        for s in subs:
            self.add(s)
        bars_lab = panel_label("class means", C["label"], x=0.0)
        self.play(
            *[ReplacementTransform(subs[c], bars[c]) for c in range(4)],
            FadeOut(row_chips),
            FadeOut(axis),
            ReplacementTransform(lab_sel, bars_lab),
            FadeIn(bar_chips),
            run_time=1.2,
        )
        board.clear("lab_sel")
        board.add(bars_lab, "bars_lab")

        mu_c = MathTex(r"\mu_c", font_size=EQ_SIZE)
        board.set_bottom(mu_c)
        tn.play_before("biggest", Write(mu_c), settle=0.3, max_run=0.8)
        tn.wait_until("biggest")

        gold_bar = bars[0]
        self.play(
            gold_bar.animate.set_fill(C["gold"], 0.95).set_stroke(C["gold"], 2.5),
            run_time=0.35,
        )
        pop_named(self, gold_bar, color=C["gold"], run_time=0.5, settle=0.12)
        mu_max_eq = MathTex(r"\mu_{\max}", r"=", r"\max_c\, \mu_c", font_size=EQ_SIZE - 4)
        board.set_bottom(mu_max_eq)
        self.play(TransformMatchingTex(mu_c, mu_max_eq), run_time=0.7)
        lab_max = MathTex(r"\mu_{\max}", font_size=30, color=C["gold"])
        lab_max.move_to([bar_x[0], bar_top(SEL_MEANS[0]) + 0.3, 0])
        self.play(FadeIn(lab_max, shift=UP * 0.1), run_time=0.4)
        board.add(lab_max, "lab_max")
        _soft_until(tn, self, "remaining", gold_bar, lab_max, max_t=0.8)

        tn.wait_until("remaining")
        rest_bar = make_bar(REST_VAL, 0.5, C["dim"])
        bars_lab2 = panel_label("favourite class vs. the rest", C["label"], x=0.0)
        tn.play_before(
            "gap",
            ReplacementTransform(VGroup(bars[1], bars[2], bars[3]), rest_bar),
            Transform(bars_lab, bars_lab2),
            FadeOut(bar_chips[1]),
            FadeOut(bar_chips[2]),
            FadeOut(bar_chips[3]),
            gold_bar.animate.move_to([-0.5, BAR_FLOOR, 0], aligned_edge=DOWN),
            lab_max.animate.move_to([-0.5, bar_top(SEL_MEANS[0]) + 0.3, 0]),
            bar_chips[0].animate.move_to([-0.5, BAR_FLOOR - 0.28, 0]),
            settle=0.5,
            max_run=1.0,
        )
        lab_rest = MathTex(r"\mu_{-\max}", font_size=30, color=C["dim"])
        lab_rest.move_to([0.5, bar_top(REST_VAL) + 0.3, 0])
        rest_chip = safe_text("other classes", font_size=15, color=C["dim"]).move_to(
            [0.72, BAR_FLOOR - 0.28, 0]
        )
        board.add(lab_rest, "lab_rest")
        self.play(FadeIn(lab_rest, shift=UP * 0.1), FadeIn(rest_chip), run_time=0.45)
        mu_rest_eq = MathTex(
            r"\mu_{-\max}", r"=", r"\mathrm{mean}_{c\neq\max}\, \mu_c", font_size=EQ_SIZE - 8
        )
        board.set_bottom(mu_rest_eq)
        self.play(TransformMatchingTex(mu_max_eq, mu_rest_eq), run_time=0.8)
        board.assert_clear()

        # ══ 10. BUILD_UP the selectivity index ══
        tn.wait_until("gap")
        level = DashedLine(
            [-1.05, bar_top(REST_VAL), 0],
            [1.05, bar_top(REST_VAL), 0],
            stroke_width=2,
            color=C["dim"],
        )
        gap_arrow = DoubleArrow(
            [-0.5, bar_top(REST_VAL), 0],
            [-0.5, bar_top(SEL_MEANS[0]), 0],
            buff=0.02,
            stroke_width=3,
            color=C["highlight"],
            max_tip_length_to_length_ratio=0.11,
        )
        self.play(Create(level), GrowArrow(gap_arrow), run_time=0.6)
        num_eq = MathTex(r"\mu_{\max}", r"-", r"\mu_{-\max}", font_size=EQ_SIZE - 4)
        board.set_bottom(num_eq)
        tn.play_before("divide", TransformMatchingTex(mu_rest_eq, num_eq), settle=0.3, max_run=1.0)
        tn.wait_until("divide")

        frac_eq = MathTex(
            r"\frac{\mu_{\max}-\mu_{-\max}}{\mu_{\max}+\mu_{-\max}}", font_size=EQ_SIZE - 4
        )
        board.set_bottom(frac_eq)
        self.play(
            ReplacementTransform(num_eq, frac_eq),
            Indicate(gold_bar, color=C["accent"], scale_factor=1.03),
            Indicate(rest_bar, color=C["accent"], scale_factor=1.03),
            run_time=0.9,
        )
        _soft_until(tn, self, "index", frac_eq, max_t=0.8)

        tn.wait_until("index")
        si_eq = MathTex(
            r"\mathrm{SI}",
            r"=",
            r"\frac{\mu_{\max}-\mu_{-\max}}{\mu_{\max}+\mu_{-\max}}",
            font_size=EQ_SIZE - 6,
        )
        board.set_bottom(si_eq)
        self.play(TransformMatchingTex(frac_eq, si_eq), run_time=0.85)
        dial = Dial(SI_SEL, label="selectivity", color=C["accent"])
        dial.scale(0.92).move_to([4.6, 0.15, 0])
        self.play(FadeIn(dial, scale=0.9), run_time=0.55)
        pop_named(self, si_eq, color=C["accent"], run_time=0.5, settle=0.15)
        _soft_until(tn, self, "ends", dial, max_t=0.8)

        # ══ 11. Read the endpoints ══
        tn.wait_until("ends")
        self.play(Indicate(dial.arc, color=C["accent"], scale_factor=1.04), run_time=0.55)
        tn.wait_until("favorite")
        self.play(
            morph_bar(rest_bar, 0.02),
            lab_rest.animate.move_to([0.5, bar_top(0.02) + 0.3, 0]),
            FadeOut(level),
            FadeOut(gap_arrow),
            run_time=0.9,
            rate_func=smooth,
        )
        dial.set_value(1.0, scene=self, run_time=0.7, color=C["right"])
        hold = max(0.0, min(1.2, tn.span_until("preference") - 3.4))
        if hold > 0.05:
            self.wait(hold)
        flat = 0.45
        tn.play_before(
            "preference",
            morph_bar(gold_bar, flat, color=C["dim"]),
            morph_bar(rest_bar, flat),
            lab_max.animate.move_to([-0.5, bar_top(flat) + 0.3, 0]),
            lab_rest.animate.move_to([0.5, bar_top(flat) + 0.3, 0]),
            settle=0.5,
            max_run=1.1,
        )
        dial.set_value(0.0, scene=self, run_time=0.7, color=C["wrong"])
        tn.wait_until("preference")

        self.play(
            morph_bar(gold_bar, SEL_MEANS[0], color=C["gold"]),
            morph_bar(rest_bar, REST_VAL, color=C["dim"]),
            lab_max.animate.move_to([-0.5, bar_top(SEL_MEANS[0]) + 0.3, 0]),
            lab_rest.animate.move_to([0.5, bar_top(REST_VAL) + 0.3, 0]),
            *dial.value_anims(SI_SEL, color=C["accent"]),
            run_time=0.8,
        )

        # ══ 12. Loudness trap — the ratio, not the raw gap ══
        tn.wait_until("faked")
        raw_gap = SEL_MEANS[0] - REST_VAL
        gap_chip = VGroup(
            safe_text("raw gap", font_size=19, color=C["wrong"]),
            safe_text(f"{raw_gap:.2f}", font_size=26, color=C["wrong"]),
        ).arrange(DOWN, buff=0.1).move_to([-4.4, 0.45, 0])
        board.add(gap_chip, "gap_chip")
        self.play(FadeIn(gap_chip, shift=RIGHT * 0.12), run_time=0.5)
        tn.wait_until("volume")

        ghost = VGroup(gold_bar.copy(), rest_bar.copy())
        ghost.set_fill(opacity=0.0).set_stroke(C["dim"], 1.6, opacity=0.55)
        self.add(ghost)
        factor = 2.2
        new_gap = safe_text(f"{raw_gap * factor:.2f}", font_size=26, color=C["wrong"])
        new_gap.move_to(gap_chip[1])
        self.play(
            morph_bar(gold_bar, SEL_MEANS[0] * factor),
            morph_bar(rest_bar, REST_VAL * factor),
            lab_max.animate.move_to([-0.5, bar_top(SEL_MEANS[0] * factor) + 0.3, 0]),
            lab_rest.animate.move_to([0.5, bar_top(REST_VAL * factor) + 0.3, 0]),
            Transform(gap_chip[1], new_gap),
            run_time=1.6,
            rate_func=smooth,
        )
        self.play(Indicate(gap_chip, color=C["wrong"], scale_factor=1.12), run_time=0.6)
        tn.wait_until("shape")
        key_shape = key_sentence(
            self,
            "same shape — just louder",
            color=C["label"],
            font_size=26,
            hold=0.08,
            park="left",
            board=board,
        )
        self.play(Indicate(ghost, color=C["dim"], scale_factor=1.03), run_time=0.6)
        tn.wait_until("ratio")
        dial.set_value(SI_SEL, scene=self, run_time=0.5)
        self.play(
            Indicate(dial, color=C["right"], scale_factor=1.06),
            Indicate(si_eq, color=C["right"], scale_factor=1.04),
            run_time=0.8,
        )
        _soft_until(tn, self, "warning", dial, max_t=0.7)

        # ══ 13. A high index is not importance ══
        tn.wait_until("warning")
        self.play(
            FadeOut(gold_bar),
            FadeOut(rest_bar),
            FadeOut(ghost),
            FadeOut(lab_max),
            FadeOut(lab_rest),
            FadeOut(bar_chips[0]),
            FadeOut(rest_chip),
            FadeOut(gap_chip),
            FadeOut(key_shape),
            FadeOut(si_eq),
            FadeOut(bars_lab),
            dial.animate.scale(0.62).move_to([5.35, 1.05, 0]),
            run_time=0.6,
        )
        board.clear("key", "bottom", "gap_chip", "lab_max", "lab_rest", "bars_lab")

        net2, layers2, edges2 = make_net(radius=0.13, layer_buff=0.8, node_buff=0.22)
        net2.scale(0.85).move_to([-2.5, -0.15, 0])
        sel_unit = layers2[1][3]
        mixed_unit = layers2[1][1]
        sel_unit.set_fill(C["gold"], 0.95).set_stroke(C["gold"], 2.5)
        acc_track = Rectangle(
            width=0.7, height=2.5, stroke_color=C["dim"], stroke_width=1.6, fill_opacity=0
        ).move_to([2.0, BAR_FLOOR + 1.25, 0])
        full_acc = 1.72
        acc_bar = make_bar(full_acc, 2.0, C["right"], width=0.7)
        acc_lab = panel_label("accuracy", C["right"], x=2.0)
        board.add(acc_lab, "acc_lab")
        self.play(FadeIn(net2), FadeIn(acc_track), FadeIn(acc_lab), run_time=0.6)
        self.play(GrowFromEdge(acc_bar, DOWN), run_time=0.6)
        base_line = DashedLine(
            [1.45, bar_top(full_acc), 0],
            [2.55, bar_top(full_acc), 0],
            stroke_width=2,
            color=C["dim"],
        )
        self.play(Create(base_line), run_time=0.3)
        pop_named(self, sel_unit, color=C["gold"], run_time=0.5, settle=0.12)
        tn.wait_until("Delete")

        cross_sel = Cross(sel_unit, stroke_color=C["wrong"], stroke_width=4).scale(1.35)
        self.play(
            Create(cross_sel),
            sel_unit.animate.set_fill(C["gold"], 0.22).set_stroke(C["gold"], 2, opacity=0.55),
            run_time=0.6,
        )
        self.play(morph_bar(acc_bar, full_acc * 0.97), run_time=0.7)
        small_drop = safe_text("barely moves", font_size=20, color=C["label"]).move_to(
            [3.85, -1.25, 0]
        )
        self.play(FadeIn(small_drop, shift=UP * 0.1), run_time=0.4)
        _soft_until(tn, self, "worse", dial, max_t=0.7)

        tn.wait_until("worse")
        cross_mix = Cross(mixed_unit, stroke_color=C["wrong"], stroke_width=4).scale(1.35)
        self.play(
            FadeOut(cross_sel),
            sel_unit.animate.set_fill(C["gold"], 0.95).set_stroke(C["gold"], 2.5, opacity=1.0),
            Create(cross_mix),
            mixed_unit.animate.set_fill(C["dim"], 0.15).set_stroke(WHITE, 2, opacity=0.4),
            FadeOut(small_drop),
            run_time=0.7,
        )
        self.play(morph_bar(acc_bar, full_acc * 0.84), run_time=0.7)
        big_drop = safe_text("real damage", font_size=20, color=C["wrong"]).move_to(
            [3.85, -1.25, 0]
        )
        note_imp = board.set_bottom(bottom_note("selective is not the same as relied upon", color=C["wrong"]))
        self.play(FadeIn(big_drop, shift=UP * 0.1), FadeIn(note_imp), run_time=0.5)
        _soft_until(tn, self, "labels", dial, max_t=0.7)

        # ══ 14. The index only sees your labels ══
        tn.wait_until("labels")
        self.play(
            FadeOut(net2),
            FadeOut(cross_mix),
            FadeOut(acc_track),
            FadeOut(acc_bar),
            FadeOut(acc_lab),
            FadeOut(base_line),
            FadeOut(big_drop),
            FadeOut(note_imp),
            run_time=0.5,
        )
        board.clear("acc_lab", "bottom")

        mix2 = make_dots(CLASS_ID)
        for d, p in zip(mix2, pos_rows(MIX_VALUES, CLASS_ID)):
            d.move_to(p)
        chips2 = VGroup(
            *[
                labeled_box(name, width=1.05, height=0.38, color=CLASS_COLORS[i], font_size=19)
                for i, name in enumerate(CLASSES)
            ]
        )
        for i, chip in enumerate(chips2):
            chip.move_to([AX_X0 - 0.95, ROW_Y[i], 0])
        group2 = VGroup(mix2, chips2, make_axis())
        centre0 = group2.get_center().copy()
        scale2, centre2 = 0.82, np.array([-0.6, -0.15, 0.0])
        group2.scale(scale2).move_to(centre2)

        def to_stage(points: np.ndarray) -> np.ndarray:
            """Map original-frame points into the scaled/moved panel frame."""
            return (np.asarray(points) - centre0) * scale2 + centre2

        self.play(FadeIn(group2, shift=UP * 0.15), run_time=0.7)
        dial.set_value(SI_MIX, scene=self, run_time=0.7, color=C["wrong"])
        _soft_until(tn, self, "tuned", mix2, max_t=0.6)

        tn.wait_until("tuned")
        tex_targets = to_stage(pos_rows(MIX_VALUES, TEX_ID))
        tex_chips = VGroup()
        for i, name in enumerate(TEXTURES):
            chip = labeled_box(name, width=1.05, height=0.38, color=CLASS_COLORS[i], font_size=21)
            chip.scale(scale2).move_to(chips2[i].get_center())
            tex_chips.add(chip)
        self.play(
            *[Transform(chips2[i], tex_chips[i]) for i in range(len(TEXTURES))],
            *[
                mix2[i].animate.move_to(tex_targets[i]).set_color(CLASS_COLORS[int(TEX_ID[i])])
                for i in range(N_TOTAL)
            ],
            run_time=1.5,
            rate_func=smooth,
        )
        dial.set_value(SI_TEX, scene=self, run_time=0.8, color=C["accent"])
        key_labels = key_sentence(
            self,
            "selectivity is relative to your labels",
            color=C["highlight"],
            font_size=26,
            hold=0.08,
            park="left",
            board=board,
        )
        _soft_until(tn, self, "several", dial, max_t=0.7)

        tn.wait_until("several")
        self.play(
            LaggedStart(
                *[Indicate(chips2[i], color=C["highlight"], scale_factor=1.14) for i in range(3)],
                lag_ratio=0.35,
            ),
            run_time=1.5,
        )
        note_poly = board.set_bottom(
            bottom_note("one unit, several unrelated features", color=C["label"])
        )
        self.play(FadeIn(note_poly), run_time=0.4)
        _soft_until(tn, self, "separates", mix2, max_t=0.8)

        # ══ 15. Settle ══
        tn.wait_until("separates")
        self.play(
            FadeOut(group2),
            FadeOut(key_labels),
            FadeOut(note_poly),
            FadeOut(dial),
            run_time=0.6,
        )
        board.clear()

        takeaway = MathTex(
            r"\mathrm{SI}",
            r"=",
            r"\frac{\mu_{\max}-\mu_{-\max}}{\mu_{\max}+\mu_{-\max}}",
            font_size=EQ_SIZE,
        )
        takeaway.move_to([0.0, 0.8, 0])
        board.add(takeaway, "takeaway")
        tn.play_before("normalized", Write(takeaway), settle=0.4, max_run=1.2)

        mini_gold = make_bar(SEL_MEANS[0] * 0.6, -4.05, C["gold"], width=0.45)
        mini_rest = make_bar(REST_VAL * 0.6, -3.15, C["dim"], width=0.45)
        mini_sel_lab = safe_text("selective", font_size=18, color=C["gold"]).move_to(
            [-3.6, BAR_FLOOR - 0.32, 0]
        )
        mini_dots = make_dots(CLASS_ID)
        for d, p in zip(mini_dots, pos_rows(MIX_VALUES, CLASS_ID)):
            d.move_to(p)
        mini_dots.scale(0.36).move_to([3.6, -0.95, 0])
        mini_mix_lab = safe_text("mixed", font_size=18, color=C["wrong"]).move_to(
            [3.6, BAR_FLOOR - 0.32, 0]
        )
        self.play(
            GrowFromEdge(mini_gold, DOWN),
            GrowFromEdge(mini_rest, DOWN),
            FadeIn(mini_sel_lab),
            FadeIn(mini_dots, shift=UP * 0.1),
            FadeIn(mini_mix_lab),
            run_time=0.8,
        )
        tn.wait_until("normalized")
        key_end = key_sentence(
            self,
            "one class high, the rest low?",
            color=C["highlight"],
            font_size=30,
            hold=0.1,
            park="left",
            board=board,
        )
        tn.wait_until("reads")
        final_note = board.set_bottom(
            bottom_note("what the unit responds to — not what the network reads", color=C["accent"])
        )
        self.play(FadeIn(final_note), run_time=0.5)
        board.assert_clear()
        soft_idle(self, takeaway, mini_gold, mini_dots, run_time=0.8)

        tn.wait_until_end(pad=0.4)
