# Day 5 - Retrieval Evaluation and Heuristic Re-ranking

This folder contains experiments on retrieval evaluation, hybrid retrieval sensitivity, and heuristic second-stage re-ranking.

The goal of Day 5 was to move from simply running retrieval methods to evaluating, comparing, and improving retrieval systems.

The current implementation is intentionally small and interpretable. The re-ranking component is a heuristic baseline, not a neural Cross-Encoder re-ranker.

---

## Topics

- Recall@k
- Precision@k
- MRR
- nDCG@k
- BM25-style retrieval vs semantic-proxy retrieval vs hybrid retrieval
- Alpha sensitivity analysis
- Heuristic second-stage re-ranking
- Re-ranking failure case

---

## Folder Structure

```text
day5_retrieval_eval_reranking/
│
├── README.md
│
├── src/
│   ├── eval_metrics_demo.py
│   ├── retrieval_eval_demo.py
│   ├── alpha_sensitivity_demo.py
│   ├── rerank_demo.py
│   └── rerank_failure_case_demo.py
│
├── results/
│
└── notes/
    └── day5_retrieval_evaluation_reranking_notes.md
```

---

## Implementation Scope

This folder uses simplified retrieval and ranking components to study retrieval evaluation.

The semantic retrieval component should be interpreted as a lightweight semantic-proxy signal rather than a production embedding-based dense retriever.

The re-ranking component should be interpreted as a heuristic second-stage re-ranker rather than a neural Cross-Encoder.

The goal is to study evaluation behavior and failure modes, especially the fact that re-ranking cannot recover relevant documents missed by first-stage retrieval.

---

## Files

### `src/eval_metrics_demo.py`

Implements basic retrieval evaluation metrics:

- Recall@k
- Precision@k
- Reciprocal Rank
- nDCG@k

This script is used to understand how the metrics are calculated manually.

---

### `src/retrieval_eval_demo.py`

Compares three retrieval methods:

- BM25-style lexical retrieval
- Lightweight semantic-proxy retrieval
- Hybrid retrieval

The script evaluates each retriever using:

- Mean Recall@3
- MRR
- Mean nDCG@3

---

### `src/alpha_sensitivity_demo.py`

Runs alpha sensitivity analysis for hybrid retrieval.

It tests different alpha values:

```text
0.00, 0.25, 0.50, 0.75, 1.00
```

The goal is to observe how changing the balance between BM25-style lexical retrieval and the semantic-proxy signal affects ranking quality.

---

### `src/rerank_demo.py`

Implements a two-stage retrieval pipeline:

```text
BM25-style first-stage retriever
        ↓
heuristic second-stage re-ranker
        ↓
reranked top results
```

This experiment shows how a second-stage re-ranking step can improve MRR and nDCG when the relevant document is already present in the first-stage candidate set.

---

### `src/rerank_failure_case_demo.py`

Demonstrates the limitation of re-ranking.

If the first-stage retriever does not retrieve the relevant document, the re-ranker cannot recover it.

---

### `notes/day5_retrieval_evaluation_reranking_notes.md`

Complete notes and analysis for Day 5.

---

## Retrieval Metrics

### Recall@k

Measures whether relevant documents are included in the top-k retrieved results.

```text
Recall@k = number of relevant documents in top-k / total number of relevant documents
```

Recall@k answers:

```text
Did the retriever find the relevant evidence at all?
```

---

### Precision@k

Measures how many top-k retrieved documents are relevant.

```text
Precision@k = number of relevant documents in top-k / k
```

Precision@k answers:

```text
How much noise exists in the retrieved top-k set?
```

---

### MRR

MRR measures how early the first relevant document appears.

```text
RR = 1 / rank of first relevant document
```

MRR is the average reciprocal rank across queries.

---

### nDCG@k

nDCG@k measures ranking quality.

It rewards systems that place relevant or highly relevant documents near the top.

In this toy project, nDCG is used as an interpretable ranking metric for controlled retrieval experiments.

---

## Main Retrieval Results

The retrieval comparison produced the following result:

| Retriever | Mean Recall@3 | MRR | Mean nDCG@3 |
|---|---:|---:|---:|
| BM25-style retrieval | 0.900 | 0.767 | 0.818 |
| Semantic-proxy retrieval | 0.900 | 1.000 | 0.983 |
| Hybrid retrieval alpha=0.5 | 0.900 | 1.000 | 0.983 |

