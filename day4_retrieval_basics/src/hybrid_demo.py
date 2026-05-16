from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

docs = [
    "PostgreSQL uses a cost based optimizer to choose query plans.",
    "B-tree indexes are useful for range queries and equality search.",
    "Vector databases use approximate nearest neighbor search for embeddings.",
    "RAG combines retrieval and generation to answer questions with external knowledge.",
    "BM25 is a sparse retrieval method based on term frequency and inverse document frequency.",
    "Dense retrieval uses neural embeddings to capture semantic similarity."
]

query = "what is ann search"

# BM25
stopwords = {"what", "is", "the", "a", "an", "of", "to", "for", "and", "with"}

def tokenize(text):
    return [
        word.strip(".,!?;:").lower()
        for word in text.split()
        if word.strip(".,!?;:").lower() not in stopwords
    ]

tokenized_docs = [tokenize(doc) for doc in docs]
tokenized_query = tokenize(query)

bm25 = BM25Okapi(tokenized_docs)
bm25_scores = bm25.get_scores(tokenized_query)

# Dense
model = SentenceTransformer("all-MiniLM-L6-v2")
doc_embeddings = model.encode(docs)
query_embedding = model.encode([query])
dense_scores = cosine_similarity(query_embedding, doc_embeddings)[0]

# Normalize scores to 0-1
bm25_norm = bm25_scores / np.max(bm25_scores) if np.max(bm25_scores) > 0 else bm25_scores
dense_norm = dense_scores / np.max(dense_scores) if np.max(dense_scores) > 0 else dense_scores

# Hybrid score
for alpha in [0.0, 0.3, 0.5, 0.7, 1.0]:
    hybrid_scores = alpha * bm25_norm + (1 - alpha) * dense_norm

    ranked_results = sorted(
        zip(docs, bm25_norm, dense_norm, hybrid_scores),
        key=lambda x: x[3],
        reverse=True
    )

    print(f"\nAlpha = {alpha}")
    for rank, (doc, bm25_score, dense_score, hybrid_score) in enumerate(ranked_results[:3], start=1):
        print(f"Rank {rank}: Hybrid={hybrid_score:.4f}")
        print(doc)