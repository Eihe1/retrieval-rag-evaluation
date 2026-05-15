# Day 5 Notes: Retrieval Evaluation and Re-ranking

## 1. Learning Goals

The goal of Day 5 was to move from simply running retrieval methods to evaluating, comparing, and improving retrieval systems.

The main topics were:

1. Retrieval evaluation
2. Common retrieval metrics:
   - Recall@k
   - Precision@k
   - MRR
   - nDCG@k
3. Comparison between BM25, Dense Retrieval, and Hybrid Retrieval
4. Alpha sensitivity in Hybrid Retrieval
5. Cross-Encoder re-ranking
6. The limitation of re-ranking when first-stage retrieval fails

---

## 2. Why Retrieval Evaluation Is Needed

In a RAG system, the final answer depends on multiple stages:

```text
query
  ↓
retriever
  ↓
top-k documents
  ↓
LLM prompt
  ↓
answer
```

If the final answer is wrong, the problem may come from different stages:

```text
Case 1: The retriever did not find the correct document.
→ retrieval failure

Case 2: The retriever found the correct document, but ranked it too low.
→ ranking quality problem

Case 3: The retriever found the correct document, but included too many noisy documents.
→ context pollution problem

Case 4: The retriever found the correct document, but the LLM did not use it correctly.
→ generation problem
```

Therefore, retrieval should be evaluated separately before evaluating the final generated answer.

---

## 3. Retrieval Metrics

### 3.1 Recall@k

Recall@k measures how many relevant documents are retrieved within the top-k results.

Formula:

```text
Recall@k = number of relevant documents in top-k / total number of relevant documents
```

Example:

```python
ranking = ["d3", "d2", "d5", "d1", "d4"]
relevant_docs = {"d2", "d4"}
```

For Recall@3:

```text
Top 3 = ["d3", "d2", "d5"]
Relevant document found = d2

Recall@3 = 1 / 2 = 0.5
```

Recall focuses on whether the system can retrieve the relevant documents.

In RAG, if the correct document is not retrieved, the LLM or re-ranker cannot use it later.

---

### 3.2 Precision@k

Precision@k measures how many of the top-k results are actually relevant.

Formula:

```text
Precision@k = number of relevant documents in top-k / k
```

Example:

```text
Top 3 = ["d3", "d2", "d5"]
Only d2 is relevant.

Precision@3 = 1 / 3 = 0.333
```

Precision focuses on how clean the retrieved results are.

---

### 3.3 MRR

MRR stands for Mean Reciprocal Rank.

It measures how early the first relevant document appears in the ranking.

For a single query:

```text
RR = 1 / rank of the first relevant document
```

Example:

```python
ranking = ["d3", "d2", "d5", "d1", "d4"]
relevant_docs = {"d2", "d4"}
```

The first relevant document is `d2`, which appears at rank 2.

```text
RR = 1 / 2 = 0.5
```

For multiple queries, MRR is the average of RR values.

MRR is especially useful for question answering, because the user often needs the first useful result to appear as early as possible.

---

### 3.4 nDCG@k

nDCG measures ranking quality, especially when relevance is graded rather than binary.

Example relevance levels:

```text
0 = not relevant
1 = slightly relevant
2 = relevant
3 = highly relevant
```

DCG formula:

```text
DCG@k = Σ (2^rel_i - 1) / log2(i + 1)
```

Where:

```text
rel_i = relevance score of the document at rank i
i = rank position, starting from 1
```

nDCG formula:

```text
nDCG@k = DCG@k / IDCG@k
```

Where:

```text
IDCG@k = DCG@k of the ideal ranking
```

The core idea of nDCG is:

```text
Highly relevant documents should appear earlier.
If a highly relevant document appears later, its contribution is discounted.
```

---

## 4. nDCG Calculation Example

Experimental data:

```python
ranking = ["d3", "d2", "d5", "d1", "d4"]

relevance_scores = {
    "d1": 0,
    "d2": 2,
    "d3": 0,
    "d4": 3,
    "d5": 1
}
```

The current ranking has the following relevance scores:

```text
d3: 0
d2: 2
d5: 1
d1: 0
d4: 3
```

### 4.1 nDCG@3

