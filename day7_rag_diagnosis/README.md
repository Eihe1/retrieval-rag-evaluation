# Day 7: RAG Diagnosis and Strategy Trade-off Analysis

This module extends the previous RAG evaluation pipeline by moving from metric-based evaluation to diagnosis-driven improvement.

Instead of only measuring whether a RAG system succeeds or fails, this experiment analyzes different failure modes and compares targeted strategies, including baseline answering, evidence-first answering, and abstention.

## 1. Motivation

Day 6 showed that retrieval success does not guarantee answer success. A RAG system may retrieve the correct document but still fail due to weak answer grounding, wrong citation selection, or unsupported generation.

Day 7 focuses on a further question:

```text
Given a RAG failure, what kind of system change should be applied?
```

This shifts the focus from evaluation to diagnosis and strategy selection.

## 2. Goal

The goal of this experiment is to compare three RAG strategies:

1. Baseline RAG
2. Evidence-First RAG
3. Abstention RAG

The experiment studies how these strategies behave under different failure modes, including:

- hallucination or unfaithful answer
- citation failure
- ranking or context selection failure
- unsupported answer
- correct abstention
- over-conservative abstention

## 3. Methods

### 3.1 Baseline RAG

The baseline pipeline follows a standard RAG flow:

```text
query
→ retrieve documents
→ generate answer
→ cite document
→ evaluate
```

This strategy answers every query. It has high coverage, but it may produce unsupported answers or incorrect citations.

### 3.2 Evidence-First RAG

The evidence-first pipeline adds an explicit evidence selection step:

```text
query
→ retrieve documents
→ select evidence sentence
→ generate answer from selected evidence
→ cite evidence document
→ evaluate
```

This strategy improves grounding because the answer is directly based on retrieved evidence. However, if the evidence selector chooses the wrong sentence, the answer may still be incorrect or incomplete.

### 3.3 Abstention RAG

The abstention pipeline checks whether the selected evidence is strong enough before answering:

```text
query
→ retrieve documents
→ select evidence sentence
→ check evidence strength
→ answer if evidence is sufficient
→ abstain if evidence is weak
```

This strategy reduces unsupported answers, but it may also become too conservative and refuse to answer even when the correct document has been retrieved.

## 4. Metrics

The experiment uses the following metrics:

| Metric | Meaning |
|---|---|
| Answer keyword score | Whether the answer contains expected key concepts |
| Faithfulness | Whether the answer is supported by the retrieved context |
| Citation relevance | Whether the cited document is the correct supporting document |
| Abstention rate | Proportion of queries where the system refuses to answer |
| Failure type | Query-level diagnosis of the failure reason |

## 5. Results

| Strategy | Answer Keyword Score | Faithfulness | Citation Relevance | Abstention Rate |
|---|---:|---:|---:|---:|
| Baseline RAG | 0.714 | 0.714 | 0.714 | 0.000 |
| Evidence-First RAG | 0.548 | 1.000 | 0.429 | 0.000 |
| Abstention RAG | 0.429 | 1.000 | 0.429 | 0.429 |

## 6. Failure Counts

### 6.1 Baseline RAG

```text
success: 3
hallucination_or_unfaithful_answer: 1
citation_failure: 1
ranking_or_context_selection_failure: 1
unsupported_answer: 1
```

The baseline strategy answers all queries, but it produces several reliability issues.

### 6.2 Evidence-First RAG

```text
success: 3
ranking_or_context_selection_failure: 3
unsupported_answer: 1
```

The evidence-first strategy improves faithfulness, but it still fails when the evidence selector chooses an irrelevant or incomplete sentence.

### 6.3 Abstention RAG

```text
success: 3
ranking_or_context_selection_failure: 1
over_conservative_abstention: 2
correct_abstention: 1
```

The abstention strategy successfully avoids one unsupported answer, but it also abstains too conservatively in two cases where the gold document was already retrieved.

## 7. Analysis

The baseline RAG system achieves the highest answer keyword score and answers every query. However, it also produces multiple reliability problems, including hallucination or unfaithful answers, citation failure, and unsupported answers.

