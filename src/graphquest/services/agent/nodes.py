"""LangGraph node functions — the responsible-inference pipeline as a graph.

Each node maps to one step of the Graphify inference pipeline
(OBS -> REL -> CONF -> CTX -> SRC) so the agent's reasoning is auditable and
its token use is attributable per step:

* ``observe``  — start from ``hot.md``, list anomalies (no source reads).
* ``relate``   — use graph tools to follow edges around the suspect region.
* ``hypothesize`` — rank root-cause hypotheses with confidence.
* ``validate`` — open ``source_file`` ONLY for the top hypothesis (SRC step).
* ``fix``      — produce a unified diff once the cause is localized.

All LLM calls route through the gatekeeper; every call appends to ``token_log``.
"""

from __future__ import annotations

from graphquest.services.agent.state import DebugState
from graphquest.services.agent.tools import GraphTools
from graphquest.shared.gatekeeper import ApiGatekeeper


class DebugNodes:
    """Factory of node callables bound to tools + gatekeeper + model.

    Args:
        tools: Graph-guided retrieval tools.
        gatekeeper: LLM chokepoint (rate limit, budget, token ledger).
        model: Model id from config.
    """

    def __init__(self, tools: GraphTools, gatekeeper: ApiGatekeeper, model: str) -> None:
        self._tools = tools
        self._gk = gatekeeper
        self._model = model

    def observe(self, state: DebugState) -> DebugState:
        """OBS: read hot.md, surface anomalies; no source reads yet."""
        raise NotImplementedError("Phase 2")

    def relate(self, state: DebugState) -> DebugState:
        """REL: walk edges (query/path) around the suspect community."""
        raise NotImplementedError("Phase 2")

    def hypothesize(self, state: DebugState) -> DebugState:
        """CONF: rank hypotheses; weight EXTRACTED over INFERRED evidence."""
        raise NotImplementedError("Phase 2")

    def validate(self, state: DebugState) -> DebugState:
        """SRC: open source_file for the top hypothesis to confirm/deny."""
        raise NotImplementedError("Phase 2")

    def fix(self, state: DebugState) -> DebugState:
        """Emit a unified diff for the confirmed root cause."""
        raise NotImplementedError("Phase 2")

    def should_continue(self, state: DebugState) -> str:
        """Conditional edge: loop to ``relate`` or stop when localized/capped."""
        raise NotImplementedError("Phase 2")
