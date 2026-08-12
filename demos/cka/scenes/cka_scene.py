"""CKA explainer v2 — Wrong→Right with formula BUILD_UP morphs + play_before sync."""

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

# Toy activation matrices (n examples × d features) — readable heatmaps
RNG = np.random.default_rng(7)
N_EX = 6
D_X, D_Y = 4, 5


def _acts() -> tuple[np.ndarray, np.ndarray]:
    x = RNG.normal(size=(N_EX, D_X))
    y = np.concatenate(
        [x @ RNG.normal(size=(D_X, 3)), RNG.normal(size=(N_EX, 2)) * 0.4],
        axis=1,
    )
    return x, y[:, :D_Y]


X_ACT, Y_ACT = _acts()
K_RAW = X_ACT @ X_ACT.T
L_RAW = Y_ACT @ Y_ACT.T


def _center_gram(g: np.ndarray) -> np.ndarray:
    n = g.shape[0]
    h = np.eye(n) - np.ones((n, n)) / n
    return h @ g @ h


K_C = _center_gram(K_RAW)
L_C = _center_gram(L_RAW)


def make_neural_net(
    sizes=(3, 5, 4, 2),
    *,
    radius: float = 0.13,
    layer_buff: float = 0.85,
    node_buff: float = 0.22,
    stroke_opacity: float = 0.28,
) -> tuple[VGroup, list[VGroup], VGroup]:
    layers: list[VGroup] = []
    for n in sizes:
        layer = VGroup(
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
        layers.append(layer)
    layer_row = VGroup(*layers).arrange(RIGHT, buff=layer_buff)
    layer_row.move_to(ORIGIN + DOWN * 0.2)

    edges = VGroup()
    for left, right in zip(layers[:-1], layers[1:]):
        for i, a in enumerate(left):
            mid = int(round(i * (len(right) - 1) / max(len(left) - 1, 1)))
            for j in sorted({mid, max(0, mid - 1), min(len(right) - 1, mid + 1)}):
                edges.add(
                    Line(
                        a.get_right(),
                        right[j].get_left(),
                        stroke_width=1.2,
                        color=GREY_B,
                        stroke_opacity=stroke_opacity,
                    )
                )
    net = VGroup(edges, *layers)
    return net, layers, edges


def make_heatmap(
    mat: np.ndarray,
    *,
    side: float = 2.4,
    cmap_lo=BLUE_E,
    cmap_hi=YELLOW_C,
) -> VGroup:
    """Grid of cells colored by matrix values (min-max within mat)."""
    m = np.asarray(mat, dtype=float)
    lo, hi = float(np.min(m)), float(np.max(m))
    span = (hi - lo) or 1.0
    n = m.shape[0]
    cell = side / n
    cells = VGroup()
    for i in range(n):
        for j in range(n):
            t = (m[i, j] - lo) / span
            col = interpolate_color(cmap_lo, cmap_hi, t)
            sq = Square(
                side_length=cell * 0.92,
                fill_color=col,
                fill_opacity=0.92,
                stroke_width=0.6,
                stroke_color=GREY_B,
            )
            sq.move_to(
                RIGHT * ((j + 0.5) * cell - side / 2)
                + UP * ((n - 0.5 - i) * cell - side / 2)
            )
            cells.add(sq)
    border = Square(side_length=side, stroke_color=WHITE, stroke_width=1.5, fill_opacity=0)
    return VGroup(border, cells)


def score_dial(value: float, *, label: str = "score", color=C["accent"]) -> VGroup:
    """Simple [0,1] dial with needle."""
    arc = Arc(radius=0.85, start_angle=PI, angle=-PI, color=C["dim"], stroke_width=6)
    needle = Line(ORIGIN, LEFT * 0.75, color=color, stroke_width=4)
    needle.rotate(-value * PI, about_point=ORIGIN)
    tip = Dot(needle.get_end(), radius=0.06, color=color)
    lab = safe_text(label, font_size=18, color=C["label"])
    val = safe_text(f"{value:.2f}", font_size=22, color=color)
    lab.next_to(arc, DOWN, buff=0.18)
    val.next_to(lab, DOWN, buff=0.08)
    return VGroup(arc, needle, tip, lab, val)


def _soft_until(tn: TimedNarration, scene: Scene, bookmark: str, *mobs, max_t: float = 1.0) -> None:
    """Breathe through baked audio pause until the next bookmark."""
    rem = tn.span_until(bookmark)
    if rem > 0.28 and mobs:
        soft_idle(scene, *mobs, run_time=min(rem * 0.85, max_t))


class CKAScene(Scene):
    def construct(self) -> None:
        tn = TimedNarration(DEMO_DIR / "timing.json", DEMO_DIR / "audio" / "narration.mp3")
        tn.attach(self)
        board = LayoutBoard()

        # ── HOOK: two nets ─────────────────────────────────────────
        title = board.set_title(section_title("Centered Kernel Alignment"))
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.7)
        tn.wait_until("train")

        net_a, layers_a, edges_a = make_neural_net((3, 5, 4, 2))
        net_b, layers_b, edges_b = make_neural_net((3, 6, 4, 2))
        net_a.scale(0.85).move_to(LEFT * 3.3 + DOWN * 0.25)
        net_b.scale(0.85).move_to(RIGHT * 3.3 + DOWN * 0.25)
        lab_a = panel_label("Net A", C["primary"], x=-3.3)
        lab_b = panel_label("Net B", C["secondary"], x=3.3)
        board.add(lab_a, "lab_a")
        board.add(lab_b, "lab_b")

        tn.play_before(
            "seeds",
            LaggedStart(
                *[GrowFromCenter(n) for layer in layers_a for n in layer],
                lag_ratio=0.03,
            ),
            LaggedStart(
                *[GrowFromCenter(n) for layer in layers_b for n in layer],
                lag_ratio=0.03,
            ),
            FadeIn(lab_a),
            FadeIn(lab_b),
            settle=0.4,
            max_run=1.5,
        )
        self.play(Create(edges_a), Create(edges_b), run_time=0.5)
        tn.wait_until("seeds")
        _soft_until(tn, self, "Pick", net_a, net_b, max_t=0.9)

        # Pick a layer from each
        tn.wait_until("Pick")
        hid_a, hid_b = layers_a[1], layers_b[1]
        focus_a = SurroundingRectangle(hid_a, buff=0.12, color=C["primary"], stroke_width=2.5)
        focus_b = SurroundingRectangle(hid_b, buff=0.12, color=C["secondary"], stroke_width=2.5)
        tn.play_before(
            "represent",
            FadeIn(focus_a),
            FadeIn(focus_b),
            *[n.animate.set_fill(C["primary"], 0.8).set_color(C["primary"]) for n in hid_a],
            *[n.animate.set_fill(C["secondary"], 0.8).set_color(C["secondary"]) for n in hid_b],
            edges_a.animate.set_stroke(opacity=0.12),
            edges_b.animate.set_stroke(opacity=0.12),
            VGroup(layers_a[0], layers_a[2], layers_a[3]).animate.set_opacity(0.25),
            VGroup(layers_b[0], layers_b[2], layers_b[3]).animate.set_opacity(0.25),
            settle=0.35,
            max_run=1.0,
        )
        pop_named(self, hid_a, hid_b, focus_a, focus_b, color=C["accent"], run_time=0.55, settle=0.2)
        tn.wait_until("represent")

        # Question over highlighted layers
        self.play(FadeOut(title), run_time=0.25)
        board.clear("title")
        q = ask_about(
            self,
            "Do they represent the world the same way?",
            hid_a,
            hid_b,
            hold=0.08,
            park="left",
            board=board,
            font_size=26,
            motion_time=0.75,
            color=C["highlight"],
        )
        tn.wait_until("measure")
        _soft_until(tn, self, "match", hid_a, hid_b, q, max_t=1.15)

        # ── WRONG #1: neuron matching ──────────────────────────────
        tn.wait_until("match")
        self.play(FadeOut(q), run_time=0.25)
        board.clear()
        fade_rest = VGroup(
            edges_a,
            edges_b,
            layers_a[0],
            layers_a[2],
            layers_a[3],
            layers_b[0],
            layers_b[2],
            layers_b[3],
        )
        self.play(FadeOut(fade_rest), run_time=0.35)
        tn.play_before(
            "Correlate",
            hid_a.animate.arrange(DOWN, buff=0.28).move_to(LEFT * 3.0 + DOWN * 0.1),
            hid_b.animate.arrange(DOWN, buff=0.28).move_to(RIGHT * 3.0 + DOWN * 0.1),
            lab_a.animate.move_to(LEFT * 3.0 + UP * PANEL_LABEL_Y),
            lab_b.animate.move_to(RIGHT * 3.0 + UP * PANEL_LABEL_Y),
            settle=0.3,
            max_run=0.7,
        )
        self.remove(focus_a, focus_b)
        focus_a = SurroundingRectangle(hid_a, buff=0.14, color=C["primary"], stroke_width=2)
        focus_b = SurroundingRectangle(hid_b, buff=0.14, color=C["secondary"], stroke_width=2)
        self.play(FadeIn(focus_a), FadeIn(focus_b), run_time=0.3)

        n_pair = min(len(hid_a), len(hid_b))
        pairings = VGroup()
        for i in range(n_pair):
            pairings.add(
                DashedLine(
                    hid_a[i].get_right(),
                    hid_b[i].get_left(),
                    color=C["wrong"],
                    stroke_width=2,
                    dash_length=0.12,
                )
            )
        self.play(LaggedStart(*[Create(p) for p in pairings], lag_ratio=0.1), run_time=0.7)
        tn.wait_until("Correlate")

        corr_chips = VGroup()
        for i in range(n_pair):
            chip = safe_text("ρ", font_size=20, color=C["wrong"])
            chip.move_to(pairings[i].get_center() + UP * 0.22)
            corr_chips.add(chip)
        self.play(
            LaggedStart(*[FadeIn(c, scale=0.8) for c in corr_chips], lag_ratio=0.1),
            run_time=0.7,
        )
        dial = score_dial(0.82, label="1-to-1", color=C["wrong"])
        dial.scale(0.9).move_to(ORIGIN + DOWN * 2.35)
        tn.play_before("shuffle", FadeIn(dial, scale=0.9), settle=0.4, max_run=0.6)
        tn.wait_until("shuffle")
        _soft_until(tn, self, "collapses", dial, max_t=0.5)

        # Permute units on B
        n_b = len(hid_b)
        order = [(i + 2) % n_b for i in range(n_b)]
        targets = [hid_b[i].get_center().copy() for i in range(n_b)]
        tn.play_before(
            "collapses",
            *[hid_b[i].animate.move_to(targets[order[i]]) for i in range(n_b)],
            settle=0.35,
            max_run=1.0,
            rate_func=smooth,
        )
        scrambled = VGroup()
        for i in range(n_pair):
            scrambled.add(
                DashedLine(
                    hid_a[i].get_right(),
                    hid_b[i].get_left(),
                    color=C["wrong"],
                    stroke_width=2,
                    dash_length=0.1,
                )
            )
        self.play(
            ReplacementTransform(pairings, scrambled),
            corr_chips.animate.set_opacity(0.35),
            run_time=0.55,
        )
        tn.wait_until("collapses")

        dial_low = score_dial(0.18, label="1-to-1", color=C["wrong"])
        dial_low.scale(0.9).move_to(dial.get_center())
        tn.play_before(
            "lied",
            FadeOut(corr_chips),
            ReplacementTransform(dial, dial_low),
            settle=0.4,
            max_run=0.9,
        )
        tn.wait_until("lied")
        ghost = board.set_bottom(
            bottom_note("same geometry — different bookkeeping", color=C["wrong"])
        )
        self.play(FadeIn(ghost), run_time=0.35)
        _soft_until(tn, self, "flatten", hid_a, hid_b, dial_low, max_t=0.8)

        # ── WRONG #2: flatten + cosine ─────────────────────────────
        tn.wait_until("flatten")
        self.play(
            FadeOut(scrambled),
            FadeOut(dial_low),
            FadeOut(focus_a),
            FadeOut(focus_b),
            FadeOut(ghost),
            FadeOut(lab_a),
            FadeOut(lab_b),
            run_time=0.4,
        )
        board.clear()

        mat_a = VGroup(
            *[
                Square(
                    side_length=0.28,
                    fill_color=C["primary"],
                    fill_opacity=0.3 + 0.5 * ((i + j) % 3) / 2,
                    stroke_width=0.8,
                )
                for i in range(4)
                for j in range(3)
            ]
        ).arrange_in_grid(4, 3, buff=0.04)
        mat_b = VGroup(
            *[
                Square(
                    side_length=0.28,
                    fill_color=C["secondary"],
                    fill_opacity=0.3 + 0.5 * ((i + 2 * j) % 3) / 2,
                    stroke_width=0.8,
                )
                for i in range(4)
                for j in range(3)
            ]
        ).arrange_in_grid(4, 3, buff=0.04)
        mat_a.move_to(LEFT * 3.2)
        mat_b.move_to(RIGHT * 3.2)
        tn.play_before(
            "cosine",
            ReplacementTransform(hid_a, mat_a),
            ReplacementTransform(hid_b, mat_b),
            settle=0.35,
            max_run=1.0,
        )
        tn.wait_until("cosine")

        vec_a = VGroup(
            *[
                Rectangle(
                    width=0.18,
                    height=0.35,
                    fill_color=C["primary"],
                    fill_opacity=0.7,
                    stroke_width=0.5,
                )
                for _ in range(12)
            ]
        ).arrange(RIGHT, buff=0.04)
        vec_b = VGroup(
            *[
                Rectangle(
                    width=0.18,
                    height=0.35,
                    fill_color=C["secondary"],
                    fill_opacity=0.7,
                    stroke_width=0.5,
                )
                for _ in range(12)
            ]
        ).arrange(RIGHT, buff=0.04)
        vec_a.move_to(LEFT * 2.5 + DOWN * 0.3)
        vec_b.move_to(RIGHT * 2.5 + DOWN * 0.3)
        tn.play_before(
            "scrambled",
            ReplacementTransform(mat_a, vec_a),
            ReplacementTransform(mat_b, vec_b),
            settle=0.5,
            max_run=1.1,
        )
        cos_arc = ArcBetweenPoints(
            vec_a.get_right(),
            vec_b.get_left(),
            angle=-TAU / 6,
            color=C["wrong"],
            stroke_width=3,
        )
        cos_lab = safe_text("cosine", font_size=22, color=C["wrong"])
        cos_lab.next_to(cos_arc, UP, buff=0.15)
        self.play(Create(cos_arc), FadeIn(cos_lab), run_time=0.65)
        tn.wait_until("scrambled")

        mess = key_sentence(
            self,
            "loses example geometry",
            color=C["wrong"],
            font_size=28,
            hold=0.1,
            park="left",
            board=board,
        )
        self.play(
            vec_a.animate.set_opacity(0.25),
            vec_b.animate.set_opacity(0.25),
            cos_arc.animate.set_opacity(0.35),
            run_time=0.75,
        )
        _soft_until(tn, self, "shared", mess, max_t=0.7)

        # ── RIGHT OBJECT: shared examples + Gram ───────────────────
        tn.wait_until("shared")
        self.play(
            FadeOut(vec_a),
            FadeOut(vec_b),
            FadeOut(cos_arc),
            FadeOut(cos_lab),
            FadeOut(mess),
            run_time=0.4,
        )
        board.clear()

        examples = VGroup(
            *[
                RoundedRectangle(
                    width=0.7,
                    height=0.45,
                    corner_radius=0.06,
                    color=C["accent"],
                    fill_opacity=0.3,
                    stroke_width=1.5,
                )
                for _ in range(N_EX)
            ]
        ).arrange(RIGHT, buff=0.18)
        examples.move_to(UP * 0.9)
        ex_nums = VGroup(
            *[
                safe_text(str(i + 1), font_size=16, color=C["label"]).move_to(examples[i])
                for i in range(N_EX)
            ]
        )
        ex_lab = safe_text("shared examples", font_size=22, color=C["highlight"])
        ex_lab.next_to(examples, UP, buff=0.2)
        board.add(ex_lab, "ex_lab")
        tn.play_before(
            "Feed",
            LaggedStart(*[FadeIn(e, shift=DOWN * 0.1) for e in examples], lag_ratio=0.08),
            FadeIn(ex_nums),
            FadeIn(ex_lab),
            settle=0.3,
            max_run=0.95,
        )
        tn.wait_until("Feed")

        box_x = RoundedRectangle(
            corner_radius=0.1,
            width=2.6,
            height=1.5,
            color=C["primary"],
            fill_opacity=0.15,
            stroke_width=2,
        )
        box_y = RoundedRectangle(
            corner_radius=0.1,
            width=2.6,
            height=1.5,
            color=C["secondary"],
            fill_opacity=0.15,
            stroke_width=2,
        )
        box_x.move_to(LEFT * 3.2 + DOWN * 1.1)
        box_y.move_to(RIGHT * 3.2 + DOWN * 1.1)
        tx = safe_text("repr X", font_size=22, color=C["primary"]).move_to(box_x)
        ty = safe_text("repr Y", font_size=22, color=C["secondary"]).move_to(box_y)
        arrows = VGroup(
            Arrow(
                examples.get_bottom() + LEFT * 1.2,
                box_x.get_top(),
                buff=0.12,
                color=C["primary"],
                stroke_width=2.5,
            ),
            Arrow(
                examples.get_bottom() + RIGHT * 1.2,
                box_y.get_top(),
                buff=0.12,
                color=C["secondary"],
                stroke_width=2.5,
            ),
        )
        tn.play_before(
            "matrices",
            FadeIn(box_x),
            FadeIn(box_y),
            FadeIn(tx),
            FadeIn(ty),
            GrowArrow(arrows[0]),
            GrowArrow(arrows[1]),
            settle=0.35,
            max_run=1.0,
        )
        tn.wait_until("matrices")

        # Formula stage 1: matrix shapes
        xy_eq = MathTex(
            r"X \in \mathbb{R}^{n \times p}",
            r",\quad",
            r"Y \in \mathbb{R}^{n \times q}",
            font_size=EQ_SIZE - 6,
        )
        board.set_bottom(xy_eq)
        tn.play_before("question", Write(xy_eq), settle=0.45, max_run=1.2)
        _soft_until(tn, self, "question", examples, xy_eq, max_t=0.9)
        tn.wait_until("question")

        self.play(FadeOut(ex_lab), run_time=0.25)
        board.clear("ex_lab")
        q_ex = ask_about(
            self,
            "which examples look similar?",
            *examples,
            hold=0.08,
            park="left",
            board=board,
            font_size=26,
            motion_time=0.8,
            color=C["highlight"],
        )
        tn.wait_until("similar")
        _soft_until(tn, self, "pair", examples, q_ex, max_t=1.0)

        # ── Gram BUILD_UP ──────────────────────────────────────────
        tn.wait_until("pair")
        self.play(
            FadeOut(q_ex),
            FadeOut(box_x),
            FadeOut(box_y),
            FadeOut(tx),
            FadeOut(ty),
            FadeOut(arrows),
            examples.animate.scale(0.65).to_edge(UP, buff=0.55),
            ex_nums.animate.scale(0.65),
            run_time=0.55,
        )
        board.clear("key")
        for i, num in enumerate(ex_nums):
            num.move_to(examples[i])

        # Partial: just the entry index idea
        k_part = MathTex(r"K_{ij}", font_size=EQ_SIZE - 2)
        board.set_bottom(k_part)
        tn.play_before(
            "entry",
            ReplacementTransform(xy_eq, k_part),
            settle=0.4,
            max_run=1.2,
        )
        tn.wait_until("entry")

        k_ij = MathTex(
            r"K_{ij}",
            r"=",
            r"\langle x_i,\, x_j\rangle",
            font_size=EQ_SIZE - 4,
        )
        board.set_bottom(k_ij)
        tn.play_before(
            "Gram",
            TransformMatchingTex(k_part, k_ij),
            settle=0.4,
            max_run=1.3,
        )
        self.play(Indicate(k_ij[-1], color=C["accent"], scale_factor=1.08), run_time=0.7)
        tn.wait_until("Gram")

        # Heatmaps begin growing as we name Gram
        hm_k = make_heatmap(K_RAW, side=2.6, cmap_lo=BLUE_E, cmap_hi=YELLOW_C)
        hm_l = make_heatmap(L_RAW, side=2.6, cmap_lo=TEAL_E, cmap_hi=YELLOW_C)
        hm_k.move_to(LEFT * 3.2 + DOWN * 0.35)
        hm_l.move_to(RIGHT * 3.2 + DOWN * 0.35)
        pl_k = panel_label("K  (X)", C["primary"], x=-3.2)
        pl_l = panel_label("L  (Y)", C["secondary"], x=3.2)
        board.add(pl_k, "pl_k")
        board.add(pl_l, "pl_l")

        tn.play_before(
            "transpose",
            LaggedStart(*[GrowFromCenter(c) for c in hm_k[1]], lag_ratio=0.02),
            LaggedStart(*[GrowFromCenter(c) for c in hm_l[1]], lag_ratio=0.02),
            FadeIn(hm_k[0]),
            FadeIn(hm_l[0]),
            FadeIn(pl_k),
            FadeIn(pl_l),
            settle=0.4,
            max_run=1.6,
        )
        tn.wait_until("transpose")

        k_xx = MathTex(
            r"K",
            r"=",
            r"XX^{\top}",
            r",\quad",
            r"L",
            r"=",
            r"YY^{\top}",
            font_size=EQ_SIZE - 4,
        )
        board.set_bottom(k_xx)
        tn.play_before(
            "kernel",
            TransformMatchingTex(k_ij, k_xx),
            settle=0.35,
            max_run=1.0,
        )
        tn.wait_until("kernel")
        pop_named(self, hm_k, pl_k, color=C["accent"], run_time=0.55, settle=0.2)
        pop_named(self, hm_l, pl_l, color=C["accent"], run_time=0.55, settle=0.2)
        _soft_until(tn, self, "trap", hm_k, hm_l, max_t=1.0)

        # ── CENTERING ─────────────────────────────────────────────
        tn.wait_until("trap")
        self.play(FadeOut(examples), FadeOut(ex_nums), FadeOut(k_xx), run_time=0.35)
        board.clear("bottom")
        trap_cap = key_sentence(
            self,
            "constant offset can fake agreement",
            color=C["wrong"],
            font_size=26,
            hold=0.08,
            park="left",
            board=board,
        )
        glow_k = hm_k[0].copy().set_stroke(C["wrong"], 4).set_fill(opacity=0)
        glow_l = hm_l[0].copy().set_stroke(C["wrong"], 4).set_fill(opacity=0)
        self.play(FadeIn(glow_k), FadeIn(glow_l), run_time=0.45)
        tn.wait_until("inflate")
        self.play(
            Indicate(glow_k, color=C["wrong"], scale_factor=1.04),
            Indicate(glow_l, color=C["wrong"], scale_factor=1.04),
            run_time=0.7,
        )
        _soft_until(tn, self, "center", hm_k, hm_l, max_t=0.6)

        tn.wait_until("center")
        self.play(FadeOut(trap_cap), FadeOut(glow_k), FadeOut(glow_l), run_time=0.25)
        board.clear("key")
        center_cap = key_sentence(
            self,
            "center",
            color=C["highlight"],
            font_size=32,
            hold=0.05,
            park="left",
            board=board,
        )
        # Short gap to Introduce — land quickly
        tn.wait_until("Introduce")

        h_eq = MathTex(
            r"H",
            r"=",
            r"I - \tfrac{1}{n}11^{\top}",
            font_size=EQ_SIZE - 4,
        )
        board.set_bottom(h_eq)
        tn.play_before("multiply", Write(h_eq), settle=0.45, max_run=1.4)
        self.play(Indicate(h_eq, color=C["accent"], scale_factor=1.06), run_time=0.7)
        _soft_until(tn, self, "multiply", h_eq, max_t=1.0)
        tn.wait_until("multiply")

        hkh_eq = MathTex(
            r"\tilde{K}",
            r"=",
            r"HKH",
            r",\quad",
            r"\tilde{L}",
            r"=",
            r"HLH",
            font_size=EQ_SIZE - 6,
        )
        board.set_bottom(hkh_eq)
        tn.play_before(
            "tilde",
            TransformMatchingTex(h_eq, hkh_eq),
            settle=0.35,
            max_run=1.1,
        )
        self.play(Indicate(hkh_eq[2], color=C["gold"], scale_factor=1.1), run_time=0.65)
        tn.wait_until("tilde")

        hm_kc = make_heatmap(K_C, side=2.6, cmap_lo=BLUE_E, cmap_hi=YELLOW_C)
        hm_lc = make_heatmap(L_C, side=2.6, cmap_lo=TEAL_E, cmap_hi=YELLOW_C)
        hm_kc.move_to(hm_k.get_center())
        hm_lc.move_to(hm_l.get_center())
        pl_kt = MathTex(r"\tilde{K}", font_size=36, color=C["primary"])
        pl_lt = MathTex(r"\tilde{L}", font_size=36, color=C["secondary"])
        pl_kt.move_to(LEFT * 3.2 + UP * PANEL_LABEL_Y)
        pl_lt.move_to(RIGHT * 3.2 + UP * PANEL_LABEL_Y)

        tn.play_before(
            "relative",
            ReplacementTransform(hm_k, hm_kc),
            ReplacementTransform(hm_l, hm_lc),
            ReplacementTransform(pl_k, pl_kt),
            ReplacementTransform(pl_l, pl_lt),
            FadeOut(center_cap),
            settle=0.4,
            max_run=1.3,
        )
        board.clear("key")
        board.clear("pl_k", "pl_l")
        board.add(pl_kt, "pl_kt")
        board.add(pl_lt, "pl_lt")
        tn.wait_until("relative")
        pop_named(self, pl_kt, pl_lt, color=C["accent"], run_time=0.55, settle=0.25)
        self.play(FadeOut(hkh_eq), run_time=0.3)
        board.clear("bottom")
        rel_note = board.set_bottom(
            bottom_note("only relative geometry remains", color=C["accent"])
        )
        self.play(FadeIn(rel_note), run_time=0.35)
        _soft_until(tn, self, "aligned", hm_kc, hm_lc, max_t=0.9)

        # ── Agreement → Frobenius → HSIC → CKA (motivate→compute→name) ──
        tn.wait_until("aligned")
        self.play(FadeOut(rel_note), run_time=0.25)
        board.clear("bottom")
        align_q = ask_about(
            self,
            "how aligned are these geometries?",
            hm_kc[0],
            hm_lc[0],  # borders only
            hold=0.08,
            park="left",
            board=board,
            font_size=26,
            motion_time=0.75,
            color=C["highlight"],
        )
        hm_fix = make_heatmap(K_C, side=2.6, cmap_lo=BLUE_E, cmap_hi=YELLOW_C)
        hm_lr = make_heatmap(L_C, side=2.6, cmap_lo=TEAL_E, cmap_hi=YELLOW_C)
        hm_fix.move_to(hm_kc.get_center())
        hm_lr.move_to(hm_lc.get_center())
        self.play(
            ReplacementTransform(hm_kc, hm_fix),
            ReplacementTransform(hm_lc, hm_lr),
            run_time=0.35,
        )
        hm_kc, hm_lc = hm_fix, hm_lr
        _soft_until(tn, self, "Look", hm_kc, hm_lc, max_t=1.0)

        # One cell (i,j) on both sides — agreement intuition
        tn.wait_until("Look")
        self.play(FadeOut(align_q), run_time=0.25)
        board.clear("key")
        n_hm = N_EX
        ij = 1 * n_hm + 2  # examples i=1, j=2
        cell_k = hm_kc[1][ij]
        cell_l = hm_lc[1][ij]
        ring_k = SurroundingRectangle(cell_k, buff=0.04, color=C["accent"], stroke_width=3)
        ring_l = SurroundingRectangle(cell_l, buff=0.04, color=C["accent"], stroke_width=3)
        self.play(Create(ring_k), Create(ring_l), run_time=0.55)
        pop_named(self, cell_k, cell_l, color=C["accent"], run_time=0.55, settle=0.2)

        tn.wait_until("alike")
        alike_lab = key_sentence(
            self,
            'both say "alike" → agreement',
            color=C["right"],
            font_size=26,
            hold=0.08,
            park="left",
            board=board,
        )
        self.play(
            cell_k.animate.set_stroke(C["right"], 3),
            cell_l.animate.set_stroke(C["right"], 3),
            run_time=0.45,
        )

        tn.wait_until("help")
        fight_lab = safe_text('disagree → does not help', font_size=22, color=C["wrong"])
        board.set_bottom(fight_lab)
        self.play(
            FadeOut(alike_lab),
            FadeIn(fight_lab),
            cell_k.animate.set_stroke(C["wrong"], 2),
            cell_l.animate.set_stroke(GREY_B, 1),
            run_time=0.55,
        )
        board.clear("key")
        _soft_until(tn, self, "matching", ring_k, ring_l, max_t=0.7)

        # Multiply matching cells → sum → Frobenius (name last)
        tn.wait_until("matching")
        self.play(FadeOut(fight_lab), run_time=0.2)
        board.clear("bottom")
        self.play(
            cell_k.animate.set_stroke(C["gold"], 3),
            cell_l.animate.set_stroke(C["gold"], 3),
            run_time=0.4,
        )
        prod = MathTex(
            r"\tilde{K}_{ij}\,\tilde{L}_{ij}",
            font_size=EQ_SIZE - 2,
        )
        board.set_bottom(prod)
        tn.play_before("products", Write(prod), settle=0.35, max_run=0.9)
        tn.wait_until("products")

        # Cascade: briefly pulse several cells as "add over every pair"
        pulse_idx = [ij, 0, n_hm + 1, 2 * n_hm + 3, 3 * n_hm + 4]
        for idx in pulse_idx:
            self.play(
                Indicate(hm_kc[1][idx], color=C["gold"], scale_factor=1.15),
                Indicate(hm_lc[1][idx], color=C["gold"], scale_factor=1.15),
                run_time=0.28,
            )
        sum_eq = MathTex(
            r"\sum_{i,j}\tilde{K}_{ij}\tilde{L}_{ij}",
            font_size=EQ_SIZE - 4,
        )
        board.set_bottom(sum_eq)
        tn.play_before(
            "patterns",
            TransformMatchingTex(prod, sum_eq),
            settle=0.35,
            max_run=1.0,
        )
        tn.wait_until("patterns")
        soft_idle(self, hm_kc, hm_lc, run_time=0.45)

        tn.wait_until("frobenius")
        fro_eq = MathTex(
            r"\sum_{i,j}\tilde{K}_{ij}\tilde{L}_{ij}",
            r"=",
            r"\langle\tilde{K},\,\tilde{L}\rangle_F",
            font_size=EQ_SIZE - 6,
        )
        board.set_bottom(fro_eq)
        tn.play_before(
            "Scale",
            TransformMatchingTex(sum_eq, fro_eq),
            FadeOut(ring_k),
            FadeOut(ring_l),
            settle=0.45,
            max_run=1.2,
        )
        self.play(Indicate(fro_eq[-1], color=C["accent"], scale_factor=1.08), run_time=0.65)
        _soft_until(tn, self, "Scale", fro_eq, max_t=0.8)

        # Scale → name HSIC
        tn.wait_until("Scale")
        scaled = MathTex(
            r"\frac{1}{(n-1)^2}",
            r"\langle\tilde{K},\,\tilde{L}\rangle_F",
            font_size=EQ_SIZE - 6,
        )
        board.set_bottom(scaled)
        tn.play_before(
            "Criterion",
            TransformMatchingTex(fro_eq, scaled),
            settle=0.4,
            max_run=1.1,
        )
        self.play(Indicate(scaled[0], color=C["highlight"], scale_factor=1.1), run_time=0.55)
        tn.wait_until("Criterion")

        hsic_eq = MathTex(
            r"\mathrm{HSIC}(K,L)",
            r"=",
            r"\frac{1}{(n-1)^2}",
            r"\langle\tilde{K},\,\tilde{L}\rangle_F",
            font_size=EQ_SIZE - 8,
        )
        board.set_bottom(hsic_eq)
        tn.play_before(
            "raw",
            TransformMatchingTex(scaled, hsic_eq),
            settle=0.35,
            max_run=1.1,
        )
        tn.wait_until("raw")
        raw_cap = key_sentence(
            self,
            "raw agreement score",
            color=C["accent"],
            font_size=26,
            hold=0.1,
            park="left",
            board=board,
        )
        _soft_until(tn, self, "louder", hsic_eq, max_t=0.7)

        # Normalize → CKA
        tn.wait_until("louder")
        self.play(FadeOut(raw_cap), run_time=0.25)
        board.clear("key")
        loud_cap = key_sentence(
            self,
            "louder activations inflate the raw score",
            color=C["wrong"],
            font_size=24,
            hold=0.08,
            park="left",
            board=board,
        )
        tn.wait_until("divide")
        self.play(FadeOut(loud_cap), run_time=0.2)
        board.clear("key")

        cka_num = MathTex(
            r"\mathrm{CKA}(K,L)",
            r"=",
            r"\frac{\mathrm{HSIC}(K,L)}{\cdot}",
            font_size=EQ_SIZE - 8,
        )
        board.set_bottom(cka_num)
        tn.play_before(
            "Numerator",
            ReplacementTransform(hsic_eq, cka_num),
            settle=0.3,
            max_run=1.1,
        )
        tn.wait_until("Numerator")
        self.play(Indicate(cka_num[2], color=C["accent"], scale_factor=1.06), run_time=0.55)

        tn.wait_until("Denominator")
        cka_eq = MathTex(
            r"\mathrm{CKA}(K,L)",
            r"=",
            r"\frac{\mathrm{HSIC}(K,L)}"
            r"{\sqrt{\mathrm{HSIC}(K,K)\,\mathrm{HSIC}(L,L)}}",
            font_size=EQ_SIZE - 10,
        )
        board.set_bottom(cka_eq)
        tn.play_before(
            "alignment",
            TransformMatchingTex(cka_num, cka_eq),
            settle=0.5,
            max_run=1.4,
        )
        self.play(Indicate(cka_eq[2], color=C["gold"], scale_factor=1.05), run_time=0.75)

        cka_val = float(
            np.sum(K_C * L_C)
            / (np.linalg.norm(K_C, "fro") * np.linalg.norm(L_C, "fro") + 1e-12)
        )
        cka_val = float(np.clip(cka_val, 0, 1))
        dial_cka = score_dial(cka_val, label="CKA", color=C["right"])
        dial_cka.scale(0.85).move_to(ORIGIN + UP * 0.15)
        hm_kc2 = make_heatmap(K_C, side=2.6 * 0.72, cmap_lo=BLUE_E, cmap_hi=YELLOW_C)
        hm_lc2 = make_heatmap(L_C, side=2.6 * 0.72, cmap_lo=TEAL_E, cmap_hi=YELLOW_C)
        hm_kc2.move_to(LEFT * 3.4 + DOWN * 0.5)
        hm_lc2.move_to(RIGHT * 3.4 + DOWN * 0.5)
        self.play(
            ReplacementTransform(hm_kc, hm_kc2),
            ReplacementTransform(hm_lc, hm_lc2),
            pl_kt.animate.move_to(LEFT * 3.4 + UP * PANEL_LABEL_Y),
            pl_lt.animate.move_to(RIGHT * 3.4 + UP * PANEL_LABEL_Y),
            FadeIn(dial_cka, scale=0.9),
            run_time=1.0,
        )
        hm_kc, hm_lc = hm_kc2, hm_lc2
        tn.wait_until("alignment")
        _soft_until(tn, self, "linear", dial_cka, max_t=1.0)

        # ── LINEAR CKA (frobenius-cosine form) ─────────────────────
        tn.wait_until("linear")
        lin_cap = key_sentence(
            self,
            "linear CKA",
            color=C["accent"],
            font_size=30,
            hold=0.08,
            park="left",
            board=board,
        )
        tn.wait_until("features")
        # Keep HSIC form briefly, then morph toward frobenius cosine
        _soft_until(tn, self, "cosine#2", dial_cka, cka_eq, max_t=0.8)
        tn.wait_until("cosine#2")

        cos_eq = MathTex(
            r"\mathrm{CKA}(K,L)",
            r"=",
            r"\frac{\langle\tilde{K},\,\tilde{L}\rangle_F}"
            r"{\|\tilde{K}\|_F\,\|\tilde{L}\|_F}",
            font_size=EQ_SIZE - 8,
        )
        board.set_bottom(cos_eq)
        tn.play_before(
            "orthogonal",
            TransformMatchingTex(cka_eq, cos_eq),
            FadeOut(lin_cap),
            settle=0.4,
            max_run=1.2,
        )
        board.clear("key")
        tn.wait_until("orthogonal")

        # ── Invariants ─────────────────────────────────────────────
        inv_cap = key_sentence(
            self,
            "invariant to orthogonal transforms",
            color=C["right"],
            font_size=26,
            hold=0.08,
            park="left",
            board=board,
        )
        tn.play_before(
            "isotropic",
            Rotate(hm_lc[1], angle=0.35, about_point=hm_lc.get_center()),
            settle=0.3,
            max_run=0.9,
        )
        tn.wait_until("isotropic")

        tn.play_before(
            "Permute",
            hm_lc.animate.scale(1.12),
            settle=0.25,
            max_run=0.7,
        )
        tn.wait_until("Permute")

        cells = list(hm_lc[1])
        shuffled = cells[::-1]
        tn.play_before(
            "collapsed",
            *[
                cells[i].animate.set_fill(shuffled[i].get_fill_color(), opacity=0.92)
                for i in range(len(cells))
            ],
            settle=0.4,
            max_run=1.0,
        )
        # Ghost of collapsed 1-to-1
        ghost_dial = score_dial(0.18, label="1-to-1", color=C["wrong"])
        ghost_dial.scale(0.55).move_to(ORIGIN + DOWN * 1.85)
        ghost_dial.set_opacity(0.45)
        flashback = board.set_bottom(
            bottom_note("1-to-1 collapsed — CKA holds", color=C["right"])
        )
        self.play(
            FadeOut(cos_eq),
            FadeIn(flashback),
            FadeIn(ghost_dial),
            run_time=0.55,
        )
        tn.wait_until("collapsed")
        _soft_until(tn, self, "asking", dial_cka, max_t=0.7)

        # ── SETTLE ─────────────────────────────────────────────────
        tn.wait_until("asking")
        self.play(
            FadeOut(inv_cap),
            FadeOut(flashback),
            FadeOut(ghost_dial),
            FadeOut(dial_cka),
            FadeOut(hm_kc),
            FadeOut(hm_lc),
            FadeOut(pl_kt),
            FadeOut(pl_lt),
            run_time=0.5,
        )
        board.clear()

        takeaway = MathTex(
            r"\mathrm{CKA}(K,L)",
            r"=",
            r"\frac{\langle\tilde{K},\,\tilde{L}\rangle_F}"
            r"{\|\tilde{K}\|_F\,\|\tilde{L}\|_F}",
            font_size=EQ_SIZE - 4,
        )
        takeaway.move_to(UP * 0.55)
        board.add(takeaway, "takeaway")
        tn.play_before("geometry", Write(takeaway), settle=0.45, max_run=1.2)
        tn.wait_until("geometry")

        geo = key_sentence(
            self,
            "same example geometry?",
            color=C["highlight"],
            font_size=30,
            hold=0.1,
            park="left",
            board=board,
            placement="key",
        )
        mini_k = make_heatmap(K_C, side=1.6).move_to(LEFT * 3.5 + DOWN * 1.3)
        mini_l = make_heatmap(L_C, side=1.6).move_to(RIGHT * 3.5 + DOWN * 1.3)
        self.play(FadeIn(mini_k), FadeIn(mini_l), run_time=0.65)
        tn.wait_until("loudness")

        loud = board.set_bottom(
            bottom_note("after centering — and after normalizing loudness", color=C["accent"])
        )
        self.play(FadeIn(loud), run_time=0.4)
        soft_idle(self, takeaway, mini_k, mini_l, run_time=0.65)

        tn.wait_until_end(pad=0.5)
        board.assert_clear()
