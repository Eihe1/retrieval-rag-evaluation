# Retrieval and RAG Evaluation Portfolio

This repository documents a research-oriented learning project on retrieval systems, retrieval evaluation, re-ranking, RAG evaluation, failure analysis, adaptive RAG strategy routing, and cost-aware RAG query optimization.

The project is organized as a multi-day portfolio. It starts from basic retrieval methods, then moves to retrieval evaluation and re-ranking, extends to answer-level RAG evaluation and failure analysis, introduces adaptive query-level strategy selection, and finally frames RAG strategy selection as a cost-aware query optimization problem.

---

## Repository Structure

```text
retrieval-rag-evaluation/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── day4_retrieval_basics/
│   ├── README.md
│   ├── src/
│   └── notes/
│
├── day5_retrieval_eval_reranking/
│   ├── README.md
│   ├── src/
│   ├── results/
│   └── notes/
│
├── day6_rag_eval/
│   ├── README.md
│   ├── src/
│   ├── results/
│   └── notes/
│
├── day7_rag_diagnosis/
│   ├── README.md
│   ├── src/
│   │   └── day7_rag_diagnosis_demo.py
│   ├── results/
│   │   ├── baseline_results.csv
│   │   ├── evidence_first_results.csv
│   │   ├── abstention_results.csv
│   │   ├── diagnosis_summary.md
│   │   ├── baseline_query_diagnosis.md
│   │   ├── evidence_first_query_diagnosis.md
│   │   └── abstention_query_diagnosis.md
│   └── notes/
│       └── day7_rag_diagnosis_notes.md
│
├── day8_adaptive_rag/
│   ├── README.md
│   ├── src/
│   │   └── adaptive_rag_demo.py
│   ├── results/
│   │   ├── adaptive_rag_results.csv
│   │   ├── strategy_comparison_results.csv
│   │   └── failure_type_summary.csv
│   └── notes/
│       └── day8_adaptive_rag_notes.md
│
└── day9_cost_aware_rag/
    ├── README.md
    ├── src/
    │   └── cost_aware_rag_demo.py
    ├── results/
    │   ├── cost_aware_rag_results.csv
    │   └── strategy_decision_log.csv
    └── notes/
        └── day9_cost_aware_rag_notes.md
```

---

## Day 4 - Retrieval Basics

Day 4 focuses on basic retrieval methods and simple RAG-style context construction.

Topics:

- BM25 sparse retrieval
- Dense retrieval with sentence-transformers
- Hybrid retrieval
- Stopword handling
- Dynamic alpha intuition
- Basic RAG context construction
- top_k trade-off

Main idea:

BM25 works well for exact keyword matching, while dense retrieval can capture semantic similarity. Hybrid retrieval combines sparse and dense signals. The top_k parameter controls the trade-off between recall and context noise.

Folder:

```text
day4_retrieval_basics/
```

---

## Day 5 - Retrieval Evaluation and Re-ranking

Day 5 focuses on evaluating retrieval quality and improving ranking with a second-stage re-ranker.

Topics:

- Recall@k
- Precision@k
- MRR
- nDCG@k
- BM25 vs Dense Retrieval vs Hybrid Retrieval
- Alpha sensitivity analysis
- Cross-Encoder re-ranking
- Re-ranking failure case

Main idea:

Retrieval systems should not only be judged by whether they retrieve relevant documents, but also by how highly they rank those documents. Re-ranking can improve ranking quality, but it cannot recover relevant documents that were missed by the first-stage retriever.

Folder:

```text
day5_retrieval_eval_reranking/
```

---

## Day 6 - RAG Evaluation and Failure Analysis

Day 6 extends retrieval evaluation into full RAG evaluation.

Topics:

- Answer keyword score
- Faithfulness
- Citation relevance
- Failure type classification
- Top-k sensitivity analysis
- Hallucination simulation

Main idea:

Retrieval success does not guarantee answer success. Even if the retriever finds the correct document, the answer generator may still select the wrong context, produce an incomplete answer, or hallucinate unsupported information.

Folder:

```text
day6_rag_eval/
```

---

## Day 7 - RAG Diagnosis and Strategy Trade-off Analysis

Day 7 focuses on moving from metric-based RAG evaluation to diagnosis-driven improvement.

Topics:

- Baseline RAG
- Evidence-First RAG
- Abstention RAG
- Faithfulness
- Citation relevance
- Hallucination or unfaithful answer
- Citation failure
- Ranking or context selection failure
- Unsupported answer
- Correct abstention
- Over-conservative abstention
- Strategy trade-off analysis

