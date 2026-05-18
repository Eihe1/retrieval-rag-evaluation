# Day 8 Notes: Adaptive RAG and Query-Level Strategy Selection

## 1. Learning Goal

The goal of Day 8 was to move from fixed RAG strategies to an adaptive RAG system.

Previous experiments showed that different RAG strategies have different strengths:

- Baseline RAG has good coverage but can answer unsupported queries.
- Evidence-First RAG improves grounding but still depends on evidence selection.
- Abstention RAG improves safety but can be too conservative.

Day 8 focuses on the following question:

```text
Can a RAG system diagnose the query first and then choose the most suitable response strategy?
```

The answer explored in this experiment is Adaptive RAG.

---

## 2. Background

A standard RAG pipeline usually follows this process:

```text
query
→ retrieve documents
→ generate answer from retrieved context
```

This design assumes that every query should go through the same process.

However, this assumption is weak.

Different queries require different behavior.

For example:

```text
What does BM25 rely on?
```

This is a direct factual query. A simple RAG answer is usually enough.

```text
Why can re-ranking fail?
```

This query asks for a reason. It requires stronger evidence and explanation.

```text
Which retrieval method is best?
```

This query is ambiguous. It does not define what "best" means.

```text
What is the capital of France?
```

If the corpus does not contain this information, the system should not answer from unrelated documents.

Therefore, a more reliable RAG system should not use one fixed strategy for all queries.

---

## 3. Adaptive RAG Design

The Adaptive RAG pipeline used in this experiment is:

```text
query
→ BM25 retrieval
→ query diagnosis
→ strategy routing
→ answer generation or abstention
→ evaluation
```

The two most important new components are:

1. Query diagnosis
2. Strategy routing

---

## 4. Query Diagnosis

Query diagnosis means classifying the query before deciding how to answer it.

The implemented query types are:

| Query Type | Meaning | Example |
|---|---|---|
| `direct_fact` | A simple factual query | `What does BM25 rely on?` |
| `evidence_sensitive` | A query requiring explanation or stronger support | `Why can re-ranking fail?` |
| `comparison` | A query comparing multiple methods or concepts | `Compare BM25 and dense retrieval` |
| `ambiguous` | A query without clear criteria | `Which retrieval method is best?` |
| `unsupported` | A query with no relevant support in the corpus | `What is the capital of France?` |

The diagnosis uses both query text and retrieval confidence.

For example, if the top BM25 score is zero, the query is treated as unsupported.

This is important because a query can look answerable linguistically but still be unsupported by the current corpus.

---

## 5. Strategy Routing

After diagnosis, the system chooses a strategy.

| Query Type | Strategy |
|---|---|
| `direct_fact` | Baseline RAG |
| `evidence_sensitive` | Evidence-First RAG |
| `comparison` | Evidence-First RAG |
| `ambiguous` | Abstention RAG |
| `unsupported` | Abstention RAG |

The logic is simple but important.

Simple factual questions can be answered directly.

Explanation-style questions require stronger grounding.

Ambiguous or unsupported questions should not be answered confidently.

---

## 6. Strategies

### 6.1 Baseline RAG

Baseline RAG uses the top retrieved document as the answer source.

It works well when the retrieved document is clearly relevant.

Example:

```text
Query: What does BM25 rely on?
Retrieved document: doc1
Answer: BM25 is a sparse retrieval method based on exact term matching and term frequency.
```

This is suitable for direct factual queries.

---

### 6.2 Evidence-First RAG

Evidence-First RAG first selects evidence and then generates an answer based on that evidence.

Example:

```text
Query: Why can re-ranking fail?
Retrieved document: doc4
Answer: Based on the retrieved evidence: Re-ranking improves the order of retrieved candidates but cannot recover relevant documents missed by first-stage retrieval.
```

This is suitable for queries that require explanation.

---

### 6.3 Abstention RAG

Abstention RAG refuses to answer when the query is ambiguous or unsupported.

Example:

```text
Query: Which retrieval method is best?
Answer: I do not have enough evidence to answer safely because the query is ambiguous.
```

This prevents unsupported or overconfident answers.

---

### 6.4 Adaptive RAG

Adaptive RAG does not define a new answer generation method.

Instead, it acts as a routing layer above existing strategies.

Its role is to decide:

```text
which query should be answered directly
which query should require stronger evidence
which query should be refused
```

This routing layer is the main contribution of the Day 8 experiment.

---

## 7. Evaluation Metrics

The experiment used five metrics.

### 7.1 Recall@3

Recall@3 checks whether the gold document appears in the top-3 retrieved documents.

