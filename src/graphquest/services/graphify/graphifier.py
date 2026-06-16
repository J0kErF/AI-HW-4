"""Graphify orchestrator — ties the evidence layers into one graph + artifacts.

Pipeline: Files → CodeLayer (deterministic, EXTRACTED) → [SemanticLayer, optional]
→ MetricsCalculator → graph.json + GRAPH_REPORT.md + Obsidian vault.

The semantic layer is *optional* and skipped when disabled or no LLM key is
configured, so the full pipeline always runs token-free and produces a real
graph; semantic enrichment only augments it.
"""

from __future__ import annotations

import json
from pathlib import Path

from graphquest.constants import GRAPH_JSON, GRAPH_REPORT
from graphquest.services.graphify.code_layer import CodeLayer
from graphquest.services.graphify.metrics import MetricsCalculator
from graphquest.services.graphify.models import CodeGraph
from graphquest.services.graphify.report_writer import ReportWriter
from graphquest.services.graphify.vault_writer import VaultWriter


class Graphifier:
    """Compose the layers and emit all Graphify artifacts.

    Args:
        code_layer: Deterministic AST extractor.
        metrics: Centrality/community calculator.
        vault_writer: Obsidian vault renderer.
        report_writer: GRAPH_REPORT.md renderer.
        artifacts_dir: Where ``graph.json`` / ``GRAPH_REPORT.md`` are written.
        semantic_layer: Optional bounded LLM augmenter (skipped if None).
        hot_seed: Optional failing-symptom text for ``hot.md``.
    """

    def __init__(
        self,
        code_layer: CodeLayer,
        metrics: MetricsCalculator,
        vault_writer: VaultWriter,
        report_writer: ReportWriter,
        artifacts_dir: Path,
        semantic_layer: object | None = None,
        hot_seed: str | None = None,
    ) -> None:
        self._code = code_layer
        self._metrics = metrics
        self._vault = vault_writer
        self._report = report_writer
        self._artifacts = artifacts_dir
        self._semantic = semantic_layer
        self._hot_seed = hot_seed

    def build(self) -> CodeGraph:
        """Run the full pipeline and return the assembled :class:`CodeGraph`."""
        nodes, edges = self._code.extract()
        graph = CodeGraph(nodes=nodes, edges=edges)
        if self._semantic is not None:
            graph.edges.extend(self._semantic.augment(graph.nodes))

        metrics = self._metrics.compute(graph)
        self._artifacts.mkdir(parents=True, exist_ok=True)
        (self._artifacts / GRAPH_JSON).write_text(
            json.dumps(graph.to_dict(), indent=2), encoding="utf-8"
        )
        self._report.write(graph, metrics, self._artifacts / GRAPH_REPORT)
        self._vault.write(graph, metrics, hot_seed=self._hot_seed)
        return graph
