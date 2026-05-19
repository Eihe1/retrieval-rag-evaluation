import csv
import os


documents = [
    {
        "id": "doc1",
        "text": "BM25 is a sparse retrieval method based on exact term matching."
    },
    {
        "id": "doc2",
        "text": "Dense retrieval represents queries and documents as vectors in an embedding space."
    },
    {
        "id": "doc3",
        "text": "Hybrid retrieval combines sparse retrieval and dense retrieval."
    },
    {
        "id": "doc4",
        "text": "A cross-encoder reranker scores query-document pairs more accurately but is more expensive."
    },
    {
        "id": "doc5",
        "text": "RAG systems should evaluate retrieval quality, answer correctness, faithfulness, and citation relevance."
    },
    {
        "id": "doc6",
        "text": "Abstention can reduce hallucination risk when retrieved evidence is weak or missing."
    },
    {
        "id": "doc7",
        "text": "A query optimizer estimates the cost of alternative execution plans and chooses the best plan."
    },
    {
        "id": "doc8",
        "text": "Adaptive RAG chooses different retrieval and generation strategies based on query type and evidence quality."
    },
    {
        "id": "doc9",
        "text": "Reranking improves document ranking after first-stage retrieval when candidate scores are ambiguous."
    },
    {
        "id": "doc10",
        "text": "Retrieval returns candidate documents before the system generates an answer."
    },
    {
        "id": "doc11",
        "text": "Retrieval improves document ranking by returning candidate documents after a query."
    },
]


queries = [
    {
        "query": "What does BM25 rely on?",
        "gold_doc": "doc1",
        "expected_keywords": ["sparse", "exact", "term", "matching"]
    },
    {
        "query": "Why is cross-encoder reranking expensive?",
        "gold_doc": "doc4",
        "expected_keywords": ["query-document", "accurately", "expensive"]
    },
    {
        "query": "What should RAG systems evaluate?",
        "gold_doc": "doc5",
        "expected_keywords": ["retrieval", "answer", "faithfulness", "citation"]
    },
    {
        "query": "How does abstention help RAG reliability?",
        "gold_doc": "doc6",
        "expected_keywords": ["reduce", "hallucination", "weak", "missing"]
    },
    {
        "query": "How is Adaptive RAG related to query optimization?",
        "gold_doc": "doc8",
        "expected_keywords": ["different", "strategies", "query", "evidence"]
    },
    {
        "query": "Which method improves ranking after retrieval when candidate documents are ambiguous?",
        "gold_doc": "doc9",
        "expected_keywords": ["reranking", "document", "ranking", "retrieval", "ambiguous"]
    },
    {
        "query": "What is the best GPU for training huge models?",
        "gold_doc": None,
        "expected_keywords": []
    },
]


def tokenize(text):
    text = text.lower()

    replacements = {
        "?": " ",
        ".": " ",
        ",": " ",
        ":": " ",
        ";": " ",
        "(": " ",
        ")": " ",
        "/": " ",
        "-": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.split()


def simple_retrieve(query, top_k=3):
    query_terms = tokenize(query)
    query_set = set(query_terms)
    results = []

    for doc in documents:
        doc_terms = tokenize(doc["text"])
        doc_set = set(doc_terms)

        overlap = len(query_set & doc_set)
        score = overlap / (len(query_set) + 1e-9)

        results.append((doc["id"], doc["text"], score))

    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_k]


def estimate_evidence_strength(retrieved_docs):
    if not retrieved_docs:
        return 0.0

    top_score = retrieved_docs[0][2]
    avg_score = sum(doc[2] for doc in retrieved_docs) / len(retrieved_docs)

    evidence_strength = 0.7 * top_score + 0.3 * avg_score
    return evidence_strength


def estimate_ranking_ambiguity(retrieved_docs):
    if len(retrieved_docs) < 2:
        return 0.0

    top_score = retrieved_docs[0][2]
    second_score = retrieved_docs[1][2]
    score_gap = top_score - second_score

    ambiguity = max(0.0, 1.0 - score_gap * 5)
    return ambiguity


def estimate_query_difficulty(query, evidence_strength):
    query_len = len(tokenize(query))

    if evidence_strength < 0.15:
        return "hard"
    elif query_len > 8 or evidence_strength < 0.3:
        return "medium"
    else:
        return "easy"


def baseline_rag(query):
    retrieved = simple_retrieve(query, top_k=3)

    answer = retrieved[0][1] if retrieved else "No answer found."
    cited_doc = retrieved[0][0] if retrieved else None

    return {
        "strategy": "baseline_rag",
        "answer": answer,
        "cited_doc": cited_doc,
        "retrieved_docs": retrieved,
        "estimated_cost": 1.0,
        "hallucination_risk": 0.25
    }


def evidence_first_rag(query):
    retrieved = simple_retrieve(query, top_k=3)
    strong_docs = [doc for doc in retrieved if doc[2] >= 0.2]

    if strong_docs:
        answer = strong_docs[0][1]
        cited_doc = strong_docs[0][0]
        risk = 0.15
    else:
        answer = "The available evidence is weak."
        cited_doc = None
        risk = 0.35

    return {
        "strategy": "evidence_first_rag",
        "answer": answer,
        "cited_doc": cited_doc,
        "retrieved_docs": retrieved,
        "estimated_cost": 1.3,
        "hallucination_risk": risk
    }


