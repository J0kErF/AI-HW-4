# Token Efficiency Report

> Honest baseline: same model, task and stopping criterion; only the
> retrieval policy differs (whole files vs graph-guided spans).
> Figures are the **mean over repeated runs** (see `results/benchmark_runs.json`
> and `notebooks/token_analysis.ipynb`) — output-token noise is averaged out.

| Metric | Naive baseline | Graph-guided | Saving |
|--------|----------------|--------------|--------|
| Total tokens | 4026 | 1761 | 56.3% |
| Input tokens | 3393 | 1363 | 59.8% |
| Output tokens | 633 | 398 | 37.1% |
| Files read | 2 | 2 | 0.0% |
| Units read | 2 | 5 | -150.0% |
| Source chars read (token proxy) | 13641 | 1386 | 89.8% |
| Iterations | 1 | 3 | -200.0% |
| Cost (USD) | 0.0016 | 0.0008 | 50.0% |
| Localized root cause | True | True | — |

![token savings](../assets/token_savings.png)

## Where the saving comes from
The baseline reads whole files (the failing test + the module under test);
the graph-guided agent follows `tested_by`/`calls` edges to the suspect and
reads only that function's source span. The one-time semantic graph-build
cost is separate (this run used the deterministic, token-free graph).

## What the numbers mean
The thesis is about **context (input) efficiency**: how much of the codebase
the model must ingest. Graph-guided wins decisively there — **input tokens**
and **source chars** drop ~60% and ~90% because the agent feeds the model two
~20-line spans instead of two ~200-line files (`Files read` is equal; the win
is content-per-read, not read count).

## Honest trade-offs
Graph-guided does **more, smaller** steps (`Units read` and `Iterations` higher:
an `explain` plus spans across observe/validate/fix). Those extra steps generate
extra **output** tokens, so the *total*-token saving is noisier than the input
saving and varies run-to-run — which is exactly why we report the mean over
several runs. The retrieval-controlled metrics (input, chars) are stable.
