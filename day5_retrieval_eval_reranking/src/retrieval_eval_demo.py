import math
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# Evaluation Metrics
# =========================

def recall_at_k(ranking, relevant_docs, k):
    top_k = ranking[:k]
    hit_count = sum(1 for doc_id in top_k if doc_id in relevant_docs)

    if len(relevant_docs) == 0:
        return 0.0

    return hit_count / len(relevant_docs)


def reciprocal_rank(ranking, relevant_docs):
    for index, doc_id in enumerate(ranking):
        rank = index + 1
        if doc_id in relevant_docs:
            return 1 / rank

    return 0.0


def dcg_at_k(ranking, relevance_scores, k):
    score = 0.0

    for index, doc_id in enumerate(ranking[:k]):
        rank = index + 1
        relevance = relevance_scores.get(doc_id, 0)

        gain = (2 ** relevance - 1)
        discount = math.log2(rank + 1)

        score += gain / discount

    return score


def ndcg_at_k(ranking, relevance_scores, k):
    actual_dcg = dcg_at_k(ranking, relevance_scores, k)

    ideal_ranking = sorted(
        relevance_scores.keys(),
        key=lambda doc_id: relevance_scores[doc_id],
        reverse=True
    )

    ideal_dcg = dcg_at_k(ideal_ranking, relevance_scores, k)

    if ideal_dcg == 0:
        return 0.0

    return actual_dcg / ideal_dcg


# =========================
# Data
# =========================

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

queries = {
    "q1": "What is dense retrieval?",
    "q2": "How does RAG use retrieved documents?",
    "q3": "What does hybrid retrieval combine?",
    "q4": "How can retrieval quality be evaluated?",
    "q5": "What is re-ranking used for?",
}

# Binary relevant documents
gold_relevant = {
    "q1": {"d2", "d7"},
    "q2": {"d4"},
    "q3": {"d3"},
    "q4": {"d8"},
    "q5": {"d5"},
}

# Graded relevance scores
gold_scores = {
    "q1": {"d2": 3, "d7": 1},
    "q2": {"d4": 3},
    "q3": {"d3": 3},
    "q4": {"d8": 3},
    "q5": {"d5": 3},
}


doc_ids = list(documents.keys())
doc_texts = [documents[doc_id] for doc_id in doc_ids]


# =========================
# BM25 Retriever
# =========================

def tokenize(text):
    return text.lower().split()


tokenized_docs = [tokenize(text) for text in doc_texts]
bm25 = BM25Okapi(tokenized_docs)


def bm25_search(query):
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)

    ranked_indices = np.argsort(scores)[::-1]
    ranking = [doc_ids[i] for i in ranked_indices]

    return ranking, scores


# =========================
# Dense Retriever
# =========================

model = SentenceTransformer("all-MiniLM-L6-v2")
doc_embeddings = model.encode(doc_texts, normalize_embeddings=True)


def dense_search(query):
    query_embedding = model.encode([query], normalize_embeddings=True)
    scores = cosine_similarity(query_embedding, doc_embeddings)[0]

    ranked_indices = np.argsort(scores)[::-1]
    ranking = [doc_ids[i] for i in ranked_indices]

    return ranking, scores


# =========================
# Hybrid Retriever
# =========================

def normalize_scores(scores):
    scores = np.array(scores)

    min_score = scores.min()
    max_score = scores.max()

    if max_score == min_score:
        return np.zeros_like(scores)

    return (scores - min_score) / (max_score - min_score)


def hybrid_search(query, alpha=0.5):
    _, bm25_scores = bm25_search(query)
    _, dense_scores = dense_search(query)

    bm25_norm = normalize_scores(bm25_scores)
    dense_norm = normalize_scores(dense_scores)

    hybrid_scores = alpha * dense_norm + (1 - alpha) * bm25_norm

    ranked_indices = np.argsort(hybrid_scores)[::-1]
    ranking = [doc_ids[i] for i in ranked_indices]

    return ranking, hybrid_scores


# =========================
# Evaluation
# =========================

def evaluate_retriever(name, search_function, k=3):
    recall_scores = []
    rr_scores = []
    ndcg_scores = []

    print(f"\n========== {name} ==========")

    for query_id, query_text in queries.items():
        ranking, _ = search_function(query_text)

        relevant_docs = gold_relevant[query_id]
        relevance_scores = gold_scores[query_id]

        recall = recall_at_k(ranking, relevant_docs, k)
        rr = reciprocal_rank(ranking, relevant_docs)
        ndcg = ndcg_at_k(ranking, relevance_scores, k)

        recall_scores.append(recall)
        rr_scores.append(rr)
        ndcg_scores.append(ndcg)

        print(f"\nQuery {query_id}: {query_text}")
        print("Ranking:", ranking[:k])
        print(f"Recall@{k}: {recall:.3f}")
        print(f"RR: {rr:.3f}")
        print(f"nDCG@{k}: {ndcg:.3f}")

    print(f"\n{name} Average Results:")
    print(f"Mean Recall@{k}: {np.mean(recall_scores):.3f}")
    print(f"MRR: {np.mean(rr_scores):.3f}")
    print(f"Mean nDCG@{k}: {np.mean(ndcg_scores):.3f}")


if __name__ == "__main__":
    evaluate_retriever("BM25", bm25_search, k=3)
    evaluate_retriever("Dense Retrieval", dense_search, k=3)
    evaluate_retriever("Hybrid Retrieval alpha=0.5", lambda q: hybrid_search(q, alpha=0.5), k=3)