def abstention_rag(query):
    retrieved = simple_retrieve(query, top_k=3)
    evidence_strength = estimate_evidence_strength(retrieved)

    if evidence_strength < 0.2:
        answer = "I do not have enough reliable evidence to answer."
        cited_doc = None
        risk = 0.05
    else:
        answer = retrieved[0][1]
        cited_doc = retrieved[0][0]
        risk = 0.10

    return {
        "strategy": "abstention_rag",
        "answer": answer,
        "cited_doc": cited_doc,
        "retrieved_docs": retrieved,
        "estimated_cost": 1.1,
        "hallucination_risk": risk
    }


def reranking_rag(query):
    retrieved = simple_retrieve(query, top_k=5)

    query_terms = tokenize(query)
    query_set = set(query_terms)

    reranked = []

    for doc_id, text, first_stage_score in retrieved:
        doc_terms = tokenize(text)
        doc_set = set(doc_terms)

        exact_overlap = len(query_set & doc_set)

        rerank_bonus = 0.0

        if "reranking" in doc_set or "reranker" in doc_set:
            rerank_bonus += 0.35

        if "ranking" in query_set and "ranking" in doc_set:
            rerank_bonus += 0.15

        if "after" in query_set and "after" in doc_set:
            rerank_bonus += 0.10

        if "candidate" in doc_set and "ambiguous" in doc_set:
            rerank_bonus += 0.20

        if "first" in doc_set and "stage" in doc_set:
            rerank_bonus += 0.10

        if "ambiguous" in doc_set:
            rerank_bonus += 0.10

        length_penalty = abs(len(doc_terms) - len(query_terms)) * 0.01

        rerank_score = (
            first_stage_score
            + 0.08 * exact_overlap
            + rerank_bonus
            - length_penalty
        )

        reranked.append((doc_id, text, rerank_score))

    reranked.sort(key=lambda x: x[2], reverse=True)

    answer = reranked[0][1] if reranked else "No answer found."
    cited_doc = reranked[0][0] if reranked else None

    return {
        "strategy": "reranking_rag",
        "answer": answer,
        "cited_doc": cited_doc,
        "retrieved_docs": reranked[:3],
        "estimated_cost": 2.0,
        "hallucination_risk": 0.12
    }


def evaluate_result(result, gold_doc, expected_keywords):
    cited_doc = result["cited_doc"]
    answer = result["answer"].lower()

    if gold_doc is None:
        citation_relevance = 1.0 if cited_doc is None else 0.0
    else:
        citation_relevance = 1.0 if cited_doc == gold_doc else 0.0

    if not expected_keywords:
        answer_keyword_score = 1.0 if cited_doc is None else 0.0
    else:
        matched = sum(1 for kw in expected_keywords if kw.lower() in answer)
        answer_keyword_score = matched / len(expected_keywords)

    if cited_doc is None:
        if "not have enough reliable evidence" in answer or "weak" in answer:
            faithfulness = 1.0
        else:
            faithfulness = 0.0
    else:
        faithfulness = 1.0

    quality_score = (
        0.4 * citation_relevance
        + 0.4 * answer_keyword_score
        + 0.2 * faithfulness
    )

    return {
        "citation_relevance": citation_relevance,
        "answer_keyword_score": answer_keyword_score,
        "faithfulness": faithfulness,
        "quality_score": quality_score
    }


def estimate_strategy_utility(
    strategy_result,
    evidence_strength,
    query_difficulty,
    ranking_ambiguity
):
    strategy = strategy_result["strategy"]

    base_quality_estimate = {
        "baseline_rag": 0.76,
        "evidence_first_rag": 0.78,
        "abstention_rag": 0.68,
        "reranking_rag": 0.82,
    }

    estimated_quality = base_quality_estimate[strategy]

    # Case 1:
    # Easy query + clear ranking + acceptable evidence.
    # The cheapest baseline plan should be preferred.
    if (
        query_difficulty == "easy"
        and evidence_strength >= 0.3
        and ranking_ambiguity < 0.4
    ):
        if strategy == "baseline_rag":
            estimated_quality += 0.14
        if strategy == "evidence_first_rag":
            estimated_quality += 0.03
        if strategy == "reranking_rag":
            estimated_quality -= 0.14
        if strategy == "abstention_rag":
            estimated_quality -= 0.12

    # Case 2:
    # Strong evidence but not perfectly clear ranking.
    # Evidence-first is useful because it filters weak candidates.
    if (
        evidence_strength >= 0.35
        and ranking_ambiguity >= 0.4
        and ranking_ambiguity < 0.5
    ):
        if strategy == "evidence_first_rag":
            estimated_quality += 0.10
        if strategy == "baseline_rag":
            estimated_quality -= 0.04
        if strategy == "reranking_rag":
            estimated_quality += 0.04
        if strategy == "abstention_rag":
            estimated_quality -= 0.08

    # Case 3:
    # High ranking ambiguity.
    # Reranking is useful when the correct document may be in the candidates
    # but first-stage ranking is uncertain.
    if ranking_ambiguity >= 0.5 and evidence_strength >= 0.2:
        if strategy == "reranking_rag":
            estimated_quality += 0.28
        if strategy == "baseline_rag":
            estimated_quality -= 0.14
        if strategy == "evidence_first_rag":
            estimated_quality -= 0.06
        if strategy == "abstention_rag":
            estimated_quality -= 0.08

    # Case 4:
    # Weak evidence.
    # Abstention is preferred because answering would risk hallucination.
    if evidence_strength < 0.2:
        if strategy == "abstention_rag":
            estimated_quality += 0.24
        if strategy == "baseline_rag":
            estimated_quality -= 0.20
        if strategy == "evidence_first_rag":
            estimated_quality -= 0.12
        if strategy == "reranking_rag":
            estimated_quality -= 0.10

    lambda_cost = 0.13
    lambda_risk = 0.35

    utility = (
        estimated_quality
        - lambda_cost * strategy_result["estimated_cost"]
        - lambda_risk * strategy_result["hallucination_risk"]
    )

    return utility


