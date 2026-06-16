"""LangGraph node functions — the responsible-inference pipeline as a graph.

observe (graph only) -> hypothesize (LLM over edge summaries, no source) ->
validate (LLM over ONE function's source span — the SRC step) -> fix (LLM diff).
Source is read last and minimally; every LLM node appends its token usage to
``token_log`` so the benchmark can attribute cost per step.
"""

from __future__ import annotations

import re

from graphquest.services.agent.state import DebugState
from graphquest.services.agent.tools import GraphTools
from graphquest.shared.llm import LLMClient

_SYS = "You are a precise debugging assistant. Be concise and cite the function."


class DebugNodes:
    """Factory of node callables bound to tools + LLM client."""

    def __init__(self, tools: GraphTools, llm: LLMClient) -> None:
        self._tools = tools
        self._llm = llm

    def observe(self, state: DebugState) -> DebugState:
        """OBS: from the failing-test names, follow tested_by edges to suspects."""
        tests = set(re.findall(r"test_\w+", state["question"]))
        suspects, summaries = [], []
        for e in self._tools.query(label="tested_by"):
            if any(e["source"].endswith(t) for t in tests) and e["target"] not in suspects:
                suspects.append(e["target"])
                summaries.append(self._tools.explain(e["target"]))
        state["visited_nodes"] = suspects
        state["hot_context"] = "\n\n".join(summaries) or "no tested_by suspects found"
        return state

    def hypothesize(self, state: DebugState) -> DebugState:
        """CONF: rank suspects from edge summaries (no source read yet)."""
        resp = self._llm.complete(
            _SYS,
            f"Failing tests: {state['question']}\n\nGraph evidence (edges only):\n"
            f"{state['hot_context']}\n\nWhich single function is the most likely root "
            f"cause and why? Answer with the function name first.",
        )
        state.setdefault("token_log", []).append((resp.input_tokens, resp.output_tokens))
        state["hypotheses"] = [resp.text]
        return state

    def validate(self, state: DebugState) -> DebugState:
        """SRC: read ONLY the top suspect's source span and confirm the cause."""
        top = state["visited_nodes"][0] if state.get("visited_nodes") else ""
        src = self._tools.read_source_span(top)
        state["suspect_src"] = src  # cache so `fix` does not re-read the file
        resp = self._llm.complete(
            _SYS,
            f"Failing tests: {state['question']}\n\nSource of `{top}`:\n```python\n{src}\n```\n"
            "State the exact root cause in one or two sentences.",
        )
        state.setdefault("token_log", []).append((resp.input_tokens, resp.output_tokens))
        state["root_cause"] = resp.text
        return state

    def fix(self, state: DebugState) -> DebugState:
        """Emit a unified diff for the confirmed root cause (reuses cached span)."""
        top = state["visited_nodes"][0] if state.get("visited_nodes") else ""
        src = state.get("suspect_src") or self._tools.read_source_span(top)
        resp = self._llm.complete(
            _SYS,
            f"Root cause: {state.get('root_cause', '')}\n\nSource of `{top}`:\n```python\n"
            f"{src}\n```\nProvide ONLY a unified diff that fixes it.",
        )
        state.setdefault("token_log", []).append((resp.input_tokens, resp.output_tokens))
        state["fix_diff"] = resp.text
        return state
