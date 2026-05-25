# Progress Summary: Day 4 to Day 10

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

## Day 10: Intent-Aware Query Optimizer for RAG Systems

Extended Day 9 cost-aware strategy selection into a more explicit database-style query optimizer for RAG execution planning.

The main goal was to move from a fixed RAG pipeline toward a system that can choose different execution plans according to query intent, expected quality, estimated cost, and risk.

Initial idea:

```text
query
→ candidate plans
→ predicted quality
→ estimated cost
→ utility calculation
→ selected plan
```

Candidate execution plans:

- `Direct Retrieval`
- `Hybrid Retrieval`
- `Hybrid + Rerank`
- `SQL Query`
- `Abstain`

The optimizer uses a utility function:

```text
utility = predicted_quality - lambda_cost * estimated_cost
```

where `lambda_cost` controls how strongly the optimizer penalizes expensive plans.

### Main development stages

#### 1. Static optimizer skeleton

The first version used fixed quality and cost values for each plan.

This version showed the basic database optimizer analogy:

```text
Database:
SQL query
→ optimizer
→ physical execution plan
→ result

RAG:
user query
→ RAG optimizer
→ retrieval / reranking / SQL / abstention plan
→ answer
```

Limitation:

The optimizer could only choose among already-defined plan scores and did not analyze the user query.

---

#### 2. Query-aware optimizer

The second version added query feature estimation.

Features:

- `difficulty`
- `evidence_strength`
- `ranking_ambiguity`

This allowed the optimizer to assign different expected qualities to different plans depending on query type.

Example:

- simple fact lookup → lower difficulty
- comparison query → higher difficulty and higher ranking ambiguity
- structured/numerical query → stronger structured signal

Limitation:

The query analysis was still mostly keyword-based and could confuse different meanings of similar words.

---

#### 3. Vocabulary-aware and structured-aware optimizer

A domain vocabulary was added:

- retrieval terms
- evaluation terms
- optimization terms
- risk terms
- structured query terms

This allowed the system to detect whether a query was likely about retrieval, evaluation metrics, optimization strategy, failure/risk, or structured aggregation.

A new `SQL Query` plan was added for structured analytical questions such as:

```text
Which product had the highest sales increase compared with the previous quarter?
```

This was an important step because such queries should not be treated as ordinary text retrieval problems. They are closer to SQL-style aggregation and ranking.

---

#### 4. Risk separation

A major issue appeared:

```text
Why can reranking fail when relevant documents are missed by first-stage retrieval?
```

The early optimizer treated words such as `fail` and `missed` as answer risk and selected `Abstain`.

This was incorrect because the query was asking for an explanation of a failure mechanism, not asking the system to answer without evidence.

The risk signal was split into:

```text
content_failure_signal
answer_risk_signal
```

Meaning:

- `content_failure_signal`: the query discusses failure, hallucination, or missed retrieval as a topic.
- `answer_risk_signal`: the query itself may be unsupported, uncertain, or risky to answer.

Result:

Failure explanation questions no longer triggered abstention.

---

#### 5. Intent layer

The optimizer was upgraded from keyword-aware to intent-aware.

Detected intents:

- `fact_lookup`
- `comparison`
- `failure_explanation`
- `counting`
- `structured_aggregation`
- `strategy_reasoning`

This solved several important issues.

Examples:

| Query | Desired Intent | Desired Plan |
|---|---|---|
| What does BM25 rely on? | `fact_lookup` | `Direct Retrieval` |
| Compare BM25 and dense retrieval under low lexical overlap. | `comparison` | `Hybrid + Rerank` |
| Why can reranking fail when relevant documents are missed? | `failure_explanation` | `Hybrid + Rerank` |
| How many documents have unsupported answers? | `counting` | `SQL Query` |
| Average nDCG across all test queries | `structured_aggregation` | `SQL Query` |
| Which strategy should be used when evidence is weak and ranking ambiguity is high? | `strategy_reasoning` | `Hybrid + Rerank` |

---

#### 6. Counting and aggregation generalization

The first counting detector only recognized:

```text
how many
```

This was too narrow.

It was expanded to recognize patterns such as:

- `number of`
- `count of`
- `total number`
- `frequency of`
- `occurrences of`
- `count(`

