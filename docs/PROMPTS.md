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
<!-- Template for future entries:
### P<phase>.<n> — <short title>
- **Context given:** …
- **Prompt (verbatim or summary):** …
- **Outcome:** …
- **Iteration / what failed and why:** …
- **Tokens / cost (if notable):** …
-->
