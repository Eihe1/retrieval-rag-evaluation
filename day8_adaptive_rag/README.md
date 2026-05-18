# Day 8: Adaptive RAG with Query-Level Strategy Routing

## 1. Overview

This experiment extends the previous RAG diagnosis experiments by introducing an adaptive RAG pipeline.

Instead of applying one fixed strategy to every query, the system first diagnoses the query type and then selects an appropriate response strategy.

The key idea is:

```text
query
→ query diagnosis
→ strategy routing
→ retrieval / evidence selection / abstention
→ answer
→ evaluation
```

This is different from a fixed RAG pipeline:

```text
query
→ retrieval
→ generation
→ answer
```

The goal of Day 8 is to show that reliable RAG systems should adapt their behavior according to query type, evidence availability, and risk level.

---

## 2. Motivation

In previous experiments, three fixed RAG strategies were tested:

| Strategy | Strength | Weakness |
|---|---|---|
| Baseline RAG | Answers supported factual queries directly | May answer ambiguous or unsupported queries too confidently |
| Evidence-First RAG | Improves evidence grounding | Still may answer ambiguous queries if retrieval returns partial evidence |
| Abstention RAG | Avoids unsupported answers | May over-abstain on answerable queries |

The limitation is that no single fixed strategy is optimal for all query types.

Some queries are simple factual questions:

```text
What does BM25 rely on?
```

Some queries require stronger evidence:

```text
Why can re-ranking fail?
```

Some queries are ambiguous:

```text
Which retrieval method is best?
```

Some queries are unsupported by the corpus:

```text
What is the capital of France?
```

A reliable RAG system should treat these cases differently.

---

## 3. Core Idea

Adaptive RAG introduces two additional steps before answer generation:

### 3.1 Query Diagnosis

The system classifies each query into one of several query types:

| Query Type | Meaning |
|---|---|
| `direct_fact` | A factual query that can usually be answered from one retrieved document |
| `evidence_sensitive` | A query that requires stronger evidence or explanation |
| `comparison` | A query that compares concepts or methods |
| `ambiguous` | A query that lacks a clear evaluation criterion |
| `unsupported` | A query for which the corpus contains no relevant support |

### 3.2 Strategy Routing

After query diagnosis, the system chooses a response strategy:

| Query Type | Selected Strategy |
|---|---|
| `direct_fact` | Baseline RAG |
| `evidence_sensitive` | Evidence-First RAG |
| `comparison` | Evidence-First RAG |
| `ambiguous` | Abstention RAG |
| `unsupported` | Abstention RAG |

This makes the system more selective and failure-aware.

---

## 4. Implemented Strategies

### 4.1 Baseline RAG

Baseline RAG directly answers using the top retrieved document.

It is useful for simple factual queries but may be unsafe for ambiguous or unsupported queries.

### 4.2 Evidence-First RAG

Evidence-First RAG first selects supporting evidence, then generates an answer based on that evidence.

It is useful for explanation-style queries where grounding matters.

### 4.3 Abstention RAG

Abstention RAG refuses to answer when the system does not have enough evidence or when the query is ambiguous.

It improves reliability but may reduce coverage if used too aggressively.

### 4.4 Adaptive RAG

Adaptive RAG selects one of the above strategies based on query type.

It aims to balance:

```text
answer coverage
faithfulness
citation relevance
abstention behavior
```

---

## 5. Dataset

The experiment uses a small toy corpus about retrieval and RAG concepts.

Example documents include:

| Document ID | Topic |
|---|---|
| `doc1` | BM25 |
| `doc2` | Dense retrieval |
| `doc3` | Hybrid retrieval |
| `doc4` | Re-ranking |
| `doc5` | RAG |
| `doc6` | Faithfulness |
| `doc7` | Abstention |
| `doc8` | Evidence-first RAG |

The query set includes both answerable and unanswerable queries.

---

## 6. Evaluation Metrics

The experiment evaluates each strategy using the following metrics:

| Metric | Meaning |
|---|---|
| `Recall@3` | Whether the gold document appears in the top-3 retrieved documents |
| `Answer Keyword Score` | Whether the answer contains expected keywords |
| `Faithfulness` | Whether the answer is supported by the cited document |
| `Citation Relevance` | Whether the cited document matches the gold document |
| `Abstention Rate` | How often the system refuses to answer |

In addition, each query is assigned a failure type.

---

## 7. Failure Types

The experiment classifies each query result into one of the following categories:

| Failure Type | Meaning |
|---|---|
| `success` | The query was answered correctly with relevant evidence |
| `unsupported_answer` | The system answered despite lacking valid support |
| `correct_abstention` | The system correctly refused to answer |
| `over_conservative_abstention` | The system refused to answer even though the query was answerable |
| `citation_or_context_selection_failure` | The system cited the wrong document |
| `generation_failure` | The system cited the correct document but produced an incomplete answer |

This allows the experiment to go beyond aggregate metrics and analyze system behavior more directly.

---

## 8. Results

### 8.1 Strategy Comparison

| Mode | Recall@3 | Answer Keyword Score | Faithfulness | Citation Relevance | Abstention Rate |
|---|---:|---:|---:|---:|---:|
| Baseline-only | 0.857 | 0.857 | 1.000 | 0.857 | 0.143 |
| Evidence-only | 0.857 | 0.857 | 1.000 | 0.857 | 0.143 |
| Abstention-only | 0.857 | 0.857 | 1.000 | 0.857 | 0.429 |
| Adaptive RAG | 0.857 | 1.000 | 1.000 | 1.000 | 0.286 |

### 8.2 Failure Type Summary

