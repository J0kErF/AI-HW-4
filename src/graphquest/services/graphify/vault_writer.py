"""Obsidian vault writer (Graphify export: ``wiki/`` + index.md/hot.md).

Renders the graph as a navigable Obsidian vault of Markdown notes linked with
``[[wikilinks]]``. ``index.md`` is the Macro map; ``hot.md`` is the focused
bug-critical region (centrality + the community of the suspect node); each node
gets a note listing its incident edges with evidence + confidence. This vault is
the agent's token-cheap context surface.
"""

from __future__ import annotations

from pathlib import Path

from graphquest.services.graphify.metrics import GraphMetrics
from graphquest.services.graphify.models import CodeGraph, Edge, Node


class VaultWriter:
    """Render a :class:`CodeGraph` + metrics into an Obsidian vault.

    Args:
        vault_dir: Target directory (``obsidian/wiki``).
    """

    def __init__(self, vault_dir: Path) -> None:
        self._dir = vault_dir

    def write(self, graph: CodeGraph, metrics: GraphMetrics, hot_seed: str | None = None) -> None:
        """Write ``index.md``, ``hot.md`` and per-node notes with wikilinks."""
        self._dir.mkdir(parents=True, exist_ok=True)
        out = {e.source: [] for e in graph.edges}
        for e in graph.edges:
            out.setdefault(e.source, []).append(e)
        for n in graph.nodes:
            self._write_note(n, out.get(n.id, []))
        self._write_index(graph, metrics)
        self._write_hot(graph, metrics, hot_seed)

    @staticmethod
    def _slug(node_id: str) -> str:
        """Obsidian-safe note name for a node id."""
        return node_id.replace("/", "_").replace("::", "__").replace(".", "_")

    def _write_note(self, node: Node, edges: list[Edge]) -> None:
        lines = [f"# {node.label}", "", f"- type: `{node.type.value}`",
                 f"- source: `{node.source_file}`", "", "## Edges"]
        for e in edges:
            lines.append(f"- `{e.label.value}` → [[{self._slug(e.target)}]] "
                         f"({e.evidence.value} {e.confidence:.2f})")
        (self._dir / f"{self._slug(node.id)}.md").write_text("\n".join(lines) + "\n", "utf-8")

    def _label(self, graph: CodeGraph, node_id: str) -> str:
        for n in graph.nodes:
            if n.id == node_id:
                return n.label
        return node_id

    def _write_index(self, graph: CodeGraph, metrics: GraphMetrics) -> None:
        n_comm = len(set(metrics.communities.values())) if metrics.communities else 0
        lines = ["# Index — Portfolio Entry (Macro view)", "",
                 f"Nodes **{len(graph.nodes)}** · Edges **{len(graph.edges)}** · "
                 f"Communities **{n_comm}**.", "", "## Central nodes (hubs)", ""]
        top = sorted(metrics.degree_centrality.items(), key=lambda kv: kv[1], reverse=True)[:8]
        for nid, _ in top:
            lines.append(f"- [[{self._slug(nid)}]] — {self._label(graph, nid)}")
        lines += ["", "See [[hot]] for the bug-critical region.", ""]
        (self._dir / "index.md").write_text("\n".join(lines), encoding="utf-8")

    def _write_hot(self, graph: CodeGraph, metrics: GraphMetrics, seed: str | None) -> None:
        lines = ["# Hot — Focused Bug Context (Meso/Micro view)", "",
                 f"Failing symptom: {seed or '_set in config target_'}", "",
                 "## God-node / bottleneck candidates", ""]
        for nid in metrics.god_nodes:
            lines.append(f"- [[{self._slug(nid)}]] — betweenness "
                         f"{metrics.betweenness_centrality.get(nid, 0):.3f}")
        lines += ["", "> Conclusions must match evidence strength — "
                  "'the graph suggests…' until validated against source.", ""]
        (self._dir / "hot.md").write_text("\n".join(lines), encoding="utf-8")
