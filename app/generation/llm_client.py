from __future__ import annotations
import os
from openai import OpenAI

DEFAULT_LLM_MODEL = "gpt-4o-mini"


class OpenAILLMClient:
    def __init__(self, model: str = DEFAULT_LLM_MODEL):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, messages):
        resp = self.client.responses.create(
            model=self.model,
            input=messages
        )
        return resp.output_text
