"""Multi-run benchmark aggregation (V3 §9.1 — systematic experiments).

A single LLM run is noisy (output verbosity varies), so we repeat the
baseline-vs-guided measurement N times and report the **mean** of each metric.
The per-run distribution feeds the analysis notebook; the mean feeds the headline
report. Retrieval-controlled metrics (input tokens, source chars) are stable
across runs; output-token noise averages out here.
"""

from __future__ import annotations

from statistics import mean

from graphquest.services.benchmark.models import BenchmarkRun

_INT_FIELDS = ("input_tokens", "output_tokens", "files_read", "units_read",
               "chars_read", "iterations")


def mean_run(runs: list[BenchmarkRun], arm: str) -> BenchmarkRun:
    """Return a :class:`BenchmarkRun` whose metrics are the means over ``runs``.

    Args:
        runs: Per-iteration results for one arm.
        arm: Arm label for the aggregate ("baseline" / "graph_guided").
    """
    if not runs:
        return BenchmarkRun(arm=arm)
    agg = BenchmarkRun(
        arm=arm,
        seconds=round(mean(r.seconds for r in runs), 3),
        cost_usd=round(mean(r.cost_usd for r in runs), 6),
        localized=all(r.localized for r in runs),
    )
    for field in _INT_FIELDS:
        setattr(agg, field, round(mean(getattr(r, field) for r in runs)))
    return agg