For answerable queries, this measures retrieval success.

For ambiguous queries, Recall@3 is less informative because ambiguity is not purely a retrieval problem.

### 7.2 Answer Keyword Score

This measures whether the generated answer contains expected keywords.

For unsupported or ambiguous queries, a correct abstention receives a high score.

### 7.3 Faithfulness

Faithfulness measures whether the answer is supported by the cited document.

A faithful answer should not contain unsupported claims.

### 7.4 Citation Relevance

Citation relevance checks whether the cited document is the correct evidence source.

If the query has no gold document, citation relevance is high only when the system does not cite an irrelevant document.

### 7.5 Abstention Rate

Abstention rate measures how often the system refuses to answer.

A high abstention rate may indicate safety, but it may also indicate reduced usefulness.

---

## 8. Failure Type Analysis

In addition to aggregate metrics, each query result was assigned a failure type.

The implemented failure types are:

| Failure Type | Meaning |
|---|---|
| `success` | The system answered correctly using relevant evidence |
| `unsupported_answer` | The system answered when it should not have |
| `correct_abstention` | The system correctly refused to answer |
| `over_conservative_abstention` | The system refused to answer even though the query was answerable |
| `citation_or_context_selection_failure` | The cited document was wrong |
| `generation_failure` | The cited document was correct, but the answer was incomplete |

This is useful because aggregate scores alone do not explain what went wrong.

Failure type analysis makes the system behavior easier to diagnose.

---

## 9. Experimental Results

### 9.1 Strategy Comparison

| Mode | Recall@3 | Answer Keyword Score | Faithfulness | Citation Relevance | Abstention Rate |
|---|---:|---:|---:|---:|---:|
| Baseline-only | 0.857 | 0.857 | 1.000 | 0.857 | 0.143 |
| Evidence-only | 0.857 | 0.857 | 1.000 | 0.857 | 0.143 |
| Abstention-only | 0.857 | 0.857 | 1.000 | 0.857 | 0.429 |
| Adaptive RAG | 0.857 | 1.000 | 1.000 | 1.000 | 0.286 |

The results show that Adaptive RAG achieved the best answer keyword score and citation relevance.

It also maintained perfect faithfulness.

The abstention rate was moderate rather than too low or too high.

---

### 9.2 Failure Type Summary

| Mode | Failure Summary |
|---|---|
| Baseline-only | `success: 5`, `unsupported_answer: 1`, `correct_abstention: 1` |
| Evidence-only | `success: 5`, `unsupported_answer: 1`, `correct_abstention: 1` |
| Abstention-only | `over_conservative_abstention: 1`, `success: 4`, `correct_abstention: 2` |
| Adaptive RAG | `success: 5`, `correct_abstention: 2` |

Adaptive RAG produced no unsupported answers and no over-conservative abstentions.

This is the most important result of the experiment.

---

## 10. Adaptive Routing Decision Table

The following table shows the query-level behavior of Adaptive RAG.

| Query | Query Type | Selected Strategy | Final Outcome |
|---|---|---|---|
| What does BM25 rely on? | `direct_fact` | `baseline` | `success` |
| How does dense retrieval use embeddings? | `direct_fact` | `baseline` | `success` |
| What is hybrid retrieval? | `direct_fact` | `baseline` | `success` |
| Why can re-ranking fail? | `evidence_sensitive` | `evidence_first` | `success` |
| What does faithfulness measure? | `direct_fact` | `baseline` | `success` |
| Which retrieval method is best? | `ambiguous` | `abstention` | `correct_abstention` |
| What is the capital of France? | `unsupported` | `abstention` | `correct_abstention` |

This table shows that Adaptive RAG is not only improving aggregate scores.

It changes the system behavior at the query level.

The key behavior is:

```text
answer supported queries
require stronger evidence for explanation queries
abstain from ambiguous or unsupported queries
```

---

## 11. Per-Query Analysis for Adaptive RAG

### 11.1 Direct Factual Queries

The following queries were diagnosed as `direct_fact` and answered using Baseline RAG:

```text
What does BM25 rely on?
How does dense retrieval use embeddings?
What is hybrid retrieval?
What does faithfulness measure?
```

All of them were answered correctly.

The system retrieved the correct gold document and cited the correct source.

---

### 11.2 Evidence-Sensitive Query

The query:

```text
Why can re-ranking fail?
```

was diagnosed as `evidence_sensitive`.

The system selected Evidence-First RAG.

This is reasonable because the query asks for an explanation, not just a short factual answer.

