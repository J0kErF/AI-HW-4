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
A single self-contained **BugsInPy** project — **`cookiecutter` bug 2** (pinned
in [`config/setup.json`](config/setup.json)). Chosen because it is
cross-platform reproducible and its root cause spans **two functions**
(`run_hook` → `find_hook`, a changed return contract) — a far stronger
*graph-navigation* demo than a single isolated function. It even ships a
**docstring-vs-code gap** (`find_hook`'s docstring promises a dict of all hooks
while the buggy code returns one path), which exercises Graphify's
rationale-vs-implementation reading. Fallback: `cookiecutter` bug 1 (one-line
`encoding='utf-8'` fix, bulletproof reproduction). Larger-codebase alternative
for a bigger token delta: `thefuck`. Real upstream fix is the ground truth.

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
uv run pytest                           # 29 tests pass, coverage ≥85% (currently ~91%)
```
> **Quality gates pass.** 29 tests green across all phases (config, acquire,
> graphify code layer/metrics/vault/Graphifier, reverse-engineering diagrams,
> gatekeeper/rate-limiter, the LangGraph agent and the benchmark — LLM mocked).
> Coverage **~91%** (≥85% gate met); ruff clean. The **live** debugging run and
> the real token numbers require an LLM key in `.env` (`graphquest debug` /
> `benchmark`); the suite itself never makes a network call.
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

## 11. Token-efficiency comparison (LIVE results — deepseek-chat)
Real run on cookiecutter bug 2 (full table in
[`reports/TOKEN_REPORT.md`](reports/TOKEN_REPORT.md), chart
`assets/token_savings.png`). Honest baseline: same model/task/stopping criterion;
only retrieval differs (whole files vs graph-guided spans).

| Metric | Naive baseline | Graph-guided | Saving |
|--------|----------------|--------------|--------|
| **Total tokens** | 4847 | 1388 | **71.4%** |
| Input tokens | 3393 | 1064 | 68.6% |
| **Source chars read** (token proxy) | 13641 | 804 | **94.1%** |
| Cost (USD) | 0.0025 | 0.0006 | 74.4% |
| Localized root cause | ✓ | ✓ | — |

> **Honest trade-off:** graph-guided does *more, smaller* steps (Units read 5 vs 2,
> Iterations 3 vs 1; Files read equal). The win isn't fewer reads — it's **far less
> content per read** (two ~20-line spans vs two ~200-line files), which is what
> drives the token/cost drop. Both arms correctly localized `find_hook`.

## 11b. Cost / budget
The whole live pipeline (graphify is token-free; debug + benchmark) costs **< $0.01**
on `deepseek-chat`. The Gatekeeper caps spend at **$1.50/session**
(`config/rate_limits.json`) and prices every call from config.

## 12. Extensions & original ideas
Candidates (≥1 per area, see RESEARCH_QUESTIONS): centrality-ranked suspects,
dynamic `hot.md` from `git diff`, orphan detection, impact report, before/after
graph `diff`.

## 13. Self-grade
**~84 / 100** — honest (not inflated; see HW1 lesson).

**Strengths:** full V3 compliance (SDK facade, API Gatekeeper with rate
limit/budget/ledger, OOP, ≤150-LOC modules, per-mechanism PRDs, C4/UML, PROMPTS
log, versioned config, uv-ready); a *real* deterministic Graphify graph (459
nodes) + Obsidian vault from an unfamiliar repo; Mermaid block + OOP diagrams and
two graph-derived insights; a working **LangGraph** agent that localizes the bug
graph-first and a **live, honest token benchmark showing 71% fewer tokens / 94%
fewer source chars**; 29 tests, **~91% coverage**, ruff-clean; reproducible
BugsInPy checkout (buggy code + fixed test).

**Known gaps:** the agent's fix is *directionally* correct (returns a list) but
not byte-identical to upstream (small model, minimal context); the bounded
semantic-layer edges are implemented but not enabled in the committed graph
(EXTRACTED-only); full `pytest` reproduction of the target's failing test in an
isolated venv is documented but not automated; `uv.lock` not yet generated here.

## 14. License & credits
MIT. Graphify/Obsidian concepts © Dr. Yoram Segal (course material). Built with
AI agents per the V3 guidelines; process logged in `docs/PROMPTS.md`.
