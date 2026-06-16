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

<!-- Template for future entries:
### P<phase>.<n> — <short title>
- **Context given:** …
- **Prompt (verbatim or summary):** …
- **Outcome:** …
- **Iteration / what failed and why:** …
- **Tokens / cost (if notable):** …
-->
