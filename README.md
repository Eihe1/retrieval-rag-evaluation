\# Retrieval Evaluation and Re-ranking Demo



\## Overview



This project is a small experimental pipeline for studying retrieval evaluation and re-ranking in retrieval-augmented generation (RAG) systems.



It compares BM25, Dense Retrieval, Hybrid Retrieval, and Cross-Encoder re-ranking using a manually defined document collection and query set. The main focus is not only whether relevant documents are retrieved, but also whether they are ranked early enough to be useful in downstream RAG pipelines.



The project demonstrates how retrieval systems can be evaluated using:



\- Recall@k

\- Precision@k

\- MRR

\- nDCG@k



It also shows why re-ranking can improve ranking quality, and why it cannot recover documents that were missed by the first-stage retriever.



\---



\## Motivation



In a RAG system, the final answer depends strongly on the quality of retrieved documents.



A typical RAG pipeline is:



```text

query

&#x20; ↓

retriever

&#x20; ↓

top-k documents

&#x20; ↓

LLM prompt

&#x20; ↓

answer

```



If the final answer is wrong, the problem may come from different stages:



```text

Case 1: The retriever did not retrieve the correct document.

→ retrieval failure



Case 2: The retriever retrieved the correct document, but ranked it too low.

→ ranking quality problem



Case 3: The retriever retrieved the correct document, but included too many noisy documents.

→ context pollution problem



Case 4: The retriever retrieved the correct document, but the LLM did not use it correctly.

→ generation problem

```



Therefore, retrieval quality should be evaluated separately before evaluating the final generated answer.



This project explores three main questions:



1\. How do BM25, Dense Retrieval, and Hybrid Retrieval differ in retrieval and ranking quality?

2\. How does the alpha parameter affect Hybrid Retrieval?

3\. How much can Cross-Encoder re-ranking improve final ranking quality?



\---



\## Methods



The project includes the following retrieval and ranking methods:



\### BM25



BM25 is a sparse lexical retrieval method based on term frequency and inverse document frequency. It is fast and effective when the query and document share exact terms.



\### Dense Retrieval



Dense Retrieval represents queries and documents as embeddings and compares them using semantic similarity. It can capture semantic relationships even when exact word overlap is limited.



\### Hybrid Retrieval



Hybrid Retrieval combines BM25 scores and Dense Retrieval scores.



The hybrid score is calculated as:



```text

hybrid\_score = alpha \* dense\_score + (1 - alpha) \* bm25\_score

```



Where:



```text

alpha = 0.0 → pure BM25

alpha = 1.0 → pure Dense Retrieval

```



\### Cross-Encoder Re-ranking



Cross-Encoder re-ranking is used as a second-stage ranking method.



The first-stage retriever retrieves candidate documents. Then the Cross-Encoder scores each query-document pair more precisely and reorders the candidates.



This structure is common in practical retrieval and RAG systems:



```text

query

&#x20; ↓

first-stage retriever

&#x20; ↓

top-k candidates

&#x20; ↓

Cross-Encoder re-ranker

&#x20; ↓

final top results

```



\---



\## Evaluation Metrics



\### Recall@k



Recall@k measures how many relevant documents are retrieved in the top-k results.



```text

Recall@k = number of relevant documents in top-k / total number of relevant documents

```



Recall focuses on whether relevant documents are found.



\---



\### Precision@k



Precision@k measures how many of the top-k results are relevant.



```text

Precision@k = number of relevant documents in top-k / k

```



Precision focuses on how clean the retrieved results are.



\---



\### MRR



MRR stands for Mean Reciprocal Rank.



For a single query:



```text

RR = 1 / rank of the first relevant document

```



MRR is the average RR across multiple queries.



MRR focuses on how early the first relevant document appears.



\---



\### nDCG@k



nDCG measures ranking quality with graded relevance.



DCG is calculated as:



```text

DCG@k = Σ (2^rel\_i - 1) / log2(i + 1)

```



nDCG is calculated as:



```text

nDCG@k = DCG@k / IDCG@k

```



Where `IDCG@k` is the DCG value of the ideal ranking.



nDCG rewards highly relevant documents appearing early in the ranking.



\---



\## Project Structure



```text

retrieval-rag-evaluation/

│

├── README.md

├── requirements.txt

├── .gitignore

│

├── src/

│   ├── eval\_metrics\_demo.py

│   ├── retrieval\_eval\_demo.py

│   ├── alpha\_sensitivity\_demo.py

│   ├── rerank\_demo.py

│   └── rerank\_failure\_case\_demo.py

│

├── notes/

│   └── day5\_retrieval\_evaluation\_reranking\_notes.md

│

└── results/

&#x20;   └── experiment\_summary.md

```



\---



\## Installation



Install the required dependencies:



```bash

pip install -r requirements.txt

```



The required packages are:



```text

numpy

scikit-learn

rank-bm25

sentence-transformers

```



\---



\## How to Run



\### 1. Retrieval Metrics Demo



```bash

python src/eval\_metrics\_demo.py

```



This script demonstrates how Recall@k, Precision@k, MRR, and nDCG@k are calculated.



