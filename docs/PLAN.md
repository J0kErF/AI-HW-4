# PLAN — GraphQuest Architecture

> Version **1.00** · Companion to `PRD.md`. Diagrams are Mermaid (render in GitHub/Obsidian).

## 1. C4 Model

### C4-L1 Context
```mermaid
flowchart TD
    Dev[Developer / Grader] -->|CLI: python -m graphquest| GQ[GraphQuest]
    GQ -->|reads| Repo[(BugsInPy target repo)]
    GQ -->|bounded LLM calls via Gatekeeper| LLM[(DeepSeek / OpenAI-compatible)]
    GQ -->|writes| Art[graph.json · vault · reports · diagrams]
```

### C4-L2 Container
```mermaid
flowchart TD
    CLI[__main__ CLI] --> SDK[GraphQuestSDK facade]
    SDK --> GF[Graphify service]
    SDK --> RE[Reverse-Eng service]
    SDK --> AG[LangGraph Agent service]
    SDK --> BM[Benchmark service]
    SDK --> GK[ApiGatekeeper]
    GF --> GK
    AG --> GK
    BM --> GK
    GK --> LLM[(LLM provider)]
```

### C4-L3 Component — Graphify
```mermaid
flowchart LR
    Files[(target files)] --> CL[CodeLayer · AST · EXTRACTED]
    CL --> GB[Graphifier]
    SL[SemanticLayer · LLM · INFERRED/AMBIGUOUS] --> GB
    GB --> MC[MetricsCalculator · centrality/communities/bridges]
    MC --> VW[VaultWriter · index.md/hot.md/notes]
    GB --> JSON[graph.json]
    MC --> REP[GRAPH_REPORT.md]
```

## 2. UML — Class (core)
```mermaid
classDiagram
    class GraphQuestSDK {
        +clone_target() Path
        +build_graph() CodeGraph
        +reverse_engineer(graph) dict
        +debug() dict
        +benchmark() tuple
        +total_cost_usd float
    }
    class ApiGatekeeper {
        +execute(service, call) Any
        +record_usage(...) CallRecord
        +get_queue_status() QueueStatus
        +total_cost_usd float
    }
    class CodeGraph { +nodes; +edges; +to_dict() }
    class Node { +id; +type; +source_file; +community }
    class Edge { +source; +target; +label; +evidence; +confidence; +source_file }
    GraphQuestSDK --> ApiGatekeeper : owns
    GraphQuestSDK --> CodeGraph : produces
    CodeGraph "1" o-- "*" Node
    CodeGraph "1" o-- "*" Edge
```

## 3. UML — Sequence (debug phase)
```mermaid
sequenceDiagram
    participant U as CLI
    participant S as SDK
    participant A as Agent(LangGraph)
    participant T as GraphTools
    participant G as Gatekeeper
    U->>S: debug()
    S->>A: run(question, hot.md)
    loop until localized or capped
        A->>T: query/path/explain (graph, not raw files)
        T-->>A: focused evidence slice
        A->>G: LLM step (counted, budgeted)
        G-->>A: hypothesis
    end
    A->>T: read_source_span(top hypothesis)  %% SRC step, last
    A-->>S: root_cause + fix_diff + token_log
```

## 4. Architecture Decision Records

- **ADR-001 — Reimplement Graphify (AST + bounded LLM) rather than wrap a
  black box.** *Rationale:* the deterministic code layer must be token-free and
  reproducible; we control the `graph.json` schema the agent depends on.
  *Trade-off:* more code to own vs. full control + testability. *Alternatives:*
  call an external Graphify CLI (less control, possible cost/availability risk).
- **ADR-002 — LangGraph over CrewAI.** *Rationale:* explicit node graph gives
  per-step control of reads/iterations, matching the token-efficiency thesis;
  the assignment "Do" section recommends it under a small budget. *Trade-off:*
  no reuse of HW3 CrewAI patterns; offset by clearer token attribution.
- **ADR-003 — Graph-first / source-last retrieval.** *Rationale:* the whole
  saving comes from reading the smallest evidence slice; source files are opened
  only in the SRC validation step. *Trade-off:* needs a good graph; mitigated by
  EXTRACTED backbone.
- **ADR-004 — Single Gatekeeper for all LLM calls incl. semantic layer & agent.**
  *Rationale:* one budget ledger, one rate limiter, honest token accounting for
  the benchmark. *Trade-off:* slight indirection.
- **ADR-005 — DeepSeek (OpenAI-compatible) default.** *Rationale:* cheap,
  matches theme; swappable via `config`/`.env`. *Trade-off:* Hebrew/edge quality
  varies; not relevant to debugging task.

## 5. Data contracts

- `graph.json` — `{version, nodes[], edges[]}` per `services/graphify/models.py`.
- `hot.md` / `index.md` — Markdown with `[[wikilinks]]`; see `PRD_graphify.md`.
- `TOKEN_REPORT.md` — comparison table schema in `PRD_token_benchmark.md`.

## 6. Module map (≤150 LOC each)
```
src/graphquest/
  sdk/sdk.py                      facade (single entry point)
  shared/{config,gatekeeper,logging_setup,version}.py
  constants.py                    enums + filenames
  services/graphify/{models,code_layer,semantic_layer,metrics,vault_writer,graphifier}.py
  services/agent/{state,tools,nodes,workflow}.py
  services/benchmark/{models,baseline,comparator}.py  (+ guided arm reuses agent)
  services/reverse_engineering/diagrams.py
  __main__.py                     thin CLI
```
