"""Graph-guided tools (Graphify query/path/explain + a minimal source read).

These are the agent's ONLY way to pull code context. They read from
``graph.json`` and return the smallest evidence slice — incident edges, or a
single function's source span (via the node's line range) — instead of whole
files. That focused retrieval is the mechanism behind the token saving.
"""

from __future__ import annotations

import json
from pathlib import Path


class GraphTools:
    """Focused-retrieval toolbox backed by ``graph.json`` and the repo.

    Args:
        graph_json: Path to ``artifacts/graph.json``.
        repo_root: Path to the checked-out target repo (for source spans).
    """

    def __init__(self, graph_json: Path, repo_root: Path) -> None:
        data = json.loads(Path(graph_json).read_text(encoding="utf-8"))
        self._nodes = {n["id"]: n for n in data["nodes"]}
        self._edges = data["edges"]
        self._repo = Path(repo_root)
        self._files: set[str] = set()
        self.units_read = 0

    @property
    def files_read(self) -> int:
        """Count of distinct source files opened (for the benchmark)."""
        return len(self._files)

    def query(self, label: str | None = None, name_contains: str | None = None) -> list[dict]:
        """Find edges by label and/or endpoint name (the ``query`` command)."""
        out = []
        for e in self._edges:
            if label and e["label"] != label:
                continue
            if name_contains and name_contains not in e["source"] and name_contains not in e["target"]:
                continue
            out.append(e)
        return out

    def neighbors(self, node_id: str) -> list[dict]:
        """Return edges incident to ``node_id`` (in or out)."""
        return [e for e in self._edges if e["source"] == node_id or e["target"] == node_id]

    def explain(self, node_id: str) -> str:
        """Summarize a node and its incident edges (replaces reading the file)."""
        self.units_read += 1
        node = self._nodes.get(node_id, {})
        lines = [f"{node.get('label', node_id)} ({node.get('type')}) @ {node.get('source_file')}"]
        for e in self.neighbors(node_id):
            arrow = "->" if e["source"] == node_id else "<-"
            other = e["target"] if e["source"] == node_id else e["source"]
            lines.append(f"  {arrow} {e['label']} {other} ({e['evidence']} {e['confidence']})")
        return "\n".join(lines)

    def read_source_span(self, node_id: str) -> str:
        """Read ONLY the source lines for one node (SRC validation step)."""
        node = self._nodes.get(node_id)
        if not node:
            return ""
        self.units_read += 1
        self._files.add(node["source_file"])
        text = (self._repo / node["source_file"]).read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        start = max(node.get("line", 1) - 1, 0)
        end = node.get("end_line") or len(lines)
        return "\n".join(lines[start:end])
