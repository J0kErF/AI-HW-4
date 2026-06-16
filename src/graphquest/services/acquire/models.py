"""BugInfo — pinned metadata for the target bug (BugsInPy ``bug.info`` shape).

Mirrors the fields BugsInPy stores per bug so the checkout is fully reproducible
from versioned config (no live network dependency at run time — V3 reproducibility).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BugInfo:
    """One reproducible bug in a BugsInPy project.

    Attributes:
        project: BugsInPy project name (e.g. ``"cookiecutter"``).
        bug_id: BugsInPy bug number (e.g. ``"2"``).
        github_url: Upstream repo URL to clone.
        buggy_commit_id: Commit where the test fails.
        fixed_commit_id: Commit where the upstream fix lands (ground truth).
        test_file: Path to the failing test file.
        test_selectors: pytest node ids that expose the bug.
        python_version: Python the project was pinned to (documentation).
    """

    project: str
    bug_id: str
    github_url: str
    buggy_commit_id: str
    fixed_commit_id: str
    test_file: str
    test_selectors: tuple[str, ...]
    python_version: str

    @classmethod
    def from_config(cls, target: dict) -> BugInfo:
        """Build from the ``setup.json`` ``target`` block.

        Args:
            target: The ``target`` dict from config.
        """
        return cls(
            project=target["project"],
            bug_id=str(target["bug_id"]),
            github_url=target["github_url"],
            buggy_commit_id=target["buggy_commit_id"],
            fixed_commit_id=target["fixed_commit_id"],
            test_file=target["test_file"],
            test_selectors=tuple(target.get("test_selectors", ())),
            python_version=target.get("python_version", ""),
        )

    def commit_for(self, ref: str) -> str:
        """Return the commit id for ``ref`` ("buggy" or "fixed").

        Raises:
            ValueError: If ``ref`` is neither "buggy" nor "fixed".
        """
        if ref == "buggy":
            return self.buggy_commit_id
        if ref == "fixed":
            return self.fixed_commit_id
        raise ValueError(f"ref must be 'buggy' or 'fixed', got {ref!r}")
