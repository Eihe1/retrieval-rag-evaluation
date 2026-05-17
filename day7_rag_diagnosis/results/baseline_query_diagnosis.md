# Query-level Diagnosis: Baseline RAG

## q1: What does BM25 rely on?

- Gold docs: ['doc1']
- Retrieved docs: ['doc1', 'doc3', 'doc2']
- Answer: BM25 is a sparse retrieval method based on lexical term matching.
- Cited doc: doc1
- Answer keyword score: 1.000
- Faithfulness: 1.000
- Citation relevance: 1.000
- Failure type: `success`

Diagnosis: The answer, retrieved context, and citation are aligned.

## q2: What is dense retrieval?

- Gold docs: ['doc2']
- Retrieved docs: ['doc1', 'doc2', 'doc3']
- Answer: Dense retrieval is mainly based on SQL joins and B-tree indexes.
- Cited doc: doc2
- Answer keyword score: 0.000
- Faithfulness: 0.000
- Citation relevance: 1.000
- Failure type: `hallucination_or_unfaithful_answer`

Diagnosis: The answer is not sufficiently supported by the retrieved context.

## q3: Why can re-ranking fail?

- Gold docs: ['doc5']
- Retrieved docs: ['doc5', 'doc1', 'doc2']
- Answer: Re-ranking improves ranking quality, but it cannot recover documents missing from the first-stage candidate set.
- Cited doc: doc4
- Answer keyword score: 1.000
- Faithfulness: 1.000
- Citation relevance: 0.000
- Failure type: `citation_failure`

Diagnosis: The answer is mostly correct, but the cited document does not match the supporting evidence.

## q4: What does faithfulness mean in RAG?

- Gold docs: ['doc7']
- Retrieved docs: ['doc6', 'doc7', 'doc1']
- Answer: Faithfulness means the answer is fluent and convincing.
- Cited doc: doc7
- Answer keyword score: 0.000
- Faithfulness: 1.000
- Citation relevance: 1.000
- Failure type: `ranking_or_context_selection_failure`

Diagnosis: The correct evidence may be retrieved, but it is not selected or used effectively.

## q5: Why is citation relevance important?

- Gold docs: ['doc8']
- Retrieved docs: ['doc8', 'doc1', 'doc7']
- Answer: Citation relevance means the cited document contains evidence for the generated answer.
- Cited doc: doc8
- Answer keyword score: 1.000
- Faithfulness: 1.000
- Citation relevance: 1.000
- Failure type: `success`

Diagnosis: The answer, retrieved context, and citation are aligned.

## q6: How does chunking affect RAG?

- Gold docs: ['doc10']
- Retrieved docs: ['doc6', 'doc10', 'doc1']
- Answer: Chunking can affect context completeness and may introduce noise.
- Cited doc: doc10
- Answer keyword score: 1.000
- Faithfulness: 1.000
- Citation relevance: 1.000
- Failure type: `success`

Diagnosis: The answer, retrieved context, and citation are aligned.

## q7: How does SQL transaction rollback work in RAG?

- Gold docs: []
- Retrieved docs: ['doc6', 'doc1', 'doc2']
- Answer: SQL transaction rollback in RAG is handled by vector embeddings.
- Cited doc: doc2
- Answer keyword score: 1.000
- Faithfulness: 0.000
- Citation relevance: 0.000
- Failure type: `unsupported_answer`

Diagnosis: The system answers despite insufficient supporting evidence.