It uses a manually defined ranking and relevance labels to show how each metric works.



\---



\### 2. Retrieval Evaluation Demo



```bash

python src/retrieval\_eval\_demo.py

```



This script compares:



\- BM25

\- Dense Retrieval

\- Hybrid Retrieval



It evaluates each retriever using:



\- Mean Recall@3

\- MRR

\- Mean nDCG@3



\---



\### 3. Alpha Sensitivity Demo



```bash

python src/alpha\_sensitivity\_demo.py

```



This script tests different alpha values in Hybrid Retrieval:



```text

alpha = 0.0

alpha = 0.25

alpha = 0.5

alpha = 0.75

alpha = 1.0

```



The goal is to observe how changing the balance between BM25 and Dense Retrieval affects ranking quality.



\---



\### 4. Re-ranking Demo



```bash

python src/rerank\_demo.py

```



This script uses:



```text

First-stage retriever: BM25

Second-stage re-ranker: Cross-Encoder

```



It compares retrieval quality before and after re-ranking.



\---



\### 5. Re-ranking Failure Case Demo



```bash

python src/rerank\_failure\_case\_demo.py

```



This script demonstrates a failure case where the relevant document is not included in the first-stage candidate set.



It shows that re-ranking cannot recover documents that were missed by the first-stage retriever.



\---



\## Experimental Data



The project uses a small manually defined document collection.



```python

documents = {

&#x20;   "d1": "BM25 is a sparse retrieval method based on term frequency and inverse document frequency.",

&#x20;   "d2": "Dense retrieval represents queries and documents as vectors and compares them using semantic similarity.",

&#x20;   "d3": "Hybrid retrieval combines sparse lexical matching and dense semantic matching.",

&#x20;   "d4": "RAG retrieves external documents and uses them as context for language model generation.",

&#x20;   "d5": "Re-ranking improves the order of retrieved candidates using a more accurate but slower model.",

&#x20;   "d6": "PostgreSQL supports indexes such as B-tree, hash indexes, and vector indexes through extensions.",

&#x20;   "d7": "Vector databases are designed to store embeddings and support approximate nearest neighbor search.",

&#x20;   "d8": "Evaluation metrics such as Recall@k, MRR, and nDCG are used to measure retrieval quality.",

}

```



Queries:



```python

queries = {

&#x20;   "q1": "What is dense retrieval?",

&#x20;   "q2": "How does RAG use retrieved documents?",

&#x20;   "q3": "What does hybrid retrieval combine?",

&#x20;   "q4": "How can retrieval quality be evaluated?",

&#x20;   "q5": "What is re-ranking used for?",

}

```



Gold relevant documents:



```python

gold\_relevant = {

&#x20;   "q1": {"d2", "d7"},

&#x20;   "q2": {"d4"},

&#x20;   "q3": {"d3"},

&#x20;   "q4": {"d8"},

&#x20;   "q5": {"d5"},

}

```



\---



\## Key Results



\### 1. BM25 vs Dense Retrieval vs Hybrid Retrieval



| Retriever | Mean Recall@3 | MRR | Mean nDCG@3 |

|---|---:|---:|---:|

| BM25 | 0.900 | 0.767 | 0.818 |

| Dense Retrieval | 0.900 | 1.000 | 0.983 |

| Hybrid Retrieval alpha=0.5 | 0.900 | 1.000 | 0.983 |



\### Finding



BM25, Dense Retrieval, and Hybrid Retrieval all achieved the same Mean Recall@3.



However, BM25 had lower MRR and nDCG@3.



This shows that Recall@k alone is not enough to evaluate retrieval systems. A retriever may find relevant documents but still rank them too low.



Dense Retrieval and Hybrid Retrieval performed better because they placed the most relevant documents earlier in the ranking.



\---



\## 2. Alpha Sensitivity



| alpha | Recall@3 | MRR | nDCG@3 |

|---:|---:|---:|---:|

| 0.00 | 0.900 | 0.767 | 0.818 |

| 0.25 | 0.900 | 0.867 | 0.892 |

| 0.50 | 0.900 | 1.000 | 0.983 |

| 0.75 | 0.900 | 1.000 | 0.983 |

| 1.00 | 0.900 | 1.000 | 0.983 |



\### Finding



Increasing the Dense Retrieval weight improved ranking quality.



When `alpha = 0.0`, Hybrid Retrieval is equivalent to pure BM25.



When `alpha = 0.5`, the system reached the best MRR and nDCG@3.



Further increasing alpha to `0.75` or `1.0` did not improve the metrics further.



This suggests that in this small experiment, Dense Retrieval was already strong enough to correct the main BM25 ranking errors.



\---



\## 3. Cross-Encoder Re-ranking



| Stage | Mean Recall@3 | MRR | Mean nDCG@3 |

|---|---:|---:|---:|

| BM25 before reranking | 0.900 | 0.767 | 0.818 |

| After Cross-Encoder reranking | 0.900 | 1.000 | 0.983 |



\### Finding



Cross-Encoder re-ranking improved:



```text

MRR: 0.767 → 1.000

Mean nDCG@3: 0.818 → 0.983

```