Top 3 ranking:

```text
[d3, d2, d5]
```

Corresponding relevance scores:

```text
[0, 2, 1]
```

DCG@3:

| Rank | Doc | rel | gain = 2^rel - 1 | discount = log2(rank + 1) | contribution |
|---:|---|---:|---:|---:|---:|
| 1 | d3 | 0 | 0 | 1.000 | 0 |
| 2 | d2 | 2 | 3 | 1.585 | 1.893 |
| 3 | d5 | 1 | 1 | 2.000 | 0.500 |

```text
DCG@3 = 0 + 1.893 + 0.5 = 2.393
```

Ideal top 3 ranking:

```text
[d4, d2, d5]
```

Corresponding relevance scores:

```text
[3, 2, 1]
```

IDCG@3:

```text
IDCG@3 = 7 / 1 + 3 / 1.585 + 1 / 2
        = 7 + 1.893 + 0.5
        = 9.393
```

Therefore:

```text
nDCG@3 = 2.393 / 9.393 = 0.2547
```

Program output:

```text
nDCG@3: 0.25474746577380225
```

---

### 4.2 nDCG@5

Top 5 ranking:

```text
[d3, d2, d5, d1, d4]
```

Corresponding relevance scores:

```text
[0, 2, 1, 0, 3]
```

DCG@5:

```text
d3: 0
d2: 3 / log2(3) = 1.893
d5: 1 / log2(4) = 0.5
d1: 0
d4: 7 / log2(6) = 2.708
```

```text
DCG@5 = 0 + 1.893 + 0.5 + 0 + 2.708
      = 5.101
```

Ideal ranking:

```text
[d4, d2, d5, d1, d3]
```

IDCG@5:

```text
IDCG@5 = 7 + 1.893 + 0.5 + 0 + 0
       = 9.393
```

Therefore:

```text
nDCG@5 = 5.101 / 9.393 = 0.5430
```

Program output:

```text
nDCG@5: 0.5430505007378631
```

---

## 5. BM25, Dense Retrieval, and Hybrid Retrieval Evaluation

### 5.1 Experimental Setup

Documents:

```python
documents = {
    "d1": "BM25 is a sparse retrieval method based on term frequency and inverse document frequency.",
    "d2": "Dense retrieval represents queries and documents as vectors and compares them using semantic similarity.",
    "d3": "Hybrid retrieval combines sparse lexical matching and dense semantic matching.",
    "d4": "RAG retrieves external documents and uses them as context for language model generation.",
    "d5": "Re-ranking improves the order of retrieved candidates using a more accurate but slower model.",
    "d6": "PostgreSQL supports indexes such as B-tree, hash indexes, and vector indexes through extensions.",
    "d7": "Vector databases are designed to store embeddings and support approximate nearest neighbor search.",
    "d8": "Evaluation metrics such as Recall@k, MRR, and nDCG are used to measure retrieval quality.",
}
```

Queries:

```python
queries = {
    "q1": "What is dense retrieval?",
    "q2": "How does RAG use retrieved documents?",
    "q3": "What does hybrid retrieval combine?",
    "q4": "How can retrieval quality be evaluated?",
    "q5": "What is re-ranking used for?",
}
```

Gold relevant documents:

```python
gold_relevant = {
    "q1": {"d2", "d7"},
    "q2": {"d4"},
    "q3": {"d3"},
    "q4": {"d8"},
    "q5": {"d5"},
}
```

---

### 5.2 Overall Results

| Retriever | Mean Recall@3 | MRR | Mean nDCG@3 |
|---|---:|---:|---:|
| BM25 | 0.900 | 0.767 | 0.818 |
| Dense Retrieval | 0.900 | 1.000 | 0.983 |
| Hybrid Retrieval alpha=0.5 | 0.900 | 1.000 | 0.983 |

---

### 5.3 Result Analysis

All three methods achieved the same Mean Recall@3:

```text
Mean Recall@3 = 0.900
```

This means that they retrieved a similar number of relevant documents within the top 3 results.

However, BM25 had lower MRR and nDCG@3:

```text
BM25:
MRR = 0.767
Mean nDCG@3 = 0.818
```

Dense Retrieval and Hybrid Retrieval had better ranking quality:

