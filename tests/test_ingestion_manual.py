from pathlib import Path
from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_cleaner import clean_text
from app.ingestion.metadata_extractor import extract_metadata
from app.ingestion.text_splitter import split_text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PDF = PROJECT_ROOT / "material" / "LAD-Front-Loading-Service-Manual-L11.pdf"

pages = load_pdf(str(PDF))
print("Pages:", len(pages))

for page in pages[:2]:
    cleaned = clean_text(page["text"])
    meta = extract_metadata(cleaned)
    chunks = split_text(cleaned)

    print("PAGE", page["page"])
    print("Severity:", meta["severity"])
    print("Chunks:", len(chunks))
    print("Sample:", chunks[0][:200])
