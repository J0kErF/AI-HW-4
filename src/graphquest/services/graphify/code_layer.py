"""Deterministic code-structure layer (Graphify spec: "Code Structure —
deterministic extraction of imports, calls and software entities via AST").

This layer costs ZERO tokens: it walks the Python AST to emit EXTRACTED edges
(imports, calls, class inheritance, function definitions). This is the cheap
backbone of the graph; the semantic layer only augments it where needed.
"""

from __future__ import annotations

from pathlib import Path

from graphquest.services.graphify.models import Edge, Node


class CodeLayer:
    """AST-based extractor for one Python source tree.

    Args:
        scan_root: Directory of the cloned target repository.
        include_globs: File patterns to include.
        exclude_globs: File patterns to skip.
    """

    def __init__(
        self,
        scan_root: Path,
        include_globs: list[str],
        exclude_globs: list[str],
    ) -> None:
        self._root = scan_root
        self._include = include_globs
        self._exclude = exclude_globs

    def extract(self) -> tuple[list[Node], list[Edge]]:
        """Return EXTRACTED nodes and edges from AST analysis.

        Emits ``module``/``class``/``function`` nodes and ``imports``/``calls``/
        ``inherits``/``tested_by`` edges, all with evidence=EXTRACTED.
        """
        raise NotImplementedError("Phase 2: ast.walk over included files")
