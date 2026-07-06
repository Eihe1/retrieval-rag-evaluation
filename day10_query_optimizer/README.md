# Day 10 — Query Optimizer for RAG Systems

## Overview

Traditional RAG systems often follow a fixed execution pipeline:

```text
Query
→ Retrieval
→ Re-ranking
→ Generation
```

However, not every query requires the same retrieval or answer strategy.

Simple factual questions may only require direct retrieval. Comparison questions may benefit from hybrid retrieval and re-ranking. Structured analytical questions may be better answered using database-style aggregation rather than free-text retrieval. Unsupported or ambiguous queries may require abstention.

This project explores the idea of treating RAG execution as a lightweight query optimization problem inspired by database management systems.

The optimizer analyzes a user query, estimates the expected quality and execution cost of multiple candidate plans, computes utilities, and selects the plan with the highest utility.

The current optimizer is rule-based and heuristic. It is designed for interpretability and research preparation, not production deployment.

---

## Implementation Scope

This folder integrates earlier prototype components:

- BM25-style lexical retrieval
- Lightweight semantic-proxy retrieval
- Hybrid scoring
- Heuristic second-stage re-ranking
- RAG answer evaluation
- Failure diagnosis
- Adaptive RAG strategy routing
- Cost-aware strategy selection
- Intent-aware execution planning

The semantic retrieval component should be understood as a lightweight proxy signal rather than a production embedding-based dense retriever.

The re-ranking component should be understood as a heuristic re-ranker rather than a neural Cross-Encoder.

The SQL Query plan is a conceptual and prototype-level structured execution path for counting, aggregation, ranking, and metric-style questions. It is not a full production database-backed RAG engine.

---

## Motivation

The project was motivated by an observation made during previous RAG evaluation experiments.

Throughout Days 4–9, several retrieval and RAG strategies were implemented or studied:

- BM25-style retrieval
- Lightweight semantic-proxy retrieval
- Hybrid retrieval
- Heuristic re-ranking
- Evidence-First RAG
- Abstention RAG
- Adaptive RAG
- Cost-aware strategy selection

A key finding was that different queries often require different strategies.

---

### Simple Fact Lookup

Query:

```text
What does BM25 rely on?
```

Desired strategy:

```text
Direct Retrieval
```

Reason:

The query is simple and the evidence is direct.

---

### Comparison Query

Query:

```text
Compare BM25-style retrieval and semantic-proxy retrieval.
```

Desired strategy:

```text
Hybrid Retrieval + Re-ranking
```

Reason:

The answer may require information from multiple pieces of evidence and stronger ranking quality.

---

### Structured Query

Query:

```text
Average nDCG across all test queries.
```

Desired strategy:

```text
SQL Query
```

Reason:

The query is metric-oriented and is better handled through structured aggregation than free-text retrieval.

---

These observations suggest that RAG pipelines can benefit from database-style optimization.

---

## System Architecture

The final optimizer follows the pipeline:

```text
Query
↓
Intent Detection
↓
Feature Extraction
↓
Candidate Plan Generation
↓
Quality Prediction
↓
Cost Prediction
↓
Utility Calculation
↓
Plan Selection
```

---

## Candidate Plans

The optimizer currently supports five execution plans.

### Direct Retrieval

Single-stage retrieval without re-ranking.

Advantages:

- Lowest cost
- Fast execution
- Suitable for simple factual lookup

Disadvantages:

- Sensitive to ranking errors
- Limited reasoning support

---

### Hybrid Retrieval

Combines multiple retrieval signals.

Advantages:

- More robust than relying on one retrieval signal
- Useful when lexical and semantic-proxy signals are complementary

Disadvantages:

- Higher retrieval cost than direct retrieval
- Still limited by first-stage candidate quality

---

### Hybrid + Rerank

Hybrid retrieval followed by heuristic re-ranking.

Advantages:

- Useful for comparison, reasoning, and failure-explanation queries
- Can improve ranking quality when relevant candidates are already retrieved

Disadvantages:

- Higher execution cost
- Cannot recover relevant documents missed by first-stage retrieval
- Current version uses heuristic re-ranking, not a neural Cross-Encoder

---

### SQL Query

Database-style aggregation and analytical execution.

Advantages:

- Exact counting
- Aggregation support
- Ranking and metric-style query support

Disadvantages:

- Only suitable for structured questions
- Requires structured data or logged evaluation results

---

### Abstain

Refuses to answer when confidence or evidence is insufficient.

Advantages:

- Prevents unsupported answers
- Reduces hallucination risk

Disadvantages:

- May over-refuse answerable questions

---

## Intent Detection

One major limitation of earlier versions was heavy reliance on keyword matching.

The system was gradually upgraded to include an intent layer.

Supported intents:

### `fact_lookup`

Examples:

- What is BM25?
- What does Recall@k mean?

Preferred plan:

```text
Direct Retrieval
```

---

### `comparison`

Examples:

- Compare BM25-style retrieval and semantic-proxy retrieval.
- What is the difference between lexical and semantic-proxy retrieval?

Preferred plan:

```text
Hybrid + Rerank
```

---

### `failure_explanation`

Examples:

- Why can reranking fail?
- Why does hallucination occur?

Preferred plan:

```text
Hybrid + Rerank
```

---

### `counting`

Examples:

- How many failed queries exist?
- Number of unsupported answers.

Preferred plan:

```text
SQL Query
```

