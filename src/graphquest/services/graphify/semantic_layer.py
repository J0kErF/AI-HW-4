"""Semantic inference layer (Graphify "Semantic Layer — LLM inference").

The ONLY token-spending part of graph construction, bounded by ``max_nodes``.
It asks the model to propose ``semantically_similar_to`` edges between the most
relevant functions (candidate duplication / closely-related logic). These are
INFERRED/AMBIGUOUS edges (confidence below the EXTRACTED band) that must be
validated against source before any conclusion — never treated as facts.

All LLM traffic goes through the :class:`LLMClient` (and thus the Gatekeeper).
"""

from __future__ import annotations

import json

from graphquest.constants import EdgeLabel, EvidenceType, NodeType
from graphquest.services.graphify.models import Edge, Node
from graphquest.shared.llm import LLMClient

_SYS = "You identify semantic relationships between Python functions. Reply with ONLY JSON."


class SemanticLayer:
    """LLM-backed augmentation over the deterministic code graph.

    Args:
        llm: LLM client (billed through the Gatekeeper).
        max_nodes: Cap on how many function nodes are considered.
        inferred_threshold: confidence at/above which an edge is INFERRED
            (below it is AMBIGUOUS — a manual-check flag).
    """

    def __init__(self, llm: LLMClient, max_nodes: int = 40, inferred_threshold: float = 0.7) -> None:
        self._llm = llm
        self._max_nodes = max_nodes
        self._threshold = inferred_threshold

    def augment(self, nodes: list[Node]) -> list[Edge]:
        """Return INFERRED/AMBIGUOUS ``semantically_similar_to`` edges.

        Bounded: only the first ``max_nodes`` function nodes are offered to the
        model, in a single call. Malformed model output yields no edges (the
        deterministic graph is never corrupted by a bad inference).
        """
        funcs = [
            n for n in nodes
            if n.type is NodeType.FUNCTION and not n.label.startswith("__")
        ][: self._max_nodes]
        if len(funcs) < 2:
            return []
        src_by_id = {n.id: n.source_file for n in funcs}
        listing = "\n".join(f"{n.id} | {n.label} | {n.source_file}" for n in funcs)
        resp = self._llm.complete(
            _SYS,
            f"Functions (id | label | file):\n{listing}\n\n"
            'Return a JSON array of up to 8 objects {"a": id, "b": id, "confidence": 0.0-1.0} '
            "for pairs whose LOGIC is semantically similar (possible duplication). "
            "`a` and `b` MUST be two DIFFERENT functions (never pair a function with "
            "itself). Use exact ids from the list. Return [] if none.",
        )
        return self._parse(resp.text, src_by_id)

    def _parse(self, text: str, src_by_id: dict[str, str]) -> list[Edge]:
        """Parse the model's JSON pairs into validated edges (fails closed)."""
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            pairs = json.loads(cleaned)
        except (ValueError, TypeError):
            return []
        edges: list[Edge] = []
        for item in pairs if isinstance(pairs, list) else []:
            a, b = item.get("a"), item.get("b")
            if a not in src_by_id or b not in src_by_id or a == b:
                continue
            conf = max(0.5, min(0.85, float(item.get("confidence", 0.6))))
            evidence = EvidenceType.INFERRED if conf >= self._threshold else EvidenceType.AMBIGUOUS
            edges.append(
                Edge(a, b, EdgeLabel.SEMANTICALLY_SIMILAR_TO, evidence, conf, src_by_id[a])
            )
        return edges
