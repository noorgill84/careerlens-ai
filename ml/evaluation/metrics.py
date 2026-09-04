"""
Evaluation metrics for the two ML tasks in this project:
  1. Information extraction (precision/recall/F1 over extracted fields)
  2. Ranking/matching (Precision@K, Recall@K, MRR, NDCG)

IMPORTANT: these functions compute real metrics from data you provide.
Nothing here fabricates a score — see docs/EVALUATION.md for how to run
this against a labeled sample and report honest numbers (spec §32/§49).
"""
from __future__ import annotations
import math


def precision_recall_f1(predicted: set, actual: set) -> dict[str, float]:
    if not predicted and not actual:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    tp = len(predicted & actual)
    precision = tp / len(predicted) if predicted else 0.0
    recall = tp / len(actual) if actual else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}


def precision_at_k(ranked_ids: list, relevant_ids: set, k: int) -> float:
    top_k = ranked_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for x in top_k if x in relevant_ids)
    return round(hits / len(top_k), 4)


def recall_at_k(ranked_ids: list, relevant_ids: set, k: int) -> float:
    if not relevant_ids:
        return 0.0
    top_k = ranked_ids[:k]
    hits = sum(1 for x in top_k if x in relevant_ids)
    return round(hits / len(relevant_ids), 4)


def mean_reciprocal_rank(list_of_ranked_ids: list[list], list_of_relevant_ids: list[set]) -> float:
    reciprocal_ranks = []
    for ranked_ids, relevant_ids in zip(list_of_ranked_ids, list_of_relevant_ids):
        rr = 0.0
        for i, item in enumerate(ranked_ids, start=1):
            if item in relevant_ids:
                rr = 1.0 / i
                break
        reciprocal_ranks.append(rr)
    return round(sum(reciprocal_ranks) / len(reciprocal_ranks), 4) if reciprocal_ranks else 0.0


def ndcg_at_k(ranked_ids: list, relevance: dict, k: int) -> float:
    """relevance: {id: graded_relevance_score (e.g. 0-3)}"""
    top_k = ranked_ids[:k]
    dcg = sum(relevance.get(item, 0) / math.log2(i + 1) for i, item in enumerate(top_k, start=1))
    ideal_order = sorted(relevance.values(), reverse=True)[:k]
    idcg = sum(rel / math.log2(i + 1) for i, rel in enumerate(ideal_order, start=1))
    return round(dcg / idcg, 4) if idcg > 0 else 0.0
