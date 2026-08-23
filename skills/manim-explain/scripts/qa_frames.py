"""Compose a contact sheet from already-captured keyframe PNGs.

The geometry pass writes stills into ``out/keyframes/`` at cues, play ends,
and the first sample of each overlap. This tool tiles those PNGs. It does
not seek an MP4: extracting frames from a movie was the old inner loop, and
it required encoding the movie first.

Usage::

    python qa_frames.py demos/<slug>
    python qa_frames.py demos/<slug> --frames demos/<slug>/out/keyframes
    python qa_frames.py demos/<slug> --out demos/<slug>/out/keyframes/contact_sheet.png
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

from wireframe import BACKGROUND, compose_tiles


def select_sheet_frames(frames: Sequence[Path], max_tiles: int = 48) -> list[Path]:
    """Pick a readable subset of stills for the contact sheet.

    A geometry walk captures every cue and play end. Tiling all of them makes
    a sheet too tall to read. Overlaps go first — those are the defects —
    then a strided sample of cues, then play ends.

    Args:
        frames: Keyframe PNG paths, usually in filename order.
        max_tiles: Maximum tiles on the sheet.

    Returns:
        A list of at most ``max_tiles`` paths, preserving time order.
    """
    if len(frames) <= max_tiles:
        return list(frames)

    def _kind(path: Path) -> str:
        name = path.name
        if "_overlap_" in name:
            return "overlap"
        if "_cue:" in name or "_cue_" in name:
            return "cue"
        if "_play-end_" in name:
            return "play"
        return "other"

    grouped: dict[str, list[Path]] = {"overlap": [], "cue": [], "play": [], "other": []}
    for path in frames:
        grouped[_kind(path)].append(path)

    def stride(items: list[Path], n: int) -> list[Path]:
        if n <= 0 or not items:
            return []
        if len(items) <= n:
            return items
        step = len(items) / n
        return [items[int(i * step)] for i in range(n)]

    overlap_n = min(len(grouped["overlap"]), max(12, max_tiles // 3))
    remaining = max_tiles - overlap_n
    cue_n = min(len(grouped["cue"]), max(remaining // 2, remaining - len(grouped["play"])))
    play_n = min(len(grouped["play"]), max(0, remaining - cue_n))
    other_n = max(0, max_tiles - overlap_n - cue_n - play_n)

    chosen = (
        grouped["overlap"][:overlap_n]
        + stride(grouped["cue"], cue_n)
        + stride(grouped["play"], play_n)
        + stride(grouped["other"], other_n)
    )
    by_name = {p.name: p for p in chosen}
    return [p for p in frames if p.name in by_name][:max_tiles]


def list_keyframes(frames_dir: Path) -> list[Path]:
    """Return still PNGs in a keyframe directory, in filename order.

    Skips the contact sheet itself so a re-run cannot tile the previous
    sheet into the new one.

    Args:
        frames_dir: Directory that holds ``NNN_reason_T.TTs.png`` files.

    Returns:
        Sorted PNG paths, excluding ``contact_sheet.png``.
    """
    frames_dir = Path(frames_dir)
    if not frames_dir.is_dir():
        return []
    return sorted(
        p
        for p in frames_dir.glob("*.png")
        if p.name != "contact_sheet.png"
    )


def compose_contact_sheet(
    frames: Sequence[Path],
    dest: Path,
    *,
    cols: int = 4,
    cell: tuple[int, int] = (320, 180),
    caption: bool = True,
) -> Path | None:
    """Tile keyframe PNGs into one contact sheet.

    Args:
        frames: Source PNG paths, in the order they should appear.
        dest: Destination PNG.
        cols: Tiles per row.
        cell: Tile size in pixels.
        caption: Draw the filename stem under each tile when True.

    Returns:
        ``dest`` when at least one frame was tiled, else ``None``.
    """
    if not frames:
        return None
    font = None
    if caption:
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                11,
            )
        except OSError:
            font = ImageFont.load_default()
    tiles: list[Image.Image] = []
    for path in frames:
        image = Image.open(path).convert("RGBA")
        image.thumbnail((cell[0], cell[1] - (16 if caption else 0)))
        pad = Image.new("RGBA", cell, BACKGROUND)
        x = (cell[0] - image.width) // 2
        y = 2
        pad.paste(image, (x, y))
        if caption and font is not None:
            draw = ImageDraw.Draw(pad)
            draw.text((4, cell[1] - 14), path.stem[:40], fill=(220, 220, 220, 255), font=font)
        tiles.append(pad)
    return compose_tiles(tiles, dest, cols=cols, cell=cell)


def main() -> None:
    """Tile ``out/keyframes/`` into a contact sheet and print the path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo_dir", type=Path)
    parser.add_argument(
        "--frames",
        type=Path,
        default=None,
        help="Directory of PNG stills (default: <demo>/out/keyframes)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Contact-sheet path (default: <frames>/contact_sheet.png)",
    )
    parser.add_argument("--cols", type=int, default=4)
    args = parser.parse_args()

    demo = args.demo_dir.resolve()
    frames_dir = (args.frames or (demo / "out" / "keyframes")).resolve()
    frames = list_keyframes(frames_dir)
    if not frames:
        raise SystemExit(
            f"No keyframe PNGs in {frames_dir}. Run geometry_pass.py on this "
            "demo first — stills are captured during the geometry walk, not "
            "extracted from an MP4."
        )
    dest = args.out or (frames_dir / "contact_sheet.png")
    sheet_frames = select_sheet_frames(frames)
    sheet = compose_contact_sheet(sheet_frames, dest, cols=args.cols)
    print(
        f"Contact sheet -> {sheet}  "
        f"({len(sheet_frames)} of {len(frames)} stills)"
    )


if __name__ == "__main__":
    main()
