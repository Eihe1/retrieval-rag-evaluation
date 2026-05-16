# Day 5 - Retrieval Evaluation and Re-ranking

This folder contains experiments on retrieval evaluation, hybrid retrieval sensitivity, and Cross-Encoder re-ranking.

The goal of Day 5 was to move from simply running retrieval methods to evaluating, comparing, and improving retrieval systems.

---

## Topics

- Recall@k
- Precision@k
- MRR
- nDCG@k
- BM25 vs Dense Retrieval vs Hybrid Retrieval
- Alpha sensitivity analysis
- Cross-Encoder re-ranking
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

- BM25
- Dense Retrieval
- Hybrid Retrieval

The script evaluates each retriever using:

- Mean Recall@3
- MRR
- Mean nDCG@3

---

### `src/alpha_sensitivity_demo.py`

Runs alpha sensitivity analysis for Hybrid Retrieval.

It tests different alpha values:

```text
0.00, 0.25, 0.50, 0.75, 1.00
```

The goal is to observe how changing the balance between BM25 and Dense Retrieval affects ranking quality.

---

### `src/rerank_demo.py`

Implements a two-stage retrieval pipeline:

```text
BM25 first-stage retriever
        ↓
Cross-Encoder re-ranker
        ↓
reranked top results
```

This experiment shows how re-ranking can improve MRR and nDCG.

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

---

### Precision@k

Measures how many top-k retrieved documents are relevant.

```text
Precision@k = number of relevant documents in top-k / k
```

---

### MRR

MRR measures how early the first relevant document appears.

```text
RR = 1 / rank of first relevant document
```

MRR is the average Reciprocal Rank across queries.

---

### nDCG@k

nDCG@k measures ranking quality with graded relevance.

It rewards systems that place highly relevant documents near the top.

---

## Main Retrieval Results

The retrieval comparison produced the following result:

| Retriever | Mean Recall@3 | MRR | Mean nDCG@3 |
|---|---:|---:|---:|
| BM25 | 0.900 | 0.767 | 0.818 |
| Dense Retrieval | 0.900 | 1.000 | 0.983 |
| Hybrid Retrieval alpha=0.5 | 0.900 | 1.000 | 0.983 |

Main conclusion:

```text
The same Recall@k does not mean the retrieval systems are equally good.
```

BM25 retrieved relevant documents, but it often ranked them lower. Dense Retrieval and Hybrid Retrieval achieved better ranking quality.

---

## Alpha Sensitivity

Hybrid Retrieval uses:

```text
hybrid_score = alpha * dense_score + (1 - alpha) * bm25_score
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

Recall@3 remained unchanged, while MRR and nDCG improved as dense retrieval received more weight.

---

## Re-ranking Experiment

The re-ranking experiment used:

```text
First-stage retriever: BM25
First-stage candidates: top 5
Re-ranker: Cross-Encoder
Evaluation: top 3
```

Result:

| Stage | Mean Recall@3 | MRR | Mean nDCG@3 |
|---|---:|---:|---:|
| BM25 before re-ranking | 0.900 | 0.767 | 0.818 |
| After Cross-Encoder re-ranking | 0.900 | 1.000 | 0.983 |

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
Query: What is dense retrieval?
Gold relevant docs: d2, d7
First-stage candidates: d1, d3
```

Since the correct documents were not included in the candidate set, re-ranking could not improve Recall, MRR, or nDCG.

---

## Main Findings

1. Retrieval evaluation should consider both recall and ranking quality.
2. Recall@k alone is not enough.
3. MRR and nDCG@k reveal whether relevant documents are ranked early.
4. Dense Retrieval and Hybrid Retrieval can improve semantic ranking quality.
5. Hybrid alpha affects the balance between sparse and dense retrieval signals.
6. Cross-Encoder re-ranking can improve ranking quality.
7. Re-ranking cannot fix missing candidates from first-stage retrieval.

---

## Key Insight

A good retrieval pipeline needs:

```text
High-recall first-stage retrieval
        +
Accurate second-stage re-ranking
```

The first-stage retriever must include relevant documents in the candidate set. The re-ranker can then improve the order of those candidates.