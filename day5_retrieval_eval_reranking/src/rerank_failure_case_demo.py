from rerank_demo import (
    queries,
    documents,
    gold_relevant,
    gold_scores,
    bm25_search,
    rerank,
    recall_at_k,
    reciprocal_rank,
    ndcg_at_k,
)


def run_failure_case(query_id="q1", first_stage_k=2, eval_k=3):
    query_text = queries[query_id]
    relevant_docs = gold_relevant[query_id]
    relevance_scores = gold_scores[query_id]

    print("========== Re-ranking Failure Case ==========")
    print(f"Query: {query_text}")
    print(f"Gold relevant docs: {relevant_docs}")
    print(f"First-stage candidates: top {first_stage_k}")
    print(f"Evaluation: top {eval_k}")

    bm25_ranking = bm25_search(query_text)
    candidates = bm25_ranking[:first_stage_k]

    reranked_ranking, reranked_with_scores = rerank(query_text, candidates)

    print("\nFull BM25 ranking:")
    print(bm25_ranking)

    print("\nBM25 first-stage candidates:")
    print(candidates)

    print("\nReranked candidates:")
    print(reranked_ranking)

    print("\nReranker scores:")
    for doc_id, score in reranked_with_scores:
        print(f"  {doc_id}: {score:.4f} | {documents[doc_id]}")

    bm25_recall = recall_at_k(candidates, relevant_docs, eval_k)
    bm25_rr = reciprocal_rank(candidates, relevant_docs)
    bm25_ndcg = ndcg_at_k(candidates, relevance_scores, eval_k)

    rerank_recall = recall_at_k(reranked_ranking, relevant_docs, eval_k)
    rerank_rr = reciprocal_rank(reranked_ranking, relevant_docs)
    rerank_ndcg = ndcg_at_k(reranked_ranking, relevance_scores, eval_k)

    print("\nBefore reranking:")
    print(f"  Recall@{eval_k}: {bm25_recall:.3f}")
    print(f"  RR: {bm25_rr:.3f}")
    print(f"  nDCG@{eval_k}: {bm25_ndcg:.3f}")

    print("\nAfter reranking:")
    print(f"  Recall@{eval_k}: {rerank_recall:.3f}")
    print(f"  RR: {rerank_rr:.3f}")
    print(f"  nDCG@{eval_k}: {rerank_ndcg:.3f}")


def run_success_case(query_id="q1", first_stage_k=5, eval_k=3):
    query_text = queries[query_id]
    relevant_docs = gold_relevant[query_id]
    relevance_scores = gold_scores[query_id]

    print("\n\n========== Re-ranking Success Case ==========")
    print(f"Query: {query_text}")
    print(f"Gold relevant docs: {relevant_docs}")
    print(f"First-stage candidates: top {first_stage_k}")
    print(f"Evaluation: top {eval_k}")

    bm25_ranking = bm25_search(query_text)
    candidates = bm25_ranking[:first_stage_k]

    reranked_ranking, reranked_with_scores = rerank(query_text, candidates)

    print("\nBM25 first-stage candidates:")
    print(candidates)

    print("\nReranked candidates:")
    print(reranked_ranking[:eval_k])

    print("\nReranker scores:")
    for doc_id, score in reranked_with_scores:
        print(f"  {doc_id}: {score:.4f} | {documents[doc_id]}")

    bm25_recall = recall_at_k(candidates, relevant_docs, eval_k)
    bm25_rr = reciprocal_rank(candidates, relevant_docs)
    bm25_ndcg = ndcg_at_k(candidates, relevance_scores, eval_k)

    rerank_recall = recall_at_k(reranked_ranking, relevant_docs, eval_k)
    rerank_rr = reciprocal_rank(reranked_ranking, relevant_docs)
    rerank_ndcg = ndcg_at_k(reranked_ranking, relevance_scores, eval_k)

    print("\nBefore reranking:")
    print(f"  Recall@{eval_k}: {bm25_recall:.3f}")
    print(f"  RR: {bm25_rr:.3f}")
    print(f"  nDCG@{eval_k}: {bm25_ndcg:.3f}")

    print("\nAfter reranking:")
    print(f"  Recall@{eval_k}: {rerank_recall:.3f}")
    print(f"  RR: {rerank_rr:.3f}")
    print(f"  nDCG@{eval_k}: {rerank_ndcg:.3f}")


if __name__ == "__main__":
    run_failure_case(query_id="q1", first_stage_k=2, eval_k=3)
    run_success_case(query_id="q1", first_stage_k=5, eval_k=3)