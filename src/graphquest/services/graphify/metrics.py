"""Graph-theory metrics via NetworkX (Graphify "Centrality and Communities").

Pure structural analysis (zero tokens): degree & betweenness centrality (hubs /
God-nodes / bottlenecks), greedy-modularity communities (connectivity patterns
that may cross folders), and bridges (single points of dependency). These signals
decide what ``hot.md`` surfaces first.
"""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx

from graphquest.services.graphify.models import CodeGraph


@dataclass
class GraphMetrics:
    """Per-graph analysis results consumed by the report and vault writers."""

    degree_centrality: dict[str, float]
    betweenness_centrality: dict[str, float]
    communities: dict[str, int]      # node id -> community id
    bridges: list[tuple[str, str]]
    god_nodes: list[str]             # highest-betweenness nodes (bottleneck candidates)


class MetricsCalculator:
    """Compute centrality, communities and bridges over a :class:`CodeGraph`."""

    def __init__(self, god_node_top_k: int = 5) -> None:
        self._top_k = god_node_top_k

    def _to_nx(self, graph: CodeGraph) -> nx.DiGraph:
        g = nx.DiGraph()
        g.add_nodes_from(n.id for n in graph.nodes)
        g.add_edges_from((e.source, e.target) for e in graph.edges)
        return g

    def compute(self, graph: CodeGraph) -> GraphMetrics:
        """Return :class:`GraphMetrics` for ``graph`` using NetworkX algorithms."""
        digraph = self._to_nx(graph)
        undirected = digraph.to_undirected()

        degree = nx.degree_centrality(digraph)
        betweenness = nx.betweenness_centrality(digraph)

        communities: dict[str, int] = {}
        for cid, members in enumerate(nx.community.greedy_modularity_communities(undirected)):
            for node_id in members:
                communities[node_id] = cid

        bridges = list(nx.bridges(undirected)) if undirected.number_of_edges() else []
        god_nodes = [
            node_id
            for node_id, _ in sorted(betweenness.items(), key=lambda kv: kv[1], reverse=True)
            if betweenness[node_id] > 0
        ][: self._top_k]

        return GraphMetrics(degree, betweenness, communities, bridges, god_nodes)
