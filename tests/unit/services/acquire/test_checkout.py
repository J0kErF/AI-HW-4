"""Tests for BugInfo and TargetCheckout (subprocess mocked — no network)."""

from pathlib import Path

import pytest

from graphquest.services.acquire.checkout import TargetCheckout
from graphquest.services.acquire.models import BugInfo

_TARGET = {
    "project": "cookiecutter",
    "bug_id": "2",
    "github_url": "https://github.com/cookiecutter/cookiecutter",
    "buggy_commit_id": "d7e7b28811e474e14d1bed747115e47dcdd15ba3",
    "fixed_commit_id": "90434ff4ea4477941444f1e83313beb414838535",
    "test_file": "tests/test_hooks.py",
    "test_selectors": ["tests/test_hooks.py::TestFindHooks::test_find_hook"],
    "python_version": "3.6.9",
}


def test_buginfo_from_config_and_commit_for() -> None:
    """BugInfo maps config and resolves buggy/fixed commits."""
    bug = BugInfo.from_config(_TARGET)
    assert bug.commit_for("buggy") == _TARGET["buggy_commit_id"]
    assert bug.commit_for("fixed") == _TARGET["fixed_commit_id"]
    with pytest.raises(ValueError, match="buggy.*fixed"):
        bug.commit_for("latest")


def test_checkout_clones_then_pins_commit(tmp_path: Path) -> None:
    """A fresh dir triggers clone, fetch and checkout of the buggy commit."""
    calls: list[list[str]] = []

    def fake_runner(cmd, cwd=None, check=False):  # noqa: ANN001, ANN202
        calls.append(cmd)

    bug = BugInfo.from_config(_TARGET)
    dest = tmp_path / "target_repo"
    out = TargetCheckout(dest, runner=fake_runner).checkout(bug, ref="buggy")

    assert out == dest
    assert calls[0][:2] == ["git", "clone"]
    assert bug.github_url in calls[0]
    # buggy code is checked out...
    assert any(c[:3] == ["git", "checkout", "--quiet"] and c[-1] == _TARGET["buggy_commit_id"]
               for c in calls)
    # ...and the failing test is overlaid from the fixed commit (BugsInPy semantics)
    assert calls[-1][:4] == ["git", "checkout", "--quiet", _TARGET["fixed_commit_id"]]
    assert calls[-1][-1] == _TARGET["test_file"]


def test_checkout_existing_repo_skips_clone(tmp_path: Path) -> None:
    """If .git exists, clone is skipped and only fetch+checkout run."""
    calls: list[list[str]] = []
    dest = tmp_path / "target_repo"
    (dest / ".git").mkdir(parents=True)

    TargetCheckout(dest, runner=lambda cmd, cwd=None, check=False: calls.append(cmd)).checkout(
        BugInfo.from_config(_TARGET), ref="fixed"
    )

    assert all(c[:2] != ["git", "clone"] for c in calls)
    assert calls[-1][-1] == _TARGET["fixed_commit_id"]
