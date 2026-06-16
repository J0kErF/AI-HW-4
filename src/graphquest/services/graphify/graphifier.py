"""Graphify orchestrator — ties the three evidence layers into one graph.

Pipeline (Graphify spec: "evidence converges here"):
    Files -> CodeLayer (deterministic) -> SemanticLayer (LLM, bounded)
          -> MetricsCalculator -> graph.json + GRAPH_REPORT.md + vault.

This is the service the SDK calls for the "build representation" deliverable.
Kept thin (composition only) so each layer stays independently testable.
"""

from __future__ import annotations

from pathlib import Path

from graphquest.services.graphify.code_layer import CodeLayer
from graphquest.services.graphify.metrics import MetricsCalculator
from graphquest.services.graphify.models import CodeGraph
from graphquest.services.graphify.semantic_layer import SemanticLayer
from graphquest.services.graphify.vault_writer import VaultWriter


class Graphifier:
    """Compose the layers and emit all Graphify artifacts.

    Args:
        code_layer: Deterministic AST extractor.
        semantic_layer: Bounded LLM augmenter.
        metrics: Centrality/community calculator.
        vault_writer: Obsidian vault renderer.
        artifacts_dir: Where ``graph.json`` / ``GRAPH_REPORT.md`` are written.
    """

    def __init__(
        self,
        code_layer: CodeLayer,
        semantic_layer: SemanticLayer,
        metrics: MetricsCalculator,
        vault_writer: VaultWriter,
        artifacts_dir: Path,
    ) -> None:
        self._code = code_layer
        self._semantic = semantic_layer
        self._metrics = metrics
        self._vault = vault_writer
        self._artifacts = artifacts_dir

    def build(self) -> CodeGraph:
        """Run the full pipeline and return the assembled :class:`CodeGraph`."""
        raise NotImplementedError("Phase 2: compose layers -> write artifacts")
