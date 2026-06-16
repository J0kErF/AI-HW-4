"""Tests for the graph visualizer (PNG always; HTML best-effort)."""

from pathlib import Path

from graphquest.constants import EdgeLabel, EvidenceType, NodeType
from graphquest.services.graphify.metrics import MetricsCalculator
from graphquest.services.graphify.models import CodeGraph, Edge, Node
from graphquest.services.graphify.visualize import GraphVisualizer


def _graph() -> CodeGraph:
    nodes = [Node(n, NodeType.FUNCTION, n, "m.py") for n in ("hub", "a", "b", "find_hook")]
    edges = [
        Edge(s, "hub", EdgeLabel.CALLS, EvidenceType.EXTRACTED, 0.9, "m.py")
        for s in ("a", "b", "find_hook")
    ]
    return CodeGraph(nodes=nodes, edges=edges)


def test_render_png_writes_file(tmp_path: Path) -> None:
    """A PNG is written for the central subgraph with the suspect highlighted."""
    graph = _graph()
    metrics = MetricsCalculator().compute(graph)
    out = tmp_path / "graph_viz.png"
    GraphVisualizer().render_png(graph, metrics, out, highlight_labels=("find_hook",))
    assert out.exists() and out.stat().st_size > 0


def test_render_html_writes_file(tmp_path: Path) -> None:
    """The interactive graph.html (pyvis) is written for the connected nodes."""
    graph = _graph()
    metrics = MetricsCalculator().compute(graph)
    out = tmp_path / "graph.html"
    GraphVisualizer().render_html(graph, metrics, out)
    assert out.exists()
    assert "html" in out.read_text(encoding="utf-8", errors="replace").lower()