Main conclusion:

```text
The same Recall@k does not mean the retrieval systems are equally good.
```

BM25-style retrieval retrieved relevant documents, but it often ranked them lower. The semantic-proxy and hybrid retrieval settings achieved better ranking quality on this toy evaluation set.

These results should be interpreted as controlled prototype results, not as evidence that semantic-proxy retrieval is generally better than BM25 or production dense retrieval.

---

## Alpha Sensitivity

Hybrid retrieval uses:

```text
hybrid_score = alpha * semantic_proxy_score + (1 - alpha) * bm25_score
```

Alpha sensitivity result:

| alpha | Recall@3 | MRR | nDCG@3 |
|---:|---:|---:|---:|
| 0.00 | 0.900 | 0.767 | 0.818 |
| 0.25 | 0.900 | 0.867 | 0.892 |
| 0.50 | 0.900 | 1.000 | 0.983 |
| 0.75 | 0.900 | 1.000 | 0.983 |
| 1.00 | 0.900 | 1.000 | 0.983 |

Main conclusion:

```text
In this experiment, alpha mainly affected ranking quality rather than recall coverage.
```

Recall@3 remained unchanged, while MRR and nDCG improved as the semantic-proxy signal received more weight.

This motivates later query-aware routing instead of fixing one global alpha value.

---

## Re-ranking Experiment

The re-ranking experiment used:

```text
First-stage retriever: BM25-style retrieval
First-stage candidates: top 5
Re-ranker: heuristic second-stage re-ranker
Evaluation: top 3
```

Result:

| Stage | Mean Recall@3 | MRR | Mean nDCG@3 |
|---|---:|---:|---:|
| BM25-style before re-ranking | 0.900 | 0.767 | 0.818 |
| After heuristic re-ranking | 0.900 | 1.000 | 0.983 |

Main conclusion:

```text
Re-ranking improves ranking quality, but does not necessarily improve recall.
```

The re-ranker only reorders the candidate documents already retrieved by the first-stage retriever.

---

## Re-ranking Failure Case

The failure case shows:

```text
If the correct document is missing from the first-stage candidate set, the re-ranker cannot recover it.
```

Example:

```text
Query: What is semantic retrieval?
Gold relevant docs: d2, d7
First-stage candidates: d1, d3
```

Since the correct documents were not included in the candidate set, re-ranking could not improve Recall, MRR, or nDCG.

This is the key recall ceiling argument:

```text
Re-ranking can improve ordering, but it cannot fix missing first-stage recall.
```

---

## Main Findings

1. Retrieval evaluation should consider both recall and ranking quality.
2. Recall@k alone is not enough.
3. MRR and nDCG@k reveal whether relevant documents are ranked early.
4. Semantic-proxy and hybrid retrieval can improve ranking quality on this toy corpus.
5. Hybrid alpha affects the balance between lexical and semantic-proxy signals.
6. Heuristic re-ranking can improve ranking quality when relevant candidates are already retrieved.
7. Re-ranking cannot fix missing candidates from first-stage retrieval.

---

## Key Insight

A good retrieval pipeline needs:

```text
High-recall first-stage retrieval
        +
Accurate second-stage ranking
```

The first-stage retriever must include relevant documents in the candidate set. The re-ranker can then improve the order of those candidates.

---

## Limitations

Current limitations:

- Small toy dataset
- Simplified relevance labels
- Lightweight semantic-proxy retrieval instead of production dense retrieval
- Heuristic re-ranking instead of neural Cross-Encoder re-ranking
- No learned ranking model
- No large-scale IR benchmark

---

## Future Work

Possible next steps:

- Add embedding-based dense retrieval
- Add a neural Cross-Encoder or reranker model
- Compare heuristic and neural re-ranking
- Evaluate on larger retrieval benchmarks
- Add graded relevance labels
- Analyze how retrieval ranking affects answer faithfulness
- Connect retrieval failures to RAG failure diagnosis

---

## Summary

Day 5 shows that retrieval evaluation must distinguish recall and ranking quality.

The main insight is that re-ranking can improve ranking only within the first-stage candidate set. If first-stage retrieval misses the relevant document, re-ranking cannot fix the failure. This motivates later work on failure diagnosis, answer-level evaluation, and adaptive RAG strategy selection.
