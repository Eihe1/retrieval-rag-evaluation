# Day 10 — Query Optimizer for RAG Systems

## Overview

Traditional RAG systems usually follow a fixed execution pipeline:

Query
→ Retrieval
→ Reranking
→ Generation

However, not every query requires the same retrieval strategy.

Simple factual questions may only require direct retrieval, while comparison questions often benefit from reranking. Structured analytical questions may be better answered using database-style aggregation rather than text retrieval.

This project explores the idea of treating RAG execution as a lightweight query optimization problem inspired by database management systems.

The optimizer analyzes a user query, estimates the expected quality and execution cost of multiple candidate plans, computes utilities, and selects the plan with the highest utility.

---

## Motivation

The project was motivated by an observation made during previous RAG evaluation experiments.

Throughout Days 4–9, several retrieval pipelines were implemented and evaluated:

- BM25 Retrieval
- Dense Retrieval
- Hybrid Retrieval
- Cross-Encoder Reranking
- Evidence-First RAG
- Abstention RAG
- Adaptive RAG

A key finding was that different queries often require different retrieval strategies.

Examples:

### Simple Fact Lookup

Query:

What does BM25 rely on?

Desired strategy:

Direct Retrieval

because retrieval is easy and evidence is obvious.

---

### Comparison Query

Query:

Compare BM25 and Dense Retrieval.

Desired strategy:

Hybrid Retrieval + Reranking

because information must be collected from multiple sources.

---

### Structured Query

Query:

Which product had the highest sales increase compared with the previous quarter?

Desired strategy:

SQL-style aggregation

rather than free-text retrieval.

---

These observations suggested that RAG pipelines could benefit from database-style optimization.

---

## System Architecture

The final optimizer follows the pipeline:

Query
↓
Intent Detection
↓
Feature Extraction
↓
Candidate Plan Generation
↓
Quality Prediction
↓
Cost Prediction
↓
Utility Calculation
↓
Plan Selection

---

## Candidate Plans

The optimizer currently supports five execution plans.

### Direct Retrieval

Single-stage retrieval without reranking.

Advantages:

- Lowest cost
- Fast execution

Disadvantages:

- Sensitive to ranking errors
- Limited reasoning support

---

### Hybrid Retrieval

Combines multiple retrieval signals.

Advantages:

- More robust retrieval
- Better coverage

Disadvantages:

- Higher retrieval cost

---

### Hybrid + Rerank

Hybrid retrieval followed by reranking.

Advantages:

- Highest answer quality
- Strong comparison and reasoning support

Disadvantages:

- Highest execution cost

---

### SQL Query

Database-style aggregation and analytical execution.

Advantages:

- Exact counting
- Aggregation support
- Ranking support

Disadvantages:

- Only suitable for structured questions

---

### Abstain

Refuses to answer when confidence is low.

Advantages:

- Prevents unsupported answers

Disadvantages:

- May over-refuse answerable questions

---

## Intent Detection

One major limitation of earlier versions was heavy reliance on keyword matching.

The system was gradually upgraded to include an intent layer.

Supported intents:

### fact_lookup

Examples:

- What is BM25?
- What does Recall@k mean?

Preferred plan:

Direct Retrieval

---

### comparison

Examples:

- Compare BM25 and Dense Retrieval
- Difference between DPR and ColBERT

Preferred plan:

Hybrid + Rerank

---

### failure_explanation

Examples:

- Why can reranking fail?
- Why does hallucination occur?

Preferred plan:

Hybrid + Rerank

---

### counting

Examples:

- How many failed queries exist?
- Number of unsupported answers

Preferred plan:

SQL Query

---

### structured_aggregation

Examples:

- Average nDCG
- Highest sales increase
- Lowest latency

Preferred plan:

SQL Query

---

### strategy_reasoning

Examples:

- Which strategy should be used?
- When should reranking be applied?

Preferred plan:

Hybrid + Rerank

---

## Evolution of the Optimizer

### Version 1

Static utility model.

Query
→ Utility Calculation
→ Plan Selection

Limitation:

No query awareness.

---

### Version 2

Query feature extraction.

Added:

- Difficulty
- Evidence Strength
- Ranking Ambiguity

Improvement:

Different queries produce different utilities.

---

### Version 3

Risk separation.

Original issue:

Queries discussing failure mechanisms were incorrectly classified as unsafe.

Example:

Why can reranking fail?

Incorrect:

Abstain

Improvement:

Risk was separated into:

- Content Failure Signal
- Answer Risk Signal

Result:

Failure analysis questions no longer trigger abstention.

---

### Version 4

Intent-aware optimizer.

Added:

- Fact Lookup
- Comparison
- Counting
- Aggregation
- Failure Explanation

Improvement:

Structured questions began routing to SQL Query.

---

### Version 5

Calibrated optimizer.

Problems addressed:

- Hybrid Retrieval dominating all plans
- SQL Query over-selected
- Fact queries not choosing Direct Retrieval

Solutions:

- Added fact lookup bias
- Reduced rerank quality inflation
- Reduced SQL quality inflation
- Added strategy reasoning intent

Result:

Plan selection became significantly more realistic.

---

## Example Outputs

### Fact Query

Query:

What does BM25 rely on?

Selected Plan:

Direct Retrieval

---

### Comparison Query

Query:

Compare BM25 and Dense Retrieval.

Selected Plan:

Hybrid + Rerank

---

### Failure Explanation

Query:

Why can reranking fail when relevant documents are missed?

Selected Plan:

Hybrid + Rerank

---

### Aggregation Query

Query:

Average nDCG across all test queries.

Selected Plan:

SQL Query

---

### Strategy Reasoning

Query:

Which strategy should be used when evidence is weak and ranking ambiguity is high?

Selected Plan:

Hybrid + Rerank

---

## Lessons Learned

The most important insight from this project is:

RAG execution can be viewed as a query optimization problem.

Instead of always executing the same retrieval pipeline, systems can estimate:

- expected quality
- expected cost
- expected utility

and choose the most suitable plan.

This perspective closely mirrors traditional database query optimization.

---

## Future Work

Current optimizer:

Rule-based Query Planner

Future direction:

Self-Calibrating Query Optimizer

Potential extensions:

- Execution feedback collection
- Actual quality measurement
- Prediction error analysis
- Automatic quality calibration
- Learned cost models
- Learned quality models
- Intent classification using ML models
- Retrieval strategy learning

Ultimate goal:

Query
↓
Learned Optimizer
↓
Execution Plan
↓
Feedback
↓
Continuous Improvement

similar to modern database optimizers.