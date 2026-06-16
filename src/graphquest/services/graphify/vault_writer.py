"""Obsidian vault writer (Graphify spec: Exports -> ``wiki/`` + index.md/hot.md).

Turns the graph into a navigable Obsidian vault of Markdown notes linked with
``[[wikilinks]]`` (the "Wikipedia analogy"). Produces:

* ``index.md`` — the Portfolio entry page: system structure + main navigation
  paths (Macro view).
* ``hot.md``   — the focused context page for the bug-critical region, built
  from centrality + the suspected-bug community (Meso/Micro view).
* one note per node, cross-linked by its edges.

The vault is the agent's primary, token-cheap context surface.
"""

from __future__ import annotations

from pathlib import Path

from graphquest.services.graphify.metrics import GraphMetrics
from graphquest.services.graphify.models import CodeGraph


class VaultWriter:
    """Render a :class:`CodeGraph` + metrics into an Obsidian vault.

    Args:
        vault_dir: Target directory (``obsidian/wiki``).
    """

    def __init__(self, vault_dir: Path) -> None:
        self._dir = vault_dir

    def write(self, graph: CodeGraph, metrics: GraphMetrics) -> None:
        """Write ``index.md``, ``hot.md`` and per-node notes with wikilinks."""
        raise NotImplementedError("Phase 2: render notes + index.md + hot.md")
