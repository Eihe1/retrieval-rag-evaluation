# Day 7: RAG Diagnosis and Improvement Loop

## 1. Motivation

In the previous days, the experiments covered retrieval methods, retrieval evaluation, re-ranking, RAG evaluation, faithfulness, citation relevance, and hallucination simulation.

Day 6 showed an important result:

```text
Retrieval success does not guarantee answer success.
```

A RAG system may retrieve the correct document, but the answer can still fail because of weak grounding, wrong citation selection, or unsupported generation.

Therefore, Day 7 focuses on diagnosis-driven improvement. The goal is not only to evaluate whether the RAG system succeeds, but also to understand why it fails and what strategy should be applied next.

## 2. From Evaluation to Diagnosis

Day 6 mainly answered:

```text
Did retrieval succeed?
Was the answer correct?
Was the answer faithful?
Was the citation relevant?
Did hallucination occur?
```

Day 7 asks a further question:

```text
Given a failure type, what should the system change?
```

This changes the focus from metric-based evaluation to diagnosis-driven optimization.

## 3. Core Idea

The core idea of Day 7 is:

```text
Different RAG failures require different optimization strategies.
```

For example:

```text
retrieval miss
→ improve retrieval or rewrite the query

low ranking
→ use re-ranking

wrong evidence selection
→ improve evidence selector

wrong citation
→ verify citation against evidence

insufficient evidence
→ abstain

over-conservative abstention
→ improve evidence sufficiency estimation
```

This motivates a more adaptive RAG pipeline instead of a fixed one.

## 4. Experimental Setup

The experiment compares three strategies:

```text
1. Baseline RAG
2. Evidence-First RAG
3. Abstention RAG
```

Each strategy is evaluated on the same set of toy RAG queries.

The experiment uses a small document collection containing topics such as:

- BM25
- Dense Retrieval
- Hybrid Retrieval
- Re-ranking
- RAG
- Faithfulness
- Citation Relevance
- Query Rewriting
- Chunking

Each query has:

```text
query_id
query
gold_docs
expected_keywords
retrieved_docs
answer
cited_doc
answer_keyword_score
faithfulness
citation_relevance
failure_type
```

## 5. Strategy 1: Baseline RAG

### 5.1 Pipeline

The baseline RAG pipeline follows:

```text
query
→ retrieve documents
→ generate answer
→ cite document
→ evaluate
```

### 5.2 Characteristics

Baseline RAG answers every query. It has high coverage because it never refuses to answer.

However, it may produce:

```text
unfaithful answers
wrong citations
unsupported answers
```

### 5.3 Result

```text
Mean answer keyword score: 0.714
Mean faithfulness: 0.714
Mean citation relevance: 0.714
Abstention rate: 0.000
```

Failure counts:

```text
success: 3
hallucination_or_unfaithful_answer: 1
citation_failure: 1
ranking_or_context_selection_failure: 1
unsupported_answer: 1
```

### 5.4 Interpretation

Baseline RAG has the highest answer keyword score among the three strategies. However, it also has multiple reliability issues.

The system answers every query, but some answers are not supported by the retrieved context, some citations are wrong, and one query is answered even though no supporting gold document exists.

Therefore, the baseline strategy has good coverage but unstable reliability.

## 6. Strategy 2: Evidence-First RAG

### 6.1 Pipeline

The evidence-first pipeline follows:

```text
query
→ retrieve documents
→ select evidence sentence
→ generate answer from selected evidence
→ cite evidence document
→ evaluate
```

### 6.2 Motivation

The goal of evidence-first RAG is to improve grounding.

Instead of allowing the answer generator to freely produce an answer from the retrieved context, the system first selects an evidence sentence. The answer is then based on this selected evidence.

### 6.3 Result

```text
Mean answer keyword score: 0.548
Mean faithfulness: 1.000
Mean citation relevance: 0.429
Abstention rate: 0.000
```

Failure counts:

```text
success: 3
ranking_or_context_selection_failure: 3
unsupported_answer: 1
```

### 6.4 Interpretation

Evidence-first RAG improves faithfulness from 0.714 to 1.000. This happens because the answers are directly grounded in retrieved evidence sentences.

However, the answer keyword score decreases from 0.714 to 0.548, and citation relevance decreases from 0.714 to 0.429.

This means that evidence-first generation improves grounding, but the current evidence selector is too simple. It relies mainly on lexical overlap, so it may select a sentence that is faithful to the retrieved context but irrelevant to the actual query.

### 6.5 Key Problem

The key problem is:

```text
faithful evidence is not always correct evidence.
```

A selected sentence may be present in the retrieved context, so the answer is faithful. However, the sentence may not answer the user's question.

This produces a failure mode where the system is faithful but still wrong.

## 7. Strategy 3: Abstention RAG

### 7.1 Pipeline

The abstention pipeline follows:

