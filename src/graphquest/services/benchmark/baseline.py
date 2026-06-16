"""Naive baseline arm of the token benchmark (HONEST baseline — V3 thesis).

CRITICAL: this is NOT a strawman. It is a *real* agent attempt with the SAME
model, SAME task and SAME stopping criterion as the graph-guided arm. The ONLY
difference is the retrieval policy: the baseline reads raw whole files (the way
an engineer with no map would), with no graph, no hot.md, no index.md.

It measures: tokens consumed, files/units read, iterations, time-to-root-cause.
See docs/PRD_token_benchmark.md for the fairness contract.
"""

from __future__ import annotations

from graphquest.services.benchmark.models import BenchmarkRun
from graphquest.shared.gatekeeper import ApiGatekeeper


class NaiveBaseline:
    """Whole-file-reading debugging attempt (no graph guidance).

    Args:
        gatekeeper: Shared LLM chokepoint so token accounting is identical.
        model: Same model id as the guided arm.
        max_iterations: Same iteration cap as the guided arm.
    """

    def __init__(self, gatekeeper: ApiGatekeeper, model: str, max_iterations: int) -> None:
        self._gk = gatekeeper
        self._model = model
        self._max_iterations = max_iterations

    def run(self, question: str, repo_root: str) -> BenchmarkRun:
        """Attempt to localize the bug by reading raw files; record metrics."""
        raise NotImplementedError("Phase 2: file-dump retrieval loop")