```text
Dense Retrieval:
MRR = 1.000
Mean nDCG@3 = 0.983

Hybrid Retrieval:
MRR = 1.000
Mean nDCG@3 = 0.983
```

Key conclusion:

```text
The same Recall@k does not mean the retrieval systems are equally good.
```

BM25 can retrieve relevant documents, but it may rank them lower.

Dense Retrieval and Hybrid Retrieval are better at placing the truly relevant documents near the top.

---

## 6. BM25 Failure Analysis

### 6.1 Query q1

Query:

```text
What is dense retrieval?
```

BM25 ranking:

```text
['d1', 'd3', 'd2']
```

The main correct document is:

```text
d2: Dense retrieval represents queries and documents as vectors and compares them using semantic similarity.
```

However, BM25 ranked `d2` at position 3.

Metrics:

```text
Recall@3 = 0.500
RR = 0.333
nDCG@3 = 0.459
```

Reason:

```text
BM25 mainly depends on lexical matching.
d1, d3, and d2 all contain retrieval-related terms.
BM25 does not fully understand the semantic meaning of dense retrieval.
```

Dense Retrieval ranking:

```text
['d2', 'd8', 'd3']
```

Dense Retrieval ranked `d2` first.

Therefore:

```text
RR = 1.000
nDCG@3 = 0.917
```

---

### 6.2 Query q5

Query:

```text
What is re-ranking used for?
```

BM25 ranking:

```text
['d8', 'd5', 'd1']
```

The correct document is:

```text
d5: Re-ranking improves the order of retrieved candidates using a more accurate but slower model.
```

BM25 ranked `d5` second.

Metrics:

```text
Recall@3 = 1.000
RR = 0.500
nDCG@3 = 0.631
```

This means:

```text
BM25 found the correct document, but did not rank it at the top.
```

Dense Retrieval and Hybrid Retrieval both ranked `d5` first:

```text
Dense: ['d5', 'd8', 'd2']
Hybrid: ['d5', 'd8', 'd1']
```

Therefore:

```text
RR = 1.000
nDCG@3 = 1.000
```

---

## 7. Hybrid Retrieval and Alpha Sensitivity

### 7.1 Hybrid Retrieval Formula

Hybrid Retrieval combines BM25 scores and Dense Retrieval scores:

```text
hybrid_score = alpha * dense_score + (1 - alpha) * bm25_score
```

Where:

```text
alpha = 0.0 → pure BM25
alpha = 1.0 → pure Dense Retrieval
```

A larger alpha gives more weight to Dense Retrieval.

A smaller alpha gives more weight to BM25.

---

### 7.2 Alpha Sensitivity Results

| alpha | Recall@3 | MRR | nDCG@3 |
|---:|---:|---:|---:|
| 0.00 | 0.900 | 0.767 | 0.818 |
| 0.25 | 0.900 | 0.867 | 0.892 |
| 0.50 | 0.900 | 1.000 | 0.983 |
| 0.75 | 0.900 | 1.000 | 0.983 |
| 1.00 | 0.900 | 1.000 | 0.983 |

---

### 7.3 Ranking Changes

q1:

```text
alpha = 0.00: ['d1', 'd3', 'd2']
alpha = 0.25: ['d1', 'd3', 'd2']
alpha = 0.50: ['d2', 'd1', 'd3']
alpha = 0.75: ['d2', 'd3', 'd1']
alpha = 1.00: ['d2', 'd8', 'd3']
```

q5:

```text
alpha = 0.00: ['d8', 'd5', 'd1']
alpha = 0.25: ['d5', 'd8', 'd1']
alpha = 0.50: ['d5', 'd8', 'd1']
alpha = 0.75: ['d5', 'd8', 'd1']
alpha = 1.00: ['d5', 'd8', 'd2']
```

---

### 7.4 Alpha Experiment Conclusion

When alpha = 0.0, Hybrid Retrieval is equivalent to pure BM25.

At this point, ranking quality is relatively poor:

```text
MRR = 0.767
nDCG@3 = 0.818
```

When alpha increases to 0.25, Dense Retrieval starts to correct the ranking error in q5:

```text
q5: d5 moves from rank 2 to rank 1
```

