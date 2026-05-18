import math
import csv
import os
from collections import Counter, defaultdict


# =========================
# 1. Toy Corpus
# =========================

documents = {
    "doc1": "BM25 is a sparse retrieval method based on exact term matching and term frequency.",
    "doc2": "Dense retrieval uses neural embeddings to capture semantic similarity between queries and documents.",
    "doc3": "Hybrid retrieval combines sparse retrieval such as BM25 with dense retrieval scores.",
    "doc4": "Re-ranking improves the order of retrieved candidates but cannot recover relevant documents missed by first-stage retrieval.",
    "doc5": "RAG systems combine retrieval with generation, using retrieved documents as external context.",
    "doc6": "Faithfulness measures whether the generated answer is supported by the retrieved context.",
    "doc7": "Abstention is useful when the system does not have enough evidence to answer safely.",
    "doc8": "Evidence-first RAG selects supporting evidence before generating the final answer."
}


queries = [
    {
        "query": "What does BM25 rely on?",
        "gold_docs": ["doc1"],
        "expected_keywords": ["sparse", "exact", "term", "matching"]
    },
    {
        "query": "How does dense retrieval use embeddings?",
        "gold_docs": ["doc2"],
        "expected_keywords": ["neural", "embeddings", "semantic", "similarity"]
    },
    {
        "query": "What is hybrid retrieval?",
        "gold_docs": ["doc3"],
        "expected_keywords": ["combines", "sparse", "dense"]
    },
    {
        "query": "Why can re-ranking fail?",
        "gold_docs": ["doc4"],
        "expected_keywords": ["cannot", "recover", "missed", "first-stage"]
    },
    {
        "query": "What does faithfulness measure?",
        "gold_docs": ["doc6"],
        "expected_keywords": ["supported", "context"]
    },
    {
        "query": "Which retrieval method is best?",
        "gold_docs": [],
        "expected_keywords": []
    },
    {
        "query": "What is the capital of France?",
        "gold_docs": [],
        "expected_keywords": []
    }
]


# =========================
# 2. Tokenization
# =========================

STOPWORDS = {
    "what", "does", "how", "is", "the", "a", "an", "of", "on", "to",
    "and", "or", "with", "by", "in", "when", "which", "can", "do", "did",
    "why", "this", "that", "it", "as", "for"
}


def tokenize(text):
    text = text.lower()

    for ch in ["?", ".", ",", ":", ";", "!", "(", ")", '"', "'"]:
        text = text.replace(ch, "")

    return [token for token in text.split() if token not in STOPWORDS]


# =========================
# 3. BM25 Retrieval
# =========================

def compute_bm25_scores(query, documents, k1=1.5, b=0.75):
    query_terms = tokenize(query)
    doc_tokens = {doc_id: tokenize(text) for doc_id, text in documents.items()}

    N = len(documents)
    avgdl = sum(len(tokens) for tokens in doc_tokens.values()) / N

    df = defaultdict(int)
    for tokens in doc_tokens.values():
        for term in set(tokens):
            df[term] += 1

    scores = {}

    for doc_id, tokens in doc_tokens.items():
        score = 0.0
        doc_len = len(tokens)
        tf = Counter(tokens)

        for term in query_terms:
            if term not in tf:
                continue

            idf = math.log((N - df[term] + 0.5) / (df[term] + 0.5) + 1)
            numerator = tf[term] * (k1 + 1)
            denominator = tf[term] + k1 * (1 - b + b * doc_len / avgdl)
            score += idf * numerator / denominator

        scores[doc_id] = score

    return scores


def retrieve(query, documents, top_k=3):
    scores = compute_bm25_scores(query, documents)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


# =========================
# 4. Query Diagnosis
# =========================

def diagnose_query(query, retrieved_docs=None):
    q = query.lower()

    if retrieved_docs is not None:
        top_score = retrieved_docs[0][1] if retrieved_docs else 0

        if top_score <= 0:
            return "unsupported"

    if any(phrase in q for phrase in ["best", "should", "which retrieval method", "which method"]):
        return "ambiguous"

    if any(word in q for word in ["why", "fail", "explain", "reason"]):
        return "evidence_sensitive"

    if any(word in q for word in ["compare", "difference", "vs", "versus"]):
        return "comparison"

    return "direct_fact"


def choose_strategy(query_type):
    if query_type == "direct_fact":
        return "baseline"

    if query_type in ["evidence_sensitive", "comparison"]:
        return "evidence_first"

    if query_type in ["ambiguous", "unsupported"]:
        return "abstention"

    return "baseline"


