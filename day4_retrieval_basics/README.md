# Day 4 - Retrieval Systems and RAG Basics

This folder contains basic retrieval experiments for understanding how retrieval systems work in RAG-style pipelines.

The goal of Day 4 was to move from database indexing concepts toward modern retrieval systems used in AI applications.

The current implementation is intentionally small and interpretable. It should be understood as a learning and research-preparation prototype, not as a production retrieval system.

---

## Implementation Scope

This folder includes:

- BM25-style lexical retrieval
- Lightweight semantic-proxy retrieval
- Hybrid retrieval
- Stopword handling
- Dynamic alpha intuition
- Basic RAG context construction
- top_k trade-off

The semantic-proxy retrieval component is not a production embedding-based dense retriever. It is a lightweight proxy signal used to study how a second matching signal can complement lexical retrieval.

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

Note: if `dense_demo.py` is kept as a legacy file name, it should be interpreted as the semantic-proxy retrieval demo in this prototype. It should not be described as a sentence-transformer dense retrieval implementation unless the code is later upgraded to use embedding vectors and cosine similarity.

---

## Files

### `src/bm25_demo.py`

BM25-style lexical retrieval demo.

It shows how BM25-style scoring ranks documents based on lexical overlap, term frequency, inverse document frequency, and document length normalization.

### `src/dense_demo.py`

Lightweight semantic-proxy retrieval demo.

In the current prototype, this component provides an interpretable proxy signal for softer matching. It is used to study how an additional retrieval signal can complement BM25-style lexical retrieval.

This file should not be described as a production dense retriever unless it is later upgraded to use an embedding model, vector representations, and cosine or dot-product similarity.

### `src/hybrid_demo.py`

Hybrid retrieval demo.

It combines BM25-style lexical scores and semantic-proxy scores with an alpha parameter.

### `src/rag_demo.py`

Basic RAG context construction demo.

It retrieves top-k documents and builds context for downstream answer generation.

### `notes/day4_retrieval_systems_and_rag_basics.md`

Learning notes for Day 4.

---

## Main Concepts

### BM25-style Lexical Retrieval

BM25-style retrieval is a sparse retrieval method based on lexical matching.

It works well when query words overlap with document words.

Strengths:

- Strong for exact keyword matching
- Useful for technical terms and entities
- Interpretable scoring behavior

Limitations:

- Cannot fully understand semantic similarity
- Sensitive to vocabulary mismatch
- Weak at handling abbreviations or paraphrases

---

### Lightweight Semantic-Proxy Retrieval

The semantic-proxy retrieval component provides a second retrieval signal beyond direct lexical matching.

In this project version, it is deliberately simple and interpretable. It should be treated as a proxy for semantic matching, not as a full dense retrieval system.

Purpose:

- Provide a complementary matching signal
- Support controlled comparison with lexical retrieval
- Help analyze when hybrid retrieval can improve ranking
- Keep the retrieval behavior inspectable on a toy corpus

Limitations:

- Not embedding-based
- Not a sentence-transformer retriever
- Not backed by FAISS or pgvector
- Not suitable as a production semantic retrieval method

---

### Hybrid Retrieval

Hybrid retrieval combines BM25-style lexical retrieval and semantic-proxy retrieval.

General form:

```text
hybrid_score = alpha * lexical_score + (1 - alpha) * semantic_proxy_score
```

The alpha value controls the balance between lexical matching and the semantic-proxy signal.

A larger alpha gives more weight to BM25-style lexical retrieval.

A smaller alpha gives more weight to the semantic-proxy signal.

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

If top_k is too small, the correct evidence may be missed.

If top_k is too large, irrelevant context may distract the answer generator.

---

## Main Finding

BM25-style retrieval, semantic-proxy retrieval, and hybrid retrieval each have different strengths.

BM25-style retrieval is strong for exact keyword matching. The semantic-proxy signal can provide complementary behavior for less exact matching. Hybrid retrieval can combine both signals, but the best alpha value depends on the query.

The key lesson is:

```text
RAG quality depends not only on the language model, but also on retrieval, ranking, context construction, and evidence selection.
```

---

## Limitations

Current limitations:

- Small toy corpus
- Simplified preprocessing
- Lightweight semantic proxy instead of production dense retrieval
- No sentence-transformer embedding pipeline
- No ANN index
- No pgvector-backed retrieval
- No large-scale benchmark evaluation

---

## Future Work

Possible next steps:

- Replace the semantic proxy with sentence-transformer embeddings
- Add cosine similarity over dense vectors
- Evaluate with larger corpora
- Add FAISS or pgvector for vector search
- Learn query-dependent alpha values
- Connect retrieval confidence to adaptive RAG routing

---

## Summary

Day 4 establishes the retrieval foundation for the later RAG experiments.

It compares BM25-style lexical retrieval, lightweight semantic-proxy retrieval, and hybrid score fusion. The main finding is that different query types benefit from different retrieval signals, motivating adaptive and query-aware retrieval strategies in later days.
