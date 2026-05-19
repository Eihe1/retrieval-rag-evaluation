# Day 9 Notes: Cost-Aware RAG Query Optimizer



## 1. Motivation



In previous days, the project moved from simple retrieval to retrieval evaluation, reranking, RAG evaluation, failure analysis, and adaptive RAG.



Day 8 introduced Adaptive RAG, where different strategies were selected based on query type and evidence condition. Day 9 extends this idea further by connecting RAG strategy selection to database query optimization.



The main question of Day 9 is:



```text

How should a RAG system choose the most suitable strategy for each query?

```



A fixed RAG pipeline is often inefficient because different queries require different levels of processing. Some queries are simple and can be answered with a cheap baseline strategy. Some queries require evidence filtering. Some require reranking. Some should not be answered at all because the retrieved evidence is weak.



Therefore, the system should not always use the strongest or most expensive strategy. It should choose the strategy with the best trade-off between quality, cost, and risk.



---



## 2. Database System Analogy



A database system does not execute every SQL query in the same way.



For example, it may choose between:



```text

sequential scan

index scan

bitmap scan

join order alternatives

different physical execution plans

```



The choice depends on estimated cost and expected performance.



Similarly, a RAG system can choose between:



```text

baseline RAG

evidence-first RAG

reranking RAG

abstention RAG

```



The analogy is:



| Database System | RAG System |

|---|---|

| SQL query | User question |

| Logical plan | Candidate RAG strategy |

| Physical plan | Actual retrieval/generation pipeline |

| Cost model | Estimated cost and hallucination risk |

| Query optimizer | Strategy selector |

| Execution result | Final answer |



The key idea is:



```text

RAG strategy selection can be treated as query optimization.

```



---



## 3. Strategies Implemented



### 3.1 Baseline RAG



`baseline\_rag` retrieves documents and directly uses the top-ranked document as evidence.



It has the lowest cost.



It is suitable when:



```text

the query is simple

the evidence is strong enough

the top-ranked document is clearly better than the others

```



This is similar to choosing a cheap database plan when it is already sufficient.



---



### 3.2 Evidence-First RAG



`evidence\_first\_rag` filters retrieved documents and only answers when the evidence score is strong enough.



It has slightly higher cost than baseline RAG, but lower risk.



It is suitable when:



```text

the query is slightly more complex

the retrieved evidence is strong

there is some need to avoid weak candidates

```



---



### 3.3 Reranking RAG



`reranking\_rag` applies an additional scoring step after first-stage retrieval.



It has higher cost because reranking requires extra query-document scoring.



It is suitable when:



```text

the correct document may already be retrieved

but the ranking among candidate documents is uncertain

```



The important point is:



```text

Reranking cannot recover missing documents.

It can only improve the order of already retrieved candidates.

```



Therefore, reranking should not be triggered simply because a query is difficult. It should be triggered when ranking ambiguity is high.



---



### 3.4 Abstention RAG



`abstention\_rag` refuses to answer when the retrieved evidence is too weak.



It has low hallucination risk.



It is suitable when:



```text

retrieved evidence is weak

the query is unsupported by the corpus

answering would likely cause hallucination

```



---



## 4. Main Signals



The optimizer uses three main query-level signals.



### 4.1 Evidence Strength



`evidence\_strength` estimates how strong the retrieved evidence is.



It is calculated from:



```text

top retrieval score

average retrieval score

```



The intuition is:



```text

higher evidence strength → more likely that the corpus supports the query

lower evidence strength → higher risk of unsupported answer

```



---



### 4.2 Ranking Ambiguity



`ranking\_ambiguity` estimates whether the top retrieved documents are difficult to distinguish.



It is based on the score gap between the top-1 and top-2 retrieved documents.



```text

large score gap → low ambiguity

small score gap → high ambiguity

```



The intuition is:



```text

if top-1 is clearly better than top-2, reranking is unnecessary

if top-1 and top-2 are close, reranking may be useful

```



This signal is important because reranking should be used for ranking uncertainty, not simply for query difficulty.



---



### 4.3 Query Difficulty



`query\_difficulty` is estimated using evidence strength and query length.