As a result:

```text
MRR: 0.767 → 0.867
nDCG@3: 0.818 → 0.892
```

When alpha reaches 0.5, the main relevant documents in q1 and q5 are both ranked first:

```text
MRR = 1.000
nDCG@3 = 0.983
```

Further increasing alpha to 0.75 or 1.0 does not improve the metrics.

This shows that:

```text
In this small dataset, Dense Retrieval is already strong enough.
alpha = 0.5 is sufficient to fix the main BM25 ranking errors.
Increasing the Dense weight further does not bring additional improvement.
```

Important conclusion:

```text
In this experiment, alpha mainly affects ranking quality rather than recall coverage.
```

Recall@3 remains unchanged:

```text
Recall@3 = 0.900
```

---

## 8. Re-ranking

### 8.1 Basic Idea

Re-ranking is a second-stage ranking process.

General structure:

```text
query
  ↓
first-stage retriever
  ↓
top-k candidates
  ↓
re-ranker
  ↓
reranked top results
```

First-stage retriever:

```text
Examples: BM25, Dense Retrieval, Hybrid Retrieval
Goal: quickly retrieve candidate documents from a large corpus
Main focus: Recall@k
```

Second-stage re-ranker:

```text
Example: Cross-Encoder
Goal: rank the candidate documents more accurately
Main focus: MRR, nDCG@k, Precision@k
```

---

### 8.2 Why Not Use the Re-ranker on the Whole Corpus?

Dense Retrieval usually uses a Bi-Encoder structure:

```text
query → embedding
document → embedding
similarity computation → ranking
```

Document embeddings can be precomputed and stored, so retrieval is efficient.

A Cross-Encoder re-ranker works differently:

```text
input: [query, document]
model reads query and document together
output: relevance score
```

It is more accurate, but each query-document pair must be processed separately by the model.

If the corpus contains 1 million documents, using a Cross-Encoder for full-corpus retrieval would require:

```text
1 million query-document model inference calls
```

This is too expensive.

Therefore, practical systems usually do this:

```text
Use a fast retriever to retrieve top 50 / top 100 / top 200 candidates.
Then use a Cross-Encoder to re-rank only those candidates.
Finally, select top 3 / top 5 documents for the RAG prompt.
```

---

## 9. BM25 + Cross-Encoder Re-ranking Experiment

### 9.1 Experimental Setup

```text
First-stage retriever: BM25
First-stage candidates: top 5
Re-ranker: cross-encoder/ms-marco-MiniLM-L-6-v2
Evaluation: top 3
```

---

### 9.2 Average Results

| Stage | Mean Recall@3 | MRR | Mean nDCG@3 |
|---|---:|---:|---:|
| BM25 before reranking | 0.900 | 0.767 | 0.818 |
| After Cross-Encoder reranking | 0.900 | 1.000 | 0.983 |

---

### 9.3 Result Analysis

After re-ranking:

```text
Mean Recall@3 did not change:
0.900 → 0.900

MRR improved:
0.767 → 1.000

Mean nDCG@3 improved:
0.818 → 0.983
```

This shows:

```text
Re-ranking does not mainly improve recall coverage.
Re-ranking mainly improves ranking quality.
```

The reason is that the re-ranker only reorders the candidates already retrieved by BM25. It does not search the full document corpus again.

---

### 9.4 q1 Analysis

Query:

```text
What is dense retrieval?
```

BM25 candidates:

```text
['d1', 'd3', 'd2', 'd8', 'd5']
```

Re-ranked candidates:

```text
['d2', 'd3', 'd1']
```

Before re-ranking:

```text
Recall@3 = 0.500
RR = 0.333
nDCG@3 = 0.459
```

After re-ranking:

```text
Recall@3 = 0.500
RR = 1.000
nDCG@3 = 0.917
```

Explanation:

```text
BM25 had already retrieved d2, but ranked it third.
The Cross-Encoder judged d2 as the most relevant document and moved it to rank 1.
Recall@3 did not change because top 3 still contained only one relevant document, d2, and did not contain d7.
MRR and nDCG improved because the main relevant document was moved to the top.
```

---

### 9.5 q5 Analysis

Query:

```text
What is re-ranking used for?
```

