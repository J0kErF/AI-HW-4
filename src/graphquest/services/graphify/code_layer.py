"""Deterministic code-structure layer (Graphify "Code Structure", 0 tokens).

Discovers Python files under the scan root, extracts per-file facts via
:mod:`ast_visitor`, and assembles module/class/function nodes plus EXTRACTED
edges (imports, inherits, calls, tested_by). Name resolution is conservative:
an edge is emitted only when a called/base name resolves to exactly one node,
keeping the graph trustworthy (no guesses — those are the semantic layer's job).
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

from graphquest.constants import EdgeLabel, EvidenceType, NodeType
from graphquest.services.graphify.ast_visitor import FileFacts, analyze_file
from graphquest.services.graphify.models import Edge, Node


class CodeLayer:
    """AST-based extractor for one Python source tree.

    Args:
        scan_root: Directory of the cloned target repository.
        include_globs: File patterns to include.
        exclude_globs: File patterns to skip.
        confidence: Confidence assigned to EXTRACTED edges (from config).
    """

    def __init__(
        self,
        scan_root: Path,
        include_globs: list[str],
        exclude_globs: list[str],
        confidence: float = 0.95,
    ) -> None:
        self._root = scan_root
        self._include = include_globs
        self._exclude = exclude_globs
        self._conf = confidence

    def _discover(self) -> list[Path]:
        """Return included, non-excluded files under the scan root (sorted)."""
        found: set[Path] = set()
        for pattern in self._include:
            found.update(self._root.glob(pattern))
        kept = []
        for path in sorted(found):
            rel = path.relative_to(self._root).as_posix()
            if not any(fnmatch.fnmatch(rel, pat.replace("**/", "*")) for pat in self._exclude):
                kept.append(path)
        return kept

    def extract(self) -> tuple[list[Node], list[Edge]]:
        """Return EXTRACTED nodes and edges from AST analysis (deterministic).

        Files that fail to parse (e.g. Jinja template fixtures masquerading as
        ``.py``) are skipped — they are not real source.
        """
        all_facts = [f for f in (self._read(p) for p in self._discover()) if f is not None]
        nodes, name_index = self._build_nodes(all_facts)
        edges = self._build_edges(all_facts, name_index)
        return nodes, edges

    def _read(self, path: Path) -> FileFacts | None:
        rel = path.relative_to(self._root).as_posix()
        module = rel[:-3].replace("/", ".") if rel.endswith(".py") else rel
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            return analyze_file(source, module, rel)
        except (SyntaxError, ValueError):
            return None  # not valid Python (template fixture, etc.)

    def _build_nodes(self, facts: list[FileFacts]) -> tuple[list[Node], dict[str, list[str]]]:
        """Create nodes and a simple-name -> node-id index for resolution."""
        nodes: list[Node] = []
        index: dict[str, list[str]] = {}

        def add(node_id, ntype, label, src, key, line=0, end=0):  # noqa: ANN001, ANN202
            nodes.append(Node(id=node_id, type=ntype, label=label, source_file=src,
                              line=line, end_line=end))
            index.setdefault(key, []).append(node_id)

        for f in facts:
            add(f.rel, NodeType.MODULE, f.module, f.rel, f.module)
            for c in f.classes:
                add(f"{f.rel}::{c.name}", NodeType.CLASS, c.name, f.rel, c.name,
                    c.lineno, c.end_lineno)
            for fn in f.functions:
                add(f"{f.rel}::{fn.qualname}", NodeType.FUNCTION, fn.name, f.rel, fn.name,
                    fn.lineno, fn.end_lineno)
        return nodes, index

    def _resolve(self, name: str, index: dict[str, list[str]], exclude_id: str) -> str | None:
        """Return the unique node id for ``name`` (else None — conservative)."""
        candidates = [c for c in index.get(name, []) if c != exclude_id]
        return candidates[0] if len(candidates) == 1 else None

    def _build_edges(self, facts: list[FileFacts], index: dict[str, list[str]]) -> list[Edge]:
        """Emit imports/inherits/calls/tested_by EXTRACTED edges."""
        edges: list[Edge] = []

        def emit(src: str, tgt: str, label: EdgeLabel, file: str) -> None:
            edges.append(
                Edge(src, tgt, label, EvidenceType.EXTRACTED, self._conf, file)
            )

        module_by_dotted = {f.module: f.rel for f in facts}
        for f in facts:
            for imp in f.imports:
                if imp in module_by_dotted and module_by_dotted[imp] != f.rel:
                    emit(f.rel, module_by_dotted[imp], EdgeLabel.IMPORTS, f.rel)
            for c in f.classes:
                cid = f"{f.rel}::{c.name}"
                for base in c.bases:
                    tgt = self._resolve(base, index, cid)
                    if tgt:
                        emit(cid, tgt, EdgeLabel.INHERITS, f.rel)
            for fn in f.functions:
                fid = f"{f.rel}::{fn.qualname}"
                for called in fn.calls:
                    tgt = self._resolve(called, index, fid)
                    if tgt:
                        label = EdgeLabel.TESTED_BY if fn.is_test else EdgeLabel.CALLS
                        emit(fid, tgt, label, f.rel)
        return edges