```text
query
→ retrieve documents
→ select evidence sentence
→ check evidence strength
→ answer if evidence is sufficient
→ abstain if evidence is weak
```

### 7.2 Motivation

The goal of abstention is to avoid unsupported answers.

A reliable RAG system should not always answer. If the retrieved evidence is weak or insufficient, the system should abstain rather than hallucinate.

### 7.3 Result

```text
Mean answer keyword score: 0.429
Mean faithfulness: 1.000
Mean citation relevance: 0.429
Abstention rate: 0.429
```

Failure counts:

```text
success: 3
ranking_or_context_selection_failure: 1
over_conservative_abstention: 2
correct_abstention: 1
```

### 7.4 Interpretation

The abstention strategy successfully converts the unsupported answer into a correct abstention.

This means that when no gold document exists, the system can avoid producing an unsupported answer.

However, abstention also introduces a new failure mode:

```text
over_conservative_abstention
```

This happens when the gold document is actually retrieved, but the system still refuses to answer because the evidence sufficiency check is too conservative or the evidence selector fails to identify the correct evidence.

### 7.5 Key Trade-off

The key trade-off is:

```text
higher reliability
↔
lower coverage
```

Abstention reduces unsupported generation, but it may also refuse to answer answerable queries.

## 8. Failure Types

### 8.1 success

This means the answer, retrieved context, and citation are aligned.

Example:

```text
The system retrieves the correct document, generates the correct answer, and cites the correct source.
```

### 8.2 hallucination_or_unfaithful_answer

This means the answer is not sufficiently supported by the retrieved context.

Example:

```text
Question:
What is dense retrieval?

Generated answer:
Dense retrieval is mainly based on SQL joins and B-tree indexes.
```

This answer is wrong because dense retrieval should be described using vector embeddings and semantic similarity.

### 8.3 citation_failure

This means the answer is mostly correct, but the cited document does not support the answer.

Example:

```text
Question:
Why can re-ranking fail?

Answer:
Re-ranking cannot recover documents missing from the first-stage candidate set.

Wrong citation:
doc4

Correct citation:
doc5
```

This shows that answer correctness and citation correctness are different.

### 8.4 ranking_or_context_selection_failure

This means the correct evidence may be retrieved, but it is not selected or used effectively.

Example:

```text
The gold document is in the retrieved documents,
but the answer is generated from a less relevant document.
```

This often happens when the retriever or evidence selector relies on simple lexical overlap.

### 8.5 unsupported_answer

This means the system answers even though there is no supporting gold document.

Example:

```text
Question:
How does SQL transaction rollback work in RAG?

Gold docs:
[]

Generated answer:
SQL transaction rollback in RAG is handled by vector embeddings.
```

This is dangerous because the system produces a fluent answer without evidence.

### 8.6 correct_abstention

This means the system refuses to answer when no supporting evidence exists.

Example:

```text
Gold docs:
[]

Answer:
Insufficient evidence.
```

This is the desired behavior when evidence is truly missing.

### 8.7 over_conservative_abstention

This means the system refuses to answer even though the correct document has been retrieved.

Example:

```text
Gold doc is retrieved,
but the system still outputs:
Insufficient evidence.
```

This indicates that the evidence sufficiency check is too conservative or the evidence selector fails to recognize the correct evidence.

## 9. Per-query Analysis

### q1: What does BM25 rely on?

The system succeeds across all strategies.

The correct document is retrieved, and the answer includes the key concepts:

```text
sparse retrieval
lexical term matching
exact word overlap
```

Failure type:

```text
success
```

This case shows that when retrieval, answer generation, and citation are aligned, the RAG pipeline works correctly.

---

### q2: What is dense retrieval?

In the baseline system, the correct document is retrieved and cited, but the answer is wrong:

```text
Dense retrieval is mainly based on SQL joins and B-tree indexes.
```

This answer is not supported by the retrieved context.

Failure type:

```text
hallucination_or_unfaithful_answer
```

In the evidence-first and abstention strategies, the system selects the BM25 document instead of the dense retrieval document. This produces a ranking or context selection failure.

This case shows that retrieving the correct document is not enough. The system must also select and use the correct evidence.

---

### q3: Why can re-ranking fail?

The baseline answer is mostly correct:

```text
Re-ranking improves ranking quality, but it cannot recover documents missing from the first-stage candidate set.
```

However, the cited document is wrong. The answer is supported by `doc5`, but the system cites `doc4`.

Failure type:

```text
citation_failure
```

This case shows that answer correctness and citation correctness must be evaluated separately.

In evidence-first and abstention RAG, the answer and citation are aligned, so the query succeeds.

---

### q4: What does faithfulness mean in RAG?

In the baseline system, the answer says:

```text
Faithfulness means the answer is fluent and convincing.
```

