# Day 7 Diagnosis Summary

## 1. Purpose

This experiment extends Day 6 RAG evaluation by moving from metric-based evaluation to diagnosis-driven improvement. The goal is to identify the main system bottlenecks and test targeted strategies such as evidence-first answering and abstention.

## 2. Baseline Summary

- Mean answer keyword score: 0.714
- Mean faithfulness: 0.714
- Mean citation relevance: 0.714
- Abstention rate: 0.000
- Failure counts: {'success': 3, 'hallucination_or_unfaithful_answer': 1, 'citation_failure': 1, 'ranking_or_context_selection_failure': 1, 'unsupported_answer': 1}

## 3. Evidence-First Summary

- Mean answer keyword score: 0.548
- Mean faithfulness: 1.000
- Mean citation relevance: 0.429
- Abstention rate: 0.000
- Failure counts: {'success': 3, 'ranking_or_context_selection_failure': 3, 'unsupported_answer': 1}

## 4. Abstention Summary

- Mean answer keyword score: 0.429
- Mean faithfulness: 1.000
- Mean citation relevance: 0.429
- Abstention rate: 0.429
- Failure counts: {'success': 3, 'ranking_or_context_selection_failure': 1, 'over_conservative_abstention': 2, 'correct_abstention': 1}

## 5. Research Takeaway

The baseline system shows that retrieval success alone does not guarantee answer quality. Some failures are caused by weak answer grounding or wrong citation selection rather than missing retrieval results. The evidence-first strategy introduces an explicit intermediate evidence selection step, which makes the generation process more grounded and easier to inspect. The abstention strategy further improves reliability by avoiding unsupported answers when the retrieved evidence is weak. This suggests that reliable RAG systems should not only retrieve relevant documents, but also diagnose bottlenecks and select different execution strategies based on query-level evidence quality.