# =========================
# 5. RAG Strategies
# =========================

def baseline_rag(query, retrieved_docs):
    if not retrieved_docs:
        return "I do not have enough information to answer.", None

    best_doc, best_score = retrieved_docs[0]

    if best_score <= 0:
        return "I do not have enough information to answer.", None

    answer = documents[best_doc]
    return answer, best_doc


def evidence_first_rag(query, retrieved_docs):
    if not retrieved_docs:
        return "I do not have enough evidence to answer.", None

    best_doc, best_score = retrieved_docs[0]

    if best_score <= 0:
        return "I do not have enough evidence to answer.", None

    evidence = documents[best_doc]
    answer = f"Based on the retrieved evidence: {evidence}"
    return answer, best_doc


def abstention_rag(query, retrieved_docs, query_type=None):
    if query_type == "ambiguous":
        return "I do not have enough evidence to answer safely because the query is ambiguous.", None

    if query_type == "unsupported":
        return "I do not have enough evidence to answer because the corpus does not contain relevant support.", None

    if not retrieved_docs:
        return "I do not have enough evidence to answer.", None

    best_doc, best_score = retrieved_docs[0]

    if best_score < 1.5:
        return "I do not have enough evidence to answer safely.", None

    return documents[best_doc], best_doc


def run_strategy(strategy, query, retrieved_docs, query_type=None):
    if strategy == "baseline":
        return baseline_rag(query, retrieved_docs)

    if strategy == "evidence_first":
        return evidence_first_rag(query, retrieved_docs)

    if strategy == "abstention":
        return abstention_rag(query, retrieved_docs, query_type)

    raise ValueError(f"Unknown strategy: {strategy}")


# =========================
# 6. Evaluation
# =========================

def recall_at_k(retrieved_doc_ids, gold_docs):
    if not gold_docs:
        return 1.0 if not retrieved_doc_ids else 0.0

    hit = any(doc_id in retrieved_doc_ids for doc_id in gold_docs)
    return 1.0 if hit else 0.0


def answer_keyword_score(answer, expected_keywords):
    answer_lower = answer.lower()

    if not expected_keywords:
        return 1.0 if "not have enough" in answer_lower else 0.0

    hits = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return hits / len(expected_keywords)


def faithfulness(answer, cited_doc):
    answer_lower = answer.lower()

    if cited_doc is None:
        return 1.0 if "not have enough" in answer_lower else 0.0

    doc_text = documents[cited_doc].lower()

    doc_terms = set(tokenize(doc_text))
    answer_terms = set(tokenize(answer_lower))

    overlap = doc_terms.intersection(answer_terms)

    return 1.0 if len(overlap) >= 3 else 0.0


def citation_relevance(cited_doc, gold_docs):
    if not gold_docs:
        return 1.0 if cited_doc is None else 0.0

    return 1.0 if cited_doc in gold_docs else 0.0


def is_abstained(answer):
    return "not have enough" in answer.lower()


def classify_failure(gold_docs, cited_doc, answer, expected_keywords, answer_score):
    abstained = is_abstained(answer)

    if not gold_docs:
        if abstained:
            return "correct_abstention"
        return "unsupported_answer"

    if abstained:
        return "over_conservative_abstention"

    if cited_doc not in gold_docs:
        return "citation_or_context_selection_failure"

    if answer_score < 1.0:
        return "generation_failure"

    return "success"


# =========================
# 7. Experiment Runner
# =========================

