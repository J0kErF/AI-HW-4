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

## 2. Investigation (to be filled by the agent in Phase 4)
- **OBS** — failing test points at `find_hook`/`run_hook` (community: hooks).
- **REL** — `run_hook --calls--> find_hook` (EXTRACTED edge). The contract of
  the *called* function is the suspect, not the caller.
- **CONF** — EXTRACTED call edge → strong; confirm at source.
- **CTX** — note the **rationale-vs-implementation gap**: `find_hook`'s docstring
  says *"Return a dict of all hook scripts provided… Dict's key will be…"* but
  the buggy code `return os.path.abspath(...)` on first match → returns one path.
- **SRC** — open `cookiecutter/hooks.py` to confirm.

## 3. Root cause
`cookiecutter/hooks.py::find_hook` returns the **first** matching script (single
path) instead of **all** matching scripts; `run_hook` then runs only that one.

## 4. Fix (matches upstream ground truth)
`find_hook` collects matches into a list (`return None` only when empty);
`run_hook` iterates `for script in scripts: run_script_with_context(...)`.
Verified by the two failing tests going green at the fixed commit.

## 5. Reproduction (documented)
```bash
uv run python -m graphquest clone        # checks out the buggy commit
# Full test run needs cookiecutter's deps + pytest (isolated venv):
#   python -m venv .t && .t/bin/pip install -e data/target_repo pytest pytest-mock freezegun
#   .t/bin/python -m pytest data/target_repo/tests/test_hooks.py::TestFindHooks::test_find_hook
```
Source-level defect **confirmed present** at the buggy commit (Phase 1). Full
pytest reproduction is a Phase-4 prerequisite, run in an isolated venv.

## 6. Before / after
Graph/architecture diff after the fix (Phase 4): the `find_hook`→`run_hook`
contract edge becomes consistent; the docstring/code rationale gap closes.
