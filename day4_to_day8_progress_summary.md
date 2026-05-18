# Progress Summary: Day 4 to Day 8

## Day 4: Retrieval Basics

Implemented BM25, dense retrieval, hybrid retrieval, and a minimal RAG pipeline.

Key learning outcome:

Retrieval methods have different strengths. BM25 relies on exact term overlap, dense retrieval captures semantic similarity, and hybrid retrieval combines sparse and dense signals.

---

## Day 5: Retrieval Evaluation and Re-ranking

Implemented Recall@k, MRR, nDCG, alpha sensitivity analysis, Cross-Encoder re-ranking, and a failure case showing that re-ranking cannot recover documents missing from first-stage retrieval.

Key learning outcome:

Retrieval quality should be evaluated not only by whether relevant documents are retrieved, but also by how highly they are ranked. Re-ranking can improve ranking quality, but only within the candidate set returned by the first-stage retriever.

---

## Day 6: RAG Evaluation

Extended retrieval evaluation to RAG answer evaluation, including answer keyword score, faithfulness, citation relevance, top-k sensitivity, and hallucination simulation.

Key learning outcome:

Retrieval success does not guarantee answer success. Even when relevant documents are retrieved, the final answer may still fail because of poor context selection, incomplete generation, weak citation grounding, or hallucination.

---

## Day 7: RAG Diagnosis and Strategy Trade-off Analysis

Extended RAG evaluation into diagnosis-driven improvement. Compared baseline RAG, evidence-first RAG, and abstention RAG.

Key learning outcome:

Different RAG strategies optimize different objectives. Baseline RAG provides higher coverage but may produce unsupported answers. Evidence-first RAG improves grounding but depends on evidence quality. Abstention RAG improves safety but may become over-conservative.

The results showed that reliable RAG requires query-level diagnosis and strategy-aware decision making.

---

## Day 8: Adaptive RAG with Query-Level Strategy Routing

Extended Day 7 strategy comparison into an adaptive RAG pipeline.

Implemented a query-level routing system that first diagnoses the query type and then selects a suitable response strategy:

```text
query
→ retrieval
→ query diagnosis
→ strategy routing
→ answer generation or abstention
→ evaluation
```

Implemented query types:

- `direct_fact`
- `evidence_sensitive`
- `comparison`
- `ambiguous`
- `unsupported`

Implemented strategy routing:

| Query Type | Selected Strategy |
|---|---|
| `direct_fact` | Baseline RAG |
| `evidence_sensitive` | Evidence-First RAG |
| `comparison` | Evidence-First RAG |
| `ambiguous` | Abstention RAG |
| `unsupported` | Abstention RAG |

Compared four modes:

- Baseline-only
- Evidence-only
- Abstention-only
- Adaptive RAG

Main results:

| Mode | Recall@3 | Answer Keyword Score | Faithfulness | Citation Relevance | Abstention Rate |
|---|---:|---:|---:|---:|---:|
| Baseline-only | 0.857 | 0.857 | 1.000 | 0.857 | 0.143 |
| Evidence-only | 0.857 | 0.857 | 1.000 | 0.857 | 0.143 |
| Abstention-only | 0.857 | 0.857 | 1.000 | 0.857 | 0.429 |
| Adaptive RAG | 0.857 | 1.000 | 1.000 | 1.000 | 0.286 |

Failure type summary:

| Mode | Failure Summary |
|---|---|
| Baseline-only | `success: 5`, `unsupported_answer: 1`, `correct_abstention: 1` |
| Evidence-only | `success: 5`, `unsupported_answer: 1`, `correct_abstention: 1` |
| Abstention-only | `success: 4`, `correct_abstention: 2`, `over_conservative_abstention: 1` |
| Adaptive RAG | `success: 5`, `correct_abstention: 2` |

Key learning outcome:

Adaptive RAG achieved a better balance between reliability and coverage. It answered supported queries correctly and abstained only when the query was ambiguous or unsupported by the corpus.

The experiment also introduced a database systems perspective: Adaptive RAG can be interpreted as a simple query optimizer for RAG. Similar to how a database optimizer chooses a physical execution plan based on query properties, an adaptive RAG system can choose a response strategy based on query type, retrieval confidence, and evidence risk.

---

## Current Research Direction

The current direction is diagnosis-driven, adaptive, and cost-aware optimization for multi-stage RAG retrieval pipelines.

The project is moving from basic retrieval evaluation toward RAG system optimization, where retrieval, re-ranking, evidence selection, generation, verification, and abstention can be treated as alternative execution strategies.

A possible long-term research framing is:

```text
RAG as adaptive query processing:
query diagnosis
→ retrieval confidence estimation
→ strategy routing
→ evidence-aware generation or abstention
→ failure-aware evaluation
```

This connects retrieval-augmented generation with database-style query optimization and execution planning.
