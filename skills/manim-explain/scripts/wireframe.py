"""Draw labelled rectangles from occupancy samples, without Manim or Cairo.

A wireframe is the occupancy JSON turned into a picture: every recorded AABB
as a rectangle on a dark field, with its label. It answers "what did the
sampler think was on stage" when a Cairo still is too expensive or when the
question is the box itself, not the glyphs inside it.

Manim's default camera is 14.222… by 8 units, origin at the centre, y-up.
PNG rows run y-down. The conversion is the only piece of camera knowledge
this module needs; it does not import Manim.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from PIL import Image, ImageDraw, ImageFont

# Manim Community default frame. Matches config.frame_width / frame_height
# for a 16:9 camera at frame_height 8.
DEFAULT_FRAME_WIDTH = 14.222222222222221
DEFAULT_FRAME_HEIGHT = 8.0

# 480p15 stills from ``-ql``; wireframes use the same canvas so a contact
# sheet of wireframes and Cairo stills line up.
DEFAULT_PIXEL_WIDTH = 854
DEFAULT_PIXEL_HEIGHT = 480

TEXT_FILL = (240, 210, 80, 255)
FRAME_FILL = (90, 170, 255, 255)
BACKGROUND = (12, 12, 18, 255)
LABEL_FILL = (230, 230, 230, 255)


def manim_to_pixel(
    x: float,
    y: float,
    *,
    pixel_width: int = DEFAULT_PIXEL_WIDTH,
    pixel_height: int = DEFAULT_PIXEL_HEIGHT,
    frame_width: float = DEFAULT_FRAME_WIDTH,
    frame_height: float = DEFAULT_FRAME_HEIGHT,
) -> tuple[float, float]:
    """Convert a Manim plane point to PNG pixel coordinates.

    Args:
        x: Manim x, origin at the frame centre, positive right.
        y: Manim y, origin at the frame centre, positive up.
        pixel_width: Image width in pixels.
        pixel_height: Image height in pixels.
        frame_width: Manim frame width in plane units.
        frame_height: Manim frame height in plane units.

    Returns:
        ``(px, py)`` with ``py`` measured down from the top of the image.
    """
    px = (x / frame_width + 0.5) * pixel_width
    py = (0.5 - y / frame_height) * pixel_height
    return px, py


def box_to_pixels(
    box: Sequence[float],
    **kwargs: Any,
) -> tuple[int, int, int, int]:
    """Convert a Manim AABB ``(x0, y0, x1, y1)`` to a pixel rectangle.

    Args:
        box: Left, bottom, right, top in Manim plane units.
        **kwargs: Forwarded to :func:`manim_to_pixel`.

    Returns:
        ``(left, top, right, bottom)`` in pixel coordinates, integers, ordered
        so PIL's ``rectangle`` can consume them even if the box was inverted.
    """
    x0, y0, x1, y1 = (float(box[0]), float(box[1]), float(box[2]), float(box[3]))
    left, bottom = manim_to_pixel(x0, y0, **kwargs)
    right, top = manim_to_pixel(x1, y1, **kwargs)
    l = int(round(min(left, right)))
    r = int(round(max(left, right)))
    t = int(round(min(top, bottom)))
    b = int(round(max(top, bottom)))
    return l, t, r, b


def _font(size: int = 12) -> ImageFont.ImageFont:
    """Load a small bitmap font; fall back to PIL's default.

    Args:
        size: Requested point size. Ignored when only the default font exists.

    Returns:
        A font object ``ImageDraw.text`` will accept.
    """
    try:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            size,
        )
    except OSError:
        return ImageFont.load_default()


def draw_sample(
    sample: Mapping[str, Any],
    dest: Path,
    *,
    pixel_width: int = DEFAULT_PIXEL_WIDTH,
    pixel_height: int = DEFAULT_PIXEL_HEIGHT,
    title: str | None = None,
) -> Path:
    """Render one occupancy sample as a labelled wireframe PNG.

    Args:
        sample: Occupancy sample with ``t`` and ``items``.
        dest: Destination PNG path. Parent directories are created.
        pixel_width: Image width.
        pixel_height: Image height.
        title: Optional header drawn at the top. Defaults to the sample time.

    Returns:
        ``dest``, after the image has been written.
    """
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", (pixel_width, pixel_height), BACKGROUND)
    draw = ImageDraw.Draw(image)
    font = _font(12)
    header = title if title is not None else f"t={float(sample.get('t', 0.0)):.2f}s"
    draw.text((8, 6), header, fill=LABEL_FILL, font=font)
    for item in sample.get("items") or []:
        box = item.get("box")
        if not box or len(box) < 4:
            continue
        rect = box_to_pixels(box, pixel_width=pixel_width, pixel_height=pixel_height)
        kind = str(item.get("kind") or "")
        color = FRAME_FILL if kind == "frame" else TEXT_FILL
        draw.rectangle(rect, outline=color, width=2)
        label = str(item.get("label") or "")[:32]
        if label:
            lx, ly = rect[0] + 3, max(rect[1] - 14, 22)
            draw.text((lx, ly), label, fill=color, font=font)
    image.save(dest)
    return dest


def write_wireframe_sheet(
    occupancy_path: Path,
    dest: Path,
    *,
    times: Sequence[float] | None = None,
    cols: int = 4,
    cell: tuple[int, int] = (320, 180),
    max_tiles: int = 24,
) -> Path | None:
    """Compose a contact sheet of wireframes at selected times.

    Args:
        occupancy_path: Path to ``out/occupancy.json``.
        dest: Destination PNG.
        times: Scene times to draw. When omitted, uses leftover first/last
            times plus a uniform stride across the duration.
        cols: Tiles per row.
        cell: Tile size in pixels.
        max_tiles: Cap on how many samples to draw.

    Returns:
        ``dest`` when at least one tile was drawn, else ``None``.
    """
    occupancy_path = Path(occupancy_path)
    if not occupancy_path.is_file():
        return None
    payload = json.loads(occupancy_path.read_text())
    samples = payload.get("samples") or []
    if not samples:
        return None
    duration = float(payload.get("duration") or samples[-1].get("t") or 0.0)
    if times is None:
        chosen: list[float] = []
        for row in payload.get("leftovers") or []:
            chosen.append(float(row.get("first") or 0.0))
            chosen.append(float(row.get("last") or 0.0))
        if duration > 0:
            n = min(8, max_tiles)
            chosen.extend(duration * (i + 0.5) / n for i in range(n))
        times = chosen
    times = sorted(float(t) for t in times)
    unique: list[float] = []
    for t in times:
        if not unique or abs(t - unique[-1]) > 0.2:
            unique.append(t)
        if len(unique) >= max_tiles:
            break
    if not unique:
        unique = [float(samples[0].get("t") or 0.0)]

    from occupancy import sample_at  # local: occupancy is a sibling script

    tiles: list[Image.Image] = []
    for t in unique:
        sample = sample_at(samples, t)
        if sample is None:
            continue
        tmp = dest.parent / f".wf_{t:.2f}.png"
        draw_sample(sample, tmp, title=f"t={t:.2f}s")
        tile = Image.open(tmp).convert("RGBA")
        tile.thumbnail(cell)
        pad = Image.new("RGBA", cell, BACKGROUND)
        pad.paste(tile, ((cell[0] - tile.width) // 2, (cell[1] - tile.height) // 2))
        tiles.append(pad)
        tmp.unlink(missing_ok=True)
    if not tiles:
        return None
    return compose_tiles(tiles, dest, cols=cols, cell=cell)


def compose_tiles(
    tiles: Sequence[Image.Image],
    dest: Path,
    *,
    cols: int = 4,
    cell: tuple[int, int] = (320, 180),
) -> Path:
    """Tile RGBA images into one PNG.

    Args:
        tiles: Images, already sized to ``cell`` or smaller.
        dest: Destination path. Parent directories are created.
        cols: Tiles per row.
        cell: Cell size; each tile is pasted top-left inside a cell of this
            size.

    Returns:
        ``dest``.
    """
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    cols = max(1, cols)
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell[0], rows * cell[1]), BACKGROUND)
    for i, tile in enumerate(tiles):
        r, c = divmod(i, cols)
        if tile.size != cell:
            pad = Image.new("RGBA", cell, BACKGROUND)
            pad.paste(tile, (0, 0))
            tile = pad
        sheet.paste(tile, (c * cell[0], r * cell[1]))
    sheet.save(dest)
    return dest
