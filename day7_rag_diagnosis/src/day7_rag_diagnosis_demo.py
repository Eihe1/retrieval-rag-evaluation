import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


DOCUMENTS = {
    "doc1": "BM25 is a sparse retrieval method based on lexical term matching and exact word overlap.",
    "doc2": "Dense retrieval represents queries and documents as vector embeddings and retrieves semantically similar documents.",
    "doc3": "Hybrid retrieval combines sparse retrieval such as BM25 with dense retrieval to balance exact matching and semantic similarity.",
    "doc4": "A cross-encoder re-ranker scores query-document pairs more accurately after first-stage retrieval.",
    "doc5": "Re-ranking can improve the order of retrieved candidates, but it cannot recover relevant documents missing from the first-stage candidate set.",
    "doc6": "RAG retrieves external documents and uses them as context for answer generation.",
    "doc7": "Faithfulness means that the generated answer is supported by the retrieved context.",
    "doc8": "Citation relevance means that the cited document actually contains evidence for the generated answer.",
    "doc9": "Query rewriting reformulates the original query to improve retrieval robustness.",
    "doc10": "Chunking splits long documents into smaller passages, but chunk size affects context completeness and noise.",
}


QUERIES = [
    {
        "query_id": "q1",
        "query": "What does BM25 rely on?",
        "gold_docs": ["doc1"],
        "expected_keywords": ["sparse", "lexical", "term", "matching"],
    },
    {
        "query_id": "q2",
        "query": "What is dense retrieval?",
        "gold_docs": ["doc2"],
        "expected_keywords": ["vector", "embedding", "semantic"],
    },
    {
        "query_id": "q3",
        "query": "Why can re-ranking fail?",
        "gold_docs": ["doc5"],
        "expected_keywords": ["cannot recover", "missing", "first-stage"],
    },
    {
        "query_id": "q4",
        "query": "What does faithfulness mean in RAG?",
        "gold_docs": ["doc7"],
        "expected_keywords": ["supported", "context"],
    },
    {
        "query_id": "q5",
        "query": "Why is citation relevance important?",
        "gold_docs": ["doc8"],
        "expected_keywords": ["cited", "evidence"],
    },
    {
        "query_id": "q6",
        "query": "How does chunking affect RAG?",
        "gold_docs": ["doc10"],
        "expected_keywords": ["chunk", "context", "noise"],
    },
    {
        "query_id": "q7",
        "query": "How does SQL transaction rollback work in RAG?",
        "gold_docs": [],
        "expected_keywords": ["transaction", "rollback"],
    },
]


BASELINE_ANSWERS = {
    "q1": {
        "answer": "BM25 is a sparse retrieval method based on lexical term matching.",
        "cited_doc": "doc1",
    },
    "q2": {
        "answer": "Dense retrieval is mainly based on SQL joins and B-tree indexes.",
        "cited_doc": "doc2",
    },
    "q3": {
        "answer": "Re-ranking improves ranking quality, but it cannot recover documents missing from the first-stage candidate set.",
        "cited_doc": "doc4",
    },
    "q4": {
        "answer": "Faithfulness means the answer is fluent and convincing.",
        "cited_doc": "doc7",
    },
    "q5": {
        "answer": "Citation relevance means the cited document contains evidence for the generated answer.",
        "cited_doc": "doc8",
    },
    "q6": {
        "answer": "Chunking can affect context completeness and may introduce noise.",
        "cited_doc": "doc10",
    },
    "q7": {
        "answer": "SQL transaction rollback in RAG is handled by vector embeddings.",
        "cited_doc": "doc2",
    },
}


def tokenize(text):
    return re.findall(r"[a-zA-Z0-9\-]+", text.lower())


def retrieval_score(query, document):
    query_terms = set(tokenize(query))
    doc_terms = set(tokenize(document))
    return len(query_terms & doc_terms)


def retrieve(query, top_k=3):
    scored = []

    for doc_id, text in DOCUMENTS.items():
        score = retrieval_score(query, text)
        scored.append((doc_id, score, text))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def keyword_score(answer, expected_keywords):
    if not expected_keywords:
        return 0.0

    answer_lower = answer.lower()
    matched = 0

    for keyword in expected_keywords:
        if keyword.lower() in answer_lower:
            matched += 1

    return matched / len(expected_keywords)


def citation_relevance(cited_doc, gold_docs):
    if not gold_docs:
        return 0.0
    return 1.0 if cited_doc in gold_docs else 0.0