BM25 candidates:

```text
['d8', 'd5', 'd1', 'd7', 'd6']
```

Re-ranked candidates:

```text
['d5', 'd8', 'd7']
```

Before re-ranking:

```text
Recall@3 = 1.000
RR = 0.500
nDCG@3 = 0.631
```

After re-ranking:

```text
Recall@3 = 1.000
RR = 1.000
nDCG@3 = 1.000
```

Explanation:

```text
BM25 had already retrieved the correct document d5, but ranked it second.
The Cross-Encoder moved d5 to rank 1.
Therefore, RR and nDCG improved to 1.000.
```

---

## 10. Re-ranking Failure Case

### 10.1 Purpose

The goal of this experiment was to verify:

```text
If the first-stage retriever does not retrieve the correct document, the re-ranker cannot fix the problem.
```

In other words:

```text
A re-ranker can only reorder documents that already exist in the candidate set.
It cannot output documents that were not retrieved in the first stage.
```

---

### 10.2 Failure Case Setup

Query:

```text
What is dense retrieval?
```

Gold relevant documents:

```text
{d2, d7}
```

Full BM25 ranking:

```text
['d1', 'd3', 'd2', 'd8', 'd5', 'd6', 'd7', 'd4']
```

Set:

```text
first_stage_k = 2
```

BM25 candidates:

```text
['d1', 'd3']
```

Neither `d2` nor `d7` is included in the candidate set.

Re-ranked candidates:

```text
['d3', 'd1']
```

Before re-ranking:

```text
Recall@3 = 0.000
RR = 0.000
nDCG@3 = 0.000
```

After re-ranking:

```text
Recall@3 = 0.000
RR = 0.000
nDCG@3 = 0.000
```

Conclusion:

```text
Because the correct documents were missing from the candidate set, the re-ranker could not move them to the top.
```

---

### 10.3 Success Case Setup

Same query:

```text
What is dense retrieval?
```

Set:

```text
first_stage_k = 5
```

BM25 candidates:

```text
['d1', 'd3', 'd2', 'd8', 'd5']
```

This time, `d2` is included in the candidate set.

Re-ranked candidates:

```text
['d2', 'd3', 'd1']
```

Before re-ranking:

```text
Recall@3 = 0.500
RR = 0.333
nDCG@3 = 0.459
```

After re-ranking:

```text
Recall@3 = 0.500
RR = 1.000
nDCG@3 = 0.917
```

Conclusion:

```text
When the correct document is included in the candidate set, the re-ranker can significantly improve ranking quality.
However, it still cannot recover relevant documents that were not retrieved.
```

---

## 11. System Meaning of first_stage_k

`first_stage_k` is the number of candidate documents retrieved by the first-stage retriever.

If `first_stage_k` is too small:

```text
Advantage: faster
Disadvantage: more likely to miss relevant documents
Result: re-ranker cannot recover missing documents
```

If `first_stage_k` is too large:

```text
Advantage: higher recall
Disadvantage: higher re-ranking cost
Result: higher latency and resource usage
```

A practical system needs a trade-off:

```text
Common design:
first-stage retriever retrieves top 50 / top 100 / top 200 candidates
re-ranker reorders those candidates
final top 3 / top 5 documents are used in the RAG prompt
```

---

## 12. Key Understanding

### 12.1 Retrieval Evaluation

```text
Recall@k measures whether relevant documents are retrieved.
Precision@k measures whether the top-k results are clean.
MRR measures how early the first relevant document appears.
nDCG@k measures overall ranking quality, especially whether highly relevant documents are ranked early.
```

---

### 12.2 BM25, Dense Retrieval, and Hybrid Retrieval

```text
BM25 depends on lexical matching. It is fast but can be misled by surface-level word overlap.

Dense Retrieval uses embeddings and semantic similarity. It can better capture the semantic relationship between queries and documents.

Hybrid Retrieval combines sparse and dense scores. The alpha parameter controls the balance between BM25 and Dense Retrieval.
```

---

### 12.3 Alpha Sensitivity

```text
A larger alpha gives more weight to Dense Retrieval.
A smaller alpha gives more weight to BM25.
```

In this experiment:

```text
alpha = 0.5 achieved the best metrics.
Increasing alpha to 0.75 or 1.0 did not further improve the results.
```

This means:

```text
Dense Retrieval was already strong enough to correct the main BM25 ranking errors.
```

---

### 12.4 Re-ranking

```text
Re-ranking is a more fine-grained second-stage ranking process.
It usually uses a Cross-Encoder to evaluate query-document relevance more accurately.
```

Advantages of re-ranking:

```text
It can improve MRR.
It can improve nDCG.
It can move already-retrieved relevant documents to higher positions.
```

Limitations of re-ranking:

```text
It cannot retrieve documents that were missed by the first-stage retriever.
It cannot fix the problem if the candidate set does not contain the correct document.
It is computationally expensive and cannot usually be applied to the full corpus directly.
```

---

## 13. Summary of Experiments

Today I completed the following experiments:

1. Implemented Recall@k, Precision@k, MRR, and nDCG@k.
2. Manually analyzed how nDCG is calculated.
3. Compared BM25, Dense Retrieval, and Hybrid Retrieval.
4. Observed that the same Recall@3 can still lead to different MRR and nDCG values.
5. Conducted an alpha sensitivity experiment for Hybrid Retrieval.
6. Found that alpha mainly affected ranking quality rather than recall coverage.
7. Implemented BM25 first-stage retrieval with Cross-Encoder re-ranking.
8. Observed that re-ranking improved MRR and nDCG.
9. Built a failure case showing that re-ranking cannot recover documents missed by first-stage retrieval.

---

## 14. Final English Summary

Today I studied retrieval evaluation and re-ranking. I first implemented common retrieval metrics, including Recall@k, Precision@k, MRR, and nDCG@k. Recall@k measures whether relevant documents are retrieved, while MRR and nDCG focus more on ranking quality. I then compared BM25, Dense Retrieval, and Hybrid Retrieval on a small retrieval dataset. Although all three methods achieved the same Mean Recall@3 of 0.900, BM25 had lower MRR and nDCG@3, showing that it could retrieve relevant documents but often ranked them lower. Dense Retrieval and Hybrid Retrieval performed better because they captured semantic similarity more effectively.

I also conducted an alpha sensitivity experiment for Hybrid Retrieval. The results showed that increasing the dense retrieval weight improved ranking quality. When alpha reached 0.5, both MRR and nDCG@3 reached their best values. However, Recall@3 remained unchanged, indicating that alpha mainly affected ranking quality rather than recall coverage in this experiment.

Finally, I implemented a two-stage retrieval pipeline using BM25 as the first-stage retriever and a Cross-Encoder as the re-ranker. The re-ranker improved MRR from 0.767 to 1.000 and nDCG@3 from 0.818 to 0.983, while Recall@3 remained unchanged. This confirmed that re-ranking improves the order of retrieved candidates but does not recover documents that were not retrieved in the first stage. A failure case further showed that if the relevant document is missing from the candidate set, the re-ranker cannot fix the problem. Therefore, a good retrieval pipeline needs a high-recall first-stage retriever and a more accurate second-stage re-ranker.

---

## 15. Key Terms

| Term | Meaning |
|---|---|
| Retrieval Evaluation | Evaluation of retrieval system quality |
| Recall@k | Measures how many relevant documents are retrieved in the top-k results |
| Precision@k | Measures how many of the top-k results are relevant |
| MRR | Measures how early the first relevant document appears |
| nDCG@k | Measures ranking quality with graded relevance |
| BM25 | Sparse retrieval method based on term frequency and inverse document frequency |
| Dense Retrieval | Retrieval based on embedding similarity |
| Hybrid Retrieval | Retrieval method combining sparse and dense scores |
| alpha | Weight controlling the dense retrieval contribution in Hybrid Retrieval |
| Bi-Encoder | Encodes query and document separately, then compares embeddings |
| Cross-Encoder | Encodes query and document together and outputs a relevance score |
| Re-ranking | Second-stage ranking over retrieved candidates |
| Candidate Set | Documents retrieved by the first-stage retriever |
| First-stage Retriever | Fast retriever used to obtain candidate documents |
| Second-stage Re-ranker | More accurate model used to reorder candidate documents |