"""Semantic inference layer (Graphify spec: "Semantic Layer — LLM inference of
relations, rationale and conceptual similarity").

This is the ONLY token-spending part of graph construction, and it is bounded
by ``graphify.semantic_max_nodes`` so it stays cheap. It emits INFERRED and
AMBIGUOUS edges (e.g. ``semantically_similar_to``, ``rationale_for``) that must
later be validated against ``source_file`` before any conclusion is drawn.

Every LLM call goes through the :class:`ApiGatekeeper` (V3 §5.1).
"""

from __future__ import annotations

from graphquest.services.graphify.models import Edge, Node
from graphquest.shared.gatekeeper import ApiGatekeeper


class SemanticLayer:
    """LLM-backed augmentation over the deterministic code graph.

    Args:
        gatekeeper: Chokepoint for all LLM calls (rate limit + budget + ledger).
        model: Model id (read from config, never hardcoded).
        max_nodes: Cap on how many nodes get semantic enrichment.
    """

    def __init__(self, gatekeeper: ApiGatekeeper, model: str, max_nodes: int) -> None:
        self._gk = gatekeeper
        self._model = model
        self._max_nodes = max_nodes

    def augment(self, nodes: list[Node]) -> list[Edge]:
        """Return INFERRED/AMBIGUOUS edges for the most central nodes.

        Rationale (WHY/TODO/NOTE) nodes and ``semantically_similar_to`` edges
        are produced here; confidence is set below the EXTRACTED band so the
        agent treats them as hypotheses, not facts.
        """
        raise NotImplementedError("Phase 2: prompt over node summaries via gatekeeper")