The evidence-first strategy improves faithfulness from 0.714 to 1.000 because answers are directly grounded in retrieved evidence. However, the answer keyword score decreases from 0.714 to 0.548, and citation relevance decreases from 0.714 to 0.429. This shows that evidence-first answering improves grounding, but naive evidence selection can select faithful yet irrelevant evidence.

The abstention strategy also achieves faithfulness of 1.000 and converts the unsupported answer into a correct abstention. However, the abstention rate increases to 0.429, and two cases become over-conservative abstentions. This shows a trade-off between reliability and coverage.

## 8. Key Findings

### Finding 1: Retrieval success does not guarantee answer success

A system may retrieve the correct document but still generate an incorrect or unsupported answer.

### Finding 2: Answer correctness and citation correctness are different

The system may generate a correct answer but cite the wrong document. This is a citation failure.

### Finding 3: Evidence-first answering improves grounding but depends on evidence selection

Evidence-first RAG reduces unfaithful generation, but if the evidence selector is weak, the system may select the wrong evidence sentence.

### Finding 4: Abstention reduces unsupported answers but may be over-conservative

Abstention can prevent unsupported answers, but it may also refuse to answer when the correct evidence is already available.

### Finding 5: No single strategy dominates all metrics

Baseline RAG has higher coverage, evidence-first RAG has stronger grounding, and abstention RAG improves reliability. Each strategy introduces different trade-offs.

## 9. Final Interpretation

The final results show that different RAG strategies optimize different objectives and introduce different failure modes.

The baseline RAG strategy achieves the highest answer keyword score and answers every query, but it also produces reliability issues, including hallucination or unfaithful answers, citation failure, and unsupported answers.

The evidence-first strategy improves faithfulness to 1.000 because answers are directly grounded in retrieved evidence. However, the answer keyword score and citation relevance decrease because the current evidence selector relies on simple lexical overlap and may select faithful but irrelevant evidence.

The abstention strategy successfully converts the unsupported answer into a correct abstention. However, it also produces over-conservative abstentions when the gold document is already retrieved but the evidence sufficiency check fails to recognize it.

Overall, the experiment shows that reliable RAG systems need diagnosis-driven strategy selection. A system should distinguish between retrieval failure, evidence selection failure, citation failure, unsupported answer, and over-conservative abstention before choosing whether to answer, re-rank, rewrite the query, verify citation, or abstain.

## 10. Research Implication

This experiment motivates the following research direction:

```text
Diagnosis-driven and cost-aware optimization for multi-stage RAG retrieval pipelines.
```

A reliable RAG system should behave more like a query optimizer. It should inspect the query, estimate retrieval quality and evidence strength, then choose an appropriate execution strategy.

For example:

| Diagnosis | Possible Strategy |
|---|---|
| Evidence missing | Query rewriting or retrieve again |
| Evidence retrieved but ranked low | Re-ranking |
| Evidence retrieved but not selected | Better evidence selector |
| Answer correct but citation wrong | Citation verification |
| No evidence exists | Abstention |
| Abstention too conservative | Relax threshold or improve evidence scoring |

## 11. Files

```text
day7_rag_diagnosis/
├── README.md
├── src/
│   └── day7_rag_diagnosis_demo.py
├── results/
│   ├── baseline_results.csv
│   ├── evidence_first_results.csv
│   ├── abstention_results.csv
│   ├── diagnosis_summary.md
│   ├── baseline_query_diagnosis.md
│   ├── evidence_first_query_diagnosis.md
│   └── abstention_query_diagnosis.md
└── notes/
    └── day7_rag_diagnosis_notes.md
```

## 12. Main Takeaway

```text
Baseline RAG answers more queries but can be unreliable.
Evidence-First RAG improves grounding but depends on evidence selection quality.
Abstention RAG avoids unsupported answers but may reduce coverage.

Therefore, reliable RAG systems should not use one fixed pipeline for all queries. They should diagnose query-level risks and select an appropriate strategy.
```