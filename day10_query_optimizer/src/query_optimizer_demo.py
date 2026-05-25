from dataclasses import dataclass
from typing import Dict, List
import csv
from pathlib import Path


DOMAIN_TERMS = {
    "retrieval": [
        "bm25", "dense retrieval", "hybrid retrieval",
        "rerank", "reranking", "retrieval", "first-stage retrieval"
    ],
    "evaluation": [
        "recall", "mrr", "ndcg", "faithfulness", "citation", "precision"
    ],
    "optimization": [
        "cost", "latency", "utility", "optimizer", "strategy",
        "trade-off", "should", "choose", "decision", "policy"
    ],
    "content_failure": [
        "fail", "failure", "missed", "hallucination"
    ],
    "answer_risk": [
        "weak evidence", "evidence is weak",
        "unsupported answer", "unsupported answers",
        "not enough evidence", "uncertain", "unknown",
        "ambiguous", "ranking ambiguity is high"
    ],
    "structured": [
        "highest", "lowest", "average", "mean", "sum", "total",
        "maximum", "minimum", "increase", "decrease",
        "previous quarter", "sales", "product",
        "how many", "number of", "count of", "total number",
        "top", "rank", "sort", "frequency"
    ],
}


COUNTING_PATTERNS = [
    "how many",
    "number of",
    "count of",
    "total number",
    "amount of",
    "frequency of",
    "occurrences of",
    "count(",
]


AGGREGATION_PATTERNS = [
    "average",
    "mean",
    "sum",
    "total",
    "maximum",
    "minimum",
    "highest",
    "lowest",
    "increase",
    "decrease",
    "top",
    "rank",
    "sort",
]


STRATEGY_REASONING_PATTERNS = [
    "strategy",
    "should",
    "when",
    "choose",
    "decision",
    "optimizer",
    "policy",
    "which method",
    "which approach",
    "which plan",
]


@dataclass
class QueryFeatures:
    query: str
    intent: str
    query_type: str
    difficulty: float
    evidence_strength: float
    ranking_ambiguity: float
    structured_signal: float
    content_failure_signal: float
    answer_risk_signal: float
    domain_hits: Dict[str, int]


@dataclass
class Plan:
    name: str
    plan_type: str
    base_quality: float
    base_cost: float


def count_domain_hits(query: str) -> Dict[str, int]:
    q = query.lower()
    return {
        category: sum(1 for term in terms if term in q)
        for category, terms in DOMAIN_TERMS.items()
    }


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def contains_any(query: str, patterns: List[str]) -> bool:
    q = query.lower()
    return any(pattern in q for pattern in patterns)


def detect_intent(query: str, hits: Dict[str, int]) -> str:
    q = query.lower()

    if contains_any(q, COUNTING_PATTERNS):
        return "counting"

    if q.startswith("why") and hits["content_failure"] > 0:
        return "failure_explanation"

    if contains_any(q, STRATEGY_REASONING_PATTERNS):
        return "strategy_reasoning"

    if contains_any(q, AGGREGATION_PATTERNS):
        return "structured_aggregation"

    if hits["structured"] >= 2:
        return "structured_aggregation"

    if any(word in q for word in ["compare", "difference", "versus", "vs"]):
        return "comparison"

    if any(word in q for word in ["why", "how", "explain"]):
        return "explanation"

    return "fact_lookup"


