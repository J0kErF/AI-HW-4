# PRD — Graphify mechanism (code-knowledge graph + Obsidian vault)

> Version **1.00** · Implements the Graphify concept taught in L07 and detailed
> in *"How to read, interpret and infer from a Graphify graph"*.

## 1. Description & theoretical background

Graphify is a **knowledge layer**, not a "picture of code". It turns a pile of
files into a navigable graph where **Node = an entity** (function, class, PRD
doc, TODO/NOTE) and **Edge = a *claim* about a relation**. Reading shifts from
"where does this word appear?" (search / RAG vector distance ≈ topic similarity)
to "what depends on what?" (associative structure). We reimplement it so the
deterministic backbone is **token-free** and the `graph.json` schema is ours.

### Three evidence layers (they converge into one graph)
1. **Code Structure (deterministic, 0 tokens):** AST walk → imports, calls,
   class defs, inheritance → **EXTRACTED** edges.
2. **Semantic (LLM, bounded):** relations, rationale, conceptual similarity →
   **INFERRED** / **AMBIGUOUS** edges. Capped by `semantic_max_nodes`.
3. **Media (out of scope here):** audio/video transcription — not needed for a
   code-only target; noted for completeness/extensibility.

### Edge evidence scale (drives conclusion language)
| Evidence | Meaning | Confidence band | Rule |
|----------|---------|-----------------|------|
| EXTRACTED | direct from source (import/call) | ~0.85–0.95 | strong; still check label/direction |
| INFERRED | semantic hypothesis | ~0.65–0.85 | validate against `source_file` |
| AMBIGUOUS | uncertain | <0.65 | stop & manual check; hedge the claim |

## 2. Requirements & I/O

**Input:** `scan_root` (cloned repo), include/exclude globs, gatekeeper, model.
**Output (Graphify "Exports"):**
- `artifacts/graph.json` — `{version, nodes[], edges[]}`
- `artifacts/GRAPH_REPORT.md` — narrative: communities, hubs, bridges, gaps
- `artifacts/graph.html` — visual (optional, for screenshots)
- `obsidian/wiki/` — the vault: `index.md`, `hot.md`, one note per node

### `graph.json` node/edge schema
```json
{
  "version": "1.00",
  "nodes": [{"id": "...", "type": "function", "label": "...", "source_file": "...", "community": 3}],
  "edges": [{"source": "...", "target": "...", "label": "calls",
             "evidence": "extracted", "confidence": 0.92, "source_file": "..."}]
}
```

### Vault contract
- **`index.md`** — Portfolio entry page (Macro view): system structure +
  main navigation paths; links to community hub notes via `[[wikilinks]]`.
- **`hot.md`** — focused context for the bug-critical region (Meso/Micro):
  built from centrality + the suspect community; the agent's cheap entry point.
- **per-node note** — title (the most important line — the "skill" heading),
  source path, incident edges as `[[links]]` with evidence + confidence.

## 3. Graph-theory signals (Centrality & Communities)
- **Degree / betweenness centrality** → hubs and **God-nodes/bottlenecks**
  (all paths through one node = architectural risk vs. a healthy organizing hub).
- **Communities (Louvain)** = connectivity patterns that may **cross folders**;
  a community is a hypothesis, validated against labels/edges/source.
- **Bridges** → cross-community dependencies (redundancy/fallback vs duplication).
- **Isolated cluster** = a *finding, not a diagnosis* (legacy / adapter / parser
  miss / semantic-only link).

## 4. Constraints, alternatives, choice
- Geometric proximity in any layout has **no meaning**; only labels, direction,
  confidence and degree matter.
- Graphify is **not real-time**: re-run after any material change.
- *Alternative considered:* wrap an external Graphify CLI — rejected (ADR-001).

## 5. Success criteria & specific tests
- Deterministic layer reproducible byte-for-byte on a fixed fixture tree.
- Every edge has a valid `evidence` ∈ {extracted, inferred, ambiguous} and a
  `source_file`.
- Vault opens in Obsidian; `[[wikilinks]]` resolve; `hot.md` references the
  suspected-bug community.
- Unit tests: AST extraction on a tiny tree; metrics on a known graph; vault
  rendering snapshot.
