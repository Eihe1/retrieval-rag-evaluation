# Day 9: Cost-Aware RAG Query Optimizer



## Overview



This folder contains the Day 9 experiment of the retrieval and RAG evaluation project.



The goal of Day 9 is to extend the previous Adaptive RAG system into a more database-inspired **cost-aware RAG query optimizer**. Instead of using a fixed RAG pipeline or a simple rule-based router, this experiment treats different RAG strategies as alternative execution plans and selects the most suitable strategy according to estimated quality, cost, risk, evidence strength, and ranking ambiguity.



The key idea is:



```text

RAG strategy selection can be framed as a query optimization problem.

```



Similar to a database query optimizer, the system estimates the properties of a query and then chooses the execution plan with the highest expected utility.



---



## Project Structure



```text

day9_cost_aware_rag/

├── README.md

├── src/

│   └── cost_aware_rag_demo.py

├── results/

│   ├── cost_aware_rag_results.csv

│   └── strategy_decision_log.csv

└── notes/

&#x20;   └── day9_cost_aware_rag_notes.md

```



---



## Main Concepts



Day 9 introduces four strategy candidates:



| Strategy | Role |

|---|---|

| `baseline_rag` | Low-cost strategy for simple queries with clear evidence |

| `evidence_first_rag` | Moderate-cost strategy that prefers stronger retrieved evidence |

| `reranking_rag` | Higher-cost strategy for ambiguous ranking situations |

| `abstention_rag` | Conservative strategy for weak or unsupported evidence |



The optimizer considers:



| Signal | Meaning |

|---|---|

| `evidence_strength` | How strong the retrieved evidence appears |

| `ranking_ambiguity` | Whether the top retrieved documents are difficult to distinguish |

| `query_difficulty` | Whether the query is easy, medium, or hard |

| `estimated_cost` | Approximate execution cost of a strategy |

| `hallucination_risk` | Estimated risk of unsupported generation |

| `utility` | Final score used to select the strategy |



---



## Utility Function



The core decision rule is based on expected utility:



```text

utility = estimated_quality - cost_penalty - risk_penalty

```



In the implementation:



```python

utility = (

&#x20;   estimated_quality

&#x20;   - lambda_cost * estimated_cost

&#x20;   - lambda_risk * hallucination_risk

)

```



This means a strategy is preferred when it has:



```text

high expected quality

low execution cost

low hallucination risk

```



---



## Strategy Selection Logic



The optimizer follows these general principles:



```text

simple query + strong evidence + low ranking ambiguity

→ baseline_rag

```



```text

strong evidence + slightly more complex query

→ evidence_first_rag

```



```text

high ranking ambiguity + sufficient evidence

→ reranking_rag

```



```text

weak evidence or unsupported query

→ abstention_rag

```



This design shows that a reliable RAG system should not always choose the most complex strategy. More expensive strategies should only be selected when their expected reliability improvement justifies the additional cost.



---



## How to Run



From the `day9_cost_aware_rag` directory:



```bash

python src/cost_aware_rag_demo.py

```



The script generates two result files:



```text

results/cost_aware_rag_results.csv

results/strategy_decision_log.csv

```



---



## Output Files



### `cost_aware_rag_results.csv`



This file records the final selected strategy for each query.



Main columns:



| Column | Meaning |

|---|---|

| `query` | Input question |

| `gold_doc` | Expected supporting document |

| `chosen_strategy` | Strategy selected by the optimizer |

| `cited_doc` | Document cited by the selected strategy |

| `answer` | Generated or extracted answer |

| `evidence_strength` | Estimated strength of retrieved evidence |

| `ranking_ambiguity` | Estimated ranking uncertainty |

| `query_difficulty` | Query difficulty category |

| `utility` | Utility score of the selected strategy |

| `quality_score` | Final evaluation score |



### `strategy_decision_log.csv`



This file records the utility of every candidate strategy for every query.



It is useful for understanding why the optimizer selected one strategy over another.



Main columns:



| Column | Meaning |

|---|---|

| `query` | Input question |

| `strategy` | Candidate strategy |

| `estimated_cost` | Estimated execution cost |

| `hallucination_risk` | Estimated hallucination risk |

| `utility` | Final utility score |

| `evidence_strength` | Evidence score for the query |

| `ranking_ambiguity` | Ranking uncertainty score |



---



## Current Experimental Results



The current run produced three main behaviors:



| Query Type | Selected Strategy | Interpretation |

|---|---|---|

| Simple factual query with clear evidence | `baseline_rag` | Cheapest strategy is sufficient |

| Strong evidence but slightly more complex query | `evidence_first_rag` | Evidence filtering is useful |

| Weak or unsupported evidence | `abstention_rag` | Refusal reduces hallucination risk |



Example results:



| Query | Chosen Strategy | Quality Score |

|---|---|---:|

| What does BM25 rely on? | `baseline_rag` | 1.0 |

| Why is cross-encoder reranking expensive? | `baseline_rag` | 1.0 |

| What should RAG systems evaluate? | `baseline_rag` | 1.0 |

| How is Adaptive RAG related to query optimization? | `baseline_rag` | 1.0 |

| Which method improves ranking after retrieval when candidate documents are ambiguous? | `evidence_first_rag` | 1.0 |

| What is the best GPU for training huge models? | `abstention_rag` | 1.0 |



---



## Observation on Reranking



In the current run, `reranking_rag` was not selected.



This is not necessarily a failure. The toy corpus did not produce a true ranking ambiguity case where the correct document was retrieved but not clearly ranked at the top. Since cheaper strategies already produced correct answers, the optimizer correctly avoided the more expensive reranking plan.



This reflects an important cost-aware principle:



```text

Reranking should be triggered by ranking uncertainty, not by query difficulty alone.

```



---



## Failure Case



One answerable query was over-abstained:



```text

How does abstention help RAG reliability?

```



The system selected `abstention_rag`, but the corpus contained a relevant document:



```text

Abstention can reduce hallucination risk when retrieved evidence is weak or missing.

```



This failure was caused by weak lexical retrieval. The query used words such as `help` and `reliability`, while the relevant document used words such as `reduce`, `hallucination`, `risk`, `weak`, and `missing`.



This can be classified as:



```text

over-conservative abstention caused by weak lexical retrieval

```



---



## Key Takeaway



Day 9 shows that RAG can be viewed as a query optimization problem.



A cost-aware RAG system should estimate query difficulty, evidence strength, ranking ambiguity, execution cost, and hallucination risk before choosing a strategy. Simple queries should use cheap plans, ambiguous rankings may justify reranking, and weak evidence should trigger abstention.



The main research takeaway is:



```text

Reliable RAG requires not only better retrieval or generation, but also better strategy selection under cost and risk constraints.

```

