# PROMPTS — AI-assisted development log (Prompt Book)

> Version **1.00** · V3 §8.3. Documents how this project was built *with* AI
> agents — the prompts, context, and reasoning. HW1 feedback explicitly flagged
> that this development narrative was missing; it is itself a graded deliverable.

## How to use this log
Append one entry per significant prompt/iteration. Keep it honest: include
prompts that *failed* and what was changed.

---

### P0.1 — Project initialization (this scaffold)
- **Context given to the agent:** EX04 assignment PDF, L07 lecture summary,
  the Graphify "how to read a graph" deck, V3 submission guidelines, HW1 detailed
  feedback, and the HW1/HW2/HW3 repositories for house-style.
- **Goal:** stand up the full HW4 infrastructure docs-first (PRD→PLAN→TODO→code
  stubs) before any implementation, per V3 §2.5.
- **Key decisions surfaced to the user:** base repo (BugsInPy), agent framework
  (LangGraph), project name (`graphquest`).
- **Outcome:** directory tree, versioned config, SDK/Gatekeeper/services skeleton
  (≤150 LOC, pre-split), and all `docs/` written; `version`+`config` implemented
  with passing tests.
- **What changed mid-flight:** read the Graphify PDF *before* writing
  `PRD_graphify.md` so the `graph.json`/`hot.md`/`index.md` schemas match the
  taught conventions (evidence types, confidence, source_file) instead of being
  invented blind.

---
### P1.1 — Acquire & pin the target bug
- **Context given:** EX04 + L07 + V3; live BugsInPy metadata inspected via the
  GitHub API (cookiecutter & thefuck bug lists, `bug.info`, `run_test.sh`,
  `bug_patch.txt`).
- **Goal:** pick one reproducible bug; implement `clone_target()` with offline,
  mockable tests; reproduce the codebase.
- **Decision & why:** flipped primary from `thefuck` to **cookiecutter bug 2** —
  cross-platform reproducible, and its root cause spans `run_hook`→`find_hook`
  (a changed return contract) for a stronger graph-navigation demo; also exhibits
  a docstring-vs-code gap. Fallback bug 1; thefuck kept as larger alternative.
- **Outcome:** `acquire` service (`BugInfo` / `bug_metadata` parser /
  `TargetCheckout` with injected runner) + `SDK.clone_target()`; metadata vendored
  into `config/setup.json` (no run-time network dependency); buggy commit cloned
  into `data/target_repo` and the defect confirmed at source.
- **Honesty note:** full pytest reproduction (needs cookiecutter deps in an
  isolated venv) deferred to a Phase-4 prerequisite; source-level defect verified.

### P2.1 — Graphify deterministic pipeline
- **Context given:** the Graphify "reading a graph" spec (Node=entity, Edge=claim
  with evidence type + confidence + source_file; Code/Semantic layers); the
  reproduced cookiecutter checkout.
- **Goal:** build the token-free graph + Obsidian vault from real source.
- **Outcome:** `ast_visitor` (per-file facts) + `CodeLayer` (module/class/function
  nodes; imports/inherits/calls/tested_by EXTRACTED edges, conservative unique-name
  resolution) + `MetricsCalculator` (NetworkX degree/betweenness/communities/
  bridges/God-nodes) + `VaultWriter` + `ReportWriter` + `Graphifier` + `graphify`
  CLI/SDK. Ran on cookiecutter → 459 nodes / 390 edges; the bug-relevant
  `run_hook→find_hook` and `test_find_hook→find_hook` edges are present.
