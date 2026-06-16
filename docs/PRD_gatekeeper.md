# PRD — API Gatekeeper, rate limits & budget

> Version **1.00** · Implements V3 §5. Single chokepoint for every external call.

## 1. Description

All external calls (LLM for the semantic layer **and** the agent) MUST pass
through `ApiGatekeeper`. There are **no direct API calls** anywhere else. The
gatekeeper enforces rate limits, queues on backpressure (never drops), retries
transient failures, logs every call, and keeps a token/cost **ledger** that
powers both the global budget cap and the token-efficiency benchmark.

## 2. Requirements (V3 §5.1)
- No API call bypasses the gatekeeper.
- Rate limits enforced **before** each call, read from `config/rate_limits.json`
  (never hardcoded — V3 §5.2).
- Over-limit requests are **queued** (FIFO, bounded `max_depth`), with
  backpressure when full — not discarded.
- Every call recorded (service, in/out tokens, cost, retries, ok).
- Global budget cap (`global_budget_usd`) raises before exceeding.

## 3. Interface
```python
class ApiGatekeeper:
    def execute(self, service, api_call, *args, **kwargs) -> Any: ...
    def record_usage(self, service, input_tokens, output_tokens) -> CallRecord: ...
    def get_queue_status(self) -> QueueStatus: ...
    @property
    def total_cost_usd(self) -> float: ...
```

## 4. Configuration (`rate_limits.json`)
- `services.<name>`: `requests_per_minute`, `requests_per_hour`,
  `concurrent_max`, `retry_after_seconds`, `max_retries`.
- `pricing_usd_per_million_tokens.<model>`: `{input, output}` for the ledger.
- `queue`: `max_depth`, `backpressure` (`block`).
- `version` must match the code version (V3 §8.1).

## 5. Constraints & alternatives
- Token counting via `tiktoken` (or provider usage field) at the call site.
- *Alternative considered:* per-service limiters scattered in callers — rejected
  (no central budget, dishonest benchmark accounting). ADR-004.

## 6. Success criteria & tests
- Unit: limit enforced (N+1th call queues, not fails); retry on transient error;
  budget cap raises at threshold; ledger sums correctly.
- No test makes a real network call (mocked `api_call`).
