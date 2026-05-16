import numpy as np

from retrieval_eval_demo import (
    queries,
    gold_relevant,
    gold_scores,
    hybrid_search,
    recall_at_k,
    reciprocal_rank,
    ndcg_at_k,
)


def evaluate_alpha(alpha, k=3):
    recall_scores = []
    rr_scores = []
    ndcg_scores = []

    query_rankings = {}

    for query_id, query_text in queries.items():
        ranking, _ = hybrid_search(query_text, alpha=alpha)

        relevant_docs = gold_relevant[query_id]
        relevance_scores = gold_scores[query_id]

        recall = recall_at_k(ranking, relevant_docs, k)
        rr = reciprocal_rank(ranking, relevant_docs)
        ndcg = ndcg_at_k(ranking, relevance_scores, k)

        recall_scores.append(recall)
        rr_scores.append(rr)
        ndcg_scores.append(ndcg)

        query_rankings[query_id] = ranking[:k]

    return {
        "alpha": alpha,
        f"Recall@{k}": np.mean(recall_scores),
        "MRR": np.mean(rr_scores),
        f"nDCG@{k}": np.mean(ndcg_scores),
        "rankings": query_rankings,
    }


if __name__ == "__main__":
    alphas = [0.0, 0.25, 0.5, 0.75, 1.0]
    k = 3

    results = []

    print("========== Alpha Sensitivity Experiment ==========")
    print("alpha = 0.0 means pure BM25")
    print("alpha = 1.0 means pure Dense Retrieval\n")

    print(f"{'alpha':<8} {'Recall@3':<10} {'MRR':<10} {'nDCG@3':<10}")
    print("-" * 42)

    for alpha in alphas:
        result = evaluate_alpha(alpha, k=k)
        results.append(result)

        print(
            f"{result['alpha']:<8.2f} "
            f"{result['Recall@3']:<10.3f} "
            f"{result['MRR']:<10.3f} "
            f"{result['nDCG@3']:<10.3f}"
        )

    print("\n========== Important Query Rankings ==========")

    for result in results:
        alpha = result["alpha"]

        print(f"\nalpha = {alpha:.2f}")
        print("q1 ranking:", result["rankings"]["q1"])
        print("q5 ranking:", result["rankings"]["q5"])

    best_by_ndcg = max(results, key=lambda x: x["nDCG@3"])
    best_by_mrr = max(results, key=lambda x: x["MRR"])

    print("\n========== Best Results ==========")
    print(f"Best alpha by nDCG@3: {best_by_ndcg['alpha']}")
    print(f"Best nDCG@3: {best_by_ndcg['nDCG@3']:.3f}")

    print(f"Best alpha by MRR: {best_by_mrr['alpha']}")
    print(f"Best MRR: {best_by_mrr['MRR']:.3f}")