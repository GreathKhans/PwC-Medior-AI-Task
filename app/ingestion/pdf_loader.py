from pypdf import PdfReader


def load_pdf(path: str) -> list[dict]:
    """
    Loads a PDF and returns a list of pages with text and page number.
    """
    reader = PdfReader(path)
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages.append({
                "page": i + 1,
                "text": text
            })

    return pages
