"""Reverse-engineering deliverables: block + OOP diagrams (EX04 §5.2).

Generates, FROM THE GRAPH (not by hand), the two mandatory visuals as Mermaid
(renders in GitHub/Obsidian):

* ``block_diagram`` — a component flowchart: modules grouped by top-level
  package directory, with import edges as data flow.
* ``oop_schema`` — a class diagram from class nodes and ``inherits`` edges.

Both reflect the *actual* code (deterministic AST layer), which is what lets us
surface PRD-vs-implementation gaps.
"""

from __future__ import annotations

from graphquest.constants import EdgeLabel, NodeType
from graphquest.services.graphify.models import CodeGraph, Node


def _mid(node_id: str) -> str:
    """Mermaid-safe node id."""
    return "n_" + node_id.replace("/", "_").replace("::", "__").replace(".", "_").replace("-", "_")


class DiagramGenerator:
    """Produce Mermaid block + class diagrams from a :class:`CodeGraph`."""

    def block_diagram(self, graph: CodeGraph) -> str:
        """Return a Mermaid ``flowchart`` of modules grouped by directory."""
        modules = [n for n in graph.nodes if n.type is NodeType.MODULE]
        groups: dict[str, list[Node]] = {}
        for m in modules:
            top = m.source_file.split("/")[0] if "/" in m.source_file else "(root)"
            groups.setdefault(top, []).append(m)

        lines = ["flowchart TD"]
        for group, members in sorted(groups.items()):
            lines.append(f"  subgraph {group}")
            for m in sorted(members, key=lambda n: n.source_file):
                lines.append(f'    {_mid(m.id)}["{m.source_file.split("/")[-1]}"]')
            lines.append("  end")

        module_ids = {m.id for m in modules}
        for e in graph.edges:
            if e.label is EdgeLabel.IMPORTS and e.source in module_ids and e.target in module_ids:
                lines.append(f"  {_mid(e.source)} --> {_mid(e.target)}")
        return "\n".join(lines)

    def oop_schema(self, graph: CodeGraph) -> str:
        """Return a Mermaid ``classDiagram`` from class + inherits edges."""
        classes = {n.id: n for n in graph.nodes if n.type is NodeType.CLASS}
        lines = ["classDiagram"]
        for c in sorted(classes.values(), key=lambda n: n.label):
            lines.append(f"  class {c.label}")
        for e in graph.edges:
            if e.label is EdgeLabel.INHERITS and e.source in classes and e.target in classes:
                base, derived = classes[e.target].label, classes[e.source].label
                lines.append(f"  {base} <|-- {derived}")
        return "\n".join(lines)
