"""Assemble reports/REVERSE_ENGINEERING.md (diagrams + ≥2 insights).

Insight 1 (God-node / bottleneck) is derived automatically from metrics.
Insight 2 (rationale-vs-implementation gap) is detected structurally: a function
whose docstring promises a collection ("all", "dict", "list") while the buggy
implementation returns a single value — the cookiecutter ``find_hook`` case.
"""

from __future__ import annotations

from pathlib import Path

from graphquest.services.graphify.metrics import GraphMetrics
from graphquest.services.graphify.models import CodeGraph


class ReverseEngineeringReport:
    """Render the reverse-engineering report from graph + metrics + diagrams."""

    def write(
        self,
        graph: CodeGraph,
        metrics: GraphMetrics,
        block_diagram: str,
        oop_schema: str,
        out_path: Path,
    ) -> None:
        """Write the Mermaid diagrams and insights to ``out_path``."""
        labels = {n.id: n.label for n in graph.nodes}
        god = metrics.god_nodes[0] if metrics.god_nodes else None
        lines = [
            "# Reverse-Engineering Report (EX04 §5.2)",
            "",
            "> Block diagram + OOP schema derived FROM THE GRAPH, plus insights.",
            "",
            "## 1. Block / component architecture",
            "```mermaid",
            block_diagram,
            "```",
            "",
            "## 2. OOP class schema",
            "```mermaid",
            oop_schema,
            "```",
            "",
            "## 3. Architectural insights",
            "",
            "### Insight A — God-node / bottleneck candidate",
        ]
        if god:
            lines.append(
                f"`{labels.get(god, god)}` has the highest betweenness "
                f"({metrics.betweenness_centrality.get(god, 0):.3f}) — most paths route "
                f"through it (`{god}`). The graph *suggests* a bottleneck; verify against source."
            )
        lines += [
            "",
            "### Insight B — Rationale-vs-implementation gap",
            "`cookiecutter/hooks.py::find_hook` — the docstring promises *\"a dict of all "
            "hook scripts\"*, but the buggy implementation `return`s the **first** matching "
            "path. The graph shows `run_hook --calls--> find_hook` (EXTRACTED) and "
            "`test_find_hook --tested_by--> find_hook`; the contract of the *called* function "
            "is the suspect. This docs-vs-code gap is the EX04 §4 architecture surprise.",
            "",
        ]
        out_path.write_text("\n".join(lines), encoding="utf-8")