Main idea:

Retrieval success does not guarantee answer success. A RAG system may retrieve the correct document but still fail due to weak grounding, wrong evidence selection, incorrect citation, or unsupported generation.

Different strategies optimize different objectives. Baseline RAG has higher coverage, evidence-first RAG improves faithfulness, and abstention RAG reduces unsupported answers but may become over-conservative.

Reliable RAG systems should diagnose the query-level failure mode before choosing whether to answer directly, select evidence first, verify citations, rewrite the query, re-rank documents, or abstain.

Folder:

```text
day7_rag_diagnosis/
```

---

## Day 8 - Adaptive RAG with Query-Level Strategy Routing

Day 8 extends Day 7 by introducing an adaptive RAG pipeline.

Instead of applying one fixed strategy to all queries, the system first diagnoses the query type and then selects a suitable response strategy.

Pipeline:

```text
query
→ BM25 retrieval
→ query diagnosis
→ strategy routing
→ answer generation or abstention
→ evaluation
```

Topics:

- Query diagnosis
- Strategy routing
- Direct factual queries
- Evidence-sensitive queries
- Ambiguous queries
- Unsupported queries
- Adaptive RAG
- Failure-aware evaluation
- Database-style query optimizer analogy

Implemented query types:

| Query Type | Meaning |
|---|---|
| `direct_fact` | Simple factual query |
| `evidence_sensitive` | Query requiring explanation or stronger support |
| `comparison` | Query comparing concepts or methods |
| `ambiguous` | Query without clear criteria |
| `unsupported` | Query with no relevant support in the corpus |

Implemented strategy routing:

| Query Type | Selected Strategy |
|---|---|
| `direct_fact` | Baseline RAG |
| `evidence_sensitive` | Evidence-First RAG |
| `comparison` | Evidence-First RAG |
| `ambiguous` | Abstention RAG |
| `unsupported` | Abstention RAG |

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

Main idea:

Adaptive RAG improves reliability by selecting different strategies for different query types. It answers supported factual queries, uses stronger evidence grounding for explanation-style queries, and abstains from ambiguous or unsupported queries.

This can be interpreted as a simple query optimizer for RAG. Similar to how a database optimizer chooses between scan, join, and index plans, an adaptive RAG system can choose between baseline answering, evidence-first answering, and abstention.

Folder:

```text
day8_adaptive_rag/
```

---

## Day 9 - Cost-Aware RAG Query Optimizer

Day 9 extends adaptive strategy routing into a cost-aware RAG query optimizer.

Instead of choosing a strategy only from query type, the system treats different RAG strategies as alternative execution plans and selects the plan with the highest estimated utility.

Pipeline:

```text
query
→ retrieval
→ evidence strength estimation
→ ranking ambiguity estimation
→ query difficulty estimation
→ utility estimation for candidate strategies
→ cost-aware strategy selection
→ answer generation or abstention
→ evaluation
```

Topics:

- Cost-aware RAG strategy selection
- Evidence strength estimation
- Ranking ambiguity estimation
- Query difficulty estimation
- Utility-based strategy optimization
- Execution cost
- Hallucination risk
- Baseline RAG as a low-cost plan
- Evidence-first RAG as a moderate-cost plan
- Reranking RAG as a high-cost plan for ambiguous rankings
- Abstention RAG as a low-risk plan for weak evidence
- Database query optimizer analogy

Implemented strategies:

| Strategy | Role |
|---|---|
| `baseline_rag` | Cheapest plan for simple queries with clear evidence |
| `evidence_first_rag` | Moderate-cost plan for strong but slightly more complex evidence |
| `reranking_rag` | Higher-cost plan for ambiguous candidate rankings |
| `abstention_rag` | Conservative plan for weak or unsupported evidence |

Implemented optimizer signals:

| Signal | Meaning |
|---|---|
| `evidence_strength` | Estimated strength of the retrieved evidence |
| `ranking_ambiguity` | Estimated uncertainty between top candidate documents |
| `query_difficulty` | Rough difficulty category of the query |
| `estimated_cost` | Approximate execution cost of a strategy |
| `hallucination_risk` | Estimated risk of unsupported generation |
| `utility` | Final score used for strategy selection |

Main utility rule:

```text
utility = estimated_quality - cost_penalty - risk_penalty
```

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

Main idea:

A reliable RAG system should not always choose the strongest or most expensive strategy. It should choose the lowest-cost strategy that is reliable enough for the current query.