---

### `structured_aggregation`

Examples:

- Average nDCG.
- Highest score.
- Lowest failure rate.

Preferred plan:

```text
SQL Query
```

---

### `strategy_reasoning`

Examples:

- Which strategy should be used?
- When should reranking be applied?

Preferred plan:

```text
Hybrid + Rerank
```

---

## Optimizer Signals

The optimizer uses interpretable heuristic signals.

| Signal | Meaning |
|---|---|
| Query intent | The broad type of the user query |
| Query difficulty | Whether the query is simple, multi-part, or reasoning-heavy |
| Evidence strength | Whether retrieved evidence appears strong enough to support an answer |
| Ranking ambiguity | Whether top retrieved candidates are clearly separated or close in score |
| Content failure signal | Whether the query discusses failure or risk as a topic |
| Answer risk signal | Whether the answer itself is likely to be unsupported |
| Estimated quality | Predicted quality of a candidate plan |
| Estimated cost | Relative cost of a candidate plan |
| Utility | Final score used for plan selection |

---

## Utility Calculation

The simplified utility form is:

```text
utility = estimated_quality - cost_penalty - risk_penalty
```

The optimizer selects the plan with the highest utility.

This mirrors the database optimizer idea:

```text
A system should not always choose the strongest plan.
It should choose the cheapest plan that is reliable enough for the current query.
```

---

## Evolution of the Optimizer

### Version 1

Static utility model.

```text
Query
→ Utility Calculation
→ Plan Selection
```

Limitation:

No query awareness.

---

### Version 2

Query feature extraction.

Added:

- Difficulty
- Evidence strength
- Ranking ambiguity

Improvement:

Different queries produce different utilities.

---

### Version 3

Risk separation.

Original issue:

Queries discussing failure mechanisms were incorrectly classified as unsafe.

Example:

```text
Why can reranking fail?
```

Incorrect result:

```text
Abstain
```

Improvement:

Risk was separated into:

- Content failure signal
- Answer risk signal

Result:

Failure analysis questions no longer trigger abstention.

---

### Version 4

Intent-aware optimizer.

Added:

- Fact lookup
- Comparison
- Counting
- Aggregation
- Failure explanation

Improvement:

Structured questions began routing to SQL Query.

---

### Version 5

Calibrated optimizer.

Problems addressed:

- Hybrid Retrieval dominating all plans
- SQL Query over-selected
- Fact queries not choosing Direct Retrieval

Solutions:

- Added fact lookup bias
- Reduced rerank quality inflation
- Reduced SQL quality inflation
- Added strategy reasoning intent

Result:

Plan selection became more realistic and interpretable.

---

## Example Outputs

### Fact Query

Query:

```text
What does BM25 rely on?
```

Selected Plan:

```text
Direct Retrieval
```

---

### Comparison Query

Query:

```text
Compare BM25-style retrieval and semantic-proxy retrieval.
```

Selected Plan:

```text
Hybrid + Rerank
```

---

### Failure Explanation

Query:

```text
Why can reranking fail when relevant documents are missed?
```

Selected Plan:

```text
Hybrid + Rerank
```

---

### Aggregation Query

Query:

```text
Average nDCG across all test queries.
```

Selected Plan:

```text
SQL Query
```

---

### Strategy Reasoning

Query:

```text
Which strategy should be used when evidence is weak and ranking ambiguity is high?
```

Selected Plan:

```text
Hybrid + Rerank
```

---

## Lessons Learned

The most important insight from this project is:

```text
RAG execution can be viewed as a query optimization problem.
```

Instead of always executing the same retrieval pipeline, systems can estimate:

- expected quality
- expected cost
- expected risk
- expected utility

and choose the most suitable plan.

This perspective closely mirrors traditional database query optimization.

---

## Limitations

Current limitations:

- Small toy corpus
- Rule-based query planner
- Heuristic query feature extraction
- Heuristic evidence strength estimation
- Heuristic ranking ambiguity estimation
- Lightweight semantic-proxy retrieval instead of production dense retrieval
- Heuristic re-ranking instead of neural Cross-Encoder re-ranking
- Prototype SQL-style routing rather than a full database-backed RAG system
- Simplified evaluation metrics
- No learned optimizer

---

## Future Work

Current optimizer:

```text
Rule-based Query Planner
```

Future direction:

```text
Self-Calibrating Query Optimizer
```

Potential extensions:

- Execution feedback collection
- Actual quality measurement
- Prediction error analysis
- Automatic quality calibration
- Learned cost models
- Learned quality models
- Intent classification using ML models
- Embedding-based dense retrieval
- Neural Cross-Encoder or reranker model
- pgvector-backed vector retrieval
- Retrieval strategy learning

Ultimate goal:

```text
Query
↓
Learned Optimizer
↓
Execution Plan
↓
Feedback
↓
Continuous Improvement
```

This would move the prototype closer to modern database optimizers that learn from execution feedback.

---

## Summary

Day 10 builds a query-aware and intent-aware RAG optimizer prototype.

The main contribution is the framing of RAG as a query optimization problem. Different retrieval and answer strategies are treated as execution plans, and the optimizer selects among them using interpretable signals such as intent, evidence strength, ranking ambiguity, query difficulty, estimated cost, and answer risk.

The result is not a production RAG system. It is a clear and reproducible prototype for studying how RAG pipelines can diagnose failures and choose strategies more intelligently.
