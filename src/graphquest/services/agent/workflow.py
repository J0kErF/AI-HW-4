"""LangGraph workflow assembly (the agent graph itself).

Wires :class:`DebugNodes` into a LangGraph ``StateGraph``:
observe -> hypothesize -> validate -> fix -> END. LangGraph is used (per the
assignment "Do" section) for explicit, controllable step execution — which is
what makes per-step token usage measurable.
"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from graphquest.services.agent.nodes import DebugNodes
from graphquest.services.agent.state import DebugState


class DebugWorkflow:
    """Compile and run the LangGraph debugging agent.

    Args:
        nodes: The bound node callables.
    """

    def __init__(self, nodes: DebugNodes) -> None:
        self._nodes = nodes

    def compile(self):  # noqa: ANN201 - returns a langgraph CompiledStateGraph
        """Build the StateGraph with the observe->hypothesize->validate->fix flow."""
        graph = StateGraph(DebugState)
        graph.add_node("observe", self._nodes.observe)
        graph.add_node("hypothesize", self._nodes.hypothesize)
        graph.add_node("validate", self._nodes.validate)
        graph.add_node("fix", self._nodes.fix)
        graph.set_entry_point("observe")
        graph.add_edge("observe", "hypothesize")
        graph.add_edge("hypothesize", "validate")
        graph.add_edge("validate", "fix")
        graph.add_edge("fix", END)
        return graph.compile()

    def run(self, question: str) -> DebugState:
        """Execute the agent on a question and return the final state."""
        initial: DebugState = {"question": question, "iterations": 0, "token_log": []}
        return self.compile().invoke(initial)
