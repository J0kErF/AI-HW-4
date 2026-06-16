# TODO — GraphQuest

> Version **1.00** · Status keys: ☐ not started · ◐ in progress · ☑ done. Each task lists its Definition of Done (DoD).

## Phase 0 — Scaffold & docs-first  ◐
- ☑ Repo tree, git init, `pyproject.toml`, `.gitignore`, `.env.example`
- ☑ Config: `setup.json`, `rate_limits.json`, `logging_config.json` (versioned)
- ☑ `src/` skeleton (SDK, shared, services) pre-split ≤150 LOC
- ☑ Mandatory docs: PRD, PLAN, TODO, PROMPTS, per-mechanism PRDs, RESEARCH_QUESTIONS
- ☑ `shared/version.py` + `shared/config.py` implemented with passing tests
- ☐ Push to GitHub; share with rmisegal@gmail.com
  - *DoD:* repo public/shared, README renders, P0 commits tell PRD→PLAN→TODO→code story.

## Phase 1 — Acquire the unfamiliar codebase  ☐
- ☐ Pick & pin one BugsInPy project + bug id (finalize `setup.json`)
- ☐ Isolated venv/Docker checkout into `data/target_repo`; reproduce the failing test
  - *DoD:* `buggy` ref fails the target test; `fixed` ref passes; documented in BUG_REPORT.
- ☐ `SDK.clone_target()` implemented + tested (mock subprocess)

## Phase 2 — Graphify  ☐
- ☐ `CodeLayer.extract()` — AST nodes/edges (EXTRACTED), token-free
  - *DoD:* deterministic `graph.json` for the target; unit tests on a fixture tree.
- ☐ `SemanticLayer.augment()` — bounded INFERRED/AMBIGUOUS edges via Gatekeeper
- ☐ `MetricsCalculator.compute()` — centrality, Louvain communities, bridges, God-nodes
- ☐ `VaultWriter.write()` — `index.md`, `hot.md`, per-node notes with `[[wikilinks]]`
- ☐ `GRAPH_REPORT.md` writer
  - *DoD:* `graphify` command emits all artifacts; vault opens in Obsidian; ≥85% cov.

## Phase 3 — Reverse engineering  ☐
- ☐ `DiagramGenerator.block_diagram()` (Mermaid flowchart from communities)
- ☐ `DiagramGenerator.oop_schema()` (Mermaid classDiagram from class/inherits/uses)
- ☐ Write `reports/REVERSE_ENGINEERING.md` with ≥2 insights (God-node, traceability gap)
  - *DoD:* diagrams render in GitHub; insights cite `source_file` + evidence type.

## Phase 4 — Graph-guided debug agent  ☐
- ☐ `GraphTools` (query/path/explain/read_source_span)
- ☐ `DebugNodes` (observe→relate→hypothesize→validate→fix) + `should_continue`
- ☐ `DebugWorkflow` (StateGraph wiring, iteration cap)
- ☐ Localize root cause + emit fix diff; confirm target test goes green
  - *DoD:* `debug` command produces correct fix; per-step `token_log` recorded.

## Phase 5 — Token benchmark (the thesis)  ☐
- ☐ `NaiveBaseline.run()` (whole-file reads, same model/task/stop)
- ☐ Guided arm (reuse agent) instrumented identically
- ☐ `BenchmarkComparator` → `TOKEN_REPORT.md` + `assets/token_savings.png`
  - *DoD:* honest comparison table; ≥60% token saving demonstrated or explained.

## Phase 6 — Docs, visuals, self-grade  ☐
- ☐ README: install/usage, screenshots, diagrams, cost table, self-grade
- ☐ `notebooks/token_analysis.ipynb` (sensitivity / per-metric charts)
- ☐ Final checklist (V3 §17), ruff-clean, coverage ≥85%, honest self-grade
  - *DoD:* every EX04 §7 deliverable present and linked from README.
