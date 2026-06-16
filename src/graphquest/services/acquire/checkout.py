"""Target-repo checkout (Phase 1).

Clones the upstream project named in :class:`BugInfo` into the checkout dir and
pins it to the buggy (or fixed) commit. Git is driven through an injected
``runner`` (defaults to :func:`subprocess.run`) so the logic is unit-testable
without touching the network (dependency injection — V3 §16 testability).
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

from graphquest.services.acquire.models import BugInfo

Runner = Callable[..., subprocess.CompletedProcess]


class TargetCheckout:
    """Clone + checkout the BugsInPy target at a chosen revision.

    Args:
        checkout_dir: Where the repo is cloned (``data/target_repo``).
        runner: Subprocess runner (injected for testing).
    """

    def __init__(self, checkout_dir: Path, runner: Runner = subprocess.run) -> None:
        self._dir = checkout_dir
        self._run = runner

    def _git(self, *args: str, cwd: Path | None = None) -> None:
        """Run a git command, raising on non-zero exit."""
        self._run(["git", *args], cwd=str(cwd) if cwd else None, check=True)

    def checkout(self, bug: BugInfo, ref: str = "buggy") -> Path:
        """Clone ``bug.github_url`` and check out the BugsInPy revision for ``ref``.

        Faithful BugsInPy reproduction: for ``ref="buggy"`` we check out the buggy
        commit's CODE but overlay the failing test from the *fixed* commit, so the
        bug is actually exposed (the raw buggy commit ships the pre-fix test, which
        passes). Idempotent: an existing repo is only fetched + re-checked-out.

        Args:
            bug: Pinned bug metadata.
            ref: "buggy" (default) or "fixed".

        Returns:
            Path to the checked-out working tree.
        """
        commit = bug.commit_for(ref)
        if not (self._dir / ".git").exists():
            self._dir.parent.mkdir(parents=True, exist_ok=True)
            self._git("clone", bug.github_url, str(self._dir))
        self._git("fetch", "--all", "--quiet", cwd=self._dir)
        self._git("checkout", "--quiet", commit, cwd=self._dir)
        if ref == "buggy" and bug.test_file:
            # Overlay the failing test from the fixed commit (BugsInPy semantics).
            self._git("checkout", "--quiet", bug.fixed_commit_id, "--", bug.test_file, cwd=self._dir)
        return self._dir
