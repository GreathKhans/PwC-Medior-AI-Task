from __future__ import annotations
from typing import List
import os
from openai import OpenAI

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


class OpenAIEmbedder:
    def __init__(self, model: str = DEFAULT_EMBEDDING_MODEL):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        resp = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [d.embedding for d in resp.data]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]
