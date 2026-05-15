import math


def recall_at_k(ranking, relevant_docs, k):
    top_k = ranking[:k]
    hit_count = sum(1 for doc_id in top_k if doc_id in relevant_docs)

    if len(relevant_docs) == 0:
        return 0.0

    return hit_count / len(relevant_docs)


def precision_at_k(ranking, relevant_docs, k):
    top_k = ranking[:k]
    hit_count = sum(1 for doc_id in top_k if doc_id in relevant_docs)

    if k == 0:
        return 0.0

    return hit_count / k


def reciprocal_rank(ranking, relevant_docs):
    for index, doc_id in enumerate(ranking):
        rank = index + 1
        if doc_id in relevant_docs:
            return 1 / rank

    return 0.0


def dcg_at_k(ranking, relevance_scores, k):
    """
    relevance_scores:
    {
        "d1": 3,
        "d2": 2,
        "d3": 0
    }
    """
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


if __name__ == "__main__":
    ranking = ["d3", "d2", "d5", "d1", "d4"]
    relevant_docs = {"d2", "d4"}

    relevance_scores = {
        "d1": 0,
        "d2": 2,
        "d3": 0,
        "d4": 3,
        "d5": 1
    }

    print("Ranking:", ranking)
    print("Relevant docs:", relevant_docs)

    print("\n=== Binary relevance metrics ===")
    print("Recall@1:", recall_at_k(ranking, relevant_docs, 1))
    print("Recall@3:", recall_at_k(ranking, relevant_docs, 3))
    print("Recall@5:", recall_at_k(ranking, relevant_docs, 5))

    print("Precision@1:", precision_at_k(ranking, relevant_docs, 1))
    print("Precision@3:", precision_at_k(ranking, relevant_docs, 3))
    print("Precision@5:", precision_at_k(ranking, relevant_docs, 5))

    print("Reciprocal Rank:", reciprocal_rank(ranking, relevant_docs))

    print("\n=== Graded relevance metric ===")
    print("nDCG@3:", ndcg_at_k(ranking, relevance_scores, 3))
    print("nDCG@5:", ndcg_at_k(ranking, relevance_scores, 5))