"""Graph-guided tools exposed to the agent (Graphify spec: query/path/explain).

These tools are the agent's ONLY way to pull code context. They read from the
graph + vault, never raw whole files, which is the mechanism that minimizes
context (vs the naive baseline reading entire files). Each tool returns the
smallest evidence slice needed to answer a focused question.
"""

from __future__ import annotations

from pathlib import Path


class GraphTools:
    """Focused-retrieval toolbox backed by ``graph.json`` and the vault.

    Args:
        graph_json: Path to ``artifacts/graph.json``.
        vault_dir: Path to ``obsidian/wiki``.
    """

    def __init__(self, graph_json: Path, vault_dir: Path) -> None:
        self._graph_json = graph_json
        self._vault = vault_dir

    def query(self, label: str | None = None, min_confidence: float = 0.0) -> list[dict]:
        """Find candidate nodes/edges by label / confidence (query command)."""
        raise NotImplementedError("Phase 2")

    def path(self, source_id: str, target_id: str) -> list[dict]:
        """Return the traceability path between two nodes (path command)."""
        raise NotImplementedError("Phase 2")

    def explain(self, node_id: str) -> str:
        """Return a node's vault note + its incident edges (explain command).

        This is the focused read that replaces opening the whole source file.
        """
        raise NotImplementedError("Phase 2")

    def read_source_span(self, node_id: str) -> str:
        """Read ONLY the source lines for one node (validation step SRC)."""
        raise NotImplementedError("Phase 2")
