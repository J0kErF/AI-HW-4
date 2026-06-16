# GraphQuest — Graph-Guided, Token-Efficient Debugging of an Unfamiliar Codebase

> HW4 · EX04 · Course: Building with LLMs (Dr. Yoram Segal)
> Group: **moamteam** · Version: **1.00**

GraphQuest reverse-engineers an **unfamiliar Python codebase** (a single
[BugsInPy](https://github.com/soarsmu/BugsInPy) project) into a **Graphify
knowledge graph** + an **Obsidian vault**, then runs a **LangGraph** debugging
agent that navigates the graph *first* and reads source *last* — and we **prove
the token saving** against an honest naive baseline.

> ⚠️ **Status: scaffold (Phase 0).** Documentation-first per the V3 guidelines
> (PRD→PLAN→TODO→code). Service logic is specified and stubbed; implementation
> follows `docs/TODO.md`.

---

## 1. Why (the problem)
An LLM's context window is the bottleneck. Dumping raw files at it wastes tokens
on irrelevant code and triggers *Lost-in-the-Middle*. A **code-knowledge graph**
lets an agent retrieve the *smallest evidence slice* needed — saving 70–95% of
tokens vs naive reading (L07).

## 2. The base repository (chosen & why)
A single self-contained **BugsInPy** project — primary **`thefuck`** (dozens of
small rule modules make graph navigation, communities and God-node analysis
vivid), fallback **`cookiecutter`**. One reproducible bug with the real upstream
fix as ground truth. Pinned in [`config/setup.json`](config/setup.json).

## 3. Installation
```bash
git clone <repo-url> && cd aihw4
uv sync                      # all deps from uv.lock
cp .env.example .env         # add your LLM key (DeepSeek/OpenAI-compatible)
```
> The target project is checked out into `data/target_repo/` in an **isolated
> venv** (BugsInPy guidance) by `graphquest clone`.

## 4. Usage
```bash
uv run python -m graphquest clone       # Phase 1: fetch the buggy project
uv run python -m graphquest graphify    # Phase 2: graph.json + Obsidian vault
uv run python -m graphquest reverse     # Phase 3: block + OOP diagrams
uv run python -m graphquest debug       # Phase 4: graph-guided agent finds+fixes
uv run python -m graphquest benchmark   # Phase 5: token report
uv run python -m graphquest all         # full pipeline

# Quality gates
uv run ruff check                       # 0 errors
uv run pytest -p no:cov                 # 6 infra tests pass (version + config)
uv run pytest                           # red until Phase 2: coverage <85% by design (TDD)
```
> **Phase 0 is intentionally a TDD "red" state.** The 6 infrastructure tests
> (`version`, `config`) pass, but the default `pytest` run enforces
> `fail_under = 85` over all of `src/` — the service modules are specified
> stubs (`NotImplementedError`) until their phase in `docs/TODO.md`, so the
> coverage gate is expected to fail until Phase 2. We do **not** `omit` stubs to
> inflate the number.
Or through the SDK (the single entry point for all logic):
```python
from graphquest import GraphQuestSDK
with GraphQuestSDK() as sdk:
    sdk.clone_target(); g = sdk.build_graph()
    sdk.reverse_engineer(g); sdk.debug(); sdk.benchmark()
```

## 5. Architecture
All logic is reachable only through `GraphQuestSDK`. Every external call goes
through the `ApiGatekeeper` (rate limit + queue + retry + budget ledger).
See [`docs/PLAN.md`](docs/PLAN.md) for C4, UML class and sequence diagrams.

```
CLI / SDK ─► GraphQuestSDK ─► Graphify (AST + bounded LLM) ─► graph.json + vault
                          ├─► ReverseEng ─► block + OOP Mermaid diagrams
                          ├─► LangGraph agent ─► OBS→REL→CONF→CTX→SRC ─► fix diff
                          └─► Benchmark ─► baseline vs guided ─► TOKEN_REPORT.md
              ApiGatekeeper ◄──── all LLM calls (budget + token ledger)
```

## 6. How Graphify is used
Three evidence layers converge into one graph: **Code** (AST, deterministic, 0
tokens → EXTRACTED edges), **Semantic** (bounded LLM → INFERRED/AMBIGUOUS), and
metrics (centrality, Louvain communities, bridges, God-nodes). Exports:
`graph.json`, `GRAPH_REPORT.md`, `graph.html`, and the Obsidian vault
(`index.md`, `hot.md`, linked notes). Every edge is a *claim* with
`evidence`, `confidence`, and `source_file`. See
[`docs/PRD_graphify.md`](docs/PRD_graphify.md).

## 7. How Obsidian is used
The vault (`obsidian/wiki/`) is the agent's cheap context surface. `index.md` =
Macro map; `hot.md` = focused bug-critical region; per-node notes link via
`[[wikilinks]]`. Reading discipline: Macro → Meso → Micro.

## 8. Documentation map
| File | Contents |
|------|----------|
| [docs/PRD.md](docs/PRD.md) | Goals, KPIs, acceptance criteria |
| [docs/PLAN.md](docs/PLAN.md) | C4 / UML / ADRs / sequence |
| [docs/TODO.md](docs/TODO.md) | Phased tasks + DoD |
| [docs/PROMPTS.md](docs/PROMPTS.md) | AI-assisted dev log |
| [docs/PRD_graphify.md](docs/PRD_graphify.md) | Graph + vault generator |
| [docs/PRD_debug_agent.md](docs/PRD_debug_agent.md) | LangGraph workflow |
| [docs/PRD_gatekeeper.md](docs/PRD_gatekeeper.md) | API gatekeeper + budget |
| [docs/PRD_token_benchmark.md](docs/PRD_token_benchmark.md) | Baseline-vs-guided contract |
| [docs/RESEARCH_QUESTIONS.md](docs/RESEARCH_QUESTIONS.md) | EX04 §4 questions + answers |

## 9. Configuration guide
| File | Controls |
|------|----------|
| `config/setup.json` | target project/bug, graphify globs, agent + benchmark settings |
| `config/rate_limits.json` | per-service limits, pricing, global budget cap |
| `config/logging_config.json` | FIFO log rotation |
> **No value is hardcoded in source.** All tunables live in `config/` (V3 §7).

## 10. Reverse engineering, bug, and before/after
_Filled in Phase 3–4:_ block diagram, OOP schema (`reports/REVERSE_ENGINEERING.md`),
root-cause analysis (`reports/BUG_REPORT.md`), before/after graph.

## 11. Token-efficiency comparison
_Filled in Phase 5:_ see [`reports/TOKEN_REPORT.md`](reports/TOKEN_REPORT.md) and
`assets/token_savings.png`. Honest baseline (same model/task/stop; only retrieval
differs) per [`docs/PRD_token_benchmark.md`](docs/PRD_token_benchmark.md).

## 12. Extensions & original ideas
Candidates (≥1 per area, see RESEARCH_QUESTIONS): centrality-ranked suspects,
dynamic `hot.md` from `git diff`, orphan detection, impact report, before/after
graph `diff`.

## 13. Self-grade
_Filled at submission — honest, not inflated (see HW1 lesson)._

## 14. License & credits
MIT. Graphify/Obsidian concepts © Dr. Yoram Segal (course material). Built with
AI agents per the V3 guidelines; process logged in `docs/PROMPTS.md`.
