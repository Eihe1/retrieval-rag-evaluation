# Progress Summary: Day 4 to Day 9

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

## Day 9: Cost-Aware RAG Query Optimizer

Extended Day 8 adaptive routing into a cost-aware RAG query optimizer.

Instead of selecting a strategy only from query type, the Day 9 system treats RAG strategies as alternative execution plans and chooses the plan with the highest estimated utility.

Implemented strategy candidates:

- `baseline_rag`
- `evidence_first_rag`
- `reranking_rag`
- `abstention_rag`

Implemented optimizer signals:

- `evidence_strength`
- `ranking_ambiguity`
- `query_difficulty`
- `estimated_cost`
- `hallucination_risk`
- `utility`

The optimizer uses the following general decision principle:

```text
utility = estimated_quality - cost_penalty - risk_penalty
```

Implemented cost-aware strategy behavior:

| Query Condition | Preferred Strategy |
|---|---|
| Simple query, sufficient evidence, low ranking ambiguity | `baseline_rag` |
| Strong evidence but slightly more complex query | `evidence_first_rag` |
| High ranking ambiguity and sufficient evidence | `reranking_rag` |
| Weak evidence or unsupported query | `abstention_rag` |

Current main results:

| Query | Difficulty | Evidence Strength | Ranking Ambiguity | Chosen Strategy | Quality Score |
|---|---|---:|---:|---|---:|
| What does BM25 rely on? | easy | 0.340 | 0.000 | `baseline_rag` | 1.0 |
| Why is cross-encoder reranking expensive? | easy | 0.567 | 0.000 | `baseline_rag` | 1.0 |
| What should RAG systems evaluate? | easy | 0.660 | 0.000 | `baseline_rag` | 1.0 |
| How does abstention help RAG reliability? | medium | 0.167 | 1.000 | `abstention_rag` | 0.2 |
| How is Adaptive RAG related to query optimization? | easy | 0.337 | 0.375 | `baseline_rag` | 1.0 |
| Which method improves ranking after retrieval when candidate documents are ambiguous? | medium | 0.664 | 0.091 | `evidence_first_rag` | 1.0 |
| What is the best GPU for training huge models? | medium | 0.200 | 0.444 | `abstention_rag` | 1.0 |

Key observations:

- `baseline_rag` was selected for simple queries with clear evidence and low ranking ambiguity, showing that cheap execution plans should still be preferred when sufficient.
- `evidence_first_rag` was selected for a stronger but more complex evidence case, where additional evidence filtering was useful without requiring expensive reranking.
- `abstention_rag` was selected for weak or unsupported evidence, reducing hallucination risk.
- `reranking_rag` was not selected in the current run because the toy corpus did not produce a true ranking ambiguity case. This is acceptable because expensive reranking should only be used when cheaper strategies are insufficient.

Failure case:

The query `How does abstention help RAG reliability?` was over-abstained even though the corpus contained a relevant document. This happened because the simple lexical retriever underestimated evidence strength due to weak term overlap between the query and the relevant document. This failure can be classified as:

```text
over-conservative abstention caused by weak lexical retrieval
```

Key learning outcome:

Day 9 reframed adaptive RAG as a cost-aware query optimization problem. A reliable RAG system should not always choose the strongest or most complex strategy. It should estimate evidence strength, ranking ambiguity, cost, and hallucination risk, then choose the lowest-cost strategy that is reliable enough for the current query.

---

## Current Research Direction

The current direction is diagnosis-driven, adaptive, and cost-aware optimization for multi-stage RAG retrieval pipelines.

The project is moving from basic retrieval evaluation toward RAG system optimization, where retrieval, re-ranking, evidence selection, generation, verification, and abstention can be treated as alternative execution strategies.

A possible long-term research framing is:

```text
RAG as adaptive query processing:
query diagnosis
→ retrieval confidence estimation
→ ranking ambiguity estimation
→ cost and risk estimation
→ strategy optimization
→ evidence-aware generation or abstention
→ failure-aware evaluation
```

This connects retrieval-augmented generation with database-style query optimization and execution planning.

The current research insight is:

```text
Reliable RAG requires not only better retrieval and generation, but also a query optimizer that decides which strategy is worth using under cost, evidence, and risk constraints.
```