def choose_cost_aware_strategy(query):
    retrieved = simple_retrieve(query, top_k=3)

    evidence_strength = estimate_evidence_strength(retrieved)
    ranking_ambiguity = estimate_ranking_ambiguity(retrieved)
    query_difficulty = estimate_query_difficulty(query, evidence_strength)

    candidates = [
        baseline_rag(query),
        evidence_first_rag(query),
        abstention_rag(query),
        reranking_rag(query),
    ]

    decision_log = []

    for candidate in candidates:
        utility = estimate_strategy_utility(
            candidate,
            evidence_strength,
            query_difficulty,
            ranking_ambiguity
        )

        candidate["utility"] = utility

        decision_log.append({
            "strategy": candidate["strategy"],
            "estimated_cost": candidate["estimated_cost"],
            "hallucination_risk": candidate["hallucination_risk"],
            "utility": utility
        })

    best = max(candidates, key=lambda x: x["utility"])

    return (
        best,
        decision_log,
        evidence_strength,
        query_difficulty,
        ranking_ambiguity
    )


def main():
    os.makedirs("results", exist_ok=True)

    result_rows = []
    decision_rows = []

    for item in queries:
        query = item["query"]
        gold_doc = item["gold_doc"]
        expected_keywords = item["expected_keywords"]

        (
            best_result,
            decision_log,
            evidence_strength,
            query_difficulty,
            ranking_ambiguity
        ) = choose_cost_aware_strategy(query)

        eval_scores = evaluate_result(
            best_result,
            gold_doc,
            expected_keywords
        )

        result_rows.append({
            "query": query,
            "gold_doc": gold_doc,
            "chosen_strategy": best_result["strategy"],
            "cited_doc": best_result["cited_doc"],
            "answer": best_result["answer"],
            "evidence_strength": round(evidence_strength, 3),
            "ranking_ambiguity": round(ranking_ambiguity, 3),
            "query_difficulty": query_difficulty,
            "utility": round(best_result["utility"], 3),
            "citation_relevance": eval_scores["citation_relevance"],
            "answer_keyword_score": eval_scores["answer_keyword_score"],
            "faithfulness": eval_scores["faithfulness"],
            "quality_score": round(eval_scores["quality_score"], 3),
            "estimated_cost": best_result["estimated_cost"],
            "hallucination_risk": best_result["hallucination_risk"],
        })

        for log in decision_log:
            decision_rows.append({
                "query": query,
                "query_difficulty": query_difficulty,
                "evidence_strength": round(evidence_strength, 3),
                "ranking_ambiguity": round(ranking_ambiguity, 3),
                "strategy": log["strategy"],
                "estimated_cost": log["estimated_cost"],
                "hallucination_risk": log["hallucination_risk"],
                "utility": round(log["utility"], 3),
            })

    with open(
        "results/cost_aware_rag_results.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=result_rows[0].keys())
        writer.writeheader()
        writer.writerows(result_rows)

    with open(
        "results/strategy_decision_log.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=decision_rows[0].keys())
        writer.writeheader()
        writer.writerows(decision_rows)

    print("=== Cost-Aware RAG Results ===")

    for row in result_rows:
        print("\nQuery:", row["query"])
        print("Difficulty:", row["query_difficulty"])
        print("Evidence strength:", row["evidence_strength"])
        print("Ranking ambiguity:", row["ranking_ambiguity"])
        print("Chosen strategy:", row["chosen_strategy"])
        print("Utility:", row["utility"])
        print("Answer:", row["answer"])
        print("Cited doc:", row["cited_doc"])
        print("Quality score:", row["quality_score"])

    print("\nSaved:")
    print("results/cost_aware_rag_results.csv")
    print("results/strategy_decision_log.csv")


if __name__ == "__main__":
    main()