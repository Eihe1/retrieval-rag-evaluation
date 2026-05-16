from rank_bm25 import BM25Okapi

docs = [
    "PostgreSQL uses a cost based optimizer to choose query plans.",
    "B-tree indexes are useful for range queries and equality search.",
    "Vector databases use approximate nearest neighbor search for embeddings.",
    "RAG combines retrieval and generation to answer questions with external knowledge.",
    "BM25 is a sparse retrieval method based on term frequency and inverse document frequency.",
    "Dense retrieval uses neural embeddings to capture semantic similarity."
]

tokenized_docs = [doc.lower().split() for doc in docs]

bm25 = BM25Okapi(tokenized_docs)

query = "semantic similarity"
tokenized_query = query.lower().split()

scores = bm25.get_scores(tokenized_query)

ranked_results = sorted(
    zip(docs, scores),
    key=lambda x: x[1],
    reverse=True
)

for rank, (doc, score) in enumerate(ranked_results, start=1):
    print(f"Rank {rank}: score={score:.4f}")
    print(doc)
    print()