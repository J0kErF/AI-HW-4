"""End-to-end Graphifier test (deterministic pipeline → artifacts + vault)."""

from pathlib import Path

from graphquest.constants import GRAPH_JSON, GRAPH_REPORT
from graphquest.services.graphify.code_layer import CodeLayer
from graphquest.services.graphify.graphifier import Graphifier
from graphquest.services.graphify.metrics import MetricsCalculator
from graphquest.services.graphify.report_writer import ReportWriter
from graphquest.services.graphify.vault_writer import VaultWriter


def test_graphifier_emits_all_artifacts(tmp_path: Path) -> None:
    """Build over a tiny repo and assert graph.json, report and vault exist."""
    repo = tmp_path / "repo"
    (repo / "pkg").mkdir(parents=True)
    (repo / "pkg" / "a.py").write_text("def foo():\n    return bar()\n", encoding="utf-8")
    (repo / "pkg" / "b.py").write_text("def bar():\n    return 1\n", encoding="utf-8")

    artifacts = tmp_path / "artifacts"
    vault = tmp_path / "vault"
    graph = Graphifier(
        code_layer=CodeLayer(repo, ["**/*.py"], []),
        metrics=MetricsCalculator(),
        vault_writer=VaultWriter(vault),
        report_writer=ReportWriter(),
        artifacts_dir=artifacts,
        semantic_layer=None,
        hot_seed="seed",
    ).build()

    assert graph.nodes and graph.edges
    assert (artifacts / GRAPH_JSON).exists()
    assert (artifacts / GRAPH_REPORT).read_text(encoding="utf-8").startswith("# GRAPH_REPORT")
    assert (vault / "index.md").exists() and (vault / "hot.md").exists()
