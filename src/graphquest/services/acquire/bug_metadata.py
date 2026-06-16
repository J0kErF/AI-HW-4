"""Parser for the BugsInPy ``bug.info`` / ``project.info`` format.

The format is a flat list of ``key="value"`` lines. This parser is pure (no
network), so it can validate vendored metadata offline and could also ingest a
raw ``bug.info`` file fetched once during pinning. Used to cross-check that the
values pinned in ``config/setup.json`` match the upstream BugsInPy record.
"""

from __future__ import annotations


def parse_info(text: str) -> dict[str, str]:
    """Parse BugsInPy ``key="value"`` info text into a dict.

    Args:
        text: Contents of a ``bug.info`` / ``project.info`` file.

    Returns:
        Mapping of key to unquoted value; blank lines and ``#`` comments skipped.
    """
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def parse_test_selectors(run_test_sh: str) -> list[str]:
    """Extract pytest node ids from a BugsInPy ``run_test.sh``.

    Args:
        run_test_sh: Contents of ``run_test.sh`` (lines like ``tox <nodeid>``
            or ``python -m pytest <nodeid>``).

    Returns:
        The trailing node-id token from each non-empty command line.
    """
    selectors: list[str] = []
    for raw_line in run_test_sh.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        selectors.append(line.split()[-1])
    return selectors
