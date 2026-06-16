"""Phase 4-5 orchestration: run the agent (debug) and both benchmark arms.

Kept out of the SDK so the facade stays thin. The SDK injects ``llm_factory``
(it owns secrets) and ``gk_factory`` (fresh ledger per arm); this module wires
tools + workflow + baseline + comparator.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from graphquest.services.agent.nodes import DebugNodes
from graphquest.services.agent.tools import GraphTools
from graphquest.services.agent.workflow import DebugWorkflow
from graphquest.services.benchmark.baseline import NaiveBaseline
from graphquest.services.benchmark.comparator import BenchmarkComparator
from graphquest.services.benchmark.models import BenchmarkRun
from graphquest.shared.gatekeeper import ApiGatekeeper
from graphquest.shared.llm import LLMClient

LLMFactory = Callable[[ApiGatekeeper], LLMClient]
GKFactory = Callable[[], ApiGatekeeper]


class BenchmarkRunner:
    """Run the graph-guided agent and the naive baseline, then compare.

    Args:
        repo_root: Checked-out target repo.
        graph_json: Path to ``artifacts/graph.json``.
        question: Failing-test symptom (drives both arms identically).
        test_file: Failing test file (baseline reads it whole).
        llm_factory: Builds an LLM client bound to a given gatekeeper.
        gk_factory: Builds a fresh gatekeeper (isolated ledger per arm).
    """

    def __init__(
        self,
        repo_root: Path,
        graph_json: Path,
        question: str,
        test_file: str,
        llm_factory: LLMFactory,
        gk_factory: GKFactory,
    ) -> None:
        self._repo = repo_root
        self._graph_json = graph_json
        self._question = question
        self._test_file = test_file
        self._llm_factory = llm_factory
        self._gk_factory = gk_factory

    def debug(self) -> dict:
        """Run only the graph-guided agent; return its result + token usage."""
        run, state, _ = self._guided_arm()
        return {
            "root_cause": state.get("root_cause", ""),
            "fix_diff": state.get("fix_diff", ""),
            "total_tokens": run.total_tokens,
            "cost_usd": run.cost_usd,
            "units_read": run.units_read,
        }

    def _guided_arm(self) -> tuple[BenchmarkRun, dict, GraphTools]:
        gk = self._gk_factory()
        llm = self._llm_factory(gk)
        tools = GraphTools(self._graph_json, self._repo)
        state = DebugWorkflow(DebugNodes(tools, llm)).run(self._question)
        answer = (state.get("root_cause", "") + state.get("fix_diff", "")).lower()
        run = BenchmarkRun(
            arm="graph_guided",
            input_tokens=sum(r.input_tokens for r in gk._ledger),
            output_tokens=sum(r.output_tokens for r in gk._ledger),
            files_read=tools.files_read,
            units_read=tools.units_read,
            iterations=len(state.get("token_log", [])),
            cost_usd=gk.total_cost_usd,
            localized="find_hook" in answer,
        )
        return run, state, tools

    def _baseline_arm(self) -> BenchmarkRun:
        gk = self._gk_factory()
        llm = self._llm_factory(gk)
        return NaiveBaseline(gk, llm, self._repo).run(self._question, self._test_file)

    def run(self, report_path: Path, chart_path: Path) -> tuple[BenchmarkRun, BenchmarkRun]:
        """Run both arms, write the token report + chart, and return the runs."""
        baseline = self._baseline_arm()
        guided, _, _ = self._guided_arm()
        comparator = BenchmarkComparator()
        comparator.render_report(baseline, guided, report_path)
        comparator.render_chart(baseline, guided, chart_path)
        return baseline, guided
