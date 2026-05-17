# Progress Summary: Day 4 to Day 7

## Day 4: Retrieval Basics

Implemented BM25, dense retrieval, hybrid retrieval, and a minimal RAG pipeline.

## Day 5: Retrieval Evaluation and Re-ranking

Implemented Recall@k, MRR, nDCG, alpha sensitivity analysis, Cross-Encoder re-ranking, and a failure case showing that re-ranking cannot recover documents missing from first-stage retrieval.

## Day 6: RAG Evaluation

Extended retrieval evaluation to RAG answer evaluation, including answer keyword score, faithfulness, citation relevance, top-k sensitivity, and hallucination simulation.

## Day 7: RAG Diagnosis and Strategy Trade-off Analysis

Extended RAG evaluation into diagnosis-driven improvement. Compared baseline RAG, evidence-first RAG, and abstention RAG. The results showed that reliable RAG requires query-level diagnosis and adaptive strategy selection.

## Current Research Direction

The current direction is diagnosis-driven and cost-aware optimization for multi-stage RAG retrieval pipelines.