"""LangGraph workflow assembly (the agent graph itself).

Wires :class:`DebugNodes` into a ``StateGraph`` with the loop
observe -> relate -> hypothesize -> (validate -> fix | back to relate).
LangGraph is chosen (per the assignment "Do" section) for tight control over
reads/iterations under a small token budget — the explicit graph is what makes
context minimization measurable.
"""

from __future__ import annotations

from graphquest.services.agent.nodes import DebugNodes
from graphquest.services.agent.state import DebugState


class DebugWorkflow:
    """Compile and run the LangGraph debugging agent.

    Args:
        nodes: The bound node callables.
        max_iterations: Hard cap on the relate/hypothesize loop.
    """

    def __init__(self, nodes: DebugNodes, max_iterations: int) -> None:
        self._nodes = nodes
        self._max_iterations = max_iterations

    def compile(self):  # noqa: ANN201 - returns a langgraph CompiledGraph
        """Build the ``StateGraph`` with nodes, edges and the conditional loop."""
        raise NotImplementedError("Phase 2: StateGraph wiring")

    def run(self, question: str, hot_context: str) -> DebugState:
        """Execute the agent on a question and return the final state."""
        raise NotImplementedError("Phase 2")