The answer correctly stated that re-ranking cannot recover relevant documents missed by first-stage retrieval.

---

### 11.3 Ambiguous Query

The query:

```text
Which retrieval method is best?
```

was diagnosed as `ambiguous`.

The system selected Abstention RAG.

This is correct because the query does not define the criterion for "best".

Possible criteria could include:

```text
accuracy
latency
interpretability
memory cost
robustness
domain suitability
```

Without a specified criterion, giving a direct answer would be unsafe.

---

### 11.4 Unsupported Query

The query:

```text
What is the capital of France?
```

was diagnosed as `unsupported`.

The system selected Abstention RAG.

This is correct because the corpus contains no document about France or capitals.

A reliable RAG system should not answer from unrelated retrieved context.

---

## 12. Main Findings

### 12.1 Fixed RAG Strategies Are Limited

Baseline-only and Evidence-only both produced an unsupported answer.

This shows that even when retrieval returns some documents, the system should still check whether the query is appropriate and sufficiently supported.

Retrieval is not the same as evidence.

---

### 12.2 Abstention Improves Safety but Can Reduce Usefulness

Abstention-only produced one over-conservative abstention.

This shows that refusing too often can make the system less useful.

A good system needs selective abstention, not constant abstention.

---

### 12.3 Adaptive RAG Gives Better Balance

Adaptive RAG achieved:

```text
success: 5
correct_abstention: 2
```

It avoided:

```text
unsupported_answer
over_conservative_abstention
citation_or_context_selection_failure
generation_failure
```

This means it answered supported queries and refused only when refusal was appropriate.

---

## 13. Database Systems Perspective

Adaptive RAG is conceptually similar to database query optimization.

A database does not execute every query with the same plan.

Instead, it estimates query properties and chooses an execution strategy.

For example:

```text
SQL query
→ estimate selectivity and cost
→ choose index scan, sequential scan, or join plan
→ execute selected plan
```

Adaptive RAG follows a similar logic:

```text
user query
→ diagnose query type and evidence risk
→ choose baseline, evidence-first, or abstention strategy
→ execute selected RAG plan
```

This connection is important for AI + database systems research.

It suggests that RAG systems can be treated as query-processing systems rather than simple retrieval-generation pipelines.

In this view:

| Database System | Adaptive RAG |
|---|---|
| SQL query | User query |
| Query optimizer | Query diagnosis and strategy router |
| Cost/selectivity estimation | Evidence risk and retrieval confidence estimation |
| Physical execution plan | RAG response strategy |
| Query execution | Retrieval, evidence selection, generation, or abstention |

This analogy suggests that future RAG systems can be designed as adaptive optimizers over multiple possible reasoning and retrieval strategies.

---

## 14. Limitations

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

These limitations are acceptable for Day 8 because the goal was to understand the system design idea, not to build a production-level RAG system.

The result should therefore be read as a proof-of-concept demonstration rather than a general benchmark result.

---

## 15. Possible Future Improvements

A natural next step is to replace rule-based routing with learned or calibrated routing.

For example, the router could use retrieval score distribution, top-k document agreement, query intent, evidence overlap, and historical failure patterns to choose a strategy.

A more advanced version could use a routing policy such as:

```text
query features + retrieval confidence + evidence overlap
→ strategy selection
```

This would make Adaptive RAG closer to a database query optimizer.

Possible extensions include:

1. Use a larger corpus.
2. Add dense retrieval and hybrid retrieval.
3. Add re-ranking before evidence selection.
4. Use a learned query classifier.
5. Add retrieval confidence calibration.
6. Evaluate with more realistic answer-level metrics.
7. Add a cost-aware routing mechanism.
8. Treat strategy routing as an optimizer problem.

---

## 16. Research Takeaway

The main research takeaway is:

```text
Reliable RAG requires query-level control.
```

A RAG system should not always retrieve and answer.

It should first decide:

```text
Is the query answerable?
Is the query ambiguous?
Does the corpus contain enough evidence?
Does the answer require stronger grounding?
Should the system answer or abstain?
```

This moves RAG toward a more controlled, interpretable, and failure-aware system design.

---

## 17. Final Conclusion

Day 8 showed that Adaptive RAG can improve reliability by selecting different strategies for different query types.

Compared with fixed strategies, Adaptive RAG achieved a better balance between answering useful queries and avoiding unsupported answers.

The experiment supports the idea that reliable RAG systems should be:

```text
query-aware
evidence-aware
failure-aware
strategy-adaptive
```

This is an important step from basic RAG evaluation toward research-oriented RAG system design.