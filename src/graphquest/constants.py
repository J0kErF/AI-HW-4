"""Immutable project constants (V3 §3.2, §7.3).

Only physical/mathematical constants, enum-like vocabularies and structural
defaults belong here. Anything tunable (paths, models, limits, budgets) lives
in ``config/*.json`` and is read through :class:`graphquest.shared.config.Config`.
"""

from enum import Enum


class EvidenceType(str, Enum):
    """Graphify edge evidence strength (Graphify spec — "Evidence Scale").

    Every edge is a *claim*; its evidence type governs how strongly a
    conclusion may be phrased (see docs/PRD_graphify.md and the responsible
    inference pipeline OBS->REL->CONF->CTX->SRC).
    """

    EXTRACTED = "extracted"   # direct from source (import/call) — strong, ~0.85-0.95
    INFERRED = "inferred"     # semantic hypothesis — needs validation, ~0.65-0.85
    AMBIGUOUS = "ambiguous"   # uncertain — manual-check flag, <0.65


class EdgeLabel(str, Enum):
    """Canonical relation labels emitted on graph edges."""

    CALLS = "calls"
    IMPORTS = "imports"
    IMPLEMENTS = "implements"
    INHERITS = "inherits"
    MENTIONS = "mentions"
    TESTED_BY = "tested_by"
    RATIONALE_FOR = "rationale_for"
    SEMANTICALLY_SIMILAR_TO = "semantically_similar_to"


class NodeType(str, Enum):
    """Kinds of node that can appear in the knowledge graph."""

    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    DOC = "doc"
    RATIONALE = "rationale"   # WHY / TODO / NOTE


# Graphify export filenames (Graphify spec — "Exports").
GRAPH_JSON = "graph.json"
GRAPH_HTML = "graph.html"
GRAPH_REPORT = "GRAPH_REPORT.md"
INDEX_MD = "index.md"
HOT_MD = "hot.md"

# Config service keys used by the Gatekeeper.
SERVICE_DEFAULT = "default"
SERVICE_LLM = "llm"
