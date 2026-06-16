# PRD — Token-efficiency benchmark (the assignment thesis)

> Version **1.00** · Implements EX04 §5.5. This is the deliverable graders
> scrutinize hardest, because it is what we *claim to prove*.

## 1. The claim

Graph-guided debugging localizes the same bug with **dramatically fewer tokens**
than a naive whole-file approach, by reading the smallest evidence slice
(graph/vault) first and source last — avoiding the *Lost-in-the-Middle* waste of
stuffing irrelevant code into the context window.

## 2. Fairness contract (NOT a strawman baseline)

Both arms are **real agent attempts** that share everything except retrieval:

| Held identical | Differs |
|----------------|---------|
| Model (`GRAPHQUEST_MODEL`) | **Retrieval policy** |
| Task / question (same failing symptom) | baseline: reads raw whole files |
| Stopping criterion (`root_cause_localized_to_function`) | guided: `hot.md`/`index.md`/graph tools |
| `max_iterations` cap | — |
| Gatekeeper token accounting | — |

A strawman (e.g. dumping the *entire* repo once) is explicitly disallowed: the
baseline is an honest engineer-without-a-map who opens files as needed.

## 3. Metrics (EX04 §5.5)

For each arm record, via the gatekeeper ledger + run instrumentation:
- **Tokens** consumed (input, output, total).
- **Files** opened and **textual units** (functions/notes) read.
- **Iterations** / investigation rounds.
- **Quality & speed** to root cause and to fix (localized? test green? seconds).

## 4. Output

`reports/TOKEN_REPORT.md`:

| Metric | Naive baseline | Graph-guided | Saving |
|--------|----------------|--------------|--------|
| Total tokens | … | … | …% |
| Files read | … | … | … |
| Units read | … | … | … |
| Iterations | … | … | … |
| Time to root cause (s) | … | … | … |
| Correctly localized | y/n | y/n | — |
| Cost (USD) | … | … | …% |

Plus `assets/token_savings.png` (Python/matplotlib bar chart) and a short
narrative: where the saving comes from, and an honest note if any metric does
not favor the guided arm (e.g. graph build cost amortization).

## 5. Honesty notes to include
- Count the **one-time graph build cost** (semantic layer tokens) separately and
  discuss amortization across multiple questions.
- If the baseline accidentally finds the bug fast (small repo), say so and
  explain why the saving narrows.

## 6. Success criteria & tests
- ≥60% total-token saving on the chosen project, or a documented explanation.
- Unit tests on `BenchmarkComparator.compare()` deltas with synthetic runs
  (no real LLM); report renders deterministically.
