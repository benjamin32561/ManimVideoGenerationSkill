"""The action vocabulary: each event action becomes manimgx animations.

Timing rule (decision 18): an event starts ``motion.start_offset`` after its anchor's first
word. Each action runs for the time the style gives it, stretched toward the phrase's
length (``span``) within the style's range, and never past the next event's start
(``limit``). Between events nothing moves.

Actions, by name:

    draw      strokes draw on; filled shapes draw their border, then fill
    write     text and math write on (glyph mode) or type letter by letter (letters mode)
    grow      objects grow from their centre, an arrow from its tail, a bar from an edge
    fade_in   objects fade in, optionally sliding by ``shift`` px
    fade_out  objects fade out (exits are shorter than entrances)
    move      objects move to a point (``to``) or along a named path (``along``)
    change    an object takes new layout fields (``to``): bar heights, edges, arrow fraction...
    recolor   objects take a palette colour
    dim       objects drop to ``opacity`` × their own opacity; a dim never brightens
    restore   dimmed objects return to their own opacity
    flash     a soft highlight rises and falls behind objects
    copy_to   a copy of ``source`` flies into ``target``: glyph by glyph when the content
              matches, as a cross-fade when it does not (unlike glyphs never morph)
    morph     ``source`` turns into ``target`` in place, matching parts move

Every action takes an optional ``delay`` (s after the event start) and, where it moves
several objects, ``lag`` (s between their starts).
"""

from dataclasses import dataclass, field

import manimgx as m
import numpy as np

from explain.objects import Builder
from explain.plan import Event, Layout
from explain.styles import Style

MIN_GROW_S = 0.3
WRITE_GROUP_LAG = 0.15


def clamp(value: float, low: float, high: float) -> float:
    """Limit a number to a closed interval.

    Args:
        value: The number.
        low: Lower bound.
        high: Upper bound.

    Returns:
        ``value`` limited to ``[low, high]``.
    """
    return max(low, min(high, value))


@dataclass
class Landing:
    """A stand-in that an animation lands on, swapped for the real object after the event.

    copy_to and morph animate into copies of their targets (manimgx restructures a
    transform's target), so the untouched target replaces the copy once the event is over.
    """

    stand_in: m.Mobject
    real: m.Mobject
    extra: list[m.Mobject] = field(default_factory=list)


