from typing import List, Dict, Any

def compute_confidence_score(retrieved: List[Dict[str, Any]]) -> float:
    if not retrieved:
        return 0.0

    scores = [r.get("score", 0.0) for r in retrieved if r.get("score") is not None]

    if not scores:
        return 0.0

    avg_score = sum(scores) / len(scores)

    coverage_bonus = min(len(scores) / 10.0, 1.0)  # max +1.0

    confidence = avg_score * 0.7 + coverage_bonus * 0.3

    return round(confidence * 100, 1)