# Token Efficiency Report

> Honest baseline: same model, task and stopping criterion; only the
> retrieval policy differs (whole files vs graph-guided spans).

| Metric | Naive baseline | Graph-guided | Saving |
|--------|----------------|--------------|--------|
| Total tokens | 4847 | 1388 | 71.4% |
| Input tokens | 3393 | 1064 | 68.6% |
| Output tokens | 1454 | 324 | 77.7% |
| Files read | 2 | 2 | 0.0% |
| Units read | 2 | 5 | -150.0% |
| Source chars read (token proxy) | 13641 | 804 | 94.1% |
| Iterations | 1 | 3 | -200.0% |
| Cost (USD) | 0.0025 | 0.0006 | 74.4% |
| Localized root cause | True | True | — |

![token savings](../assets/token_savings.png)

## Where the saving comes from
The baseline reads whole files (the failing test + the module under test);
the graph-guided agent follows `tested_by`/`calls` edges to the suspect and
reads only that function's source span. The one-time semantic graph-build
cost is separate (this run used the deterministic, token-free graph).

## Honest trade-offs
Graph-guided does **more, smaller** steps: `Units read` and `Iterations` are
higher (an `explain` plus two short spans across observe/validate/fix) and
`Files read` is equal — both arms touch the test file and the module. The win
is not fewer reads but **far less content per read**: the agent feeds the model
two ~20-line spans instead of two ~200-line files, which is why `Source chars`
and `Total tokens` drop sharply while step counts rise.