Day 9 shows that:

- Simple and clear queries should use `baseline_rag`.
- Strong but slightly more complex evidence can use `evidence_first_rag`.
- Weak or unsupported evidence should use `abstention_rag`.
- Reranking should only be used when ranking ambiguity is high enough to justify the extra cost.

The current run did not select `reranking_rag` because the toy corpus did not create a true ranking ambiguity case. This is consistent with cost-aware optimization: expensive reranking should be avoided when cheaper strategies already produce correct answers.

Folder:

```text
day9_cost_aware_rag/
```

---

## Learning Path

```text
Day 4: Build retrieval methods
Day 5: Evaluate and improve retrieval ranking
Day 6: Evaluate RAG answers and analyze failures
Day 7: Diagnose RAG failures and compare response strategies
Day 8: Route queries adaptively to suitable RAG strategies
Day 9: Optimize RAG strategy selection using cost, evidence, and risk signals
```

The project follows this progression:

```text
BM25 / Dense / Hybrid Retrieval
        ↓
Retrieval Metrics and Re-ranking
        ↓
RAG Answer Evaluation and Failure Analysis
        ↓
Diagnosis-Driven RAG Strategy Comparison
        ↓
Adaptive RAG Strategy Routing
        ↓
Cost-Aware RAG Query Optimization
```

---

## Key Insight

The central finding of this project is:

```text
Retrieval success does not guarantee answer success.
```

A reliable RAG system must satisfy all of the following:

1. Retrieve the correct evidence
2. Rank useful evidence highly
3. Select the correct context
4. Generate a correct answer
5. Ensure that the answer is faithful to the retrieved documents
6. Decide when not to answer
7. Select an appropriate strategy based on query type and evidence risk
8. Estimate the cost and risk of alternative RAG execution plans
9. Choose the lowest-cost strategy that is reliable enough for the current query

Therefore, RAG evaluation should include both retrieval-level and answer-level evaluation, and reliable RAG systems should include query-level diagnosis, adaptive strategy routing, and cost-aware strategy optimization.

---

## Main Techniques Covered

| Area | Techniques |
|---|---|
| Sparse retrieval | BM25 |
| Dense retrieval | Sentence embeddings, cosine similarity |
| Hybrid retrieval | BM25 + dense score fusion |
| Retrieval evaluation | Recall@k, Precision@k, MRR, nDCG@k |
| Re-ranking | Cross-Encoder re-ranking, reranking failure analysis |
| RAG evaluation | Answer correctness, faithfulness, citation relevance |
| Failure analysis | Retrieval failure, generation failure, context selection failure, hallucination, unsupported answer, over-conservative abstention |
| Strategy comparison | Baseline RAG, Evidence-First RAG, Abstention RAG |
| Adaptive RAG | Query diagnosis, strategy routing, selective abstention |
| Cost-aware RAG | Evidence strength, ranking ambiguity, query difficulty, cost estimation, hallucination risk, utility-based strategy selection |
| Database systems connection | Query optimizer analogy, strategy selection as execution planning, cost-aware plan selection |

---

## Research Direction

This repository is moving toward a research direction on diagnosis-driven, adaptive, and cost-aware optimization for multi-stage RAG systems.

The current research framing is:

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

From a database systems perspective, retrieval, re-ranking, evidence selection, generation, verification, and abstention can be treated as alternative execution strategies.

A future system could choose among these strategies based on query type, evidence availability, ranking ambiguity, confidence, cost, and risk.

The current research insight is:

```text
Reliable RAG requires not only better retrieval and generation, but also a query optimizer that decides which strategy is worth using under cost, evidence, and risk constraints.
```

---

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

Some scripts use sentence-transformers models and may download model files on first run.

---

## Notes

This repository is intended as a research preparation portfolio. The experiments are intentionally small and interpretable so that each retrieval and RAG evaluation concept can be inspected directly.

The Day 8 Adaptive RAG result should be interpreted as a proof-of-concept demonstration rather than a general benchmark result. The corpus is small, the router is rule-based, and the evaluation is simplified. The value of the experiment is to demonstrate the system design principle of query-level routing and failure-aware strategy selection.

The Day 9 Cost-Aware RAG result should also be interpreted as a proof-of-concept demonstration. The corpus is small, the retriever is lexical and simplified, the utility model is manually designed, and the cost/risk estimates are heuristic. The value of the experiment is to show how RAG strategy selection can be framed as a database-style query optimization problem.
