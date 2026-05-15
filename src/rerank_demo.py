import math
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder


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

gold_relevant = {
    "q1": {"d2", "d7"},
    "q2": {"d4"},
    "q3": {"d3"},
    "q4": {"d8"},
    "q5": {"d5"},
}

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
# BM25 First-stage Retriever
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

    return ranking


# =========================
# Cross-Encoder Re-ranker
# =========================

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(query, candidate_doc_ids):
    pairs = []

    for doc_id in candidate_doc_ids:
        pairs.append([query, documents[doc_id]])

    scores = reranker.predict(pairs)

    sorted_candidates = sorted(
        zip(candidate_doc_ids, scores),
        key=lambda x: x[1],
        reverse=True
    )

    reranked_doc_ids = [doc_id for doc_id, score in sorted_candidates]

    return reranked_doc_ids, sorted_candidates


# =========================
# Evaluation
# =========================

def evaluate_bm25_vs_rerank(first_stage_k=5, eval_k=3):
    bm25_recall_scores = []
    bm25_rr_scores = []
    bm25_ndcg_scores = []

    rerank_recall_scores = []
    rerank_rr_scores = []
    rerank_ndcg_scores = []

    print("========== BM25 First-stage + Cross-Encoder Re-ranking ==========")
    print(f"First-stage candidates: top {first_stage_k}")
    print(f"Evaluation: top {eval_k}")

    for query_id, query_text in queries.items():
        bm25_ranking = bm25_search(query_text)
        candidates = bm25_ranking[:first_stage_k]

        reranked_ranking, reranked_with_scores = rerank(query_text, candidates)

        relevant_docs = gold_relevant[query_id]
        relevance_scores = gold_scores[query_id]

        bm25_recall = recall_at_k(bm25_ranking, relevant_docs, eval_k)
        bm25_rr = reciprocal_rank(bm25_ranking, relevant_docs)
        bm25_ndcg = ndcg_at_k(bm25_ranking, relevance_scores, eval_k)

        rerank_recall = recall_at_k(reranked_ranking, relevant_docs, eval_k)
        rerank_rr = reciprocal_rank(reranked_ranking, relevant_docs)
        rerank_ndcg = ndcg_at_k(reranked_ranking, relevance_scores, eval_k)

        bm25_recall_scores.append(bm25_recall)
        bm25_rr_scores.append(bm25_rr)
        bm25_ndcg_scores.append(bm25_ndcg)

        rerank_recall_scores.append(rerank_recall)
        rerank_rr_scores.append(rerank_rr)
        rerank_ndcg_scores.append(rerank_ndcg)

        print(f"\nQuery {query_id}: {query_text}")
        print("BM25 top candidates:", candidates)
        print("Reranked candidates:", reranked_ranking[:eval_k])

        print("\nReranker scores:")
        for doc_id, score in reranked_with_scores:
            print(f"  {doc_id}: {score:.4f} | {documents[doc_id]}")

        print("\nBefore reranking:")
        print(f"  Recall@{eval_k}: {bm25_recall:.3f}")
        print(f"  RR: {bm25_rr:.3f}")
        print(f"  nDCG@{eval_k}: {bm25_ndcg:.3f}")

        print("After reranking:")
        print(f"  Recall@{eval_k}: {rerank_recall:.3f}")
        print(f"  RR: {rerank_rr:.3f}")
        print(f"  nDCG@{eval_k}: {rerank_ndcg:.3f}")

    print("\n========== Average Results ==========")

    print("\nBM25 before reranking:")
    print(f"Mean Recall@{eval_k}: {np.mean(bm25_recall_scores):.3f}")
    print(f"MRR: {np.mean(bm25_rr_scores):.3f}")
    print(f"Mean nDCG@{eval_k}: {np.mean(bm25_ndcg_scores):.3f}")

    print("\nAfter Cross-Encoder reranking:")
    print(f"Mean Recall@{eval_k}: {np.mean(rerank_recall_scores):.3f}")
    print(f"MRR: {np.mean(rerank_rr_scores):.3f}")
    print(f"Mean nDCG@{eval_k}: {np.mean(rerank_ndcg_scores):.3f}")


if __name__ == "__main__":
    evaluate_bm25_vs_rerank(first_stage_k=5, eval_k=3)