The current categories are:



```text

easy

medium

hard

```



In this experiment, difficulty is a rough heuristic. It is not the only factor used for strategy selection.



---



## 5. Utility Function



The optimizer selects the strategy with the highest utility.



The general form is:



```text

utility = estimated\_quality - cost\_penalty - risk\_penalty

```



In the implementation:



```python

utility = (

&#x20;   estimated\_quality

&#x20;   - lambda\_cost \* estimated\_cost

&#x20;   - lambda\_risk \* hallucination\_risk

)

```



This means a strategy is better when it has:



```text

higher estimated quality

lower execution cost

lower hallucination risk

```



This is the central design of the Day 9 system.



---



## 6. Current Experimental Results



The latest run produced the following output:



| Query | Difficulty | Evidence Strength | Ranking Ambiguity | Chosen Strategy | Quality Score |

|---|---|---:|---:|---|---:|

| What does BM25 rely on? | easy | 0.340 | 0.000 | `baseline\_rag` | 1.0 |

| Why is cross-encoder reranking expensive? | easy | 0.567 | 0.000 | `baseline\_rag` | 1.0 |

| What should RAG systems evaluate? | easy | 0.660 | 0.000 | `baseline\_rag` | 1.0 |

| How does abstention help RAG reliability? | medium | 0.167 | 1.000 | `abstention\_rag` | 0.2 |

| How is Adaptive RAG related to query optimization? | easy | 0.337 | 0.375 | `baseline\_rag` | 1.0 |

| Which method improves ranking after retrieval when candidate documents are ambiguous? | medium | 0.664 | 0.091 | `evidence\_first\_rag` | 1.0 |

| What is the best GPU for training huge models? | medium | 0.200 | 0.444 | `abstention\_rag` | 1.0 |



---



## 7. Result Analysis



### 7.1 Baseline RAG for Simple Queries



The system selected `baseline\_rag` for several simple queries:



```text

What does BM25 rely on?

Why is cross-encoder reranking expensive?

What should RAG systems evaluate?

How is Adaptive RAG related to query optimization?

```



This is correct because these queries have:



```text

sufficient evidence

low ranking ambiguity

clear top-1 retrieved document

```



Since baseline RAG already produces correct answers with the lowest cost, more complex strategies are unnecessary.



This is the expected behavior of a cost-aware optimizer.



---



### 7.2 Evidence-First RAG for Strong but More Complex Evidence



The system selected `evidence\_first\_rag` for:



```text

Which method improves ranking after retrieval when candidate documents are ambiguous?

```



The selected answer was correct:



```text

Reranking improves document ranking after first-stage retrieval when candidate scores are ambiguous.

```



The quality score was 1.0.



Although the query is about reranking, the optimizer did not choose `reranking\_rag` because the ranking ambiguity was low:



```text

ranking\_ambiguity = 0.091

```



This means the first-stage retriever already ranked the correct document clearly at the top. Since evidence-first RAG could answer correctly at lower cost than reranking, the optimizer avoided the expensive reranking plan.



This behavior is reasonable.



---



### 7.3 Abstention RAG for Unsupported Query



The system selected `abstention\_rag` for:



```text

What is the best GPU for training huge models?

```



The corpus does not contain GPU-related information. Therefore, refusing to answer is correct.



The quality score was 1.0 because the system avoided an unsupported answer.



This demonstrates that abstention can improve reliability by reducing hallucination risk.



---



## 8. Failure Case



The main failure case is:



```text

How does abstention help RAG reliability?

```



The selected strategy was:



```text

abstention\_rag

```



The answer was:



```text

I do not have enough reliable evidence to answer.

```



However, the corpus contains a relevant document:



```text

Abstention can reduce hallucination risk when retrieved evidence is weak or missing.

```



The expected supporting document was `doc6`.



This failure occurred because the simple lexical retriever did not match the query well. The query used words such as:



```text

help

RAG

reliability

```



while the relevant document used words such as:



```text

reduce

hallucination

risk

weak

missing

```



The retriever therefore underestimated evidence strength and caused over-abstention.



This failure type can be classified as:



```text

over-conservative abstention caused by weak lexical retrieval

```



This is an important observation because it shows that the optimizer depends on the quality of the retrieval signals. If the retrieval model produces weak evidence estimates, the optimizer may select an overly conservative strategy.



---



## 9. Observation on Reranking



`reranking\_rag` was not selected in the current run.



This is not necessarily a problem.



The reason is:



```text

the current toy corpus does not produce a true ranking ambiguity case

```



For the reranking-related query, the correct document was already retrieved as a clear top-1 result. Therefore, a cost-aware optimizer should not choose reranking because it would add unnecessary cost without improving the result.



The correct conclusion is:



```text

Reranking should be selected when ranking uncertainty is high, not simply when the query is about reranking or when the query is difficult.

```



A better future experiment would create a case where:



```text

the correct document is retrieved

but the top candidate documents have similar first-stage retrieval scores

```



In that case, reranking should become more useful.



---



## 10. Lessons Learned



### Lesson 1: Baseline RAG should not disappear



A cost-aware optimizer should still select baseline RAG when the query is simple and the evidence is clear.



Using a more complex strategy in that situation would waste cost.



---



### Lesson 2: Reranking is not a default strategy



Reranking has higher execution cost.



It should be used when:



```text

retrieval recall is sufficient

but ranking precision is uncertain

```



It should not be used when the first-stage retriever already gives a clear and correct top-1 result.



---



### Lesson 3: Abstention improves reliability but may over-refuse



Abstention is useful when evidence is weak or missing.



However, if the retriever underestimates relevant evidence, the system may abstain even when the answer is available.



This creates an over-conservative abstention failure.



---



### Lesson 4: Cost models strongly affect strategy selection



The selected strategy depends heavily on:



```text

estimated quality

estimated cost

hallucination risk

evidence strength

ranking ambiguity

```



If these estimates are inaccurate, the optimizer may choose a suboptimal strategy.



This is similar to database query optimization, where inaccurate cardinality or cost estimates can lead to poor execution plans.



---



## 11. Research Takeaway



The main research takeaway is:



```text

Reliable RAG should be viewed as a query optimization problem.

```



A RAG system should not use the same pipeline for every query. Instead, it should estimate the query condition and choose an execution strategy based on quality, cost, and risk.



The Day 9 system demonstrates this idea through a small toy implementation:



```text

simple and clear query → baseline RAG

strong but slightly more complex evidence → evidence-first RAG

weak or unsupported query → abstention RAG

ambiguous ranking → reranking RAG, if needed

```



The final insight is:



```text

Adaptive RAG becomes more meaningful when strategy selection is cost-aware, evidence-aware, and risk-aware.

```



---



## 12. Possible Future Improvements



Future versions could improve the system in several ways:



1\. Replace simple lexical retrieval with BM25 or dense retrieval.

2\. Use actual cross-encoder reranking instead of heuristic reranking.

3\. Learn the utility weights from evaluation data instead of manually setting them.

4\. Add more realistic cost estimates, such as latency, token usage, and model calls.

5\. Create more difficult ranking ambiguity cases to evaluate reranking behavior.

6\. Separate retrieval failure, ranking failure, generation failure, and over-abstention more explicitly.

7\. Compare fixed RAG, adaptive RAG, and cost-aware RAG on the same evaluation set.



---



## 13. Final Summary



Day 9 transformed the RAG pipeline from a simple adaptive router into a cost-aware strategy optimizer.



The system estimates evidence strength, ranking ambiguity, query difficulty, execution cost, and hallucination risk. It then selects the strategy with the highest utility.



The current result is meaningful because it shows different behavior for different query conditions:



```text

baseline\_rag for simple and clear queries

evidence\_first\_rag for strong but slightly more complex evidence

abstention\_rag for weak or unsupported queries

```



Reranking was not selected because the current dataset did not create a true ranking ambiguity case. This is acceptable and consistent with the cost-aware design: expensive reranking should be avoided when cheaper strategies already work.



The final conclusion is:



```text

A reliable RAG system needs not only retrieval and generation, but also a query optimizer that decides which strategy is worth using for each query.

```

