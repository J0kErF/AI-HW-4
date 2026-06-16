"""Tests for Mermaid diagram generation and the RE report."""

from pathlib import Path

from graphquest.constants import EdgeLabel, EvidenceType, NodeType
from graphquest.services.graphify.metrics import MetricsCalculator
from graphquest.services.graphify.models import CodeGraph, Edge, Node
from graphquest.services.reverse_engineering.diagrams import DiagramGenerator
from graphquest.services.reverse_engineering.report import ReverseEngineeringReport


def _graph() -> CodeGraph:
    """Two modules (a imports b) and a class hierarchy (Derived inherits Base)."""
    nodes = [
        Node("pkg/a.py", NodeType.MODULE, "pkg.a", "pkg/a.py"),
        Node("pkg/b.py", NodeType.MODULE, "pkg.b", "pkg/b.py"),
        Node("pkg/b.py::Base", NodeType.CLASS, "Base", "pkg/b.py"),
        Node("pkg/a.py::Derived", NodeType.CLASS, "Derived", "pkg/a.py"),
    ]
    edges = [
        Edge("pkg/a.py", "pkg/b.py", EdgeLabel.IMPORTS, EvidenceType.EXTRACTED, 0.95, "pkg/a.py"),
        Edge("pkg/a.py::Derived", "pkg/b.py::Base", EdgeLabel.INHERITS,
             EvidenceType.EXTRACTED, 0.95, "pkg/a.py"),
    ]
    return CodeGraph(nodes=nodes, edges=edges)


def test_block_diagram_groups_and_flows() -> None:
    """Block diagram is a flowchart with a subgraph and an import edge."""
    out = DiagramGenerator().block_diagram(_graph())
    assert out.startswith("flowchart TD")
    assert "subgraph pkg" in out
    assert "-->" in out  # the import edge


def test_oop_schema_renders_inheritance() -> None:
    """OOP schema declares classes and the Base<|--Derived relation."""
    out = DiagramGenerator().oop_schema(_graph())
    assert out.startswith("classDiagram")
    assert "class Base" in out and "class Derived" in out
    assert "Base <|-- Derived" in out


def test_report_includes_diagrams_and_two_insights(tmp_path: Path) -> None:
    """Report embeds both Mermaid blocks and both insight sections."""
    graph = _graph()
    metrics = MetricsCalculator().compute(graph)
    gen = DiagramGenerator()
    out = tmp_path / "RE.md"
    ReverseEngineeringReport().write(
        graph, metrics, gen.block_diagram(graph), gen.oop_schema(graph), out
    )
    text = out.read_text(encoding="utf-8")
    assert "```mermaid" in text
    assert "Insight A" in text and "Insight B" in text
    assert "find_hook" in text  # the rationale-vs-implementation gap
