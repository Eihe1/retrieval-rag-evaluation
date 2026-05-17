# Retrieval and RAG Evaluation Portfolio

This repository documents a research-oriented learning project on retrieval systems, retrieval evaluation, re-ranking, and RAG evaluation.

The project is organized as a multi-day portfolio. It starts from basic retrieval methods, then moves to retrieval evaluation and re-ranking, and finally extends to answer-level RAG evaluation and failure analysis.

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
└── day7_rag_diagnosis/
    ├── README.md
    ├── src/
    │   └── day7_rag_diagnosis_demo.py
    ├── results/
    │   ├── baseline_results.csv
    │   ├── evidence_first_results.csv
    │   ├── abstention_results.csv
    │   ├── diagnosis_summary.md
    │   ├── baseline_query_diagnosis.md
    │   ├── evidence_first_query_diagnosis.md
    │   └── abstention_query_diagnosis.md
    └── notes/
        └── day7_rag_diagnosis_notes.md
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

Retrieval success does not guarantee answer success. A RAG system may retrieve the correct document but still fail due to weak grounding, wrong evidence selection, incorrect citation, or unsupported generation. Different strategies optimize different objectives: baseline RAG has higher coverage, evidence-first RAG improves faithfulness, and abstention RAG reduces unsupported answers but may become over-conservative. Reliable RAG systems should diagnose the query-level failure mode before choosing whether to answer directly, select evidence first, verify citations, rewrite the query, re-rank documents, or abstain.

Folder:

```text
day7_rag_diagnosis/
```

---

## Learning Path

```text
Day 4: Build retrieval methods
Day 5: Evaluate and improve retrieval ranking
Day 6: Evaluate RAG answers and analyze failures
```

The project follows this progression:

```text
BM25 / Dense / Hybrid Retrieval
        ↓
Retrieval Metrics and Re-ranking
        ↓
RAG Answer Evaluation and Failure Analysis
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

Therefore, RAG evaluation should include both retrieval-level and answer-level evaluation.

---

## Main Techniques Covered

| Area | Techniques |
|---|---|
| Sparse retrieval | BM25 |
| Dense retrieval | Sentence embeddings, cosine similarity |
| Hybrid retrieval | BM25 + dense score fusion |
| Retrieval evaluation | Recall@k, Precision@k, MRR, nDCG@k |
| Re-ranking | Cross-Encoder re-ranking |
| RAG evaluation | Answer correctness, faithfulness, citation relevance |
| Failure analysis | Retrieval failure, generation failure, context selection failure, hallucination |

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