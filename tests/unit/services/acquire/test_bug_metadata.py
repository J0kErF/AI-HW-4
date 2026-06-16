"""Tests for the BugsInPy info parsers (pure, offline)."""

from graphquest.services.acquire.bug_metadata import parse_info, parse_test_selectors

_BUG_INFO = """\
python_version="3.6.9"
pythonpath="cookiecutter/build/lib/"
# a comment line
buggy_commit_id="d7e7b28811e474e14d1bed747115e47dcdd15ba3"
fixed_commit_id="90434ff4ea4477941444f1e83313beb414838535"
test_file="tests/test_hooks.py"
"""

_RUN_TEST = """\
tox tests/test_hooks.py::TestFindHooks::test_find_hook
tox tests/test_hooks.py::TestExternalHooks::test_run_hook
"""


def test_parse_info_unquotes_and_skips_comments() -> None:
    """key="value" lines are parsed; comments/blank lines ignored."""
    info = parse_info(_BUG_INFO)
    assert info["python_version"] == "3.6.9"
    assert info["buggy_commit_id"] == "d7e7b28811e474e14d1bed747115e47dcdd15ba3"
    assert info["test_file"] == "tests/test_hooks.py"
    assert "# a comment line" not in info


def test_parse_test_selectors_extracts_nodeids() -> None:
    """The trailing node-id token is taken from each command line."""
    sels = parse_test_selectors(_RUN_TEST)
    assert sels == [
        "tests/test_hooks.py::TestFindHooks::test_find_hook",
        "tests/test_hooks.py::TestExternalHooks::test_run_hook",
    ]
