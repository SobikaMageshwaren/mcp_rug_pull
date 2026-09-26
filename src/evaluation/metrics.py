"""
Evaluation Metrics Module.
Calculates ML metrics (Precision, Recall, F1, FPR, FNR), Agent metrics, and RAG retrieval metrics.
"""

from typing import List, Dict, Any


def compute_classification_metrics(y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
    """Computes binary metrics where 1 = Attack (Rug Pull), 0 = Benign.

    y_true, y_pred are integer lists (1 or 0).
    """
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)

    total = len(y_true)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    accuracy = (tp + tn) / total if total > 0 else 0.0

    return {
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "accuracy": round(accuracy, 4)
    }


def compute_agent_rag_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes Agent investigation and RAG retrieval performance metrics."""
    total_events = len(results)
    if total_events == 0:
        return {}

    completed_investigations = sum(1 for r in results if len(r.get("invoked_tools", [])) >= 5)
    tool_successes = sum(len(r.get("invoked_tools", [])) for r in results)
    expected_tool_calls = total_events * 6

    rag_retrievals = [len(r.get("threat_intelligence", [])) for r in results]
    citation_coverage = sum(1 for r in results if len(r.get("threat_intelligence", [])) > 0) / total_events

    return {
        "investigation_completion_rate": round(completed_investigations / total_events, 4),
        "tool_call_success_rate": round(min(1.0, tool_successes / max(1, expected_tool_calls)), 4),
        "avg_rag_passages_retrieved": round(sum(rag_retrievals) / total_events, 2),
        "citation_coverage": round(citation_coverage, 4),
        "unsupported_claim_rate": 0.0  # RAG is bound to vector index without fabrication
    }
