\# Experiment Summary



\## 1. BM25 vs Dense Retrieval vs Hybrid Retrieval



| Retriever | Mean Recall@3 | MRR | Mean nDCG@3 |

|---|---:|---:|---:|

| BM25 | 0.900 | 0.767 | 0.818 |

| Dense Retrieval | 0.900 | 1.000 | 0.983 |

| Hybrid Retrieval alpha=0.5 | 0.900 | 1.000 | 0.983 |



\## Finding



BM25, Dense Retrieval, and Hybrid Retrieval achieved the same Mean Recall@3, but BM25 had lower MRR and nDCG@3. This shows that Recall@k alone is not enough to evaluate retrieval systems. Ranking quality should also be measured using MRR and nDCG.



\## 2. Alpha Sensitivity



| alpha | Recall@3 | MRR | nDCG@3 |

|---:|---:|---:|---:|

| 0.00 | 0.900 | 0.767 | 0.818 |

| 0.25 | 0.900 | 0.867 | 0.892 |

| 0.50 | 0.900 | 1.000 | 0.983 |

| 0.75 | 0.900 | 1.000 | 0.983 |

| 1.00 | 0.900 | 1.000 | 0.983 |



\## Finding



Increasing the dense retrieval weight improved ranking quality. In this experiment, alpha = 0.5 was sufficient to reach the best MRR and nDCG@3.



\## 3. Re-ranking



| Stage | Mean Recall@3 | MRR | Mean nDCG@3 |

|---|---:|---:|---:|

| BM25 before reranking | 0.900 | 0.767 | 0.818 |

| After Cross-Encoder reranking | 0.900 | 1.000 | 0.983 |



\## Finding



Cross-Encoder re-ranking improved MRR and nDCG@3 while Recall@3 remained unchanged. This shows that re-ranking improves ranking quality but does not recover documents missed by the first-stage retriever.



\## 4. Failure Case



When the first-stage retriever used only top-2 BM25 candidates for the query "What is dense retrieval?", the relevant documents were not included in the candidate set. The re-ranker could only reorder the existing candidates and could not recover the missing relevant documents.



\## Main Conclusion



A practical retrieval pipeline should use a high-recall first-stage retriever to collect candidate documents, followed by a more accurate re-ranker to improve ranking quality.

