# PRD — GraphQuest

> HW4 · EX04 · Course: Building with LLMs (Dr. Yoram Segal) · Group: **moamteam** · Version **1.00**

## 1. Overview & Context

**Problem.** Understanding and debugging an *unfamiliar* large Python codebase is
bottlenecked by the LLM **context window**. The naive approach — feed the model
raw files until something sticks — is dominated by the *Lost-in-the-Middle*
effect and burns tokens on code irrelevant to the current question.

**Solution.** GraphQuest reverse-engineers an unfamiliar codebase into a
**Graphify knowledge graph** (`graph.json`) and an **Obsidian vault**
(`index.md`, `hot.md`, linked notes), then drives a **LangGraph** debugging
agent that navigates the graph *first* and reads source *last*. We prove the
token saving against an honest naive baseline.

**Target system under study.** A single self-contained **BugsInPy** project
(primary: `thefuck` — dozens of small rule modules make graph navigation and
God-node analysis vivid; fallback `cookiecutter`). One reproducible bug, with
the real upstream fix as ground truth. Configured in `config/setup.json`.

**User.** A developer dropped into a codebase they have never seen, who must
locate and fix one bug under a tight token/$ budget.

## 2. Goals, KPIs & Acceptance Criteria

| KPI | Target | Verified by |
|-----|--------|-------------|
| Token saving (graph-guided vs naive) | ≥ 60 % fewer total tokens | `reports/TOKEN_REPORT.md` |
| Files / units read | guided ≪ baseline | benchmark metrics |
| Root cause correctly localized | function-level match to upstream fix | `reports/BUG_REPORT.md` |
| Fix passes the project's failing test | `buggy` → `fixed` test goes green | pytest on target |
| Test coverage (our code) | ≥ 85 % | `pytest --cov` |
| Ruff | 0 errors | `ruff check` |
| Budget | ≤ $1.50 / session | gatekeeper ledger |

**Acceptance:** all of the above met, all mandatory deliverables (§7 of EX04)
present, and the README renders every required visual.

## 3. Functional Requirements

- **FR1 — Acquire.** Clone/checkout the configured BugsInPy project at its
  buggy revision into `data/target_repo`.
- **FR2 — Graphify.** Build `graph.json`, `GRAPH_REPORT.md`, `graph.html`, and
  the Obsidian vault (`index.md`, `hot.md`, per-node notes with `[[wikilinks]]`).
  Edges carry `label`, `direction`, `confidence`, `evidence` (extracted/
  inferred/ambiguous) and `source_file`.
- **FR3 — Reverse engineer.** Emit a **block (component) diagram** and an
  **OOP class schema** *derived from the graph*, plus ≥2 architectural insights
  (e.g. God-node / bottleneck, traceability gap).
- **FR4 — Debug agent.** A LangGraph agent that runs the responsible-inference
  pipeline (OBS→REL→CONF→CTX→SRC), reads the graph/vault first and source last,
  localizes the root cause, and proposes a fix diff.
- **FR5 — Token benchmark.** Run a naive baseline arm and a graph-guided arm
  under identical model/task/stopping-criterion; report tokens, files/units,
  iterations and time-to-root-cause.

## 4. Non-Functional Requirements

- **Architecture:** all logic behind `GraphQuestSDK` (V3 §4.1); OOP, no
  duplication; files ≤150 LOC; modular `src/` layout.
- **Security:** API keys only from env (`.env`, git-ignored); `.env.example`
  committed; no secrets in source (V3 §7.4).
- **Cost control:** every external call through the `ApiGatekeeper` (rate
  limit + queue + retry + budget ledger) (V3 §5).
- **Quality:** TDD, ≥85 % coverage, ruff-clean, FIFO logging, `uv`-managed.
- **Reproducibility:** versioned config (`1.00`), pinned deps, deterministic
  code layer (token-free).

## 5. Assumptions, Dependencies, Constraints

- Python ≥3.10; isolated venv per BugsInPy guidance (avoid dependency hell).
- OpenAI-compatible LLM (DeepSeek by default) reachable with a funded key.
- The deterministic AST layer needs no key; only the bounded semantic layer and
  the agent spend tokens.
- **Out of scope:** fixing more than one bug; full-system rewrite; supporting
  non-Python targets.

## 6. Risks

| Risk | Mitigation |
|------|-----------|
| BugsInPy env/deps are fragile | Pin one self-contained project; document venv steps; fallback project configured |
| Strawman baseline accusation | Honest baseline contract in `PRD_token_benchmark.md` (same model/task/stop) |
| Semantic layer cost blow-up | Hard `semantic_max_nodes` cap; gatekeeper budget |
| Graphify-vs-implementation drift | Re-run Graphify after any change (it is not real-time) |

## 7. Timeline & Milestones

See `docs/TODO.md`. Phases: P0 scaffold (this) → P1 acquire → P2 graphify →
P3 reverse-engineer → P4 agent → P5 benchmark → P6 docs/visuals/self-grade.

## 8. Per-mechanism PRDs

- `docs/PRD_graphify.md` — graph + vault generator
- `docs/PRD_debug_agent.md` — LangGraph workflow
- `docs/PRD_gatekeeper.md` — API gatekeeper, rate limits, budget
- `docs/PRD_token_benchmark.md` — baseline-vs-guided fairness contract