Aggregation detection was also expanded to include:

- `average`
- `mean`
- `sum`
- `total`
- `maximum`
- `minimum`
- `highest`
- `lowest`
- `top`
- `rank`
- `sort`

This made the optimizer more general for structured analytical queries.

---

#### 7. Strategy reasoning correction

Another misclassification appeared:

```text
Which strategy should be used when evidence is weak and ranking ambiguity is high?
```

The query was initially classified as `structured_aggregation` and routed to `SQL Query`.

This was wrong because the query is asking about optimizer policy, not database aggregation.

A new `strategy_reasoning` intent was added using terms such as:

- `strategy`
- `should`
- `when`
- `choose`
- `decision`
- `optimizer`
- `policy`

Result:

Strategy reasoning questions were correctly routed to `Hybrid + Rerank`.

---

#### 8. Plan calibration

Several calibration problems appeared during testing:

1. `Hybrid Retrieval` dominated simple fact queries.
2. `Hybrid + Rerank` often reached quality `1.0`.
3. `SQL Query` was sometimes over-selected.
4. `Abstain` was too strong when the query merely discussed risk.

Calibration changes:

- Added a fact lookup bias favoring `Direct Retrieval`.
- Penalized unnecessary complex plans for simple fact queries.
- Reduced the evidence bonus for `Hybrid + Rerank`.
- Penalized `Hybrid + Rerank` on structured queries.
- Reduced SQL base quality to avoid uncontrolled SQL dominance.
- Penalized SQL for non-structured reasoning intents.
- Penalized abstention for explanation, counting, aggregation, and strategy reasoning intents.

---

### Final behavior

The final optimizer behaved as expected on the test queries:

| Query Type | Example | Selected Plan |
|---|---|---|
| Fact lookup | What does BM25 rely on? | `Direct Retrieval` |
| Comparison | Compare BM25 and dense retrieval under low lexical overlap. | `Hybrid + Rerank` |
| Failure explanation | Why can reranking fail when relevant documents are missed? | `Hybrid + Rerank` |
| Strategy reasoning | Which strategy should be used when evidence is weak and ranking ambiguity is high? | `Hybrid + Rerank` |
| Structured aggregation | Which product had the highest sales increase compared with the previous quarter? | `SQL Query` |
| Counting | How many documents have unsupported answers? | `SQL Query` |
| Metric aggregation | Average nDCG across all test queries | `SQL Query` |
| Ranking over records | Top 3 strategies by utility | `SQL Query` |

Key learning outcome:

Day 10 showed that RAG execution can be framed as a query optimization problem. A RAG system should not always execute the same retrieval and generation pipeline. Instead, it can analyze query intent, estimate quality and cost for candidate plans, and select the best execution strategy.

Important user insight during the experiment:

The current rule-based optimizer is still only a blueprint. A more realistic system should first parse the user query, understand the information need, estimate quality and cost based on corpus/database statistics, and then choose among retrieval, reranking, SQL, or abstention. Cost estimation could later be connected to SQL optimizer estimates, document scan cost, corpus size, candidate count, reranker cost, and LLM token cost.

Remaining limitation:

The final Day 10 optimizer is still heuristic. Quality and cost are manually estimated. The next step should not be adding more rules, but introducing a feedback loop.

Proposed Day 11 direction:

```text
Self-Calibrating Query Optimizer:
query
→ predicted plan quality
→ execute selected plan
→ observe actual quality
→ log prediction error
→ update quality/cost estimates
```

This would move the project from a rule-based optimizer toward a feedback-aware and eventually learned optimizer.

---

## Current Research Direction

The current direction is diagnosis-driven, adaptive, cost-aware, and intent-aware optimization for multi-stage RAG retrieval pipelines.

The project is moving from basic retrieval evaluation toward RAG system optimization, where direct retrieval, hybrid retrieval, re-ranking, SQL-style structured querying, evidence selection, generation, verification, and abstention can be treated as alternative execution strategies.

A possible long-term research framing is:

```text
RAG as adaptive query processing:
query diagnosis
→ intent detection
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
Reliable RAG requires not only better retrieval and generation, but also a query optimizer that decides which execution plan is worth using under intent, cost, evidence, and risk constraints.
```
