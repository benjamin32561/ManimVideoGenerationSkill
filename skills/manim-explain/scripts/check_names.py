#!/usr/bin/env python3
"""Catch undefined names and bad call signatures in a scene, without rendering.

`from manim import *` defeats a normal linter's undefined-name check: ruff sees
the star import and stops guessing, so a helper that was used but never imported
reports clean. That is not academic — an un-imported `safe_multiline` and a
`note()` call missing a required argument each survived many "clean" logic passes
and only surfaced after a full render, one wasted render apiece.

This resolves names the way the interpreter will: the star-imported module's
namespace, the file's explicit imports, its own module-level definitions,
builtins, and every local binding it can see. Anything left is a name that will
raise at run time. It then checks each call against the signature of the
function, when that function can be resolved.

Usage::

    python check_names.py demos/<slug>/scenes/<file>.py
    python check_names.py demos/*/scenes/*.py
"""

from __future__ import annotations

import argparse
import ast
import builtins
import importlib
import inspect
import sys
from pathlib import Path


def _star_namespaces(tree: ast.Module) -> set[str]:
    """Collect names provided by every ``from X import *`` in the file.

    Args:
        tree: Parsed module.

    Returns:
        The union of public names in each star-imported module. Modules that
        cannot be imported contribute nothing.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and any(a.name == "*" for a in node.names):
            if not node.module:
                continue
            try:
                mod = importlib.import_module(node.module)
            except Exception:  # noqa: BLE001 - an unimportable module is just unknown
                continue
            names |= {n for n in dir(mod) if not n.startswith("_")}
    return names


def _bound_names(tree: ast.Module) -> set[str]:
    """Collect every name the module binds anywhere.

    Deliberately flat: scopes are ignored, which trades false negatives for zero
    false positives from comprehensions, walrus targets and nested functions.

    Args:
        tree: Parsed module.

    Returns:
        Every bound identifier.
    """
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Lambda):
            for a in (list(node.args.args) + list(node.args.posonlyargs)
                      + list(node.args.kwonlyargs)):
                out.add(a.arg)
            for a in (node.args.vararg, node.args.kwarg):
                if a is not None:
                    out.add(a.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(node.name)
            args = getattr(node, "args", None)
            if args is not None:
                for a in (list(args.args) + list(args.posonlyargs)
                          + list(args.kwonlyargs)):
                    out.add(a.arg)
                for a in (args.vararg, args.kwarg):
                    if a is not None:
                        out.add(a.arg)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                if a.name == "*":
                    continue
                out.add(a.asname or a.name.split(".")[0])
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            out.add(node.id)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            out.add(node.name)
        elif isinstance(node, ast.Global):
            out.update(node.names)
    return out


def undefined_names(path: Path, tree: ast.Module) -> list[tuple[int, str]]:
    """Find loaded names that nothing in scope can provide.

    Args:
        path: The scene file, used only for messages.
        tree: Parsed module.

    Returns:
        ``(line, name)`` pairs, sorted and deduplicated by name.
    """
    known = (_bound_names(tree) | _star_namespaces(tree)
             | set(dir(builtins)) | {"__file__", "__name__", "__doc__"})
    seen: dict[str, int] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id not in known and node.id not in seen:
                seen[node.id] = node.lineno
    return sorted(((ln, n) for n, ln in seen.items()), key=lambda t: t[0])


def _resolvable_functions(path: Path, tree: ast.Module) -> dict[str, inspect.Signature]:
    """Map callable names in the file to signatures, where they can be found.

    Covers functions defined in the file itself and names imported from a
    ``utils.*`` module next to the scene, which is where this project's shared
    builders live.

    Args:
        path: The scene file.
        tree: Parsed module.

    Returns:
        Name to signature, for every callable that could be resolved.
    """
    sigs: dict[str, inspect.Signature] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            try:
                sigs[node.name] = _sig_from_ast(node)
            except Exception:  # noqa: BLE001
                continue

    demo_dir = path.resolve().parent.parent
    sys.path.insert(0, str(demo_dir))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module \
                and node.module.startswith("utils"):
            try:
                mod = importlib.import_module(node.module)
            except Exception:  # noqa: BLE001
                continue
            for a in node.names:
                if a.name == "*":
                    continue
                obj = getattr(mod, a.name, None)
                if callable(obj):
                    try:
                        sigs[a.asname or a.name] = inspect.signature(obj)
                    except (TypeError, ValueError):
                        pass
    return sigs


def _sig_from_ast(node: ast.FunctionDef) -> inspect.Signature:
    """Build a signature from a function definition in the parsed file.

    Args:
        node: The function definition node.

    Returns:
        An ``inspect.Signature`` with defaults marked present but unevaluated.
    """
    a = node.args
    params = []
    pos = list(a.posonlyargs) + list(a.args)
    n_def = len(a.defaults)
    for i, arg in enumerate(pos):
        has_default = i >= len(pos) - n_def
        params.append(inspect.Parameter(
            arg.arg, inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=None if has_default else inspect.Parameter.empty))
    if a.vararg:
        params.append(inspect.Parameter(a.vararg.arg, inspect.Parameter.VAR_POSITIONAL))
    for arg, d in zip(a.kwonlyargs, a.kw_defaults):
        params.append(inspect.Parameter(
            arg.arg, inspect.Parameter.KEYWORD_ONLY,
            default=None if d is not None else inspect.Parameter.empty))
    if a.kwarg:
        params.append(inspect.Parameter(a.kwarg.arg, inspect.Parameter.VAR_KEYWORD))
    return inspect.Signature(params)


def bad_calls(path: Path, tree: ast.Module) -> list[tuple[int, str, str]]:
    """Find calls that do not match the callee's signature.

    Args:
        path: The scene file.
        tree: Parsed module.

    Returns:
        ``(line, callee, reason)`` for each call that would raise ``TypeError``.
    """
    sigs = _resolvable_functions(path, tree)
    out: list[tuple[int, str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        sig = sigs.get(node.func.id)
        if sig is None:
            continue
        if any(isinstance(a, ast.Starred) for a in node.args) \
                or any(k.arg is None for k in node.keywords):
            continue                       # unpacking: cannot be checked statically
        args = [None] * len(node.args)
        kwargs = {k.arg: None for k in node.keywords}
        try:
            sig.bind(*args, **kwargs)
        except TypeError as exc:
            out.append((node.lineno, node.func.id, str(exc)))
    return out


def main() -> int:
    """Check each file named on the command line.

    Returns:
        1 if any problem was found, else 0.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scenes", nargs="+", type=Path)
    args = ap.parse_args()

    bad = 0
    for path in args.scenes:
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError as exc:
            print(f"{path}:{exc.lineno}: SYNTAX ERROR {exc.msg}")
            bad += 1
            continue
        undef = undefined_names(path, tree)
        calls = bad_calls(path, tree)
        print(f"\n{path}  —  {len(undef)} undefined name(s), {len(calls)} bad call(s)")
        for ln, name in undef:
            print(f"  {path.name}:{ln:<5} undefined: {name}")
        for ln, fn, why in calls:
            print(f"  {path.name}:{ln:<5} {fn}(): {why}")
        bad += len(undef) + len(calls)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
