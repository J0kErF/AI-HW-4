"""Naive baseline arm of the token benchmark (HONEST baseline — V3 thesis).

NOT a strawman: same model, same question, same stopping criterion as the
graph-guided arm. The ONLY difference is retrieval — the baseline reads RAW
WHOLE FILES (the failing test file and the module under test), the way an
engineer with no map would, with no graph/hot.md/index.md.
"""

from __future__ import annotations

from pathlib import Path

from graphquest.services.benchmark.models import BenchmarkRun
from graphquest.shared.gatekeeper import ApiGatekeeper
from graphquest.shared.llm import LLMClient

_SYS = "You are a precise debugging assistant. Be concise and cite the function."


class NaiveBaseline:
    """Whole-file-reading debugging attempt (no graph guidance).

    Args:
        gatekeeper: This arm's own ledger (token accounting isolated per arm).
        llm: LLM client bound to ``gatekeeper``.
        repo_root: Checked-out target repo.
    """

    def __init__(self, gatekeeper: ApiGatekeeper, llm: LLMClient, repo_root: Path) -> None:
        self._gk = gatekeeper
        self._llm = llm
        self._repo = Path(repo_root)

    def _module_under_test(self, test_file: str) -> Path | None:
        """Heuristic: test_X.py -> the first X.py in the package (not under tests)."""
        stem = Path(test_file).stem.replace("test_", "")
        for path in sorted(self._repo.rglob(f"{stem}.py")):
            if "test" not in path.parts and "test" not in path.name:
                return path
        return None

    def run(self, question: str, test_file: str) -> BenchmarkRun:
        """Read the whole test file + module under test, ask the LLM, measure."""
        files: list[str] = []
        test_path = self._repo / test_file
        if test_path.exists():
            files.append(test_path.read_text(encoding="utf-8", errors="replace"))
        module = self._module_under_test(test_file)
        if module:
            files.append(module.read_text(encoding="utf-8", errors="replace"))

        joined = "\n\n# ---- next file ----\n\n".join(files)
        resp = self._llm.complete(
            _SYS,
            f"Failing tests: {question}\n\nFull source files:\n```python\n{joined}\n```\n"
            "Identify the single root-cause function and give a unified-diff fix.",
        )
        return BenchmarkRun(
            arm="baseline",
            input_tokens=sum(r.input_tokens for r in self._gk._ledger),
            output_tokens=sum(r.output_tokens for r in self._gk._ledger),
            files_read=len(files),
            units_read=len(files),
            chars_read=sum(len(f) for f in files),
            iterations=1,
            cost_usd=self._gk.total_cost_usd,
            localized="find_hook" in resp.text.lower(),
        )