- **Iteration / what failed:** a Jinja-template `.py` test fixture broke
  `ast.parse`; fixed by skipping unparseable files (they aren't real source).
- **Decision:** NetworkX is installed, so used it for real graph theory (rather
  than a pure-Python fallback). Semantic layer + Gatekeeper deferred to the agent
  phase (need an LLM key); deterministic graph is complete and token-free.
- **Quality:** 17 tests pass; ruff clean; coverage 77% (gap is Phase 3-5 stubs).

### P3.1 — Reverse-engineering diagrams + insights
- **Context given:** EX04 §5.2 (block diagram + OOP schema *from the graph*); the
  real cookiecutter `graph.json`.
- **Outcome:** `DiagramGenerator` (Mermaid `flowchart` of modules grouped by dir;
  `classDiagram` from class+inherits edges) + `ReverseEngineeringReport`
  (auto God-node insight from betweenness + the `find_hook` docstring-vs-code gap)
  + `SDK.reverse_engineer` + `reverse` CLI. Ran on cookiecutter → renders the
  `CookiecutterException` hierarchy (17 inherits) and both insights.
- **Quality:** 20 tests pass (diagrams 100%, report 92%); ruff clean; coverage 78%.

### P4.0 — API Gatekeeper (Phase 4 prerequisite)
- **Context given:** V3 §5 (single chokepoint; rate limit from config; queue/
  backpressure; retries; token/cost ledger; budget cap).
- **Outcome:** `RateLimiter` (sliding-window, blocks on limit, injected clock/
  sleep) + `ApiGatekeeper` (execute with rate-limit→budget→retry→record; pricing
  from config; `BudgetExceededError`). Fully offline-tested (mock call, virtual
  clock — no waits/network); gatekeeper 97%, limiter 100%.
- **Note:** the live debugging agent + token benchmark (Phases 4-5) need a real
  LLM key in `.env`; the machinery and budget accounting are ready.

### P4.1 / P5.1 — LangGraph agent + token benchmark (machinery)
- **Context given:** PRD_debug_agent + PRD_token_benchmark; the real cookiecutter
  graph.json (with line ranges added so the agent reads a function span, not a file).
- **Outcome:** `LLMClient` (OpenAI-compatible, billed via Gatekeeper); `GraphTools`
  (query/neighbors/explain/read_source_span); `DebugNodes`
  (observe→hypothesize→validate→fix, source-last, span cached to avoid re-reads);
  `DebugWorkflow` (real LangGraph StateGraph); `NaiveBaseline` (whole test file +
  module under test); `BenchmarkComparator` (TOKEN_REPORT.md + matplotlib chart);
  `BenchmarkRunner`; `SDK.debug`/`benchmark` + CLI.
- **Iteration:** the fake LLM returns fixed token counts, so a mock can't show the
  token *saving* — switched the benchmark test to assert the structural claim it
  CAN prove (guided opens 1 span-file vs baseline's 2 whole files); real numbers
  come from the live run. Also cached the suspect span so `fix` doesn't re-read.
- **Quality:** 29 tests pass; coverage **~91% (gate met)**; ruff clean. LLM is
  mocked — no network in tests. Live run needs a key.

### P4.2 / P5.2 — LIVE run on deepseek-chat
- **Context:** real DeepSeek key in `.env` (git-ignored, never committed).
- **Iteration / what failed and why:** first live debug gave a wrong root cause
  ("returns None, expects {}") — because the raw buggy commit ships the *pre-fix*
  test (consistent with buggy code → no failure exposed). Fixed `TargetCheckout`
  to overlay the failing test from the fixed commit (true BugsInPy semantics);
  re-cloned + re-graphified. Also made `validate` follow the `tested_by` edge to
  read the test span, so the root cause is grounded in the assertion.
- **Result (debug):** agent localized `find_hook` graph-first and correctly stated
  the list-vs-single contract; fix returns a list (directionally upstream-correct);
  ~1.3k tokens, $0.0006.
- **Result (benchmark):** **71.4% total-token saving** (4847→1388), 94.1% fewer
  source chars, 74.4% lower cost; both arms localized. Honest trade-offs (units 5
  vs 2, iterations 3 vs 1) reported, not hidden.
- **Quality:** 29 tests pass, coverage ~91%, ruff clean; tests never hit network.

<!-- Template for future entries:
### P<phase>.<n> — <short title>
- **Context given:** …
- **Prompt (verbatim or summary):** …
- **Outcome:** …
- **Iteration / what failed and why:** …
- **Tokens / cost (if notable):** …
-->
