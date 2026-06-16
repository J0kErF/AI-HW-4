# Research Questions (EX04 §4)

> These are answered with evidence in the README, `reports/`, and the Obsidian
> vault. This file tracks each question and where its answer will live. Phrasing
> follows the conclusion discipline: "the graph *suggests*…" until validated.

| # | Question | Answer lives in | Status |
|---|----------|-----------------|--------|
| 1 | What is the project's **actual** architecture, and what surprised us vs first impression? | `reports/REVERSE_ENGINEERING.md` (block diagram) | ◐ surprise: `find_hook` docs-vs-code gap |
| 2 | Which components / modules / functions are most **central**? | `GRAPH_REPORT.md` + centrality table | ◐ `generate_files`/`main`/`run_hook` |
| 3 | Where are the **God-nodes** / bottlenecks / mixed responsibility? | RE report, hub-vs-bottleneck analysis | ◐ betweenness ranking emitted |
| 4 | Can we extract a block diagram and **OOP schema** from code when docs are partial/absent? | `reports/REVERSE_ENGINEERING.md` (Mermaid) | ☑ both Mermaid diagrams generated |
| 5 | How did we identify the bug, what was the **root cause**, and what steps led there? | `reports/BUG_REPORT.md` (OBS→REL→CONF→CTX→SRC) | ☑ agent localized find_hook graph-first |
| 6 | What is the advantage of **graph navigation** vs linear file reading? | `reports/TOKEN_REPORT.md` | ☑ 71% fewer tokens, 94% fewer chars |
| 7 | How did graph-guided agent use **save tokens** / avoid redundant reads? | `TOKEN_REPORT.md` + token chart | ☑ reads 20-line spans not 200-line files; span cached |
| 8 | What **extensions / original ideas** did we add? | README §12 | ☑ chars_read metric, N-run suite + sensitivity, centrality-seeded hot.md, tested_by-following validate, semantic layer, faithful BugsInPy repro, interactive graph.html |

## Candidate original extensions (EX04 §5.6 — pick ≥1 per area)
- Rank suspect nodes by `centrality` × proximity to the failing test.
- Build `hot.md` dynamically from `git diff` (buggy vs fixed) + `graph.json`.
- Detect orphan/dead components and auto-document them.
- Flag ambiguous-responsibility edges and suggest a refactor.
- "Impact report": what else breaks if we change this function/class.
- Before/after graph `diff` proving the fix reduced a bottleneck.
