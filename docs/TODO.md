# TODO — GraphQuest

> Version **1.00** · Status keys: ☐ not started · ◐ in progress · ☑ done. Each task lists its Definition of Done (DoD).

## Phase 0 — Scaffold & docs-first  ◐
- ☑ Repo tree, git init, `pyproject.toml`, `.gitignore`, `.env.example`
- ☑ Config: `setup.json`, `rate_limits.json`, `logging_config.json` (versioned)
- ☑ `src/` skeleton (SDK, shared, services) pre-split ≤150 LOC
- ☑ Mandatory docs: PRD, PLAN, TODO, PROMPTS, per-mechanism PRDs, RESEARCH_QUESTIONS
- ☑ `shared/version.py` + `shared/config.py` implemented with passing tests
  - *Note:* default `pytest` is **red until Phase 2** by design — `fail_under=85`
    over stubbed `src/`. Run `pytest -p no:cov` for the 6 green infra tests.
- ☑ Generate `uv.lock` and commit it (`uv lock` — 71 packages resolved);
  `pyproject.toml` + `uv.lock` are the single dependency source.
- ☑ Push to GitHub → **https://github.com/J0kErF/AI-HW-4** (`main` pushed)
- ☑ Shared repo with rmisegal@gmail.com (done by submitter via GitHub Settings)
  - *DoD met:* repo shared, README renders, commits tell PRD→PLAN→TODO→code story.

## Phase 1 — Acquire the unfamiliar codebase  ◐
- ☑ Pick & pin one BugsInPy project + bug id → **cookiecutter bug 2** (`setup.json`)
- ☑ Checkout buggy commit into `data/target_repo`; source-level defect confirmed
  (`find_hook` returns single path; docstring-vs-code gap noted in BUG_REPORT)
- ☑ `acquire` service (`BugInfo`, `bug_metadata` parser, `TargetCheckout`) + SDK
  `clone_target()` implemented + tested (subprocess mocked — no network)
- ☑ Reproduce the failing test in an isolated venv (`buggy` red → `fixed` green) —
  **verified** (Windows/py3.13): both `test_hooks.py` selectors **2 failed** at buggy,
  **2 passed** at fixed; logged in `reports/BUG_REPORT.md §5`.

## Phase 2 — Graphify  ◐
- ☑ `CodeLayer.extract()` — AST nodes/edges (EXTRACTED), token-free; resilient to
  non-Python fixtures. Ran on cookiecutter: **459 nodes / 390 edges**; the
  `run_hook→find_hook` (calls) and `test_find_hook→find_hook` (tested_by) edges
  are present. Unit tests on a fixture tree.
- ☑ `MetricsCalculator.compute()` — NetworkX degree/betweenness, greedy-modularity
  communities, bridges, God-nodes. (NetworkX is installed; pure graph theory.)
- ☑ `VaultWriter.write()` — `index.md`, `hot.md`, per-node notes with `[[wikilinks]]`
- ☑ `ReportWriter` → `GRAPH_REPORT.md`; `Graphifier` composition; `graphify` CLI + SDK
- ☑ `SemanticLayer.augment()` — bounded LLM layer (≤40 functions, dunders skipped)
  emits `semantically_similar_to` INFERRED/AMBIGUOUS edges via the Gatekeeper.
  Enabled in `build_graph` when `semantic_layer_enabled` + a key are present;
  off → deterministic graph. **Live on cookiecutter: +8 edges** (6 inferred,
  2 ambiguous), e.g. `get_config~get_user_config`, `generate_file~generate_files`.
  Graph now demonstrates all three Graphify layers. (SDK split into
  `sdk/builders.py` mixin to keep files ≤150 LOC.)
  - *DoD met:* `graph.json` carries extracted+inferred+ambiguous evidence.

## Phase 3 — Reverse engineering  ☑
- ☑ `DiagramGenerator.block_diagram()` (Mermaid flowchart, modules grouped by dir)
- ☑ `DiagramGenerator.oop_schema()` (Mermaid classDiagram from class/inherits) —
  renders the `CookiecutterException` hierarchy (17 inherits edges)
- ☑ `reports/REVERSE_ENGINEERING.md` with 2 insights: God-node/bottleneck (auto
  from betweenness) + the `find_hook` docstring-vs-code gap (cites source + edges)
  - *DoD met:* diagrams render in GitHub; insights cite `source_file` + evidence.
  - 20 tests pass; diagrams 100%, report 92%; ruff clean.

## Phase 4 — Graph-guided debug agent  ◐
- ☑ **Prereq:** `ApiGatekeeper` + `RateLimiter` implemented (blocking backpressure,
  retries, token/cost ledger, budget cap) — fully offline-tested (97%/100%).
  Unblocks the semantic layer and the agent's LLM calls.
- ☑ `GraphTools` (query/neighbors/explain/read_source_span — reads function spans, not files)
- ☑ `DebugNodes` (observe→hypothesize→validate→fix; source read last, span cached)
- ☑ `DebugWorkflow` (real LangGraph `StateGraph`); `SDK.debug` + `debug` CLI
- ☑ `LLMClient` (OpenAI-compatible, billed via Gatekeeper); machinery fully
  mocked-tested (agent localizes find_hook, emits fix, 3-step token_log)
- ☑ **LIVE RUN** (deepseek-chat): faithful BugsInPy repro (buggy code + fixed test
  overlaid by `TargetCheckout`); agent localized `find_hook` graph-first and gave
  the correct root cause (test expects a list) + a list-returning fix, ~1.3k
  tokens / $0.0006. Fix is directionally correct, not byte-identical to upstream.

## Phase 5 — Token benchmark (the thesis)  ◐
- ☑ `NaiveBaseline.run()` (whole test file + module under test; same model/task/stop)
- ☑ Guided arm via the agent; isolated gatekeeper ledger per arm
- ☑ `BenchmarkComparator` → `TOKEN_REPORT.md` + matplotlib `token_savings.png`;
  `SDK.benchmark` + `benchmark` CLI. Mocked tests prove guided opens fewer files.
- ☑ **LIVE RUN** (deepseek-chat): **71.4% total-token saving** (4847→1388),
  94.1% fewer source chars, 74.4% lower cost; both arms localized. Honest
  trade-offs (units/iterations higher) shown in `reports/TOKEN_REPORT.md` + chart.
  - *DoD met:* honest table; ≥60% token saving demonstrated.

## Phase 6 — Docs, visuals, self-grade  ☐
- ☐ README: install/usage, screenshots, diagrams, cost table, self-grade
- ☐ `notebooks/token_analysis.ipynb` (sensitivity / per-metric charts)
- ☐ Final checklist (V3 §17), ruff-clean, coverage ≥85%, honest self-grade
  - *DoD:* every EX04 §7 deliverable present and linked from README.
