from __future__ import annotations
import os
from typing import List, Dict, Any
from pathlib import Path
import sys
from dotenv import load_dotenv

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_cleaner import clean_text
from app.ingestion.metadata_extractor import extract_metadata
from app.ingestion.text_splitter import split_text

from app.guardrails.answer_validator import validate_safety_verbatim
from app.guardrails.confidence_checker import compute_confidence_score

from app.retrieval.embedder import OpenAIEmbedder
from app.retrieval.vector_store import InMemoryVectorStore
from app.retrieval.retriever import retrieve_top_chunks

from app.generation.prompt_builder import build_messages
from app.generation.intent_detector import detect_intent
from app.generation.llm_client import OpenAILLMClient
from app.generation.answer_formatter import format_answer

from app.logging.audit_logger import log_interaction

load_dotenv()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

def ingest_document(path: str) -> List[Dict[str, Any]]:
    pages = load_pdf(path)
    all_chunks: List[Dict[str, Any]] = []

    for page in pages:
        cleaned = clean_text(page["text"])
        meta = extract_metadata(cleaned)
        chunks = split_text(cleaned, max_length=900)

        for ch in chunks:
            ch_meta = extract_metadata(ch)
            merged = {
                "severity": ch_meta.get("severity", meta.get("severity")),
                "section": meta.get("section"),
                "page": page["page"],
                "source": os.path.basename(path),
            }
            all_chunks.append({"text": ch, "metadata": merged})

    return all_chunks


def build_index(pdf_paths: List[str]) -> InMemoryVectorStore:
    embedder = OpenAIEmbedder()
    store = InMemoryVectorStore()

    all_records: List[Dict[str, Any]] = []
    for p in pdf_paths:
        all_records.extend(ingest_document(p))

    texts = [r["text"] for r in all_records]
    metas = [r["metadata"] for r in all_records]

    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        batch_metas = metas[i:i + batch_size]
        embeddings = embedder.embed_texts(batch_texts)
        for t, e, m in zip(batch_texts, embeddings, batch_metas):
            store.add(text=t, embedding=e, metadata=m)

    return store

def main():
    print("AI Documentation Assistant (PoC)")
    print("Type 'exit' to quit.\n")

    material_dir = PROJECT_ROOT / "material"
    pdf_paths = list(material_dir.glob("*.pdf"))

    print("Indexing documents (this may take a bit the first time)...")
    store = build_index(pdf_paths)
    print(f"Indexed chunks: {len(store)}\n")

    embedder = OpenAIEmbedder()
    llm = OpenAILLMClient()

    while True:
        question = input(">> ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue

        intent = detect_intent(question)

        q_emb = embedder.embed_query(question)
        retrieved = retrieve_top_chunks(store, q_emb, top_k=25, min_score=0.15)
        confidence = compute_confidence_score(retrieved)

        if not retrieved:
            answer = "Not found in the provided documentation."
            print("\nAnswer:\n" + answer + "\n" + "-" * 50)
            log_interaction(question, answer)
            continue

        messages = build_messages(question, retrieved)
        raw = llm.generate(messages)


        if intent != "SAFETY" and not validate_safety_verbatim(raw, retrieved):
            raw += (
                "\n\n[WARNING]\n"
                "Some mandatory safety instructions from the official documentation "
                "may be missing or incomplete in the answer above. "
                "Please consult the full service manual before performing any work."
            )

        answer = format_answer(raw)
        answer += f"\n\n[CONFIDENCE]\n- Documentation support level: {confidence}%"

        print("\nAnswer:\n" + answer + "\n" + "-" * 50)
        log_interaction(question, answer)


if __name__ == "__main__":
    main()
