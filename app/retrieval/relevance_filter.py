from __future__ import annotations
from typing import List, Dict, Any


def prioritize_safety(results):
    def severity_rank(r):
        sev = (r.get("metadata", {}) or {}).get("severity", "NORMAL")
        if sev == "DANGER":
            return 2
        if sev == "WARNING":
            return 1
        return 0

    def safe_score(r):
        score = r.get("score")
        return score if isinstance(score, (int, float)) else 0.0

    return sorted(
        results,
        key=lambda r: (severity_rank(r), safe_score(r)),
        reverse=True
    )



def apply_threshold(results: List[Dict[str, Any]], min_score: float = 0.25) -> List[Dict[str, Any]]:
    return [r for r in results if r.get("score", 0.0) >= min_score]
