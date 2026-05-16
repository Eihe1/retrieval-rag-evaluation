# Day 6 - RAG Evaluation and Failure Analysis

## 1. Goal

The goal of Day 6 was to extend retrieval evaluation into RAG evaluation.

In previous experiments, I evaluated retrieval systems using metrics such as Recall@k, MRR, and nDCG@k. These metrics measure whether the retriever can find relevant documents and rank them highly.

However, a RAG system has an additional generation stage. Even if the retriever finds the correct document, the final answer may still be incomplete, incorrect, grounded in the wrong document, or unsupported by the retrieved context.

Therefore, today's goal was to evaluate a RAG system from three perspectives:

1. Retrieval quality
2. Answer correctness
3. Faithfulness and grounding

---

## 2. RAG Evaluation Pipeline

The experiment used a small toy RAG pipeline:

```text
query
  ↓
BM25 retriever
  ↓
top-k retrieved documents
  ↓
extractive answer generator
  ↓
retrieval + answer evaluation
```

The system used:

- A toy corpus about retrieval and RAG concepts
- A BM25 retriever
- A simple extractive answer generator
- A manually defined QA evaluation dataset
- Retrieval-level and answer-level metrics

The purpose was not to build a strong RAG system, but to understand how different types of RAG errors can be evaluated and analyzed.

---

## 3. Retrieval-Level Metrics

The retrieval-level metrics were:

| Metric | Meaning |
|---|---|
| Recall@k | Whether the gold document is included in the top-k retrieved results |
| MRR | How highly the first relevant document is ranked |
| nDCG@k | Whether relevant documents are ranked near the top |

These metrics evaluate the retriever only.

They do not directly evaluate whether the final answer is correct.

For example, a system may retrieve the gold document, but the generator may still ignore it or use a different document to produce the final answer.

---

## 4. Answer-Level Metrics

The answer-level metrics were:

| Metric | Meaning |
|---|---|
| Answer keyword score | Whether the answer contains expected key information |
| Faithfulness | Whether the answer is supported by the retrieved context |
| Citation relevance | Whether the answer comes from the correct gold document |

---

## 5. Answer Keyword Score

Answer keyword score checks how many expected keywords appear in the generated answer.

For example, if the expected keywords are:

```text
sparse, exact, term, matching
```

and the generated answer contains all of them, then:

```text
answer_keyword_score = 4 / 4 = 1.0
```

This is a simple proxy for answer correctness.

It is not a perfect metric, because a correct answer may use different wording. However, it is useful for a small controlled experiment because it makes answer evaluation easy to inspect.

---

## 6. Faithfulness

Faithfulness measures whether the answer is supported by the retrieved context.

In this experiment, the faithfulness score was computed by checking whether the generated answer appeared in the retrieved documents.

If the answer appeared in the retrieved context:

```text
faithfulness = 1.0
```

Otherwise:

```text
faithfulness = 0.0
```

Because the default answer generator is extractive, most generated answers are faithful. This means they are copied from the retrieved context.

However, a faithful answer is not always correct. If the retriever provides the wrong context, the answer may be faithful to the wrong document.

---

## 7. Citation Relevance

Citation relevance checks whether the answer came from the gold document.

If the answer was generated from the correct gold document:

```text
citation_relevance = 1.0
```

Otherwise:

```text
citation_relevance = 0.0
```

This metric connects retrieval and answer generation.

It helps detect cases where the correct document was retrieved, but the generator selected another document to answer the query.

---

## 8. Main Results

The main result was:

```text
recall_at_k: 1.000
mrr: 0.929
ndcg_at_k: 0.947
answer_keyword_score: 0.690
faithfulness: 1.000
citation_relevance: 0.857
```

The retriever achieved perfect Recall@k, meaning that all gold documents were included in the top-k retrieved results.

However, the answer keyword score was only 0.690.

This shows that retrieval success does not guarantee answer success.

The system retrieved the correct documents, but the generator did not always use them correctly or produce complete answers.

---

## 9. Failure Type Analysis

I added a failure classification function to categorize each RAG result.

The failure types were:

| Failure Type | Meaning |
|---|---|
| success | The system retrieved the right document and generated a correct, faithful answer |
| retrieval_failure | The gold document was not retrieved |
| generation_failure | The gold document was retrieved and cited, but the answer was incomplete |
| citation_or_context_selection_failure | The gold document was retrieved, but the answer came from the wrong document |
| hallucination_or_unfaithful_answer | The answer was not supported by the retrieved context |
| mixed_failure | Other mixed error cases |