class Director:
    """Turns events into animations and keeps the state that spans events.

    State: each object's current layout spec (``change`` updates it), its displacement from
    moves, each leaf's dim level and recolour, and an untouched copy of each leaf as built (as
    last changed), which ``dim`` and ``restore`` scale from.

    Args:
        scene: The running scene.
        style: The series' style pack.
        layout: The video's layout plan.
        builder: The object builder (for ``change`` rebuilds).
        registry: Leaf or object id → mobject.
    """

    def __init__(self, scene: m.Scene, style: Style, layout: Layout, builder: Builder,
                 registry: dict[str, m.Mobject]) -> None:
        """Keep the scene and the objects, and an untouched copy of every leaf as built.

        Args:
            scene: The running scene.
            style: The series' style pack.
            layout: The video's layout plan.
            builder: The object builder.
            registry: Leaf or object id → mobject.
        """
        self.scene = scene
        self.motion = style.motion
        self.kit = builder.kit
        self.layout = layout
        self.builder = builder
        self.reg = registry
        self.specs = {oid: dict(spec) for oid, spec in layout.objects.items()}
        self.offsets: dict[str, np.ndarray] = {}
        self.levels: dict[str, float] = {}
        self.colors: dict[str, str] = {}
        self.pristine = {leaf: registry[leaf].copy() for leaf in layout.leaves(list(layout.objects))}
        self.landings: list[Landing] = []
        self.flashes: list[m.Mobject] = []

    def event(self, event: Event, limit: float) -> list[m.Animation]:
        """Build every animation of one event.

        Args:
            event: The resolved event.
            limit: Seconds until the next event starts (or the narration ends).

        Returns:
            The animations, to be played together.

        Raises:
            ValueError: For an action outside the vocabulary.
        """
        span = event.end - event.start
        anims = []
        for action in event.actions:
            handler = getattr(self, f"do_{action['action']}", None)
            if handler is None:
                raise ValueError(f"{event.id}: unknown action {action['action']!r}")
            delay = float(action.get("delay", 0.0))
            for anim in handler(action, span, max(limit - delay, 0.05)):
                anims.append(m.Succession(m.Wait(run_time=delay), anim) if delay > 0 else anim)
        return anims

    def after_event(self) -> None:
        """Remove spent flash highlights and swap landed stand-ins for the real objects.

        Both swaps are pixel-identical, so the frame does not change.
        """
        if self.flashes:
            self.scene.remove(*self.flashes)
            self.flashes = []
        for landing in self.landings:
            self.scene.remove(landing.stand_in, *landing.extra)
            self.scene.add(landing.real)
        self.landings = []

    def leaves(self, ids: list[str]) -> list[m.Mobject]:
        """Resolve ids (objects, parts, groups) to the mobjects on screen.

        Args:
            ids: Ids as written in the action.

        Returns:
            The leaf mobjects in order.
        """
        return [self.reg[leaf] for leaf in self.layout.leaves(ids)]

    def run_time(self, span: float, bounds: tuple[float, float], limit: float) -> float:
        """The run time of an action: the phrase length within the style's bounds, cut at
        the next event.

        Args:
            span: The anchor phrase's length (s).
            bounds: The style's [min, max] for this action.
            limit: Seconds available.

        Returns:
            The run time.
        """
        return min(clamp(span, *bounds), limit)

    def staggered(self, anims: list[m.Animation], lag: float, each: float) -> list[m.Animation]:
        """Stagger animations by ``lag`` seconds, or play them together when lag is 0.

        Args:
            anims: Animations of equal run time ``each``.
            lag: Seconds between starts.
            each: Each animation's run time.

        Returns:
            One LaggedStart, or the animations unchanged.
        """
        if lag > 0 and len(anims) > 1:
            return [m.LaggedStart(*anims, lag_ratio=lag / each)]
        return anims

    def do_draw(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``draw``: Create strokes; draw border then fill for filled shapes.

        Args:
            a: The action (``targets``, optional ``lag``).
            span: Phrase length (s).
            limit: Seconds available.

        Returns:
            The animations.
        """
        mobs = self.leaves(a["targets"])
        lag = float(a.get("lag", 0.0))
        rt = self.run_time(span, self.motion.draw, limit)
        each = max(rt - lag * (len(mobs) - 1), MIN_GROW_S)
        anims = []
        for mob in mobs:
            filled = mob.get_fill_opacity() > 0 and not isinstance(mob, m.Arrow)
            anims.append(m.DrawBorderThenFill(mob, run_time=each) if filled else m.Create(mob, run_time=each))
        return self.staggered(anims, lag, each)

    def do_write(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``write``: each target writes on as one unit (a group's members in one stroke).

        In ``letters`` mode, plain text types on at the style's letter rate.

        Args:
            a: The action (``targets``).
            span: Phrase length (s).
            limit: Seconds available.

        Returns:
            One animation per written target.
        """
        anims = []
        for target in a["targets"]:
            leaves = self.leaves([target])
            plain = target in self.layout.objects and self.layout.objects[target]["type"] == "text"
            if self.motion.write_mode == "letters" and plain:
                letters = len(self.layout.objects[target]["content"].replace(" ", ""))
                rt = min(letters / self.motion.letters_per_s, limit)
                anims.append(m.AddTextLetterByLetter(leaves[0], time_per_char=rt / max(letters, 1), run_time=rt))
                continue
            rt = self.run_time(span, self.motion.write, limit)
            if len(leaves) == 1:
                anims.append(m.Write(leaves[0], run_time=rt))
            else:
                anims.append(m.LaggedStart(*(m.Write(leaf) for leaf in leaves), lag_ratio=WRITE_GROUP_LAG,
                                           run_time=rt))
        return anims

    def do_grow(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``grow``: from the centre, an arrow or line from its tail, or a bar from an edge.

        ``from: tail`` grows from the object's first point (``points[0]``, px); the plan check
        accepts it only for objects with ``points``.

        Args:
            a: The action (``targets``, optional ``from`` and ``lag``).
            span: Phrase length (s).
            limit: Seconds available.

        Returns:
            The animations, staggered over the phrase.
        """
        mobs = self.leaves(a["targets"])
        lag = float(a.get("lag", 0.0))
        each = clamp(min(span, limit) - lag * (len(mobs) - 1), *self.motion.grow)
        each = max(min(each, limit - lag * (len(mobs) - 1)), MIN_GROW_S)
        how = a.get("from", "center")
        edges = {"bottom": m.DOWN, "top": m.UP, "left": m.LEFT, "right": m.RIGHT}
        anims = []
        for leaf, mob in zip(self.layout.leaves(a["targets"]), mobs, strict=True):
            if how == "tail":
                tail = self.kit.pt(*self.specs[leaf]["points"][0]) + self.offsets.get(leaf, np.zeros(3))
                anims.append(m.GrowFromPoint(mob, tail, run_time=each))
            elif how in edges:
                anims.append(m.GrowFromEdge(mob, edges[how], run_time=each))
            else:
                anims.append(m.GrowFromCenter(mob, run_time=each))
        return self.staggered(anims, lag, each)

    def do_fade_in(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``fade_in``: optionally sliding in by ``shift`` px.

        Args:
            a: The action (``targets``, optional ``shift`` [dx, dy] px and ``lag``).
            span: Phrase length (s).
            limit: Seconds available.

        Returns:
            The animations.
        """
        mobs = self.leaves(a["targets"])
        lag = float(a.get("lag", 0.0))
        each = max(min(self.motion.fade_in, limit - lag * (len(mobs) - 1)), MIN_GROW_S)
        dx, dy = a.get("shift", (0.0, 0.0))
        shift = np.array([self.kit.units(dx), -self.kit.units(dy), 0.0])
        anims = [m.FadeIn(mob, shift=shift, run_time=each) for mob in mobs]
        return self.staggered(anims, lag, each)

    def do_fade_out(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``fade_out``: short exits.

        Args:
            a: The action (``targets``).
            span: Phrase length (s).
            limit: Seconds available.

        Returns:
            One FadeOut per leaf.
        """
        rt = min(self.motion.fade_out, limit)
        return [m.FadeOut(mob, run_time=rt) for mob in self.leaves(a["targets"])]

    def do_move(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``move``: to a point, or along a named path through its waypoints.

        A move to a point moves the targets together (their joint centre lands on ``to``);
        ``arc`` bends the path (radians). Paths pass smoothly through the layout's waypoints.

        Args:
            a: The action (``targets`` and ``to`` [x, y] or ``along``; optional ``lag``, ``arc``).
            span: Phrase length (s).
            limit: Seconds available.

        Returns:
            The animations.
        """
        ids = self.layout.leaves(a["targets"])
        rt = min(max(span, self.motion.change[0]), limit)
        if "to" in a:
            delta = self.kit.pt(*a["to"]) - m.VGroup(*(self.reg[i] for i in ids)).get_center()
            arc = float(a.get("arc", 0.0))
            anims = []
            for i in ids:
                self.offsets[i] = self.offsets.get(i, np.zeros(3)) + delta
                anims.append(self.reg[i].animate(run_time=rt, rate_func=m.smooth, path_arc=arc).shift(delta))
            return anims
        lag = float(a.get("lag", 0.0))
        each = max(rt - lag * (len(ids) - 1), MIN_GROW_S)
        anims = []
        for i in ids:
            mob = self.reg[i]
            waypoints = [self.kit.pt(*p) for p in self.layout.paths[a["along"]][i]]
            path = m.VMobject().set_points_smoothly(waypoints)
            self.offsets[i] = self.offsets.get(i, np.zeros(3)) + waypoints[-1] - mob.get_center()
            anims.append(m.MoveAlongPath(mob, path, run_time=each, rate_func=m.smooth))
        return self.staggered(anims, lag, each)

    def parts_of(self, oid: str, mob: m.Mobject) -> list[tuple[str, m.Mobject]]:
        """Pair an object's leaf ids with the matching parts of a mobject built from it.

        Args:
            oid: Object id.
            mob: A mobject built from the object's spec.

        Returns:
            ``(leaf id, part)`` for each named math part, or ``[(oid, mob)]`` for any other
            object.
        """
        parts = self.specs[oid].get("parts")
        if not parts:
            return [(oid, mob)]
        return [(part["id"], mob[i]) for i, part in enumerate(parts) if part.get("id")]

    def do_change(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``change``: rebuild each target with new layout fields and transform into it.

        The object keeps any displacement from earlier moves, and each leaf keeps its dim level
        and recolour (a ``color`` in ``to`` replaces the recolour). The rebuilt leaves become
        the copies that later ``dim`` and ``restore`` scale from.

        Args:
            a: The action (``targets`` object ids, ``to`` field overrides).
            span: Phrase length (s).
            limit: Seconds available.

        Returns:
            One Transform per target.
        """
        rt = self.run_time(span, self.motion.change, limit)
        anims = []
        for oid in a["targets"]:
            self.specs[oid] = {**self.specs[oid], **a["to"]}
            goal = self.builder.build(self.specs[oid], self.reg)
            goal.shift(self.offsets.get(oid, np.zeros(3)))
            for leaf, part in self.parts_of(oid, goal):
                self.pristine[leaf] = part.copy()
                if "color" in a["to"]:
                    self.colors.pop(leaf, None)
                self.dress(part, leaf, self.levels.get(leaf, 1.0))
            anims.append(m.Transform(self.reg[oid], goal, run_time=rt))
        return anims

    def do_recolor(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``recolor``: fill and stroke take a palette colour, kept through later dims and changes.

        Args:
            a: The action (``targets``, ``color``).
            span: Phrase length (s).
            limit: Seconds available.

        Returns:
            One animation per leaf.
        """
        rt = min(self.motion.dim, limit)
        color = self.kit.color(a["color"])
        ids = self.layout.leaves(a["targets"])
        self.colors.update(dict.fromkeys(ids, color))
        return [self.reg[i].animate(run_time=rt).set_color(color) for i in ids]

    def dress(self, mob: m.Mobject, leaf_id: str, level: float) -> m.Mobject:
        """Give an as-built leaf its recolour and scale every part's opacities by ``level``.

        Args:
            mob: An untouched build of the leaf (changed in place).
            leaf_id: The leaf id (its recolour, if any, is applied).
            level: Opacity factor (1 = as built).

        Returns:
            ``mob``.
        """
        if leaf_id in self.colors:
            mob.set_color(self.colors[leaf_id])
        for part in mob.family_members_with_points():
            fill, stroke = part.get_fill_opacity(), part.get_stroke_opacity()
            back = part.get_stroke_opacity(background=True)
            part.set_fill(opacity=fill * level, family=False)
            part.set_stroke(opacity=stroke * level, family=False)
            part.set_stroke(opacity=back * level, background=True, family=False)
        return mob

    def faded(self, leaf_id: str, level: float) -> m.Mobject:
        """A dim or restore target: the leaf as built, recoloured, at ``level`` × its own opacity.

        It is centred where the leaf is now, and built from the untouched copy, not from the leaf on screen: a transform may have
        restructured the leaf's glyphs, and their current opacities are not their own.

        Args:
            leaf_id: The leaf id.
            level: Opacity factor (1 = as built).

        Returns:
            The transform target.
        """
        target = self.dress(self.pristine[leaf_id].copy(), leaf_id, level)
        return target.move_to(self.reg[leaf_id].get_center())

    def do_dim(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``dim``: to ``opacity`` × own opacity; never brightens an already dimmer leaf.

        Args:
            a: The action (``targets``, ``opacity``).
            span: Phrase length (s).
            limit: Seconds available.

        Returns:
            One Transform per leaf.
        """
        rt = min(self.motion.dim, limit)
        anims = []
        for leaf in self.layout.leaves(a["targets"]):
            self.levels[leaf] = min(self.levels.get(leaf, 1.0), float(a["opacity"]))
            anims.append(m.Transform(self.reg[leaf], self.faded(leaf, self.levels[leaf]), run_time=rt))
        return anims

    def do_restore(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``restore``: dimmed leaves return to their own opacity.

        Args:
            a: The action (``targets``).
            span: Phrase length (s).
            limit: Seconds available.

        Returns:
            One Transform per leaf.
        """
        rt = min(self.motion.dim, limit)
        anims = []
        for leaf in self.layout.leaves(a["targets"]):
            self.levels[leaf] = 1.0
            anims.append(m.Transform(self.reg[leaf], self.faded(leaf, 1.0), run_time=rt))
        return anims

    def do_flash(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``flash``: a rounded highlight behind each target rises to the style's peak and fades.

        Args:
            a: The action (``targets``, ``color``).
            span: Phrase length (s).
            limit: Seconds available (the highlight runs across them, up to the phrase).

        Returns:
            One there-and-back animation per highlight.
        """
        rt = min(max(span, self.motion.write[0]), limit)
        pad = self.kit.units(self.motion.flash_pad_px)
        anims = []
        for mob in self.leaves(a["targets"]):
            glow = m.RoundedRectangle(width=mob.width + 2 * pad, height=mob.height + 2 * pad,
                                      corner_radius=pad, fill_color=self.kit.color(a["color"]),
                                      fill_opacity=0.0, stroke_width=0).move_to(mob.get_center())
            glow.set_z_index(mob.z_index - 1)
            self.scene.add(glow)
            self.flashes.append(glow)
            anims.append(glow.animate(run_time=rt, rate_func=m.there_and_back)
                         .set_fill(opacity=self.motion.flash_peak))
        return anims

    def content(self, oid: str) -> str:
        """The text or TeX an object or part shows, for deciding whether glyphs match.

        Args:
            oid: Object or part id.

        Returns:
            The content string.
        """
        if oid in self.layout.parts:
            owner = self.layout.objects[self.layout.parts[oid]]
            return next(p["tex"] for p in owner["parts"] if p.get("id") == oid)
        spec = self.layout.objects[oid]
        return spec.get("content") or spec.get("tex") or "".join(p["tex"] for p in spec.get("parts", []))

    def do_copy_to(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``copy_to``: a copy of the source flies into the target.

        Matching content morphs glyph for glyph; anything else cross-fades along the flight,
        because morphing unlike glyphs passes through blobs. ``arc`` bends the flight.

        Args:
            a: The action (``source``, ``target``, optional ``arc``).
            span: Phrase length (s).
            limit: Seconds available.

        Returns:
            One animation.
        """
        rt = min(self.motion.copy, limit)
        src, dst = self.reg[a["source"]], self.reg[a["target"]]
        arc = float(a.get("arc", 0.0))
        src_leaves = src.family_members_with_points()
        dst_leaves = dst.family_members_with_points()
        if self.content(a["source"]) == self.content(a["target"]) and len(src_leaves) == len(dst_leaves):
            landing = m.VGroup(*(leaf.copy() for leaf in dst_leaves))
            flyer = m.VGroup(*(leaf.copy() for leaf in src_leaves))
            self.landings.append(Landing(landing, dst))
            return [m.ReplacementTransform(flyer, landing, run_time=rt, path_arc=arc)]
        landing = dst.copy()
        self.landings.append(Landing(landing, dst))
        return [m.FadeTransform(src.copy(), landing, run_time=rt, path_arc=arc)]

    def do_morph(self, a: dict, span: float, limit: float) -> list[m.Animation]:
        """``morph``: the source becomes the target in place; matching parts move, others fade.

        Args:
            a: The action (``source``, ``target``).
            span: Phrase length (s).
            limit: Seconds available.

        Returns:
            One TransformMatchingTex.
        """
        rt = min(self.motion.morph, limit)
        dst = self.reg[a["target"]]
        landing = dst.copy()
        self.landings.append(Landing(landing, dst))
        both_math = all(i in self.layout.parts or self.layout.objects[i]["type"] == "math"
                        for i in (a["source"], a["target"]))
        matcher = m.TransformMatchingTex if both_math else m.TransformMatchingShapes
        return [matcher(self.reg[a["source"]], landing, run_time=rt)]
