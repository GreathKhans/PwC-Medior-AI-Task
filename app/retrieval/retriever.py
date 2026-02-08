from __future__ import annotations
from typing import List, Dict, Any
from collections import Counter
from app.retrieval.vector_store import InMemoryVectorStore
from app.retrieval.relevance_filter import apply_threshold, prioritize_safety


def _select_primary_source(results):
    """
    Pick the most frequent source among retrieved results.
    """
    sources = [
        (r.get("metadata") or {}).get("source")
        for r in results
        if (r.get("metadata") or {}).get("source")
    ]
    if not sources:
        return None
    return Counter(sources).most_common(1)[0][0]


def _deduplicate(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate chunks based on (source, page, text).
    """
    seen = set()
    unique = []

    for r in results:
        md = r.get("metadata", {}) or {}
        key = (
            md.get("source"),
            md.get("page"),
            r.get("text", "").strip()
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    return unique


def retrieve_top_chunks(
    store: InMemoryVectorStore,
    query_embedding: List[float],
    top_k: int = 6,
    min_score: float = 0.25,
    safety_k: int = 4
) -> List[Dict[str, Any]]:

    raw = store.search(query_embedding, top_k=top_k)
    filtered = apply_threshold(raw, min_score=min_score)

    primary_source = _select_primary_source(filtered)
    if not primary_source:
        return []

    safety_chunks = store.filter_by(
        lambda md: (
            md.get("source") == primary_source
            and md.get("severity") in ("WARNING", "DANGER")
        )
    )[:safety_k]

    related_checks = store.filter_by(
        lambda md: (
            md.get("source") == primary_source
            and md.get("severity") == "NORMAL"
        )
    )[:6]

    merged = _deduplicate(filtered + safety_chunks + related_checks)


    return prioritize_safety(merged)