The failure summary was:

```text
success: count=3, ratio=0.429
citation_or_context_selection_failure: count=1, ratio=0.143
generation_failure: count=3, ratio=0.429
```

This shows that only 3 out of 7 examples were fully successful.

---

## 10. Important Failure Case

The most important failure case was:

```text
Query: Why is dense retrieval useful?
Gold docs: doc2
Retrieved docs: doc3,doc2,doc1
Answer: Hybrid retrieval combines sparse retrieval and dense retrieval.
Cited doc: doc3
```

The gold document was retrieved, but it was ranked second. The answer generator selected a sentence from the wrong document.

This is not a pure retrieval failure.

The correct document was already in the retrieved results. The problem was that the generator selected the wrong context.

This is a context selection or grounding failure.

It shows that RAG systems require more than high retrieval recall. They also require reliable context selection and answer grounding.

---

## 11. Top-k Sensitivity Analysis

I tested the pipeline with:

```text
top_k = 1, 2, 3, 5
```

The results were:

```text
top_k = 1
Recall@k: 0.857
MRR: 0.857
nDCG@k: 0.857
Answer keyword score: 0.690
Faithfulness: 1.000
Citation relevance: 0.857
Retrieval failure count: 1

top_k = 2
Recall@k: 1.000
MRR: 0.929
nDCG@k: 0.947
Answer keyword score: 0.690
Faithfulness: 1.000
Citation relevance: 0.857
Context selection failure count: 1

top_k = 3
Recall@k: 1.000
MRR: 0.929
nDCG@k: 0.947
Answer keyword score: 0.690
Faithfulness: 1.000
Citation relevance: 0.857

top_k = 5
Recall@k: 1.000
MRR: 0.929
nDCG@k: 0.947
Answer keyword score: 0.690
Faithfulness: 1.000
Citation relevance: 0.857
```

Increasing top_k from 1 to 2 improved Recall@k from 0.857 to 1.000, because the gold document was included in the retrieved context.

However, the answer keyword score stayed at 0.690.

This shows that increasing top_k can improve retrieval coverage, but it does not necessarily improve answer quality.

A larger top_k may include the correct document, but the generator still needs to select and use the correct context.

---

## 12. Hallucination Simulation

I also simulated a hallucination case by forcing the generator to produce an unsupported answer:

```text
Answer: A hallucination is always caused by database indexing errors.
```

The result was:

```text
Faithfulness: 0.0
Failure type: hallucination_or_unfaithful_answer
```

This answer was not found in the retrieved context, so it was classified as unfaithful.

This demonstrates why faithfulness must be evaluated separately from retrieval quality and answer correctness.

An answer may sound fluent or plausible, but if it is not supported by the retrieved context, it should be considered unreliable in a RAG system.

---

## 13. Key Lessons

The main lessons from Day 6 are:

1. Retrieval quality is not the same as RAG quality.
2. High Recall@k does not guarantee correct final answers.
3. Increasing top_k can improve retrieval coverage, but it does not always improve answer quality.
4. RAG systems need context selection and grounding, not just retrieval.
5. Faithfulness must be evaluated separately because a generated answer may be unsupported by the retrieved documents.
6. Failure analysis is necessary to distinguish retrieval failure, generation failure, context selection failure, and hallucination.

---

## 14. Comparison with Day 5

Day 5 focused on retrieval evaluation.

The main question in Day 5 was:

```text
Can the retriever find the right documents?
```

Day 6 focused on RAG evaluation.

The main question in Day 6 was:

```text
Can the system generate a correct and faithful answer using the retrieved documents?
```

This is a major difference.

Retrieval evaluation only measures the retriever.

RAG evaluation measures the full pipeline.

---

## 15. Final Conclusion

RAG evaluation should include both retrieval-level and answer-level evaluation.

Retrieval-level metrics such as Recall@k, MRR, and nDCG@k measure whether the system retrieves the correct evidence.

Answer-level metrics such as answer keyword score, faithfulness, and citation relevance measure whether the final answer is correct, supported, and grounded in the right documents.

The key conclusion is:

```text
RAG evaluation = retrieval evaluation + answer correctness evaluation + faithfulness and grounding evaluation.
```

A reliable RAG system must not only retrieve relevant documents, but also generate answers that are correct, faithful, and supported by the retrieved context.