def faithfulness(answer, retrieved_doc_ids):
    retrieved_context = " ".join(DOCUMENTS[doc_id] for doc_id in retrieved_doc_ids).lower()
    answer_terms = set(tokenize(answer))

    if not answer_terms:
        return 0.0

    supported_terms = [term for term in answer_terms if term in retrieved_context]
    support_ratio = len(supported_terms) / len(answer_terms)

    return 1.0 if support_ratio >= 0.6 else 0.0


def recall_at_k(gold_docs, retrieved_doc_ids):
    if not gold_docs:
        return 0.0
    return 1.0 if any(doc in retrieved_doc_ids for doc in gold_docs) else 0.0


def first_gold_rank(gold_docs, retrieved_doc_ids):
    for idx, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id in gold_docs:
            return idx
    return None


def classify_failure(row):
    gold_docs = row["gold_docs"]
    retrieved_doc_ids = row["retrieved_docs"]
    answer_score = row["answer_keyword_score"]
    citation_score = row["citation_relevance"]
    faithful = row["faithfulness"]

    # Handle abstention first
    if row["abstained"]:
        if not gold_docs:
            return "correct_abstention"

        if recall_at_k(gold_docs, retrieved_doc_ids) == 1.0:
            return "over_conservative_abstention"

        return "abstention_due_to_retrieval_miss"

    # No gold evidence but system still answers
    if not gold_docs:
        return "unsupported_answer"

    # Gold evidence not retrieved
    if recall_at_k(gold_docs, retrieved_doc_ids) == 0:
        return "retrieval_miss"

    # Retrieved context does not support answer
    if faithful == 0.0:
        return "hallucination_or_unfaithful_answer"

    # Gold doc retrieved but answer is poor
    rank = first_gold_rank(gold_docs, retrieved_doc_ids)
    if rank is not None and rank > 1 and answer_score < 0.7:
        return "ranking_or_context_selection_failure"

    # Answer does not contain expected concepts
    if answer_score < 0.7:
        return "generation_grounding_failure"

    # Answer is good but citation is wrong
    if citation_score == 0.0:
        return "citation_failure"

    return "success"


def baseline_rag(top_k=3):
    results = []

    for item in QUERIES:
        retrieved = retrieve(item["query"], top_k=top_k)
        retrieved_doc_ids = [doc_id for doc_id, _, _ in retrieved]

        baseline = BASELINE_ANSWERS[item["query_id"]]
        answer = baseline["answer"]
        cited_doc = baseline["cited_doc"]

        row = {
            "query_id": item["query_id"],
            "query": item["query"],
            "gold_docs": item["gold_docs"],
            "retrieved_docs": retrieved_doc_ids,
            "answer": answer,
            "cited_doc": cited_doc,
            "abstained": False,
            "answer_keyword_score": keyword_score(answer, item["expected_keywords"]),
            "faithfulness": faithfulness(answer, retrieved_doc_ids),
            "citation_relevance": citation_relevance(cited_doc, item["gold_docs"]),
        }

        row["failure_type"] = classify_failure(row)
        results.append(row)

    return results


def select_best_evidence(query, retrieved):
    query_terms = set(tokenize(query))

    best_doc_id = None
    best_sentence = ""
    best_score = -1

    for doc_id, _, doc_text in retrieved:
        sentences = re.split(r"(?<=[.!?])\s+", doc_text)

        for sentence in sentences:
            sentence_terms = set(tokenize(sentence))
            score = len(query_terms & sentence_terms)

            if score > best_score:
                best_score = score
                best_doc_id = doc_id
                best_sentence = sentence

    return best_doc_id, best_sentence, best_score


def evidence_first_rag(top_k=3):
    results = []

    for item in QUERIES:
        retrieved = retrieve(item["query"], top_k=top_k)
        retrieved_doc_ids = [doc_id for doc_id, _, _ in retrieved]

        evidence_doc, evidence_sentence, evidence_score = select_best_evidence(item["query"], retrieved)

        answer = evidence_sentence
        cited_doc = evidence_doc

        row = {
            "query_id": item["query_id"],
            "query": item["query"],
            "gold_docs": item["gold_docs"],
            "retrieved_docs": retrieved_doc_ids,
            "answer": answer,
            "cited_doc": cited_doc,
            "abstained": False,
            "answer_keyword_score": keyword_score(answer, item["expected_keywords"]),
            "faithfulness": faithfulness(answer, retrieved_doc_ids),
            "citation_relevance": citation_relevance(cited_doc, item["gold_docs"]),
        }

        row["failure_type"] = classify_failure(row)
        results.append(row)

    return results


