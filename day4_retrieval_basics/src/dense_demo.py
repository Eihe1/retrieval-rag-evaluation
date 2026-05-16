from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

docs = [
    "PostgreSQL uses a cost based optimizer to choose query plans.",
    "B-tree indexes are useful for range queries and equality search.",
    "Vector databases use approximate nearest neighbor search for embeddings.",
    "RAG combines retrieval and generation to answer questions with external knowledge.",
    "BM25 is a sparse retrieval method based on term frequency and inverse document frequency.",
    "Dense retrieval uses neural embeddings to capture semantic similarity."
]

query = "semantic similarity"

model = SentenceTransformer("all-MiniLM-L6-v2")

doc_embeddings = model.encode(docs)
query_embedding = model.encode([query])

scores = cosine_similarity(query_embedding, doc_embeddings)[0]

ranked_results = sorted(
    zip(docs, scores),
    key=lambda x: x[1],
    reverse=True
)

for rank, (doc, score) in enumerate(ranked_results, start=1):
    print(f"Rank {rank}: score={score:.4f}")
    print(doc)
    print()