This is not the correct meaning. Faithfulness means that the generated answer is supported by the retrieved context.

Failure type:

```text
ranking_or_context_selection_failure
```

In evidence-first RAG, the system selects a general RAG definition rather than the specific faithfulness definition.

In abstention RAG, the system refuses to answer even though the gold document has been retrieved.

Failure type:

```text
over_conservative_abstention
```

This case shows that the system must distinguish between truly missing evidence and poorly selected evidence.

---

### q5: Why is citation relevance important?

The system succeeds across all strategies.

The answer correctly states that citation relevance means the cited document contains evidence for the generated answer.

Failure type:

```text
success
```

This case shows correct alignment between answer and citation.

---

### q6: How does chunking affect RAG?

In baseline RAG, the system succeeds because the answer mentions context completeness and noise, which are the key concepts for chunking.

In evidence-first RAG, the system selects a general RAG definition instead of the chunking document.

Failure type:

```text
ranking_or_context_selection_failure
```

In abstention RAG, the system refuses to answer even though the gold document has been retrieved.

Failure type:

```text
over_conservative_abstention
```

This case shows that evidence selection and evidence sufficiency estimation are both important.

---

### q7: How does SQL transaction rollback work in RAG?

This query has no gold document in the document collection.

In baseline RAG, the system still generates an answer:

```text
SQL transaction rollback in RAG is handled by vector embeddings.
```

Failure type:

```text
unsupported_answer
```

In evidence-first RAG, the system also answers using an irrelevant RAG document.

Failure type:

```text
unsupported_answer
```

In abstention RAG, the system outputs:

```text
Insufficient evidence.
```

Failure type:

```text
correct_abstention
```

This case shows that abstention can prevent unsupported answers when evidence is truly insufficient.

## 10. Comparison of the Three Strategies

| Strategy | Strength | Weakness |
|---|---|---|
| Baseline RAG | High coverage and highest answer keyword score | Can hallucinate, cite wrong sources, or answer without evidence |
| Evidence-First RAG | Highest faithfulness and better grounding | Depends heavily on evidence selection quality |
| Abstention RAG | Avoids unsupported answers | May be over-conservative and reduce coverage |

## 11. Main Insights

### Insight 1: RAG failure is not a single problem

RAG failures can come from:

```text
retrieval
ranking
context selection
evidence selection
generation
citation
evidence insufficiency
over-conservative abstention
```

Therefore, a single optimization method cannot solve all failures.

### Insight 2: Faithfulness and correctness are different

Evidence-first RAG achieves faithfulness of 1.000, but its answer keyword score is lower than baseline.

This means an answer can be faithful to retrieved context but still fail to answer the query correctly.

### Insight 3: Citation correctness must be evaluated separately

A system can generate a correct answer but cite the wrong document.

Therefore, citation relevance should be treated as an independent metric.

### Insight 4: Abstention is useful but risky

Abstention prevents unsupported answers, but it may also reject answerable queries.

The system must distinguish between:

```text
true evidence insufficiency
poor evidence selection
```

### Insight 5: RAG needs strategy selection

The experiment shows that no fixed RAG pipeline is optimal for all queries.

A reliable RAG system should diagnose the query-level risk and choose a suitable strategy.

## 12. Research Implication

This experiment motivates the following research direction:

```text
Diagnosis-driven and cost-aware optimization for multi-stage RAG retrieval pipelines.
```

The system should not blindly use the same RAG process for every query. Instead, it should behave more like a database query optimizer.

A database query optimizer chooses different execution plans based on cost and data statistics:

```text
SQL query
→ optimizer
→ choose index scan / sequential scan / join order
→ execute
```

A diagnosis-driven RAG optimizer could follow a similar idea:

```text
user query
→ diagnosis module
→ estimate retrieval quality, evidence strength, citation reliability, and cost
→ choose baseline / re-ranking / evidence-first / query rewriting / abstention
→ answer
```

## 13. Possible Future Improvements

The current experiment uses simple lexical overlap for retrieval and evidence selection. Future improvements may include:

```text
semantic evidence selection
cross-encoder evidence scoring
citation verification
query rewriting before abstention
multi-evidence aggregation
adaptive abstention threshold
cost-aware strategy selection
```

These improvements would make the system better at distinguishing between:

```text
missing evidence
retrieved but poorly ranked evidence
retrieved but poorly selected evidence
unsupported generation
over-conservative refusal
```

## 14. Final Takeaway

The main conclusion of Day 7 is:

```text
Reliable RAG requires diagnosis before optimization.
```

Baseline RAG answers more queries but can be unreliable.

Evidence-First RAG improves faithfulness but depends on evidence selection quality.

Abstention RAG avoids unsupported answers but may reduce coverage.

Therefore, a reliable RAG system should not use one fixed pipeline for all queries. It should first diagnose the likely failure mode, then choose the appropriate strategy.