def abstention_rag(top_k=3, min_evidence_score=2):
    results = []

    for item in QUERIES:
        retrieved = retrieve(item["query"], top_k=top_k)
        retrieved_doc_ids = [doc_id for doc_id, _, _ in retrieved]

        evidence_doc, evidence_sentence, evidence_score = select_best_evidence(item["query"], retrieved)

        if evidence_score < min_evidence_score:
            answer = "Insufficient evidence."
            cited_doc = ""
            abstained = True
        else:
            answer = evidence_sentence
            cited_doc = evidence_doc
            abstained = False

        row = {
            "query_id": item["query_id"],
            "query": item["query"],
            "gold_docs": item["gold_docs"],
            "retrieved_docs": retrieved_doc_ids,
            "answer": answer,
            "cited_doc": cited_doc,
            "abstained": abstained,
            "answer_keyword_score": keyword_score(answer, item["expected_keywords"]),
            "faithfulness": 1.0 if abstained else faithfulness(answer, retrieved_doc_ids),
            "citation_relevance": citation_relevance(cited_doc, item["gold_docs"]),
        }

        row["failure_type"] = classify_failure(row)
        results.append(row)

    return results


def summarize(results):
    summary = {}

    summary["mean_answer_keyword_score"] = sum(r["answer_keyword_score"] for r in results) / len(results)
    summary["mean_faithfulness"] = sum(r["faithfulness"] for r in results) / len(results)
    summary["mean_citation_relevance"] = sum(r["citation_relevance"] for r in results) / len(results)
    summary["abstention_rate"] = sum(1 for r in results if r["abstained"]) / len(results)

    failure_counts = Counter(r["failure_type"] for r in results)
    summary["failure_counts"] = dict(failure_counts)

    return summary


def save_csv(path, results):
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "query_id",
        "query",
        "gold_docs",
        "retrieved_docs",
        "answer",
        "cited_doc",
        "abstained",
        "answer_keyword_score",
        "faithfulness",
        "citation_relevance",
        "failure_type",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in results:
            row_copy = dict(row)
            row_copy["gold_docs"] = ",".join(row_copy["gold_docs"])
            row_copy["retrieved_docs"] = ",".join(row_copy["retrieved_docs"])
            writer.writerow(row_copy)