| Mode | Failure Types |
|---|---|
| Baseline-only | `success: 5`, `unsupported_answer: 1`, `correct_abstention: 1` |
| Evidence-only | `success: 5`, `unsupported_answer: 1`, `correct_abstention: 1` |
| Abstention-only | `success: 4`, `correct_abstention: 2`, `over_conservative_abstention: 1` |
| Adaptive RAG | `success: 5`, `correct_abstention: 2` |

---

## 9. Adaptive Routing Decisions

The following table shows how Adaptive RAG diagnosed each query, selected a strategy, and produced the final outcome.

| Query | Query Type | Selected Strategy | Final Outcome |
|---|---|---|---|
| What does BM25 rely on? | `direct_fact` | `baseline` | `success` |
| How does dense retrieval use embeddings? | `direct_fact` | `baseline` | `success` |
| What is hybrid retrieval? | `direct_fact` | `baseline` | `success` |
| Why can re-ranking fail? | `evidence_sensitive` | `evidence_first` | `success` |
| What does faithfulness measure? | `direct_fact` | `baseline` | `success` |
| Which retrieval method is best? | `ambiguous` | `abstention` | `correct_abstention` |
| What is the capital of France? | `unsupported` | `abstention` | `correct_abstention` |

This table shows the main value of Adaptive RAG:

```text
query diagnosis
→ strategy routing
→ failure-aware outcome
```

The system does not simply retrieve and answer. It first decides whether the query should be answered directly, answered with stronger evidence, or refused.

---

## 10. Key Observations

### 10.1 Fixed Strategies Are Not Enough

Baseline-only and Evidence-only both produced one unsupported answer.

This happened because they answered the ambiguous query:

```text
Which retrieval method is best?
```

The query has no clear evaluation criterion, but fixed strategies still attempted to answer using retrieved documents.

This shows that retrieval alone is not enough. The system also needs query-level diagnosis.

---

### 10.2 Abstention-Only Is Too Conservative

Abstention-only avoided unsupported answers, but it produced one over-conservative abstention.

This shows that always using a conservative strategy improves safety but may reduce usefulness.

A reliable system should use selective abstention rather than constant abstention.

---

### 10.3 Adaptive RAG Achieves Better Balance

Adaptive RAG produced:

```text
success: 5
correct_abstention: 2
```

It did not produce:

```text
unsupported_answer
over_conservative_abstention
citation_or_context_selection_failure
generation_failure
```

This means Adaptive RAG answered all supported queries and abstained only when the query was ambiguous or unsupported.

---

## 11. Database Systems Perspective

This experiment can be interpreted as a simple query optimizer for RAG.

In databases, a query optimizer does not execute every SQL query with the same physical plan. It estimates query properties such as selectivity, cost, and available access paths, then chooses a suitable execution strategy.

Similarly, Adaptive RAG does not answer every user query with the same RAG strategy. It first estimates the query type and evidence risk, then chooses one of several response strategies.

Database analogy:

```text
SQL query
→ optimizer estimates cost/selectivity
→ choose scan/join/index plan
→ execute plan
```

Adaptive RAG analogy:

```text
user query
→ diagnose query type and evidence risk
→ choose baseline/evidence-first/abstention strategy
→ execute RAG plan
```

This suggests that future RAG systems can be designed as adaptive query-processing systems, where retrieval, evidence selection, generation, and abstention are treated as alternative execution plans.

---

## 12. Limitations

The perfect result of Adaptive RAG in this experiment should not be interpreted as a general performance guarantee.

It is mainly used to demonstrate the design principle of query-level routing.

In real RAG systems, query diagnosis, retrieval confidence estimation, and abstention decisions are much harder.

The main limitations are:

1. The corpus is small.
2. Query diagnosis uses simple rule-based logic.
3. BM25 is the only retriever.
4. The answer generator is extractive and template-based.
5. Evaluation uses simple keyword matching.
6. Failure classification is rule-based.
7. The query set is manually designed to illustrate different failure modes.

These limitations are acceptable for this stage because the goal is not to build a production-level RAG system. The goal is to understand why adaptive strategy selection can improve reliability.

---

## 13. Future Work

A natural next step is to replace rule-based routing with learned or calibrated routing.

For example, the router could use:

```text
query features
retrieval score distribution
top-k document agreement
evidence overlap
query intent
historical failure patterns
```

to choose a strategy.

A more advanced routing policy could be:

```text
query features + retrieval confidence + evidence overlap
→ strategy selection
```

This would make the system closer to a cost-aware and risk-aware RAG optimizer.

Possible extensions include:

1. Add dense retrieval and hybrid retrieval.
2. Add cross-encoder re-ranking before evidence selection.
3. Use a learned query classifier instead of simple rules.
4. Use retrieval confidence calibration.
5. Add larger and more realistic corpora.
6. Evaluate with more realistic answer-level metrics.
7. Add cost-aware routing.
8. Treat RAG strategy selection as an optimizer problem.

---

## 14. Main Takeaway

The main takeaway from Day 8 is:

```text
Reliable RAG systems should not rely on a single fixed strategy.
Different queries require different response behaviors.
Adaptive strategy routing can improve reliability by selecting when to answer, when to require evidence, and when to abstain.
```

Adaptive RAG shifts the system from a fixed retrieval-generation pipeline to a failure-aware and query-adaptive system.

---

## 15. Files

```text
day8_adaptive_rag/
├── README.md
├── src/
│   └── adaptive_rag_demo.py
├── results/
│   ├── adaptive_rag_results.csv
│   ├── strategy_comparison_results.csv
│   └── failure_type_summary.csv
└── notes/
    └── day8_adaptive_rag_notes.md
```