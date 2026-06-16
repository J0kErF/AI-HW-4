"""Service construction helpers for the SDK (kept out of the facade).

A mixin that wires config + secrets into concrete services (gatekeeper, LLM
client, semantic layer, graphifier, benchmark runner). Splitting this keeps
``sdk.py`` thin — the facade exposes phases; this assembles them (V3 §3.2).
"""

from __future__ import annotations

import os
from pathlib import Path

from graphquest.services.benchmark.runner import BenchmarkRunner
from graphquest.services.graphify.code_layer import CodeLayer
from graphquest.services.graphify.graphifier import Graphifier
from graphquest.services.graphify.metrics import MetricsCalculator
from graphquest.services.graphify.report_writer import ReportWriter
from graphquest.services.graphify.semantic_layer import SemanticLayer
from graphquest.services.graphify.vault_writer import VaultWriter
from graphquest.shared.config import Config, get_secret
from graphquest.shared.gatekeeper import ApiGatekeeper
from graphquest.shared.llm import LLMClient, build_chat_client


class SdkBuilders:
    """Mixin providing service construction (expects ``self._config``)."""

    _config: Config

    def _new_gatekeeper(self) -> ApiGatekeeper:
        """A fresh gatekeeper with its own ledger (one per benchmark arm)."""
        return ApiGatekeeper(rate_limits=self._config.rate_limits)

    def _llm(self, gatekeeper: ApiGatekeeper) -> LLMClient:
        """Build an LLM client bound to ``gatekeeper`` from env config."""
        model_env = self._config.get("agent.model_env", "GRAPHQUEST_MODEL")
        model = os.environ.get(model_env, "deepseek-chat")
        client = build_chat_client(get_secret("OPENAI_API_KEY"), os.environ.get("OPENAI_BASE_URL"))
        return LLMClient(gatekeeper, model, client)

    def _semantic_layer(self) -> SemanticLayer | None:
        """Build the bounded semantic layer if enabled in config and a key is set.

        Returns None (deterministic, token-free graph) when disabled or no key,
        so ``graphify`` always works offline; the layer only augments the graph.
        """
        if not self._config.get("graphify.semantic_layer_enabled", False):
            return None
        if not os.environ.get("OPENAI_API_KEY"):
            return None
        thresholds = self._config.get("graphify.confidence_thresholds", {})
        return SemanticLayer(
            llm=self._llm(self._new_gatekeeper()),
            max_nodes=int(self._config.get("graphify.semantic_max_nodes", 40)),
            inferred_threshold=float(thresholds.get("inferred", 0.7)),
        )

    def _build_graphifier(self) -> Graphifier:
        """Assemble the Graphify pipeline from config."""
        scan_root = Path(self._config.get("graphify.scan_root", "data/target_repo"))
        thresholds = self._config.get("graphify.confidence_thresholds", {})
        artifacts = Path(self._config.get("graphify.outputs_dir", "artifacts"))
        code_layer = CodeLayer(
            scan_root=scan_root,
            include_globs=self._config.get("graphify.include_globs", ["**/*.py"]),
            exclude_globs=self._config.get("graphify.exclude_globs", []),
            confidence=float(thresholds.get("extracted", 0.95)),
        )
        return Graphifier(
            code_layer=code_layer,
            metrics=MetricsCalculator(),
            vault_writer=VaultWriter(Path(self._config.get("graphify.vault_dir", "obsidian/wiki"))),
            report_writer=ReportWriter(),
            artifacts_dir=artifacts,
            semantic_layer=self._semantic_layer(),
            hot_seed=f"BugsInPy {self._config.get('target.project')} bug "
            f"{self._config.get('target.bug_id')} — {self._config.get('target.test_file')}",
        )

    def _runner(self) -> BenchmarkRunner:
        """Construct the Phase 4-5 orchestration runner."""
        selectors = self._config.get("target.test_selectors", [])
        question = " ".join(selectors) or self._config.get("target.test_file", "")
        return BenchmarkRunner(
            repo_root=Path(self._config.get("graphify.scan_root", "data/target_repo")),
            graph_json=Path(self._config.get("graphify.outputs_dir", "artifacts")) / "graph.json",
            question=question,
            test_file=self._config.get("target.test_file", ""),
            llm_factory=self._llm,
            gk_factory=self._new_gatekeeper,
        )
