# Research Questions (EX04 §4)

> These are answered with evidence in the README, `reports/`, and the Obsidian
> vault. This file tracks each question and where its answer will live. Phrasing
> follows the conclusion discipline: "the graph *suggests*…" until validated.

| # | Question | Answer lives in | Status |
|---|----------|-----------------|--------|
| 1 | What is the project's **actual** architecture, and what surprised us vs first impression? | `reports/REVERSE_ENGINEERING.md` (block diagram) | ☐ |
| 2 | Which components / modules / functions are most **central**? | `GRAPH_REPORT.md` + centrality table | ☐ |
| 3 | Where are the **God-nodes** / bottlenecks / mixed responsibility? | RE report, hub-vs-bottleneck analysis | ☐ |
| 4 | Can we extract a block diagram and **OOP schema** from code when docs are partial/absent? | `reports/REVERSE_ENGINEERING.md` (Mermaid) | ☐ |
| 5 | How did we identify the bug, what was the **root cause**, and what steps led there? | `reports/BUG_REPORT.md` (OBS→REL→CONF→CTX→SRC) | ☐ |
| 6 | What is the advantage of **graph navigation** vs linear file reading? | `reports/TOKEN_REPORT.md` | ☐ |
| 7 | How did graph-guided agent use **save tokens** / avoid redundant reads? | `TOKEN_REPORT.md` + token chart | ☐ |
| 8 | What **extensions / original ideas** did we add (centrality-ranked suspects, dynamic `hot.md` from `git diff`, orphan detection, etc.)? | README §"Extensions" | ☐ |

## Candidate original extensions (EX04 §5.6 — pick ≥1 per area)
- Rank suspect nodes by `centrality` × proximity to the failing test.
- Build `hot.md` dynamically from `git diff` (buggy vs fixed) + `graph.json`.
- Detect orphan/dead components and auto-document them.
- Flag ambiguous-responsibility edges and suggest a refactor.
- "Impact report": what else breaks if we change this function/class.
- Before/after graph `diff` proving the fix reduced a bottleneck.
