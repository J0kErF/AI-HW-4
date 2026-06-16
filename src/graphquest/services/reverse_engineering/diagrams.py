"""Reverse-engineering deliverables: block diagram + OOP schema (EX04 §5.2).

Generates, FROM THE GRAPH (not by hand), the two mandatory visual insights:

* a block (component) architecture diagram showing the main parts and data flow
* an OOP/class schema (usage, composition, inheritance, wrappers)

Both are emitted as Mermaid so they render in GitHub/Obsidian, and both are
derived from the deterministic code layer so they reflect the *actual* code,
not the PRD's intent (Graphify spec: PRD-vs-implementation gap).
"""

from __future__ import annotations

from graphquest.services.graphify.models import CodeGraph


class DiagramGenerator:
    """Produce Mermaid block + class diagrams from a :class:`CodeGraph`."""

    def block_diagram(self, graph: CodeGraph) -> str:
        """Return a Mermaid ``flowchart`` of components grouped by community."""
        raise NotImplementedError("Phase 2: communities -> subgraphs + flows")

    def oop_schema(self, graph: CodeGraph) -> str:
        """Return a Mermaid ``classDiagram`` from class/inherits/uses edges."""
        raise NotImplementedError("Phase 2: classes -> classDiagram")
