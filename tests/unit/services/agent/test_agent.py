"""Tests for GraphTools and the LangGraph debugging agent (mocked LLM)."""

import json
from pathlib import Path

import pytest

from graphquest.services.agent.nodes import DebugNodes
from graphquest.services.agent.tools import GraphTools
from graphquest.services.agent.workflow import DebugWorkflow
from graphquest.shared.gatekeeper import ApiGatekeeper
from graphquest.shared.llm import LLMClient


@pytest.fixture
def graph_and_repo(tmp_path: Path) -> tuple[Path, Path]:
    """A minimal repo + graph.json: test_find_hook --tested_by--> find_hook."""
    repo = tmp_path / "repo"
    (repo / "pkg").mkdir(parents=True)
    (repo / "pkg" / "hooks.py").write_text(
        "def find_hook(name):\n    for f in files:\n        return f  # bug: single\n    return None\n",
        encoding="utf-8",
    )
    (repo / "t").mkdir()
    (repo / "t" / "test_hooks.py").write_text(
        "def test_find_hook():\n    assert find_hook('x') == ['a', 'b']\n", encoding="utf-8"
    )
    graph = {
        "version": "1.00",
        "nodes": [
            {"id": "pkg/hooks.py::find_hook", "type": "function", "label": "find_hook",
             "source_file": "pkg/hooks.py", "line": 1, "end_line": 4},
            {"id": "t/test_hooks.py::test_find_hook", "type": "function", "label": "test_find_hook",
             "source_file": "t/test_hooks.py", "line": 1, "end_line": 2},
        ],
        "edges": [
            {"source": "t/test_hooks.py::test_find_hook", "target": "pkg/hooks.py::find_hook",
             "label": "tested_by", "evidence": "extracted", "confidence": 0.9,
             "source_file": "t/test_hooks.py"},
        ],
    }
    gj = tmp_path / "graph.json"
    gj.write_text(json.dumps(graph), encoding="utf-8")
    return gj, repo


def test_tools_read_only_one_function_span(graph_and_repo: tuple[Path, Path]) -> None:
    """read_source_span returns just the function body and counts one file."""
    gj, repo = graph_and_repo
    tools = GraphTools(gj, repo)
    span = tools.read_source_span("pkg/hooks.py::find_hook")
    assert "def find_hook" in span and "bug: single" in span
    assert tools.files_read == 1


def test_agent_localizes_and_proposes_fix(graph_and_repo, fake_llm_client) -> None:
    """The agent follows tested_by to find_hook, reads its span, and emits a fix."""
    gj, repo = graph_and_repo
    gk = ApiGatekeeper({"services": {}, "global_budget_usd": 999})
    llm = LLMClient(gk, "fake-model", fake_llm_client)
    tools = GraphTools(gj, repo)
    state = DebugWorkflow(DebugNodes(tools, llm)).run("tests/test_hooks.py::test_find_hook")

    assert "pkg/hooks.py::find_hook" in state["visited_nodes"]
    assert "find_hook" in state["root_cause"]
    assert "diff" in state["fix_diff"]
    assert len(state["token_log"]) == 3  # hypothesize, validate, fix
