"""Locate the skill and the working project, wherever the skill is installed.

A skill is portable: it may live in this repo under ``skills/manim-explain/``,
in ``~/.claude/skills/``, ``~/.cursor/skills/``, ``~/.agents/skills/``, or in a
plugin cache. Demos live in the *user's* project, which is a different tree.
Nothing here may hard-code an install path.
"""

from __future__ import annotations

import os
from pathlib import Path

# Locations an installed skill can sit in, relative to a project or home dir
SKILL_DIR_NAMES = ("skills", ".claude/skills", ".cursor/skills", ".agents/skills")
SKILL_NAME = "manim-explain"


def skill_root() -> Path:
    """Return the skill directory (the one holding ``SKILL.md``).

    Returns:
        Absolute path to the skill root, derived from this file's location so
        it stays correct under any install path or symlink farm.
    """
    return Path(__file__).resolve().parent.parent


def scripts_dir() -> Path:
    """Return the skill's ``scripts/`` directory.

    Returns:
        Absolute path to the directory holding the pipeline scripts.
    """
    return skill_root() / "scripts"


def find_skill_root(start: Path | None = None) -> Path:
    """Find the skill root from an arbitrary file, e.g. a copied demo module.

    Resolution order: ``MANIM_EXPLAIN_ROOT`` → an install directory in any
    parent of ``start`` → an install directory under ``$HOME``.

    Args:
        start: Directory to search upward from. Defaults to the caller's cwd.

    Returns:
        Absolute path to the skill root.

    Raises:
        FileNotFoundError: If no installed copy of the skill can be located.
    """
    env_root = os.environ.get("MANIM_EXPLAIN_ROOT")
    if env_root and (Path(env_root) / "SKILL.md").is_file():
        return Path(env_root).resolve()

    here = Path(__file__).resolve()
    if (here.parent.parent / "SKILL.md").is_file():
        return here.parent.parent

    bases: list[Path] = []
    start_path = Path(start).resolve() if start else Path.cwd().resolve()
    bases.extend([start_path, *start_path.parents])
    bases.append(Path.home())
    for base in bases:
        for rel in SKILL_DIR_NAMES:
            candidate = base / rel / SKILL_NAME
            if (candidate / "SKILL.md").is_file():
                return candidate.resolve()
    raise FileNotFoundError(
        f"Cannot locate the {SKILL_NAME} skill. Set MANIM_EXPLAIN_ROOT to the "
        "directory containing SKILL.md, or install the skill under one of: "
        + ", ".join(SKILL_DIR_NAMES)
    )


def find_project_root(start: Path) -> Path:
    """Find the root of the *user's* project (where ``.env`` and demos live).

    The project is whatever tree the demo sits in — usually a git repository.
    This is deliberately independent of where the skill is installed.

    Args:
        start: A path inside the project, typically the demo directory.

    Returns:
        The nearest ancestor containing ``.git``, ``.env`` or ``demos/``,
        falling back to ``start`` itself.
    """
    start = Path(start).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists() or (candidate / ".env").is_file():
            return candidate
        if (candidate / "demos").is_dir() and candidate != start:
            return candidate
    return start


def load_dotenv(project_root: Path) -> None:
    """Load ``KEY=value`` pairs from the project's ``.env`` into the environment.

    Existing environment variables always win, so an exported key overrides the
    file. Missing files are ignored — the caller reports the missing key.

    Args:
        project_root: Directory that may contain a ``.env`` file.
    """
    env_path = Path(project_root) / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
