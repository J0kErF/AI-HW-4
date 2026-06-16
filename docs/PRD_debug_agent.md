# PRD — Graph-guided debugging agent (LangGraph)

> Version **1.00** · Implements EX04 §5.3 (build an AI agent that operates
> graph-first) using LangGraph, per the assignment "Do" recommendation.

## 1. Description & rationale

A LangGraph `StateGraph` whose nodes mirror the **responsible-inference
pipeline** taught in L07: **OBS → REL → CONF → CTX → SRC**. The agent must
"start from Graphify outputs and the Obsidian vault, and only afterwards request
relevant code spans" (EX04 §5.3). Source files are opened **last**, only to
validate the top hypothesis — this is the mechanism behind the token saving.

LangGraph (not CrewAI) is chosen because the explicit node graph gives precise
control over how many reads/iterations occur, which both bounds cost and makes
per-step token usage measurable (ADR-002).

## 2. Workflow

```
observe ──► relate ──► hypothesize ──► should_continue?
   ▲                                      │  loop (relate) if not localized & < max_iter
   └──────────────────────────────────────┘
                                          │ localized
                                          ▼
                                    validate (open source_file — SRC step)
                                          ▼
                                         fix (emit unified diff)
```

| Node | Pipeline step | Reads | Tokens |
|------|---------------|-------|--------|
| `observe` | OBS | `hot.md` only | small |
| `relate` | REL | graph `query`/`path`/`explain` | small slices |
| `hypothesize` | CONF | accumulated evidence | medium |
| `validate` | CTX+SRC | ONE `source_file` span | one read |
| `fix` | — | confirmed span | one gen |

## 3. State (I/O contract)

`DebugState` (see `services/agent/state.py`): `question`, `hot_context`,
`visited_nodes`, `hypotheses[]`, `root_cause`, `fix_diff`, `iterations`,
`token_log[]`. `token_log` is the per-step ledger consumed by the benchmark.

## 4. Tools (focused retrieval — the saving)

- `query(label, min_confidence)` — find candidate nodes/edges.
- `path(a, b)` — traceability path (requirement→code→test).
- `explain(node)` — node note + incident edges (replaces opening whole file).
- `read_source_span(node)` — minimal source lines (SRC validation only).

All LLM calls route through the `ApiGatekeeper`; tools read the graph/vault,
never raw whole files.

## 5. Conclusion discipline

Language must match evidence strength: EXTRACTED supports a strong claim;
INFERRED/AMBIGUOUS require "the graph *suggests*…" until validated against
`source_file`. The agent must not over-claim from a visual cue.

## 6. Multi-agent option (extensibility)

L07 suggests an orchestration of specialists (acquire / analyze-graph-and-find /
rewrite-per-graph). v1.00 ships a single agent with role-specialized nodes;
a `CrewBuilderMixin`-style split is an ADR-able extension.

## 7. Success criteria & tests

- Localizes the configured bug to the correct function (matches upstream fix).
- Proposed diff makes the target's failing test pass.
- `validate` opens **≤2** source files (proves source-last behavior).
- Unit tests mock the LLM (no real calls) and assert node transitions + that
  `should_continue` respects `max_iterations`.
