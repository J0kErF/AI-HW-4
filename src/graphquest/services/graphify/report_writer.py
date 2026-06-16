"""GRAPH_REPORT.md writer (Graphify export: the narrative "story" of the graph).

Renders a human-readable summary — size, central nodes, God-node/bottleneck
candidates, communities and bridges — so a reader interprets the graph
responsibly instead of trusting a pretty picture.
"""

from __future__ import annotations

from pathlib import Path

from graphquest.services.graphify.metrics import GraphMetrics
from graphquest.services.graphify.models import CodeGraph


class ReportWriter:
    """Write ``GRAPH_REPORT.md`` from a graph + its metrics."""

    def write(self, graph: CodeGraph, metrics: GraphMetrics, out_path: Path) -> None:
        """Render the narrative report to ``out_path``."""
        labels = {n.id: n.label for n in graph.nodes}
        n_comm = len(set(metrics.communities.values())) if metrics.communities else 0
        lines = [
            "# GRAPH_REPORT — Graphify",
            "",
            f"- Nodes: **{len(graph.nodes)}**  ·  Edges: **{len(graph.edges)}**  ·  "
            f"Communities: **{n_comm}**  ·  Bridges: **{len(metrics.bridges)}**",
            "",
            "## God-node / bottleneck candidates (highest betweenness)",
            "_All paths through one node = architectural risk; verify against source._",
            "",
        ]
        for nid in metrics.god_nodes:
            lines.append(f"- `{labels.get(nid, nid)}` — betweenness "
                         f"{metrics.betweenness_centrality.get(nid, 0):.3f} (`{nid}`)")
        lines += ["", "## Top central nodes (degree)", ""]
        top = sorted(metrics.degree_centrality.items(), key=lambda kv: kv[1], reverse=True)[:8]
        for nid, val in top:
            lines.append(f"- `{labels.get(nid, nid)}` — degree {val:.3f}")
        lines += ["", "## Bridges (single points of dependency)", ""]
        for a, b in metrics.bridges[:15]:
            lines.append(f"- `{labels.get(a, a)}` — `{labels.get(b, b)}`")
        lines.append("")
        out_path.write_text("\n".join(lines), encoding="utf-8")
