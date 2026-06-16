"""Benchmark comparator — turns two BenchmarkRuns into the token report.

Computes the savings the assignment requires (tokens, files/units read,
iterations, time-to-root-cause) and renders ``reports/TOKEN_REPORT.md`` plus a
matplotlib bar chart for ``assets/token_savings.png``.
"""

from __future__ import annotations

from pathlib import Path

from graphquest.services.benchmark.models import BenchmarkRun


class BenchmarkComparator:
    """Compare baseline vs graph-guided runs and emit the report."""

    def compare(self, baseline: BenchmarkRun, guided: BenchmarkRun) -> dict:
        """Return a dict of absolute + percentage deltas across all metrics."""
        raise NotImplementedError("Phase 2: compute deltas")

    def render_report(self, deltas: dict, report_path: Path) -> None:
        """Write ``TOKEN_REPORT.md`` with the comparison table and findings."""
        raise NotImplementedError("Phase 2")

    def render_chart(self, deltas: dict, chart_path: Path) -> None:
        """Write the token-savings bar chart (Python-generated graph)."""
        raise NotImplementedError("Phase 2: matplotlib")
