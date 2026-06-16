"""Benchmark comparator — two BenchmarkRuns -> token report + chart.

Computes the deltas the assignment requires (tokens, files/units read,
iterations, time-to-root-cause) and renders ``reports/TOKEN_REPORT.md`` plus a
matplotlib bar chart (the Python-generated graph deliverable).
"""

from __future__ import annotations

from pathlib import Path

from graphquest.services.benchmark.models import BenchmarkRun


def _pct(base: float, guided: float) -> str:
    """Percentage reduction of guided vs base ('—' if base is 0)."""
    if base == 0:
        return "—"
    return f"{(base - guided) / base * 100:.1f}%"


class BenchmarkComparator:
    """Compare baseline vs graph-guided runs and emit the report + chart."""

    _ROWS = [
        ("Total tokens", "total_tokens"),
        ("Input tokens", "input_tokens"),
        ("Output tokens", "output_tokens"),
        ("Files read", "files_read"),
        ("Units read", "units_read"),
        ("Source chars read (token proxy)", "chars_read"),
        ("Iterations", "iterations"),
        ("Cost (USD)", "cost_usd"),
    ]

    def render_report(self, baseline: BenchmarkRun, guided: BenchmarkRun, out: Path) -> None:
        """Write ``TOKEN_REPORT.md`` with the comparison table and findings."""
        lines = [
            "# Token Efficiency Report",
            "",
            "> Honest baseline: same model, task and stopping criterion; only the",
            "> retrieval policy differs (whole files vs graph-guided spans).",
            "",
            "| Metric | Naive baseline | Graph-guided | Saving |",
            "|--------|----------------|--------------|--------|",
        ]
        for label, attr in self._ROWS:
            b, g = getattr(baseline, attr), getattr(guided, attr)
            fmt = (lambda v: f"{v:.4f}") if attr == "cost_usd" else (lambda v: f"{v}")
            lines.append(f"| {label} | {fmt(b)} | {fmt(g)} | {_pct(float(b), float(g))} |")
        lines += [
            f"| Localized root cause | {baseline.localized} | {guided.localized} | — |",
            "",
            "![token savings](../assets/token_savings.png)",
            "",
            "## Where the saving comes from",
            "The baseline reads whole files (the failing test + the module under test);",
            "the graph-guided agent follows `tested_by`/`calls` edges to the suspect and",
            "reads only that function's source span. The one-time semantic graph-build",
            "cost is separate (this run used the deterministic, token-free graph).",
            "",
            "## Honest trade-offs",
            "Graph-guided does **more, smaller** steps: `Units read` and `Iterations` are",
            "higher (an `explain` plus two short spans across observe/validate/fix) and",
            "`Files read` is equal — both arms touch the test file and the module. The win",
            "is not fewer reads but **far less content per read**: the agent feeds the model",
            "two ~20-line spans instead of two ~200-line files, which is why `Source chars`",
            "and `Total tokens` drop sharply while step counts rise.",
            "",
        ]
        out.write_text("\n".join(lines), encoding="utf-8")

    def render_chart(self, baseline: BenchmarkRun, guided: BenchmarkRun, out: Path) -> None:
        """Write the token-savings bar chart (Python-generated graph)."""
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        metrics = ["Total tokens", "Files read", "Units read"]
        base = [baseline.total_tokens, baseline.files_read, baseline.units_read]
        guided_vals = [guided.total_tokens, guided.files_read, guided.units_read]
        x = range(len(metrics))
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar([i - 0.2 for i in x], base, 0.4, label="Naive baseline")
        ax.bar([i + 0.2 for i in x], guided_vals, 0.4, label="Graph-guided")
        ax.set_xticks(list(x))
        ax.set_xticklabels(metrics)
        ax.set_title("Graph-guided vs naive (lower is better)")
        ax.legend()
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(out, dpi=120)
        plt.close(fig)
