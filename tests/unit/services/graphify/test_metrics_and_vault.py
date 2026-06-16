"""Tests for NetworkX metrics and the Obsidian vault writer."""

from pathlib import Path

from graphquest.constants import EdgeLabel, EvidenceType, NodeType
from graphquest.services.graphify.metrics import MetricsCalculator
from graphquest.services.graphify.models import CodeGraph, Edge, Node
from graphquest.services.graphify.vault_writer import VaultWriter


def _graph() -> CodeGraph:
    """A small star: hub called by a, b, c (hub = high centrality)."""
    nodes = [Node(n, NodeType.FUNCTION, n, "m.py") for n in ("hub", "a", "b", "c")]
    edges = [
        Edge(s, "hub", EdgeLabel.CALLS, EvidenceType.EXTRACTED, 0.9, "m.py")
        for s in ("a", "b", "c")
    ]
    return CodeGraph(nodes=nodes, edges=edges)


def test_metrics_rank_hub_highest_degree() -> None:
    """The hub has the highest degree centrality and a community assignment."""
    m = MetricsCalculator().compute(_graph())
    assert max(m.degree_centrality, key=m.degree_centrality.get) == "hub"
    assert set(m.communities) == {"hub", "a", "b", "c"}


def test_vault_writer_emits_index_hot_and_notes(tmp_path: Path) -> None:
    """Vault contains index.md, hot.md and one note per node with wikilinks."""
    graph = _graph()
    m = MetricsCalculator().compute(graph)
    VaultWriter(tmp_path).write(graph, m, hot_seed="symptom X")

    assert (tmp_path / "index.md").exists()
    hot = (tmp_path / "hot.md").read_text(encoding="utf-8")
    assert "symptom X" in hot
    note = (tmp_path / "a.md").read_text(encoding="utf-8")
    assert "[[hub]]" in note and "calls" in note
