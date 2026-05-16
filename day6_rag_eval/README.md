# Day 6 - RAG Evaluation and Failure Analysis

This folder extends retrieval evaluation into RAG evaluation.

In Day 5, the focus was on whether the retriever could find and rank relevant documents. In Day 6, the focus moves to the final answer: whether it is correct, faithful, and grounded in the retrieved context.

---

## Topics

- RAG evaluation pipeline
- Retrieval-level metrics
- Answer-level metrics
- Answer keyword score
- Faithfulness
- Citation relevance
- Failure type classification
- Top-k sensitivity analysis
- Hallucination simulation

---

## Folder Structure

```text
day6_rag_eval/
│
├── README.md
│
├── src/
│   └── rag_eval_demo.py
│
├── results/
│   ├── rag_eval_results.csv
│   └── topk_sensitivity_results.csv
│
└── notes/
    └── day6_rag_evaluation_notes.md
```

---

## Files

### `src/rag_eval_demo.py`

Main experiment script.

It implements:

- Toy document corpus
- BM25 retriever
- Extractive answer generator
- Retrieval metrics
- Answer metrics
- Failure type classification
- Top-k sensitivity experiment
- Hallucination simulation

---

### `results/rag_eval_results.csv`

Per-query RAG evaluation results.

Includes:

- Query
- Gold document ID
- Retrieved document IDs
- Generated answer
- Cited document ID
- Retrieval metrics
- Answer metrics
- Failure type

---

### `results/topk_sensitivity_results.csv`

Top-k sensitivity experiment results.

Compares:

```text
top_k = 1, 2, 3, 5
```

---

### `notes/day6_rag_evaluation_notes.md`

Complete notes and analysis for Day 6.

---

## RAG Evaluation Pipeline

The experiment uses a small toy RAG pipeline:

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

The goal is not to build a production RAG system, but to inspect different failure cases in a controlled setting.

---

## Metrics

### Retrieval-Level Metrics

| Metric | Meaning |
|---|---|
| Recall@k | Whether the gold document appears in the top-k retrieved results |
| MRR | How highly the first relevant document is ranked |
| nDCG@k | Whether relevant documents are ranked near the top |

---

### Answer-Level Metrics

| Metric | Meaning |
|---|---|
| Answer keyword score | Whether the answer contains expected key information |
| Faithfulness | Whether the answer is supported by the retrieved context |
| Citation relevance | Whether the answer comes from the correct gold document |

---

## Failure Types

The script classifies each result into one of the following failure types:

| Failure Type | Meaning |
|---|---|
| success | The system retrieved the right document and generated a correct, faithful answer |
| retrieval_failure | The gold document was not retrieved |
| generation_failure | The gold document was retrieved and cited, but the answer was incomplete |
| citation_or_context_selection_failure | The gold document was retrieved, but the answer came from the wrong document |
| hallucination_or_unfaithful_answer | The answer was not supported by the retrieved context |
| mixed_failure | Other mixed error cases |

---

## Main Result

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

However, the average answer keyword score was only 0.690. This shows that retrieval success does not guarantee answer success.

---

## Failure Type Summary

```text
success: count=3, ratio=0.429
citation_or_context_selection_failure: count=1, ratio=0.143
generation_failure: count=3, ratio=0.429
```

The most important failure case was:

```text
Query: Why is dense retrieval useful?
Gold doc: doc2
Retrieved docs: doc3, doc2, doc1
Cited doc: doc3
```

The correct document was retrieved, but the generator selected the wrong context.

This is a context selection or grounding failure.

---

## Top-k Sensitivity

The experiment tested:

```text
top_k = 1, 2, 3, 5
```

Result summary:

```text
top_k = 1
Recall@k: 0.857
Answer keyword score: 0.690
Retrieval failure count: 1

top_k = 2
Recall@k: 1.000
Answer keyword score: 0.690
Context selection failure count: 1

top_k = 3
Recall@k: 1.000
Answer keyword score: 0.690

top_k = 5
Recall@k: 1.000
Answer keyword score: 0.690
```

Increasing top_k improved retrieval coverage, but it did not improve answer quality.

---

## Hallucination Simulation

The script also simulates an unsupported answer:

```text
Answer: A hallucination is always caused by database indexing errors.
Faithfulness: 0.0
Failure type: hallucination_or_unfaithful_answer
```

This answer was not supported by the retrieved context.

This shows why faithfulness must be evaluated separately from retrieval quality and answer correctness.

---

## Main Findings

1. Retrieval success does not guarantee answer success.
2. Recall@k alone is not enough to evaluate a RAG system.
3. Increasing top_k can improve retrieval coverage, but not necessarily answer quality.
4. Correct documents may be retrieved but ignored by the generator.
5. Faithfulness must be evaluated separately.
6. Hallucination is an answer-level failure, not a retrieval metric failure.

---

## Key Insight

RAG evaluation should include:

```text
retrieval evaluation
+
answer correctness evaluation
+
faithfulness and grounding evaluation
```

A reliable RAG system must retrieve the right evidence, select the correct context, and generate answers that are correct and supported by the retrieved documents.