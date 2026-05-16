# Day 4 - Retrieval Systems and RAG Basics

This folder contains basic retrieval experiments for understanding how retrieval systems work in RAG-style pipelines.

The goal of Day 4 was to move from database indexing concepts toward modern retrieval systems used in AI applications.

---

## Topics

- BM25 sparse retrieval
- Dense retrieval
- Hybrid retrieval
- Stopword handling
- Dynamic alpha intuition
- Basic RAG context construction
- top_k trade-off

---

## Folder Structure

```text
day4_retrieval_basics/
│
├── README.md
│
├── src/
│   ├── bm25_demo.py
│   ├── dense_demo.py
│   ├── hybrid_demo.py
│   └── rag_demo.py
│
└── notes/
    └── day4_retrieval_systems_and_rag_basics.md
```

---

## Files

### `src/bm25_demo.py`

BM25 sparse retrieval demo.

It shows how BM25 ranks documents based on keyword overlap, term frequency, and inverse document frequency.

### `src/dense_demo.py`

Dense retrieval demo using sentence-transformers.

It converts documents and queries into embedding vectors and ranks documents using cosine similarity.

### `src/hybrid_demo.py`

Hybrid retrieval demo.

It combines BM25 scores and dense retrieval scores with an alpha parameter.

### `src/rag_demo.py`

Basic RAG context construction demo.

It retrieves top-k documents and builds context for downstream answer generation.

### `notes/day4_retrieval_systems_and_rag_basics.md`

Learning notes for Day 4.

---

## Main Concepts

### BM25 Retrieval

BM25 is a sparse retrieval method based on exact lexical matching.

It works well when query words overlap with document words.

Limitations:

- Cannot fully understand semantic similarity
- Sensitive to stopwords
- Weak at handling abbreviations or paraphrases

---

### Dense Retrieval

Dense retrieval represents queries and documents as vectors.

It can retrieve semantically related documents even when exact words do not match.

Advantages:

- Captures semantic similarity
- Less dependent on exact word overlap
- Useful for natural language queries

Limitations:

- May introduce semantic noise
- Can be weaker for exact entity matching

---

### Hybrid Retrieval

Hybrid retrieval combines sparse retrieval and dense retrieval.

General form:

```text
hybrid_score = alpha * BM25_score + (1 - alpha) * dense_score
```

The alpha value controls the balance between lexical matching and semantic matching.

---

### top_k Trade-off

The top_k parameter controls how many documents are used as context.

Small top_k:

```text
Cleaner context
Lower recall
```

Large top_k:

```text
Higher recall
More noise
```

This is an important trade-off in RAG systems.

---

## Main Finding

BM25, Dense Retrieval, and Hybrid Retrieval each have different strengths.

BM25 is strong for exact keyword matching. Dense retrieval is better for semantic similarity. Hybrid retrieval can combine both signals.

The key lesson is that modern RAG systems are not only LLMs. They also depend on retrieval systems, embeddings, ranking methods, and context construction.