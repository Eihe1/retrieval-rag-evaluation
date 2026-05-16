import math
import csv
import re
from collections import Counter, defaultdict


# -----------------------------
# 1. Toy corpus
# -----------------------------

documents = [
    {
        "id": "doc1",
        "text": "BM25 is a sparse retrieval method based on exact term matching. It works well when query words overlap with document words."
    },
    {
        "id": "doc2",
        "text": "Dense retrieval represents queries and documents as vectors. It can retrieve semantically similar documents even when exact words do not match."
    },
    {
        "id": "doc3",
        "text": "Hybrid retrieval combines sparse retrieval and dense retrieval. It can balance exact keyword matching and semantic similarity."
    },
    {
        "id": "doc4",
        "text": "Cross-encoder re-ranking scores each query-document pair jointly. It is usually more accurate but slower than first-stage retrieval."
    },
    {
        "id": "doc5",
        "text": "RAG systems combine retrieval with text generation. The retriever provides external context, and the generator produces an answer from that context."
    },
    {
        "id": "doc6",
        "text": "Faithfulness measures whether an answer is supported by the retrieved context. A faithful answer should not contain unsupported claims."
    },
    {
        "id": "doc7",
        "text": "Recall at k measures whether relevant documents are included in the top-k retrieved results. It does not evaluate answer quality."
    },
    {
        "id": "doc8",
        "text": "A hallucination occurs when a language model produces information that is not supported by the provided context."
    }
]


# -----------------------------
# 2. Evaluation dataset
# -----------------------------

qa_dataset = [
    {
        "query": "What does BM25 rely on?",
        "gold_doc_ids": ["doc1"],
        "answer_keywords": ["sparse", "exact", "term", "matching"]
    },
    {
        "query": "Why is dense retrieval useful?",
        "gold_doc_ids": ["doc2"],
        "answer_keywords": ["vectors", "semantically", "similar", "exact words"]
    },
    {
        "query": "What does hybrid retrieval combine?",
        "gold_doc_ids": ["doc3"],
        "answer_keywords": ["sparse", "dense", "exact", "semantic"]
    },
    {
        "query": "Why is cross-encoder re-ranking expensive?",
        "gold_doc_ids": ["doc4"],
        "answer_keywords": ["query-document", "jointly", "slower"]
    },
    {
        "query": "What is faithfulness in RAG?",
        "gold_doc_ids": ["doc6"],
        "answer_keywords": ["supported", "context", "unsupported claims"]
    },
    {
        "query": "Does Recall at k evaluate answer quality?",
        "gold_doc_ids": ["doc7"],
        "answer_keywords": ["does not", "answer quality"]
    },
    {
        "query": "What is hallucination in RAG?",
        "gold_doc_ids": ["doc8"],
        "answer_keywords": ["not supported", "context"]
    }
]


# -----------------------------
# 3. Basic text processing
# -----------------------------

def tokenize(text):
    text = text.lower()
    return re.findall(r"[a-z0-9]+", text)


def split_sentences(text):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


# -----------------------------
# 4. Simple BM25 retriever
# -----------------------------

