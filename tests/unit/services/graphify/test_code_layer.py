"""Tests for the deterministic AST code layer (token-free)."""

from pathlib import Path

import pytest

from graphquest.constants import EdgeLabel, EvidenceType
from graphquest.services.graphify.code_layer import CodeLayer


@pytest.fixture
def tiny_repo(tmp_path: Path) -> Path:
    """A 3-file repo: a calls b; a test exercises a; b is a base class."""
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "a.py").write_text(
        "from pkg.b import bar\n\nclass A(Base):\n    pass\n\ndef foo():\n    return bar()\n",
        encoding="utf-8",
    )
    (tmp_path / "pkg" / "b.py").write_text("class Base:\n    pass\n\ndef bar():\n    return 1\n",
                                           encoding="utf-8")
    (tmp_path / "test_a.py").write_text("from pkg.a import foo\n\ndef test_foo():\n    assert foo()\n",
                                        encoding="utf-8")
    return tmp_path


def _labels(edges) -> set[tuple[str, str, str]]:
    return {(e.source.split("::")[-1], e.label.value, e.target.split("::")[-1]) for e in edges}


def test_extracts_nodes_and_calls_edge(tiny_repo: Path) -> None:
    """foo --calls--> bar is an EXTRACTED edge; nodes cover module/class/function."""
    nodes, edges = CodeLayer(tiny_repo, ["**/*.py"], []).extract()
    types = {n.type.value for n in nodes}
    assert {"module", "class", "function"} <= types
    assert ("foo", "calls", "bar") in _labels(edges)
    assert all(e.evidence is EvidenceType.EXTRACTED for e in edges)


def test_tested_by_and_inherits_edges(tiny_repo: Path) -> None:
    """test_foo --tested_by--> foo, and A --inherits--> Base."""
    _, edges = CodeLayer(tiny_repo, ["**/*.py"], []).extract()
    labels = _labels(edges)
    assert ("test_foo", "tested_by", "foo") in labels
    assert ("A", EdgeLabel.INHERITS.value, "Base") in labels


def test_unparseable_file_is_skipped(tiny_repo: Path) -> None:
    """A Jinja-template .py (invalid Python) is skipped, not fatal."""
    (tiny_repo / "pkg" / "tmpl.py").write_text("{% if x %}\n", encoding="utf-8")
    nodes, _ = CodeLayer(tiny_repo, ["**/*.py"], []).extract()
    assert not any(n.source_file.endswith("tmpl.py") for n in nodes)
