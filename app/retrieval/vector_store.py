from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Callable
import numpy as np


@dataclass
class ChunkRecord:
    text: str
    embedding: np.ndarray
    metadata: Dict[str, Any]


class InMemoryVectorStore:
    def __init__(self):
        self._items: List[ChunkRecord] = []

    def add(self, text: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        self._items.append(
            ChunkRecord(
                text=text,
                embedding=np.array(embedding, dtype=np.float32),
                metadata=metadata,
            )
        )

    def __len__(self) -> int:
        return len(self._items)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if not self._items:
            return []

        q = np.array(query_embedding, dtype=np.float32)
        mat = np.vstack([it.embedding for it in self._items])

        q = q / (np.linalg.norm(q) + 1e-12)
        mat = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-12)
        sims = mat @ q

        idxs = np.argsort(-sims)[:top_k]

        results = []
        for i in idxs:
            item = self._items[int(i)]
            results.append({
                "text": item.text,
                "metadata": item.metadata,
                "score": float(sims[int(i)])
            })

        return results

    def filter_by(self, predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
        """
        Return chunks whose metadata satisfies the predicate.
        Used for safety backstop (WARNING / DANGER).
        """
        results = []
        for it in self._items:
            if predicate(it.metadata):
                results.append({
                    "text": it.text,
                    "metadata": it.metadata,
                    "score": None
                })
        return results
