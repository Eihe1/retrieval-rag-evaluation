# Day 4 — Retrieval Systems and RAG Basics

## 1. BM25 Retrieval

### Key Ideas
- Sparse retrieval based on keyword overlap
- Uses term frequency and inverse document frequency
- Works well for exact keyword matching

### Problems
- Cannot understand semantic similarity
- Sensitive to stopwords
- Cannot understand abbreviations like ANN

### Experiment
Queries tested:
- what is ann search
- approximate nearest neighbor search
- semantic similarity

Observation:
BM25 ranking depends heavily on exact word overlap.

---

## 2. Dense Retrieval

### Key Ideas
- Converts query and documents into embedding vectors
- Uses cosine similarity for ranking
- Can capture semantic similarity

### Advantages
- Handles semantic meaning better
- Less affected by stopwords

### Problems
- May introduce semantic noise
- Exact entity matching can be weaker than BM25

### Experiment
Used:
- sentence-transformers
- all-MiniLM-L6-v2

Observation:
Dense retrieval successfully connected ANN search with approximate nearest neighbor search.

---

## 3. Hybrid Retrieval

### Formula

Hybrid = alpha * BM25 + (1 - alpha) * Dense

### Key Ideas
- Combine exact keyword matching and semantic retrieval
- Alpha controls retrieval preference

### Observation
- Higher alpha favors BM25
- Lower alpha favors semantic retrieval
- Stopword removal improves BM25 quality

---

## 4. Dynamic Alpha

### Key Ideas
Different query types may require different retrieval strategies.

Examples:
- Technical entities → larger alpha
- Natural language semantic questions → smaller alpha

Observation:
Real systems may dynamically adjust alpha according to query characteristics.

---

## 5. RAG Pipeline

### Basic Structure

User Query
↓
Retriever
↓
Top-k Documents
↓
Context Construction
↓
LLM Prompt

### Key Observation
Retrieval quality directly affects final generation quality.

---

## 6. top_k Analysis

### Observation
- Small top_k → cleaner context but lower recall
- Large top_k → more recall but more noise

### Tradeoff
Recall vs Noise

---

## 7. Main Understanding

Modern AI systems are not only LLMs.

They are:
- Retrieval systems
- Embedding models
- ANN indexes
- Re-ranking systems
- Databases
- LLM generation systems

working together as one pipeline.