def analyze_query(query: str) -> QueryFeatures:
    hits = count_domain_hits(query)

    structured_signal = clamp(hits["structured"] / 3)
    content_failure_signal = clamp(hits["content_failure"] / 2)
    answer_risk_signal = clamp(hits["answer_risk"] / 2)

    intent = detect_intent(query, hits)

    if intent == "counting":
        query_type = "structured_reasoning"
        difficulty = 0.65
        evidence_strength = 0.75
        ranking_ambiguity = 0.35
        structured_signal = max(structured_signal, 0.70)

    elif intent == "structured_aggregation":
        query_type = "structured_reasoning"
        difficulty = 0.80
        evidence_strength = 0.65
        ranking_ambiguity = 0.55
        structured_signal = max(structured_signal, 0.80)

    elif intent == "strategy_reasoning":
        query_type = "policy_reasoning"
        difficulty = 0.80
        evidence_strength = 0.70
        ranking_ambiguity = 0.65
        structured_signal = 0.0

    elif intent == "failure_explanation":
        query_type = "multi_hop_reasoning"
        difficulty = 0.75
        evidence_strength = 0.70
        ranking_ambiguity = 0.55
        structured_signal = 0.0

    elif intent == "comparison":
        query_type = "comparison"
        difficulty = 0.75
        evidence_strength = 0.70
        ranking_ambiguity = 0.65

    elif intent == "explanation":
        query_type = "multi_hop_reasoning"
        difficulty = 0.70
        evidence_strength = 0.65
        ranking_ambiguity = 0.60

    else:
        query_type = "fact_lookup"
        difficulty = 0.30
        evidence_strength = 0.90
        ranking_ambiguity = 0.20

    if answer_risk_signal > 0 and intent not in [
        "failure_explanation",
        "strategy_reasoning",
        "counting",
        "structured_aggregation",
    ]:
        evidence_strength -= 0.25 * answer_risk_signal
        ranking_ambiguity += 0.25 * answer_risk_signal
        difficulty += 0.15 * answer_risk_signal

    if content_failure_signal > 0 and intent in [
        "failure_explanation",
        "comparison",
        "explanation",
    ]:
        difficulty += 0.05 * content_failure_signal

    if hits["evaluation"] > 0 or hits["optimization"] > 0:
        difficulty += 0.10

    return QueryFeatures(
        query=query,
        intent=intent,
        query_type=query_type,
        difficulty=clamp(difficulty),
        evidence_strength=clamp(evidence_strength),
        ranking_ambiguity=clamp(ranking_ambiguity),
        structured_signal=structured_signal,
        content_failure_signal=content_failure_signal,
        answer_risk_signal=answer_risk_signal,
        domain_hits=hits,
    )


def estimate_cost(plan: Plan, features: QueryFeatures) -> float:
    cost = plan.base_cost

    if plan.plan_type == "text":
        cost += 0.5 * features.ranking_ambiguity
        cost += 0.3 * features.difficulty

        if features.intent == "fact_lookup" and plan.name != "Direct Retrieval":
            cost += 0.5

    elif plan.plan_type == "structured":
        cost += 0.8 * features.structured_signal
        cost += 0.2 * features.difficulty

    elif plan.plan_type == "safety":
        cost += 0.1 * features.answer_risk_signal

    return cost


def predict_quality(plan: Plan, features: QueryFeatures) -> float:
    quality = plan.base_quality

    if plan.name == "Direct Retrieval":
        quality -= 0.35 * features.difficulty
        quality -= 0.25 * features.ranking_ambiguity
        quality += 0.20 * features.evidence_strength
        quality -= 0.25 * features.structured_signal

        if features.intent == "fact_lookup":
            quality += 0.10

    elif plan.name == "Hybrid Retrieval":
        quality -= 0.20 * features.difficulty
        quality -= 0.10 * features.ranking_ambiguity
        quality += 0.25 * features.evidence_strength
        quality -= 0.10 * features.structured_signal

        if features.intent == "fact_lookup":
            quality -= 0.10

    elif plan.name == "Hybrid + Rerank":
        quality -= 0.10 * features.difficulty
        quality -= 0.05 * features.ranking_ambiguity
        quality += 0.15 * features.evidence_strength
        quality -= 0.15 * features.structured_signal

        if features.intent == "fact_lookup":
            quality -= 0.20

        if features.intent in ["strategy_reasoning", "failure_explanation", "comparison"]:
            quality += 0.05

    elif plan.name == "SQL Query":
        quality -= 0.10 * features.difficulty
        quality += 0.35 * features.structured_signal
        quality -= 0.15 * (1.0 - features.structured_signal)
        quality += 0.10 * features.evidence_strength

        if features.intent in [
            "fact_lookup",
            "strategy_reasoning",
            "failure_explanation",
            "comparison",
            "explanation",
        ]:
            quality -= 0.20

    elif plan.name == "Abstain":
        quality = 0.30
        quality += 0.50 * features.answer_risk_signal
        quality += 0.25 * (1.0 - features.evidence_strength)

        if features.intent in [
            "failure_explanation",
            "strategy_reasoning",
            "counting",
            "structured_aggregation",
        ]:
            quality -= 0.40

    return clamp(quality)


