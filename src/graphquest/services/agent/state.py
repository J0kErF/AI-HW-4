"""LangGraph debugging-agent state (V3 §16 building block: explicit I/O).

The state is the single object threaded through every node. Keeping it explicit
is what lets us *measure and cap* token usage per step — the core of the
token-efficiency thesis (Graphify spec: "Lost in the Middle" / short sessions).
"""

from __future__ import annotations

from typing import TypedDict


class DebugState(TypedDict, total=False):
    """Mutable state carried across the agent graph.

    Keys:
        question: The investigation question (e.g. the failing test symptom).
        hot_context: Contents of ``hot.md`` — the focused starting context.
        visited_nodes: Graph node ids the agent has already pulled.
        hypotheses: Ranked root-cause hypotheses with evidence + confidence.
        root_cause: Final localized cause (file::function) once converged.
        fix_diff: Unified diff of the proposed fix.
        iterations: Step counter, capped by ``agent.max_iterations``.
        token_log: Per-step (input, output) token counts for the benchmark.
    """

    question: str
    hot_context: str
    visited_nodes: list[str]
    suspect_src: str
    hypotheses: list[dict]
    root_cause: str
    fix_diff: str
    iterations: int
    token_log: list[tuple[int, int]]
