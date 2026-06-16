"""Graph data model — nodes and edges (Graphify spec: "Node is an entity;
Edge is a claim").

These dataclasses define the schema of ``artifacts/graph.json``. Each edge
carries a label, direction, confidence and evidence type plus its
``source_file`` so every conclusion can be traced back to the source.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from graphquest.constants import EdgeLabel, EvidenceType, NodeType


@dataclass(frozen=True)
class Node:
    """A software/knowledge entity in the graph.

    Args:
        id: Stable unique id, e.g. ``"thefuck/rules/cd_mkdir.py::match"``.
        type: One of :class:`~graphquest.constants.NodeType`.
        label: Human-readable name shown in the vault / html.
        source_file: Path (relative to the scan root) where the entity lives.
        community: Louvain community id, filled in by the metrics pass.
    """

    id: str
    type: NodeType
    label: str
    source_file: str
    line: int = 0
    end_line: int = 0
    community: int | None = None

    def to_dict(self) -> dict:
        """Serialize for ``graph.json`` (enum values flattened to strings)."""
        d = asdict(self)
        d["type"] = self.type.value
        return d


@dataclass(frozen=True)
class Edge:
    """A directed *claim* about a relation between two nodes.

    Args:
        source: Source node id.
        target: Target node id.
        label: One of :class:`~graphquest.constants.EdgeLabel`.
        evidence: Evidence strength (extracted/inferred/ambiguous).
        confidence: 0.55-0.95 score aligned with ``evidence``.
        source_file: File the claim was derived from.
    """

    source: str
    target: str
    label: EdgeLabel
    evidence: EvidenceType
    confidence: float
    source_file: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["label"] = self.label.value
        d["evidence"] = self.evidence.value
        return d


@dataclass
class CodeGraph:
    """Container for the full graph plus convenience serialization."""

    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Render the whole graph as the ``graph.json`` payload."""
        return {
            "version": "1.00",
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }
