"""GraphQuestSDK — the single entry point for ALL logic (V3 §4.1).

Every consumer (CLI, tests, notebooks, future GUI/REST) goes through this
facade. No business logic lives in the CLI; it only delegates here. Service
construction lives in :class:`SdkBuilders`; this class exposes the five
assignment phases as thin methods.
"""

from __future__ import annotations

from pathlib import Path

from graphquest.sdk.builders import SdkBuilders
from graphquest.services.acquire.checkout import TargetCheckout
from graphquest.services.acquire.models import BugInfo
from graphquest.services.benchmark.models import BenchmarkRun
from graphquest.services.graphify.metrics import MetricsCalculator
from graphquest.services.graphify.models import CodeGraph
from graphquest.services.reverse_engineering.diagrams import DiagramGenerator
from graphquest.services.reverse_engineering.report import ReverseEngineeringReport
from graphquest.shared.config import Config
from graphquest.shared.gatekeeper import ApiGatekeeper


class GraphQuestSDK(SdkBuilders):
    """Facade orchestrating the whole HW4 pipeline.

    Args:
        config: Loaded :class:`Config` (defaults to repo ``config/``).

    Usage:
        >>> with GraphQuestSDK() as sdk:
        ...     sdk.clone_target()
        ...     graph = sdk.build_graph()
        ...     sdk.reverse_engineer(graph)
        ...     sdk.debug()
        ...     sdk.benchmark()
    """

    def __init__(self, config: Config | None = None) -> None:
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass
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
        """
        bug = BugInfo.from_config(self._config.get("target"))
        checkout_dir = Path(self._config.get("target.checkout_dir", "data/target_repo"))
        return TargetCheckout(checkout_dir).checkout(bug, ref=ref)

    # --- Phase 2: build the Graphify representation ---
    def build_graph(self) -> CodeGraph:
        """Run Graphify -> graph.json, GRAPH_REPORT.md, Obsidian vault.

        Deterministic (token-free) unless the semantic layer is enabled in config
        and an LLM key is set, in which case bounded INFERRED edges are added.
        """
        return self._build_graphifier().build()

    # --- Phase 3: reverse engineering ---
    def reverse_engineer(self, graph: CodeGraph) -> dict:
        """Emit block + OOP diagrams and the two architectural insights."""
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
        return self._runner().debug()

    # --- Phase 5: token-efficiency proof ---
    def benchmark(self) -> tuple[BenchmarkRun, BenchmarkRun]:
        """Run baseline vs graph-guided arms and write the token report + chart."""
        base_dir = Path(self._config.get("graphify.outputs_dir", "artifacts")).parent
        (base_dir / "reports").mkdir(parents=True, exist_ok=True)
        return self._runner().run(
            base_dir / "reports/TOKEN_REPORT.md", base_dir / "assets/token_savings.png"
        )

    @property
    def total_cost_usd(self) -> float:
        """Live spend from the gatekeeper ledger (budget awareness)."""
        return self._gatekeeper.total_cost_usd
