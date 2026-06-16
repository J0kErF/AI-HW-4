"""Tests for the benchmark runner and comparator (mocked LLM, no network)."""

import json
from pathlib import Path

import pytest

from graphquest.services.benchmark.comparator import BenchmarkComparator
from graphquest.services.benchmark.models import BenchmarkRun
from graphquest.services.benchmark.runner import BenchmarkRunner
from graphquest.shared.gatekeeper import ApiGatekeeper
from graphquest.shared.llm import LLMClient


@pytest.fixture
def repo_and_graph(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    (repo / "pkg").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "pkg" / "hooks.py").write_text(
        "def find_hook(n):\n    return None\n" + "# padding\n" * 40, encoding="utf-8"
    )
    (repo / "tests" / "test_hooks.py").write_text("def test_find_hook():\n    assert find_hook('x')\n",
                                                  encoding="utf-8")
    graph = {
        "version": "1.00",
        "nodes": [{"id": "pkg/hooks.py::find_hook", "type": "function", "label": "find_hook",
                   "source_file": "pkg/hooks.py", "line": 1, "end_line": 2}],
        "edges": [{"source": "tests/test_hooks.py::test_find_hook",
                   "target": "pkg/hooks.py::find_hook", "label": "tested_by",
                   "evidence": "extracted", "confidence": 0.9, "source_file": "tests/test_hooks.py"}],
    }
    gj = tmp_path / "graph.json"
    gj.write_text(json.dumps(graph), encoding="utf-8")
    return repo, gj


def _runner(repo: Path, gj: Path, fake_llm_client) -> BenchmarkRunner:
    return BenchmarkRunner(
        repo_root=repo, graph_json=gj,
        question="tests/test_hooks.py::test_find_hook",
        test_file="tests/test_hooks.py",
        llm_factory=lambda gk: LLMClient(gk, "fake", fake_llm_client),
        gk_factory=lambda: ApiGatekeeper({"services": {}, "global_budget_usd": 999}),
    )


def test_debug_returns_fix(repo_and_graph, fake_llm_client) -> None:
    """The guided debug run returns a root cause and counts tokens."""
    repo, gj = repo_and_graph
    out = _runner(repo, gj, fake_llm_client).debug()
    assert "find_hook" in out["root_cause"]
    assert out["total_tokens"] > 0 and out["units_read"] >= 1


def test_benchmark_writes_report_and_chart(repo_and_graph, fake_llm_client, tmp_path: Path) -> None:
    """Both arms run; report + chart written; guided reads fewer source chars.

    (Absolute token *saving* is proven in the real run; a fixed-count mock can't
    show it. The honest structural claim the mock proves is: graph-guided reads
    far fewer source characters — function spans vs whole files — which is the
    direct driver of the token saving.)
    """
    repo, gj = repo_and_graph
    report = tmp_path / "TOKEN_REPORT.md"
    chart = tmp_path / "token_savings.png"
    baseline, guided = _runner(repo, gj, fake_llm_client).run(report, chart)
    assert report.exists() and chart.exists()
    assert baseline.arm == "baseline" and guided.arm == "graph_guided"
    assert guided.chars_read < baseline.chars_read  # spans << whole files


def test_comparator_renders_dash_for_zero_baseline(tmp_path: Path) -> None:
    """Saving column renders '—' when a baseline metric is zero (no divide error)."""
    out = tmp_path / "R.md"
    BenchmarkComparator().render_report(
        BenchmarkRun(arm="baseline"), BenchmarkRun(arm="graph_guided"), out
    )
    assert "—" in out.read_text(encoding="utf-8")