However, Mean Recall@3 remained unchanged:



```text

Mean Recall@3: 0.900 → 0.900

```



This confirms that re-ranking mainly improves ranking quality rather than recall coverage.



The re-ranker only reorders documents that were already retrieved by the first-stage retriever.



\---



\## 4. Re-ranking Failure Case



For the query:



```text

What is dense retrieval?

```



Gold relevant documents:



```text

{d2, d7}

```



Full BM25 ranking:



```text

\['d1', 'd3', 'd2', 'd8', 'd5', 'd6', 'd7', 'd4']

```



When only top-2 BM25 candidates were used:



```text

\['d1', 'd3']

```



Neither `d2` nor `d7` was included in the candidate set.



After re-ranking:



```text

\['d3', 'd1']

```



Metrics before and after re-ranking:



| Stage | Recall@3 | RR | nDCG@3 |

|---|---:|---:|---:|

| Before re-ranking | 0.000 | 0.000 | 0.000 |

| After re-ranking | 0.000 | 0.000 | 0.000 |



\### Finding



If the first-stage retriever does not retrieve the relevant document, the re-ranker cannot fix the problem.



A re-ranker can only reorder existing candidates. It cannot recover documents that are missing from the candidate set.



\---



\## Main Findings



1\. BM25 can retrieve relevant documents but may rank them lower due to lexical matching limitations.

2\. Dense Retrieval can better capture semantic similarity between queries and documents.

3\. Hybrid Retrieval combines sparse and dense retrieval signals, but the alpha parameter needs to be tuned.

4\. Recall@k alone is not enough to evaluate retrieval systems.

5\. MRR and nDCG@k are important for measuring ranking quality.

6\. Cross-Encoder re-ranking can significantly improve ranking quality.

7\. Re-ranking does not improve recall if the relevant documents are not included in the candidate set.

8\. A practical retrieval pipeline should combine a high-recall first-stage retriever with a more accurate second-stage re-ranker.



\---



\## Practical Interpretation



A practical retrieval or RAG system should usually use a two-stage design:



```text

Stage 1: First-stage retriever

\- BM25

\- Dense Retrieval

\- Hybrid Retrieval



Goal:

Retrieve a candidate set with high recall.



Stage 2: Re-ranker

\- Cross-Encoder



Goal:

Improve the ranking quality of retrieved candidates.

```



The first-stage retriever should avoid missing relevant documents.



The re-ranker should improve the order of the retrieved candidates.



This creates a balance between efficiency and accuracy.



\---



\## Skills Demonstrated



This project demonstrates the following skills:



\- Python programming

\- Information retrieval

\- BM25 sparse retrieval

\- Dense Retrieval with SentenceTransformers

\- Hybrid Retrieval score fusion

\- Retrieval evaluation

\- Recall@k

\- Precision@k

\- MRR

\- nDCG@k

\- Cross-Encoder re-ranking

\- RAG system analysis

\- Experimental result interpretation

\- Failure case analysis



\---



\## Limitations



This project uses a small manually defined dataset.



The results are useful for understanding retrieval concepts, but they are not meant to represent large-scale production performance.



Main limitations:



1\. The document collection is small.

2\. Queries and relevance labels are manually defined.

3\. There is no real-world dataset.

4\. The evaluation only focuses on retrieval, not full RAG answer generation.

5\. The project does not yet evaluate answer faithfulness or hallucination.



\---



\## Future Work



Possible extensions:



1\. Use a larger real-world dataset.

2\. Add FAISS or pgvector for vector search.

3\. Evaluate retrieval latency.

4\. Add more queries and graded relevance labels.

5\. Add full RAG answer generation.

6\. Evaluate answer quality separately from retrieval quality.

7\. Measure faithfulness between generated answers and retrieved context.

8\. Compare different embedding models.

9\. Compare different Cross-Encoder re-rankers.

10\. Add visualization for metric comparison.



\---



\## Notes



Detailed study notes are available in:



```text

notes/day5\_retrieval\_evaluation\_reranking\_notes.md

```



Experiment summary is available in:



```text

results/experiment\_summary.md

```



\---



\## Final Summary



This project studies retrieval evaluation and re-ranking for RAG-style systems.



The experiments show that retrieval systems should not be evaluated only by whether relevant documents appear in the top-k results. Ranking quality also matters.



BM25 achieved the same Mean Recall@3 as Dense Retrieval and Hybrid Retrieval, but had lower MRR and nDCG@3. This means BM25 retrieved relevant documents but often ranked them lower.



Hybrid Retrieval improved ranking quality when the Dense Retrieval weight increased. In this experiment, `alpha = 0.5` was sufficient to reach the best performance.



Cross-Encoder re-ranking improved MRR from `0.767` to `1.000` and Mean nDCG@3 from `0.818` to `0.983`, while Mean Recall@3 stayed unchanged at `0.900`.



The failure case showed that re-ranking cannot recover relevant documents that were missed by the first-stage retriever.



Overall, the project demonstrates that a good retrieval pipeline needs both:



```text

1\. A high-recall first-stage retriever

2\. A more accurate second-stage re-ranker

```