def run_experiment(mode):
    results = []

    for item in queries:
        query = item["query"]
        gold_docs = item["gold_docs"]
        expected_keywords = item["expected_keywords"]

        retrieved = retrieve(query, documents, top_k=3)
        retrieved_doc_ids = [doc_id for doc_id, score in retrieved if score > 0]

        query_type = diagnose_query(query, retrieved)

        if mode == "adaptive":
            strategy = choose_strategy(query_type)
        elif mode == "baseline_only":
            strategy = "baseline"
        elif mode == "evidence_only":
            strategy = "evidence_first"
        elif mode == "abstention_only":
            strategy = "abstention"
        else:
            raise ValueError(f"Unknown mode: {mode}")

        answer, cited_doc = run_strategy(strategy, query, retrieved, query_type)

        ans_score = answer_keyword_score(answer, expected_keywords)
        faith_score = faithfulness(answer, cited_doc)
        citation_score = citation_relevance(cited_doc, gold_docs)

        failure_type = classify_failure(
            gold_docs=gold_docs,
            cited_doc=cited_doc,
            answer=answer,
            expected_keywords=expected_keywords,
            answer_score=ans_score
        )

        row = {
            "mode": mode,
            "query": query,
            "query_type": query_type,
            "strategy": strategy,
            "retrieved_docs": "|".join(retrieved_doc_ids),
            "gold_docs": "|".join(gold_docs),
            "answer": answer,
            "cited_doc": cited_doc if cited_doc else "",
            "recall_at_3": recall_at_k(retrieved_doc_ids, gold_docs),
            "answer_keyword_score": ans_score,
            "faithfulness": faith_score,
            "citation_relevance": citation_score,
            "abstained": 1.0 if is_abstained(answer) else 0.0,
            "failure_type": failure_type
        }

        results.append(row)

    return results


def summarize_results(results):
    metrics = [
        "recall_at_3",
        "answer_keyword_score",
        "faithfulness",
        "citation_relevance",
        "abstained"
    ]

    summary = {}

    for metric in metrics:
        summary[metric] = sum(row[metric] for row in results) / len(results)

    return summary


def count_failure_types(results):
    counts = Counter(row["failure_type"] for row in results)
    return dict(counts)


def save_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def save_failure_summary(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    fieldnames = ["mode", "failure_type", "count"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_per_query_results(results, mode):
    print()
    print(f"=== Per-query Results: {mode} ===")

    for row in results:
        print()
        print(f"Query: {row['query']}")
        print(f"Query Type: {row['query_type']}")
        print(f"Strategy: {row['strategy']}")
        print(f"Retrieved Docs: {row['retrieved_docs']}")
        print(f"Gold Docs: {row['gold_docs']}")
        print(f"Cited Doc: {row['cited_doc']}")
        print(f"Answer: {row['answer']}")
        print(f"Recall@3: {row['recall_at_3']:.3f}")
        print(f"Answer Keyword Score: {row['answer_keyword_score']:.3f}")
        print(f"Faithfulness: {row['faithfulness']:.3f}")
        print(f"Citation Relevance: {row['citation_relevance']:.3f}")
        print(f"Abstained: {row['abstained']:.3f}")
        print(f"Failure Type: {row['failure_type']}")


def main():
    modes = [
        "baseline_only",
        "evidence_only",
        "abstention_only",
        "adaptive"
    ]

    all_results = []
    comparison_rows = []
    failure_summary_rows = []
    mode_to_results = {}

    for mode in modes:
        results = run_experiment(mode)
        mode_to_results[mode] = results
        all_results.extend(results)

        summary = summarize_results(results)
        summary_row = {
            "mode": mode,
            **summary
        }
        comparison_rows.append(summary_row)

        failure_counts = count_failure_types(results)
        for failure_type, count in failure_counts.items():
            failure_summary_rows.append({
                "mode": mode,
                "failure_type": failure_type,
                "count": count
            })

    save_csv("day8_adaptive_rag/results/adaptive_rag_results.csv", all_results)
    save_csv("day8_adaptive_rag/results/strategy_comparison_results.csv", comparison_rows)
    save_failure_summary("day8_adaptive_rag/results/failure_type_summary.csv", failure_summary_rows)

    print("=== Strategy Comparison ===")

    for row in comparison_rows:
        print()
        print(f"Mode: {row['mode']}")
        print(f"Recall@3: {row['recall_at_3']:.3f}")
        print(f"Answer Keyword Score: {row['answer_keyword_score']:.3f}")
        print(f"Faithfulness: {row['faithfulness']:.3f}")
        print(f"Citation Relevance: {row['citation_relevance']:.3f}")
        print(f"Abstention Rate: {row['abstained']:.3f}")

    print()
    print("=== Failure Type Summary ===")

    for mode in modes:
        print()
        print(f"Mode: {mode}")
        failure_counts = count_failure_types(mode_to_results[mode])
        for failure_type, count in failure_counts.items():
            print(f"{failure_type}: {count}")

    print_per_query_results(mode_to_results["adaptive"], "adaptive")

    print()
    print("Saved results to:")
    print("day8_adaptive_rag/results/adaptive_rag_results.csv")
    print("day8_adaptive_rag/results/strategy_comparison_results.csv")
    print("day8_adaptive_rag/results/failure_type_summary.csv")


if __name__ == "__main__":
    main()