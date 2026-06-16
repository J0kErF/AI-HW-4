# Bug Analysis Report

> Target pinned in Phase 1. Investigation (Phase 4) follows OBS→REL→CONF→CTX→SRC.

## 0. Target (pinned)
- **Project:** cookiecutter (BugsInPy bug **2**) — 18 Python modules in the package.
- **Upstream:** https://github.com/cookiecutter/cookiecutter
- **Buggy commit:** `d7e7b28811e474e14d1bed747115e47dcdd15ba3` (reproduced into `data/target_repo`)
- **Fixed commit:** `90434ff4ea4477941444f1e83313beb414838535` (ground truth)
- **Failing tests:**
  - `tests/test_hooks.py::TestFindHooks::test_find_hook`
  - `tests/test_hooks.py::TestExternalHooks::test_run_hook`

## 1. Problem description
With multiple matching hook scripts in a template's `hooks/` dir, only the
**first** one runs. `test_find_hook` expects a *list* of hook paths; the buggy
`find_hook` returns a single path (or `None`).

## 2. Investigation (LIVE — graph-guided LangGraph agent, deepseek-chat)
Faithful BugsInPy reproduction: buggy code + the *fixed commit's* test overlaid
(`TargetCheckout` does this), so `test_find_hook` asserts `find_hook(...)[0]` —
indexing a **list** the buggy code never returns.

- **OBS** — from the failing-test name the agent followed `tested_by` edges to
  the suspect `cookiecutter/hooks.py::find_hook` (no source read yet).
- **REL/CONF** — EXTRACTED `tested_by` edge → strong; also `run_hook --calls-->
  find_hook`. The *called* function's contract is the suspect.
- **CTX/SRC** — the agent read ONLY two spans (find_hook + test_find_hook), not
  whole files, and concluded:
  > "The test expects `hooks.find_hook` to return a list where the first element
  > is an absolute path … causing the assertion `expected_pre == actual_hook_path[0]`
  > to fail."
- **Cost of the agent run:** ~1.3k tokens, ~$0.0006.

## 3. Root cause
`cookiecutter/hooks.py::find_hook` returns the **first** matching script (a single
path / `None`) instead of a **list** of all matching scripts; the updated test
indexes the result as a list (`[0]`), so it fails. `run_hook` likewise runs only
the one returned script.

## 3a. Agent's proposed fix (directionally correct)
The agent emitted a diff making `find_hook` `return [hook_path]` / `return []`
(a list) — the correct *direction* of the upstream fix. It is not byte-identical
to upstream (which collects ALL matches and updates `run_hook` to iterate); a
small model reading minimal context gets the contract right but not every detail.
The upstream ground-truth patch is in §4.

## 4. Fix (matches upstream ground truth)
`find_hook` collects matches into a list (`return None` only when empty);
`run_hook` iterates `for script in scripts: run_script_with_context(...)`.
Verified by the two failing tests going green at the fixed commit.

## 5. Reproduction (VERIFIED in an isolated venv, Windows / Python 3.13)
```bash
uv run python -m graphquest clone   # buggy code + fixed-commit test overlaid
python -m venv .repro
.repro/Scripts/pip install -e data/target_repo pytest pytest-mock freezegun
cd data/target_repo
python -m pytest tests/test_hooks.py::TestFindHooks::test_find_hook \
                 tests/test_hooks.py::TestExternalHooks::test_run_hook -o addopts=""
```
Result (both selectors):
- **Buggy** (code `d7e7b28` + fixed test): **2 failed** — `test_find_hook` fails on
  `actual_hook_path[0]` (buggy code returns a string, not a list).
- **Fixed** (`90434ff`): **2 passed**.

`buggy → red`, `fixed → green` confirmed. (`-o addopts=""` clears the target's
`--cov` inifile options; the target's own deps install cleanly.)

## 6. Before / after
Graph/architecture diff after the fix (Phase 4): the `find_hook`→`run_hook`
contract edge becomes consistent; the docstring/code rationale gap closes.
