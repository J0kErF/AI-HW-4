"""Tests for the bounded LLM semantic layer (mocked — no network)."""

from types import SimpleNamespace

from graphquest.constants import EvidenceType, NodeType
from graphquest.services.graphify.models import Node
from graphquest.services.graphify.semantic_layer import SemanticLayer
from graphquest.shared.gatekeeper import ApiGatekeeper
from graphquest.shared.llm import LLMClient


def _fake_client(reply: str):  # noqa: ANN202
    class _C:
        def create(self, model, messages, temperature=0.0):  # noqa: ANN001, ANN202
            usage = SimpleNamespace(prompt_tokens=20, completion_tokens=5)
            msg = SimpleNamespace(content=reply)
            return SimpleNamespace(choices=[SimpleNamespace(message=msg)], usage=usage)

    return SimpleNamespace(chat=SimpleNamespace(completions=_C()))


def _nodes() -> list[Node]:
    return [
        Node("m.py::parse_user", NodeType.FUNCTION, "parse_user", "m.py"),
        Node("n.py::parse_client", NodeType.FUNCTION, "parse_client", "n.py"),
    ]


def _layer(reply: str) -> SemanticLayer:
    gk = ApiGatekeeper({"services": {}, "global_budget_usd": 999})
    return SemanticLayer(LLMClient(gk, "fake", _fake_client(reply)), max_nodes=40)


def test_inferred_edge_above_threshold() -> None:
    """A high-confidence pair becomes an INFERRED semantically_similar_to edge."""
    reply = '```json\n[{"a": "m.py::parse_user", "b": "n.py::parse_client", "confidence": 0.8}]\n```'
    edges = _layer(reply).augment(_nodes())
    assert len(edges) == 1
    assert edges[0].evidence is EvidenceType.INFERRED
    assert edges[0].label.value == "semantically_similar_to"


def test_low_confidence_is_ambiguous() -> None:
    """A low-confidence pair is flagged AMBIGUOUS (manual check)."""
    reply = '[{"a": "m.py::parse_user", "b": "n.py::parse_client", "confidence": 0.55}]'
    edges = _layer(reply).augment(_nodes())
    assert edges[0].evidence is EvidenceType.AMBIGUOUS


def test_malformed_output_yields_no_edges() -> None:
    """Non-JSON / unknown ids never corrupt the graph (fails closed)."""
    assert _layer("not json at all").augment(_nodes()) == []
    bad_ids = '[{"a": "x", "b": "y", "confidence": 0.9}]'
    assert _layer(bad_ids).augment(_nodes()) == []