class BM25Retriever:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = docs
        self.k1 = k1
        self.b = b

        self.doc_tokens = [tokenize(doc["text"]) for doc in docs]
        self.doc_lengths = [len(tokens) for tokens in self.doc_tokens]
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths)

        self.df = defaultdict(int)
        for tokens in self.doc_tokens:
            for term in set(tokens):
                self.df[term] += 1

        self.N = len(docs)

    def idf(self, term):
        df = self.df.get(term, 0)
        return math.log(1 + (self.N - df + 0.5) / (df + 0.5))

    def score(self, query, doc_index):
        query_terms = tokenize(query)
        doc_terms = self.doc_tokens[doc_index]
        tf = Counter(doc_terms)
        dl = self.doc_lengths[doc_index]

        score = 0.0
        for term in query_terms:
            if term not in tf:
                continue

            numerator = tf[term] * (self.k1 + 1)
            denominator = tf[term] + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            score += self.idf(term) * numerator / denominator

        return score

    def retrieve(self, query, top_k=3):
        scored = []
        for i, doc in enumerate(self.docs):
            scored.append((doc, self.score(query, i)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


# -----------------------------
# 5. Simple extractive answer generator
# -----------------------------

def generate_answer(query, retrieved_docs):
    """
    This is not a real LLM.
    It selects the sentence with the highest word overlap with the query.
    This makes the evaluation process easier to inspect.
    """

    query_terms = set(tokenize(query))
    best_sentence = None
    best_doc_id = None
    best_score = -1

    for doc, _score in retrieved_docs:
        for sent in split_sentences(doc["text"]):
            sent_terms = set(tokenize(sent))
            overlap = len(query_terms & sent_terms)

            if overlap > best_score:
                best_score = overlap
                best_sentence = sent
                best_doc_id = doc["id"]

    if best_sentence is None:
        return {
            "answer": "I do not know.",
            "cited_doc_id": None
        }

    return {
        "answer": best_sentence,
        "cited_doc_id": best_doc_id
    }


def generate_answer_with_hallucination(query, retrieved_docs):
    """
    A simulated generator that sometimes produces unsupported answers.
    This is used to test faithfulness evaluation.
    """

    if "hallucination" in query.lower():
        return {
            "answer": "A hallucination is always caused by database indexing errors.",
            "cited_doc_id": None
        }

    return generate_answer(query, retrieved_docs)



# -----------------------------
# 6. Retrieval metrics
# -----------------------------

def recall_at_k(retrieved_doc_ids, gold_doc_ids, k):
    retrieved_at_k = set(retrieved_doc_ids[:k])
    gold = set(gold_doc_ids)
    return len(retrieved_at_k & gold) / len(gold)


def mrr(retrieved_doc_ids, gold_doc_ids):
    gold = set(gold_doc_ids)
    for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id in gold:
            return 1.0 / rank
    return 0.0


def dcg(relevance_scores):
    total = 0.0
    for i, rel in enumerate(relevance_scores, start=1):
        total += rel / math.log2(i + 1)
    return total


def ndcg_at_k(retrieved_doc_ids, gold_doc_ids, k):
    gold = set(gold_doc_ids)

    relevance = []
    for doc_id in retrieved_doc_ids[:k]:
        relevance.append(1 if doc_id in gold else 0)

    ideal_relevance = sorted(relevance, reverse=True)

    actual_dcg = dcg(relevance)
    ideal_dcg = dcg(ideal_relevance)

    if ideal_dcg == 0:
        return 0.0

    return actual_dcg / ideal_dcg


# -----------------------------
# 7. Answer metrics
# -----------------------------

def keyword_answer_score(answer, answer_keywords):
    """
    A simple correctness proxy.
    It checks whether important expected keywords appear in the answer.
    """

    answer_lower = answer.lower()
    hits = 0

    for keyword in answer_keywords:
        if keyword.lower() in answer_lower:
            hits += 1

    return hits / len(answer_keywords)


def faithfulness_score(answer, retrieved_docs):
    """
    Simple faithfulness:
    If the answer is copied from retrieved context, it is faithful.
    This is strict but useful for a toy extractive RAG system.
    """

    context = " ".join([doc["text"] for doc, _score in retrieved_docs])
    return 1.0 if answer in context else 0.0


def citation_relevance(cited_doc_id, gold_doc_ids):
    if cited_doc_id is None:
        return 0.0
    return 1.0 if cited_doc_id in set(gold_doc_ids) else 0.0


def classify_failure(row):
    """
    Classify the error type of each RAG result.
    """

    retrieval_success = row["recall_at_k"] > 0
    answer_success = row["answer_keyword_score"] >= 0.7
    faithful = row["faithfulness"] == 1.0
    citation_correct = row["citation_relevance"] == 1.0

    if retrieval_success and answer_success and faithful and citation_correct:
        return "success"

    if not faithful:
        return "hallucination_or_unfaithful_answer"

    if not retrieval_success:
        return "retrieval_failure"

    if retrieval_success and not answer_success and citation_correct:
        return "generation_failure"

    if retrieval_success and not citation_correct:
        return "citation_or_context_selection_failure"

    return "mixed_failure"


def run_topk_sensitivity():
    topk_values = [1, 2, 3, 5]
    all_results = []

    print()
    print("=== Top-k Sensitivity Experiment ===")

    for k in topk_values:
        rows = run_experiment(top_k=k)
        summary = summarize(rows)
        failure_summary = summarize_failure_types(rows)

        result = {
            "top_k": k,
            "recall_at_k": summary["recall_at_k"],
            "mrr": summary["mrr"],
            "ndcg_at_k": summary["ndcg_at_k"],
            "answer_keyword_score": summary["answer_keyword_score"],
            "faithfulness": summary["faithfulness"],
            "citation_relevance": summary["citation_relevance"],
            "success_count": failure_summary.get("success", {"count": 0})["count"],
            "generation_failure_count": failure_summary.get("generation_failure", {"count": 0})["count"],
            "context_selection_failure_count": failure_summary.get(
                "citation_or_context_selection_failure",
                {"count": 0}
            )["count"],
            "retrieval_failure_count": failure_summary.get("retrieval_failure", {"count": 0})["count"]
        }

        all_results.append(result)

        print()
        print(f"top_k = {k}")
        print(f"Recall@k: {result['recall_at_k']:.3f}")
        print(f"MRR: {result['mrr']:.3f}")
        print(f"nDCG@k: {result['ndcg_at_k']:.3f}")
        print(f"Answer keyword score: {result['answer_keyword_score']:.3f}")
        print(f"Faithfulness: {result['faithfulness']:.3f}")
        print(f"Citation relevance: {result['citation_relevance']:.3f}")
        print(f"Success count: {result['success_count']}")
        print(f"Generation failure count: {result['generation_failure_count']}")
        print(f"Context selection failure count: {result['context_selection_failure_count']}")
        print(f"Retrieval failure count: {result['retrieval_failure_count']}")

    return all_results



# -----------------------------
# 8. Full experiment
# -----------------------------

def run_experiment(top_k=3, use_hallucination_generator=False):
    retriever = BM25Retriever(documents)
    rows = []

    for item in qa_dataset:
        query = item["query"]
        gold_doc_ids = item["gold_doc_ids"]
        answer_keywords = item["answer_keywords"]

        retrieved = retriever.retrieve(query, top_k=top_k)
        retrieved_doc_ids = [doc["id"] for doc, _score in retrieved]

        if use_hallucination_generator:
              generated = generate_answer_with_hallucination(query, retrieved)
        else:
              generated = generate_answer(query, retrieved)
        answer = generated["answer"]
        cited_doc_id = generated["cited_doc_id"]

        row = {
            "query": query,
            "gold_doc_ids": ",".join(gold_doc_ids),
            "retrieved_doc_ids": ",".join(retrieved_doc_ids),
            "answer": answer,
            "cited_doc_id": cited_doc_id,
            "recall_at_k": recall_at_k(retrieved_doc_ids, gold_doc_ids, top_k),
            "mrr": mrr(retrieved_doc_ids, gold_doc_ids),
            "ndcg_at_k": ndcg_at_k(retrieved_doc_ids, gold_doc_ids, top_k),
            "answer_keyword_score": keyword_answer_score(answer, answer_keywords),
            "faithfulness": faithfulness_score(answer, retrieved),
            "citation_relevance": citation_relevance(cited_doc_id, gold_doc_ids)
        }

        row["failure_type"] = classify_failure(row)

        rows.append(row)

    return rows


def summarize(rows):
    metric_names = [
        "recall_at_k",
        "mrr",
        "ndcg_at_k",
        "answer_keyword_score",
        "faithfulness",
        "citation_relevance"
    ]

    summary = {}
    for metric in metric_names:
        summary[metric] = sum(row[metric] for row in rows) / len(rows)

    return summary


def save_results(rows, path):
    fieldnames = list(rows[0].keys())

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def summarize_failure_types(rows):
    counts = Counter(row["failure_type"] for row in rows)
    total = len(rows)

    summary = {}
    for failure_type, count in counts.items():
        summary[failure_type] = {
            "count": count,
            "ratio": count / total
        }

    return summary


def save_topk_results(rows, path):
    fieldnames = list(rows[0].keys())

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    rows = run_experiment(top_k=3)
    summary = summarize(rows)

    failure_summary = summarize_failure_types(rows)

    save_results(rows, "results/rag_eval_results.csv")

    print("=== Per-query Results ===")
    for row in rows:
        print()
        print("Query:", row["query"])
        print("Gold docs:", row["gold_doc_ids"])
        print("Retrieved docs:", row["retrieved_doc_ids"])
        print("Answer:", row["answer"])
        print("Cited doc:", row["cited_doc_id"])
        print("Recall@k:", row["recall_at_k"])
        print("MRR:", row["mrr"])
        print("nDCG@k:", row["ndcg_at_k"])
        print("Answer keyword score:", row["answer_keyword_score"])
        print("Faithfulness:", row["faithfulness"])
        print("Citation relevance:", row["citation_relevance"])
        print("Failure type:", row["failure_type"])

    print()
    print("=== Average Metrics ===")
    for metric, value in summary.items():
        print(f"{metric}: {value:.3f}")

        print()
    print("=== Failure Type Summary ===")
    for failure_type, item in failure_summary.items():
        print(f"{failure_type}: count={item['count']}, ratio={item['ratio']:.3f}")

    print()
    print("Saved results to results/rag_eval_results.csv")

    topk_results = run_topk_sensitivity()
    save_topk_results(topk_results, "results/topk_sensitivity_results.csv")

    print()
    print("Saved top-k sensitivity results to results/topk_sensitivity_results.csv")

    print()
    print("=== Hallucination Simulation ===")

    hallucination_rows = run_experiment(
        top_k=3,
        use_hallucination_generator=True
    )

    for row in hallucination_rows:
        if row["faithfulness"] == 0.0:
            print()
            print("Query:", row["query"])
            print("Answer:", row["answer"])
            print("Faithfulness:", row["faithfulness"])
            print("Failure type:", row["failure_type"])