def write_report(path, baseline_results, evidence_results, abstention_results):
    path.parent.mkdir(parents=True, exist_ok=True)

    baseline_summary = summarize(baseline_results)
    evidence_summary = summarize(evidence_results)
    abstention_summary = summarize(abstention_results)

    lines = []

    lines.append("# Day 7 Diagnosis Summary\n")

    lines.append("## 1. Purpose\n")
    lines.append(
        "This experiment extends Day 6 RAG evaluation by moving from metric-based evaluation "
        "to diagnosis-driven improvement. The goal is to identify the main system bottlenecks "
        "and test targeted strategies such as evidence-first answering and abstention.\n"
    )

    lines.append("## 2. Baseline Summary\n")
    lines.append(f"- Mean answer keyword score: {baseline_summary['mean_answer_keyword_score']:.3f}")
    lines.append(f"- Mean faithfulness: {baseline_summary['mean_faithfulness']:.3f}")
    lines.append(f"- Mean citation relevance: {baseline_summary['mean_citation_relevance']:.3f}")
    lines.append(f"- Abstention rate: {baseline_summary['abstention_rate']:.3f}")
    lines.append(f"- Failure counts: {baseline_summary['failure_counts']}\n")

    lines.append("## 3. Evidence-First Summary\n")
    lines.append(f"- Mean answer keyword score: {evidence_summary['mean_answer_keyword_score']:.3f}")
    lines.append(f"- Mean faithfulness: {evidence_summary['mean_faithfulness']:.3f}")
    lines.append(f"- Mean citation relevance: {evidence_summary['mean_citation_relevance']:.3f}")
    lines.append(f"- Abstention rate: {evidence_summary['abstention_rate']:.3f}")
    lines.append(f"- Failure counts: {evidence_summary['failure_counts']}\n")

    lines.append("## 4. Abstention Summary\n")
    lines.append(f"- Mean answer keyword score: {abstention_summary['mean_answer_keyword_score']:.3f}")
    lines.append(f"- Mean faithfulness: {abstention_summary['mean_faithfulness']:.3f}")
    lines.append(f"- Mean citation relevance: {abstention_summary['mean_citation_relevance']:.3f}")
    lines.append(f"- Abstention rate: {abstention_summary['abstention_rate']:.3f}")
    lines.append(f"- Failure counts: {abstention_summary['failure_counts']}\n")

    lines.append("## 5. Research Takeaway\n")
    lines.append(
        "The baseline system shows that retrieval success alone does not guarantee answer quality. "
        "Some failures are caused by weak answer grounding or wrong citation selection rather than missing retrieval results. "
        "The evidence-first strategy introduces an explicit intermediate evidence selection step, which makes the generation process more grounded and easier to inspect. "
        "The abstention strategy further improves reliability by avoiding unsupported answers when the retrieved evidence is weak. "
        "This suggests that reliable RAG systems should not only retrieve relevant documents, but also diagnose bottlenecks and select different execution strategies based on query-level evidence quality.\n"
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(name, results):
    summary = summarize(results)

    print(f"\n=== {name} ===")
    print(f"Mean answer keyword score: {summary['mean_answer_keyword_score']:.3f}")
    print(f"Mean faithfulness: {summary['mean_faithfulness']:.3f}")
    print(f"Mean citation relevance: {summary['mean_citation_relevance']:.3f}")
    print(f"Abstention rate: {summary['abstention_rate']:.3f}")
    print(f"Failure counts: {summary['failure_counts']}")


def main():
    result_dir = Path("results")

    baseline_results = baseline_rag(top_k=3)
    evidence_results = evidence_first_rag(top_k=3)
    abstention_results = abstention_rag(top_k=3, min_evidence_score=2)

    save_csv(result_dir / "baseline_results.csv", baseline_results)
    save_csv(result_dir / "evidence_first_results.csv", evidence_results)
    save_csv(result_dir / "abstention_results.csv", abstention_results)

    def write_query_diagnosis(path, results, strategy_name):
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = []
        lines.append(f"# Query-level Diagnosis: {strategy_name}\n")

        for row in results:
            lines.append(f"## {row['query_id']}: {row['query']}\n")
            lines.append(f"- Gold docs: {row['gold_docs']}")
            lines.append(f"- Retrieved docs: {row['retrieved_docs']}")
            lines.append(f"- Answer: {row['answer']}")
            lines.append(f"- Cited doc: {row['cited_doc']}")
            lines.append(f"- Answer keyword score: {row['answer_keyword_score']:.3f}")
            lines.append(f"- Faithfulness: {row['faithfulness']:.3f}")
            lines.append(f"- Citation relevance: {row['citation_relevance']:.3f}")
            lines.append(f"- Failure type: `{row['failure_type']}`\n")

            if row["failure_type"] == "success":
                lines.append("Diagnosis: The answer, retrieved context, and citation are aligned.\n")
            elif row["failure_type"] == "ranking_or_context_selection_failure":
                lines.append("Diagnosis: The correct evidence may be retrieved, but it is not selected or used effectively.\n")
            elif row["failure_type"] == "citation_failure":
                lines.append("Diagnosis: The answer is mostly correct, but the cited document does not match the supporting evidence.\n")
            elif row["failure_type"] == "unsupported_answer":
                lines.append("Diagnosis: The system answers despite insufficient supporting evidence.\n")
            elif row["failure_type"] == "correct_abstention":
                lines.append("Diagnosis: The system correctly avoids answering when evidence is insufficient.\n")
            elif row["failure_type"] == "hallucination_or_unfaithful_answer":
                lines.append("Diagnosis: The answer is not sufficiently supported by the retrieved context.\n")
            elif row["failure_type"] == "over_conservative_abstention":
                lines.append(
                    "Diagnosis: The system abstains even though the gold document is retrieved. "
                    "This indicates that the evidence sufficiency check is too conservative or the evidence selector fails to recognize the correct evidence.\n"
                )
            elif row["failure_type"] == "abstention_due_to_retrieval_miss":
                lines.append(
                    "Diagnosis: The system abstains because the gold document is not retrieved. "
                    "This suggests a retrieval-side failure rather than a generation-side failure.\n"
                )
            else:
                lines.append("Diagnosis: The failure is related to answer generation or grounding.\n")

        path.write_text("\n".join(lines), encoding="utf-8")

    write_report(
        result_dir / "diagnosis_summary.md",
        baseline_results,
        evidence_results,
        abstention_results,
    )

    write_query_diagnosis(
        result_dir / "baseline_query_diagnosis.md",
        baseline_results,
        "Baseline RAG",
    )

    write_query_diagnosis(
        result_dir / "evidence_first_query_diagnosis.md",
        evidence_results,
        "Evidence-First RAG",
    )

    write_query_diagnosis(
        result_dir / "abstention_query_diagnosis.md",
        abstention_results,
        "Abstention RAG",
    )

    print_summary("Baseline RAG", baseline_results)
    print_summary("Evidence-First RAG", evidence_results)
    print_summary("Abstention RAG", abstention_results)

    print("\nSaved results to:")
    print("- results/baseline_results.csv")
    print("- results/evidence_first_results.csv")
    print("- results/abstention_results.csv")
    print("- results/diagnosis_summary.md")


if __name__ == "__main__":
    main()