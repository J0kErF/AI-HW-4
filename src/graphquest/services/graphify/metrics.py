"""Graph-theory metrics (Graphify spec: "Centrality and Communities").

Computes the signals an engineer reads off the graph: degree & betweenness
centrality (hubs / God-nodes / bottlenecks), Louvain communities (connectivity
patterns that may cross folders), and bridge detection. Pure NetworkX — zero
tokens. These metrics drive ``hot.md`` (what to investigate first).
"""

from __future__ import annotations

from dataclasses import dataclass

from graphquest.services.graphify.models import CodeGraph


@dataclass
class GraphMetrics:
    """Per-graph analysis results consumed by the report and vault writers."""

    degree_centrality: dict[str, float]
    betweenness_centrality: dict[str, float]
    communities: dict[str, int]      # node id -> community id
    bridges: list[tuple[str, str]]
    god_nodes: list[str]             # high betweenness => bottleneck candidates


class MetricsCalculator:
    """Compute centrality, communities and bridges over a :class:`CodeGraph`."""

    def compute(self, graph: CodeGraph) -> GraphMetrics:
        """Return :class:`GraphMetrics` for ``graph`` using NetworkX algorithms.

        God-node detection uses betweenness above a knee in the distribution,
        flagged for the bottleneck-vs-healthy-hub judgement (Graphify spec).
        """
        raise NotImplementedError("Phase 2: nx.betweenness_centrality + community.louvain")
