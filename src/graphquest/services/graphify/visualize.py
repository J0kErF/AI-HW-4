"""Graph visualization (Graphify exports: graph.html + a PNG "screenshot").

Completes the Graphify export triad — `graph.html` to *see* structure (interactive,
pyvis), alongside `graph.json` (verify) and `GRAPH_REPORT.md` (understand). Also
renders a static PNG of the most-central subgraph (community-coloured, suspects
highlighted) for the README and notebook. Pure structure → zero tokens.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402

from graphquest.services.graphify.metrics import GraphMetrics  # noqa: E402
from graphquest.services.graphify.models import CodeGraph  # noqa: E402

_PALETTE = ["#4e79a7", "#f28e2b", "#59a14f", "#e15759", "#b07aa1",
            "#76b7b2", "#edc948", "#ff9da7", "#9c755f", "#bab0ac"]


def _digraph(graph: CodeGraph) -> nx.DiGraph:
    g = nx.DiGraph()
    g.add_nodes_from(n.id for n in graph.nodes)
    g.add_edges_from((e.source, e.target) for e in graph.edges)
    return g


class GraphVisualizer:
    """Render a :class:`CodeGraph` to a PNG and an interactive HTML."""

    def render_png(
        self, graph: CodeGraph, metrics: GraphMetrics, out_png: Path,
        highlight_labels: tuple[str, ...] = (), top_k: int = 45,
    ) -> None:
        """Render the top-degree subgraph (community-coloured) to ``out_png``."""
        labels = {n.id: n.label for n in graph.nodes}
        ranked = sorted(metrics.degree_centrality, key=metrics.degree_centrality.get, reverse=True)
        core = set(ranked[:top_k]) | {n for n, lbl in labels.items() if lbl in highlight_labels}
        sub = _digraph(graph).subgraph(core).to_undirected()
        if sub.number_of_nodes() == 0:
            return
        pos = nx.spring_layout(sub, seed=42, k=0.6)
        colors = [_PALETTE[(metrics.communities.get(n, 0)) % len(_PALETTE)] for n in sub.nodes]
        sizes = [200 + 4000 * metrics.degree_centrality.get(n, 0) for n in sub.nodes]
        edgecols = ["#d62728" if labels.get(n) in highlight_labels else "#ffffff" for n in sub.nodes]

        fig, ax = plt.subplots(figsize=(11, 8))
        nx.draw_networkx_edges(sub, pos, ax=ax, alpha=0.25, edge_color="#888888")
        nx.draw_networkx_nodes(sub, pos, ax=ax, node_color=colors, node_size=sizes,
                               edgecolors=edgecols, linewidths=2.0)
        show = sorted(sub.nodes, key=lambda n: metrics.degree_centrality.get(n, 0), reverse=True)[:12]
        show += [n for n in sub.nodes if labels.get(n) in highlight_labels]
        nx.draw_networkx_labels(sub, pos, ax=ax, font_size=8,
                                labels={n: labels.get(n, n) for n in set(show)})
        ax.set_title("GraphQuest — central subgraph (colour = community, ring = bug suspect)")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(out_png, dpi=130)
        plt.close(fig)

    def render_html(self, graph: CodeGraph, metrics: GraphMetrics, out_html: Path) -> None:
        """Render the connected graph to an interactive ``graph.html`` (pyvis)."""
        from pyvis.network import Network

        labels = {n.id: n.label for n in graph.nodes}
        files = {n.id: n.source_file for n in graph.nodes}
        connected = {e.source for e in graph.edges} | {e.target for e in graph.edges}
        # cdn_resources="remote" -> self-contained HTML (vis-network from CDN, no lib/ dir)
        net = Network(height="800px", width="100%", directed=True, notebook=False,
                      cdn_resources="remote")
        for nid in connected:
            comm = metrics.communities.get(nid, 0)
            net.add_node(nid, label=labels.get(nid, nid), title=files.get(nid, ""),
                         color=_PALETTE[comm % len(_PALETTE)],
                         size=10 + 60 * metrics.degree_centrality.get(nid, 0))
        for e in graph.edges:
            net.add_edge(e.source, e.target, title=f"{e.label.value} ({e.evidence.value})")
        out_html.parent.mkdir(parents=True, exist_ok=True)
        net.write_html(str(out_html), notebook=False)