def compute_utility(predicted_quality: float, estimated_cost: float, lambda_cost: float) -> float:
    return predicted_quality - lambda_cost * estimated_cost


def choose_best_plan(plans: List[Plan], features: QueryFeatures, lambda_cost: float):
    scored_plans = []

    for plan in plans:
        predicted_quality = predict_quality(plan, features)
        estimated_cost = estimate_cost(plan, features)
        utility = compute_utility(predicted_quality, estimated_cost, lambda_cost)

        scored_plans.append({
            "plan": plan.name,
            "plan_type": plan.plan_type,
            "predicted_quality": predicted_quality,
            "estimated_cost": estimated_cost,
            "utility": utility,
        })

    best_plan = max(scored_plans, key=lambda x: x["utility"])
    return best_plan, scored_plans


def save_results(records: List[Dict], output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "query",
        "intent",
        "query_type",
        "difficulty",
        "evidence_strength",
        "ranking_ambiguity",
        "structured_signal",
        "content_failure_signal",
        "answer_risk_signal",
        "selected_plan",
        "selected_plan_type",
        "selected_quality",
        "selected_cost",
        "selected_utility",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main():
    plans = [
        Plan("Direct Retrieval", "text", 0.70, 1.0),
        Plan("Hybrid Retrieval", "text", 0.85, 2.0),
        Plan("Hybrid + Rerank", "text", 0.95, 3.0),
        Plan("SQL Query", "structured", 0.82, 2.5),
        Plan("Abstain", "safety", 0.60, 0.5),
    ]

    queries = [
        "What does BM25 rely on?",
        "Compare BM25 and dense retrieval under low lexical overlap.",
        "Why can reranking fail when relevant documents are missed by first-stage retrieval?",
        "Which strategy should be used when evidence is weak and ranking ambiguity is high?",
        "Which product had the highest sales increase compared with the previous quarter?",
        "How many documents have unsupported answers?",
        "Number of failed retrieval cases",
        "Count of hallucinated responses",
        "Total number of queries with low faithfulness",
        "Average nDCG across all test queries",
        "Top 3 strategies by utility",
        "Which method has the lowest cost?",
    ]

    lambda_cost = 0.10
    records = []

    print("=== Strategy-Aware Query Optimizer Demo ===")

    for query in queries:
        features = analyze_query(query)
        best_plan, scored_plans = choose_best_plan(plans, features, lambda_cost)

        print("\nQuery:", query)
        print("Intent:", features.intent)
        print("Query type:", features.query_type)
        print(f"Difficulty: {features.difficulty:.2f}")
        print(f"Evidence strength: {features.evidence_strength:.2f}")
        print(f"Ranking ambiguity: {features.ranking_ambiguity:.2f}")
        print(f"Structured signal: {features.structured_signal:.2f}")
        print(f"Content failure signal: {features.content_failure_signal:.2f}")
        print(f"Answer risk signal: {features.answer_risk_signal:.2f}")
        print("Domain hits:", features.domain_hits)

        print("\nCandidate plans:")
        for item in scored_plans:
            print(
                f"- {item['plan']}: "
                f"type={item['plan_type']}, "
                f"quality={item['predicted_quality']:.3f}, "
                f"cost={item['estimated_cost']:.3f}, "
                f"utility={item['utility']:.3f}"
            )

        print("Selected plan:", best_plan["plan"])

        records.append({
            "query": query,
            "intent": features.intent,
            "query_type": features.query_type,
            "difficulty": round(features.difficulty, 3),
            "evidence_strength": round(features.evidence_strength, 3),
            "ranking_ambiguity": round(features.ranking_ambiguity, 3),
            "structured_signal": round(features.structured_signal, 3),
            "content_failure_signal": round(features.content_failure_signal, 3),
            "answer_risk_signal": round(features.answer_risk_signal, 3),
            "selected_plan": best_plan["plan"],
            "selected_plan_type": best_plan["plan_type"],
            "selected_quality": round(best_plan["predicted_quality"], 3),
            "selected_cost": round(best_plan["estimated_cost"], 3),
            "selected_utility": round(best_plan["utility"], 3),
        })

    save_results(records, "results/optimizer_results.csv")
    print("\nSaved results to results/optimizer_results.csv")


if __name__ == "__main__":
    main()