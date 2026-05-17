# Query-level Diagnosis: Evidence-First RAG

## q1: What does BM25 rely on?

- Gold docs: ['doc1']
- Retrieved docs: ['doc1', 'doc3', 'doc2']
- Answer: BM25 is a sparse retrieval method based on lexical term matching and exact word overlap.
- Cited doc: doc1
- Answer keyword score: 1.000
- Faithfulness: 1.000
- Citation relevance: 1.000
- Failure type: `success`

Diagnosis: The answer, retrieved context, and citation are aligned.

## q2: What is dense retrieval?

- Gold docs: ['doc2']
- Retrieved docs: ['doc1', 'doc2', 'doc3']
- Answer: BM25 is a sparse retrieval method based on lexical term matching and exact word overlap.
- Cited doc: doc1
- Answer keyword score: 0.000
- Faithfulness: 1.000
- Citation relevance: 0.000
- Failure type: `ranking_or_context_selection_failure`

Diagnosis: The correct evidence may be retrieved, but it is not selected or used effectively.

## q3: Why can re-ranking fail?

- Gold docs: ['doc5']
- Retrieved docs: ['doc5', 'doc1', 'doc2']
- Answer: Re-ranking can improve the order of retrieved candidates, but it cannot recover relevant documents missing from the first-stage candidate set.
- Cited doc: doc5
- Answer keyword score: 1.000
- Faithfulness: 1.000
- Citation relevance: 1.000
- Failure type: `success`

Diagnosis: The answer, retrieved context, and citation are aligned.

## q4: What does faithfulness mean in RAG?

- Gold docs: ['doc7']
- Retrieved docs: ['doc6', 'doc7', 'doc1']
- Answer: RAG retrieves external documents and uses them as context for answer generation.
- Cited doc: doc6
- Answer keyword score: 0.500
- Faithfulness: 1.000
- Citation relevance: 0.000
- Failure type: `ranking_or_context_selection_failure`

Diagnosis: The correct evidence may be retrieved, but it is not selected or used effectively.

## q5: Why is citation relevance important?

- Gold docs: ['doc8']
- Retrieved docs: ['doc8', 'doc1', 'doc7']
- Answer: Citation relevance means that the cited document actually contains evidence for the generated answer.
- Cited doc: doc8
- Answer keyword score: 1.000
- Faithfulness: 1.000
- Citation relevance: 1.000
- Failure type: `success`

Diagnosis: The answer, retrieved context, and citation are aligned.

## q6: How does chunking affect RAG?

- Gold docs: ['doc10']
- Retrieved docs: ['doc6', 'doc10', 'doc1']
- Answer: RAG retrieves external documents and uses them as context for answer generation.
- Cited doc: doc6
- Answer keyword score: 0.333
- Faithfulness: 1.000
- Citation relevance: 0.000
- Failure type: `ranking_or_context_selection_failure`

Diagnosis: The correct evidence may be retrieved, but it is not selected or used effectively.

## q7: How does SQL transaction rollback work in RAG?

- Gold docs: []
- Retrieved docs: ['doc6', 'doc1', 'doc2']
- Answer: RAG retrieves external documents and uses them as context for answer generation.
- Cited doc: doc6
- Answer keyword score: 0.000
- Faithfulness: 1.000
- Citation relevance: 0.000
- Failure type: `unsupported_answer`

Diagnosis: The system answers despite insufficient supporting evidence.
