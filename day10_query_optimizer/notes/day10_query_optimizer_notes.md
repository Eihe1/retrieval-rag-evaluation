# Day 10 Notes — Query Optimizer for RAG Systems

## Objective

Investigate whether ideas from database query optimization can be applied to Retrieval-Augmented Generation systems.

Instead of executing a fixed retrieval pipeline for every query, build an optimizer that selects different execution plans according to query characteristics.

---

# Background

Previous experiments (Days 4–9) implemented:

- BM25 Retrieval
- Dense Retrieval
- Hybrid Retrieval
- Cross-Encoder Reranking
- Retrieval Evaluation
- Failure Diagnosis
- Adaptive RAG
- Cost-Aware RAG

A recurring observation was:

Different queries require different retrieval strategies.

Examples:

Simple factual questions rarely require reranking.

Comparison questions benefit from reranking.

Counting questions are better handled by structured aggregation.

This observation motivated the construction of a query optimizer.

---

# Initial Design

Initial architecture:

Query
↓
Quality Estimation
↓
Cost Estimation
↓
Utility Calculation
↓
Best Plan

Candidate plans:

- Direct Retrieval
- Hybrid Retrieval
- Hybrid + Rerank

Utility:

Utility = Quality − λ × Cost

---

# First Limitation

Problem:

The optimizer ignored query semantics.

Example:

What does BM25 rely on?

and

Compare BM25 and Dense Retrieval

received similar treatment.

Improvement:

Introduce feature extraction.

---

# Query Features

Three signals were added.

## Difficulty

Estimated reasoning complexity.

Examples:

Fact lookup → low

Comparison → high

---

## Evidence Strength

Estimated evidence availability.

High evidence:

Definition questions

Low evidence:

Ambiguous reasoning tasks

---

## Ranking Ambiguity

Measures uncertainty in retrieval ranking.

High ambiguity:

Comparison questions

Low ambiguity:

Definition questions

---

# Risk Modeling

Original approach:

Single risk signal.

Problem:

The optimizer confused discussion about failures with actual uncertainty.

Example:

Why can reranking fail?

incorrectly triggered Abstain.

---

## Solution

Split risk into two signals.

### Content Failure Signal

Query discusses:

- failures
- hallucinations
- missed retrievals

This should increase reasoning difficulty but not trigger abstention.

---

### Answer Risk Signal

Query may genuinely lack evidence.

Examples:

- unsupported answer
- unknown information
- insufficient evidence

This may justify abstention.

---

Result:

Failure analysis questions no longer route to Abstain.

---

# Intent Layer

A major limitation remained.

Keyword-based rules alone were insufficient.

An intent detection layer was introduced.

Supported intents:

- fact_lookup
- comparison
- failure_explanation
- counting
- structured_aggregation
- strategy_reasoning

---

# Counting Detection Evolution

Original rule:

if "how many" in query

Problems:

Too narrow.

Failed to detect:

- number of failures
- count of hallucinations
- total number of queries

---

Improvement:

Counting patterns:

- how many
- number of
- count of
- total number
- frequency of

Result:

Reliable counting detection.

---

# Aggregation Detection

Added support for:

- average
- mean
- maximum
- minimum
- highest
- lowest
- top-k

Result:

Analytical questions correctly routed to SQL Query.

---

# Strategy Reasoning

Unexpected issue:

Query:

Which strategy should be used when evidence is weak and ranking ambiguity is high?

was classified as:

structured_aggregation

because of matching keywords.

---

Solution:

Added:

strategy_reasoning

patterns:

- strategy
- should
- choose
- decision
- optimizer
- policy

Result:

Correctly routed to reasoning plans.

---

# Plan Calibration

Several calibration iterations were required.

---

## Issue 1

Hybrid Retrieval selected almost everything.

Reason:

Quality bonuses too large.

Solution:

Reduce quality inflation.

---

## Issue 2

Hybrid + Rerank frequently reached quality = 1.0.

Reason:

Excessive evidence bonuses.

Solution:

Reduce rerank bonus.

---

## Issue 3

Fact queries selected Hybrid Retrieval.

Example:

What does BM25 rely on?

Solution:

Introduce fact lookup bias.

Effects:

Direct Retrieval rewarded.

Complex plans penalized.

Result:

Fact questions now select Direct Retrieval.

---

## Issue 4

SQL Query over-selected.

Reason:

Structured reward too large.

Solution:

Reduce SQL base quality.

Result:

Better balance.

---

# Final Architecture

Query
↓
Intent Detection
↓
Feature Extraction
↓
Quality Prediction
↓
Cost Prediction
↓
Utility Calculation
↓
Plan Selection

---

# Final Behavior

Fact Lookup

→ Direct Retrieval

Comparison

→ Hybrid + Rerank

Failure Explanation

→ Hybrid + Rerank

Counting

→ SQL Query

Aggregation

→ SQL Query

Strategy Reasoning

→ Hybrid + Rerank

---

# Main Insight

RAG pipelines should not always use the same execution strategy.

Query-dependent planning can improve both efficiency and answer quality.

This is conceptually similar to database query optimization.

---

# Remaining Limitations

Current optimizer remains heuristic.

Quality estimates are manually designed.

Cost estimates are manually designed.

Intent detection relies on rules.

No execution feedback is incorporated.

No learning mechanism exists.

---

# Proposed Day 11 Direction

Self-Calibrating Query Optimizer

Pipeline:

Query
↓
Optimizer
↓
Plan
↓
Execution
↓
Observed Quality
↓
Prediction Error
↓
Model Update

Goals:

- collect optimizer history
- compare predicted vs actual quality
- estimate prediction error
- calibrate quality models
- move toward learned optimization

Transition:

Rule-Based Optimizer
↓
Feedback-Aware Optimizer
↓
Learned Optimizer