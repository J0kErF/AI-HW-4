"""GraphQuestSDK — the single entry point for ALL logic (V3 §4.1).

Every consumer (CLI, tests, notebooks, future GUI/REST) goes through this
facade. No business logic lives in the CLI; it only delegates here. The SDK
wires config -> gatekeeper -> services and exposes the five assignment phases
as methods.
"""

from __future__ import annotations

from pathlib import Path

from graphquest.services.acquire.checkout import TargetCheckout
from graphquest.services.acquire.models import BugInfo
from graphquest.services.benchmark.models import BenchmarkRun
from graphquest.services.graphify.code_layer import CodeLayer
from graphquest.services.graphify.graphifier import Graphifier
from graphquest.services.graphify.metrics import MetricsCalculator
from graphquest.services.graphify.models import CodeGraph
from graphquest.services.graphify.report_writer import ReportWriter
from graphquest.services.graphify.vault_writer import VaultWriter
from graphquest.services.reverse_engineering.diagrams import DiagramGenerator
from graphquest.services.reverse_engineering.report import ReverseEngineeringReport
from graphquest.shared.config import Config
from graphquest.shared.gatekeeper import ApiGatekeeper


class GraphQuestSDK:
    """Facade orchestrating the whole HW4 pipeline.

    Args:
        config: Loaded :class:`Config` (defaults to repo ``config/``).

    Usage:
        >>> with GraphQuestSDK() as sdk:
        ...     sdk.clone_target()
        ...     graph = sdk.build_graph()
        ...     sdk.reverse_engineer(graph)
        ...     result = sdk.debug()
        ...     sdk.benchmark()
    """

    def __init__(self, config: Config | None = None) -> None:
        self._config = config or Config()
        self._gatekeeper = ApiGatekeeper(rate_limits=self._config.rate_limits)

    def __enter__(self) -> GraphQuestSDK:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    # --- Phase 1: acquire the unfamiliar codebase ---
    def clone_target(self, ref: str = "buggy") -> Path:
        """Check out the configured BugsInPy project into the checkout dir.

        Args:
            ref: "buggy" (default — the revision whose test fails) or "fixed".

        Returns:
            Path to the checked-out target repository.
        """
        bug = BugInfo.from_config(self._config.get("target"))
        checkout_dir = Path(self._config.get("target.checkout_dir", "data/target_repo"))
        return TargetCheckout(checkout_dir).checkout(bug, ref=ref)

    # --- Phase 2: build the Graphify representation ---
    def build_graph(self) -> CodeGraph:
        """Run Graphify -> graph.json, GRAPH_REPORT.md, Obsidian vault.

        Deterministic (token-free) by default; the bounded semantic layer is
        added later when an LLM key is wired (it only augments the graph).
        """
        scan_root = Path(self._config.get("graphify.scan_root", "data/target_repo"))
        thresholds = self._config.get("graphify.confidence_thresholds", {})
        code_layer = CodeLayer(
            scan_root=scan_root,
            include_globs=self._config.get("graphify.include_globs", ["**/*.py"]),
            exclude_globs=self._config.get("graphify.exclude_globs", []),
            confidence=float(thresholds.get("extracted", 0.95)),
        )
        graphifier = Graphifier(
            code_layer=code_layer,
            metrics=MetricsCalculator(),
            vault_writer=VaultWriter(Path(self._config.get("graphify.vault_dir", "obsidian/wiki"))),
            report_writer=ReportWriter(),
            artifacts_dir=Path(self._config.get("graphify.outputs_dir", "artifacts")),
            semantic_layer=None,
            hot_seed=f"BugsInPy {self._config.get('target.project')} bug "
            f"{self._config.get('target.bug_id')} — {self._config.get('target.test_file')}",
        )
        return graphifier.build()

    # --- Phase 3: reverse engineering ---
    def reverse_engineer(self, graph: CodeGraph) -> dict:
        """Emit block + OOP diagrams and the two architectural insights.

        Returns:
            Dict with the Mermaid sources and the report path.
        """
        metrics = MetricsCalculator().compute(graph)
        gen = DiagramGenerator()
        block = gen.block_diagram(graph)
        oop = gen.oop_schema(graph)
        report_path = Path(self._config.get("graphify.outputs_dir", "artifacts")).parent / (
            "reports/REVERSE_ENGINEERING.md"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        ReverseEngineeringReport().write(graph, metrics, block, oop, report_path)
        return {"block_diagram": block, "oop_schema": oop, "report_path": str(report_path)}

    # --- Phase 4: graph-guided debugging agent ---
    def debug(self) -> dict:
        """Run the LangGraph agent to localize and fix the bug, graph-first."""
        raise NotImplementedError("Phase 4")

    # --- Phase 5: token-efficiency proof ---
    def benchmark(self) -> tuple[BenchmarkRun, BenchmarkRun]:
        """Run baseline vs graph-guided arms and write the token report."""
        raise NotImplementedError("Phase 5")

    @property
    def total_cost_usd(self) -> float:
        """Live spend from the gatekeeper ledger (budget awareness)."""
        return self._gatekeeper.total_cost_usd
