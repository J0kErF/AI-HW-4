"""Per-file AST extraction (the deterministic, token-free heart of Graphify).

Walks one Python file's AST and returns plain facts — defs, calls, bases,
imports — which :mod:`code_layer` turns into graph nodes and EXTRACTED edges.
No LLM, no network: this is the "carved in stone" evidence layer.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field


@dataclass
class FuncFact:
    """A function/method definition and the simple names it calls."""

    qualname: str
    name: str
    lineno: int
    calls: set[str] = field(default_factory=set)
    is_test: bool = False


@dataclass
class ClassFact:
    """A class definition and its base-class simple names."""

    name: str
    lineno: int
    bases: list[str] = field(default_factory=list)


@dataclass
class FileFacts:
    """All facts extracted from a single source file."""

    module: str
    rel: str
    classes: list[ClassFact] = field(default_factory=list)
    functions: list[FuncFact] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)


def _called_name(node: ast.Call) -> str | None:
    """Return the simple callee name of a Call (``f()`` or ``obj.f()``)."""
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _collect_calls(fn: ast.AST) -> set[str]:
    """Return the set of simple names called anywhere inside ``fn``."""
    names: set[str] = set()
    for sub in ast.walk(fn):
        if isinstance(sub, ast.Call):
            name = _called_name(sub)
            if name:
                names.add(name)
    return names


def analyze_file(source: str, module: str, rel: str) -> FileFacts:
    """Parse ``source`` and return its :class:`FileFacts`.

    Args:
        source: File contents.
        module: Dotted module name (e.g. ``cookiecutter.hooks``).
        rel: Posix path relative to the scan root (the node ``source_file``).
    """
    facts = FileFacts(module=module, rel=rel)
    is_test_file = "test" in rel.rsplit("/", 1)[-1]
    tree = ast.parse(source, filename=rel)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            facts.classes.append(ClassFact(name=node.name, lineno=node.lineno, bases=bases))
        elif isinstance(node, ast.ImportFrom) and node.module:
            facts.imports.append(node.module)
        elif isinstance(node, ast.Import):
            facts.imports.extend(alias.name for alias in node.names)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            is_test = is_test_file and node.name.startswith("test")
            facts.functions.append(
                FuncFact(
                    qualname=node.name,
                    name=node.name,
                    lineno=node.lineno,
                    calls=_collect_calls(node),
                    is_test=is_test,
                )
            )
    return facts
