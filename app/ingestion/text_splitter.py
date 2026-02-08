def split_text(text: str, max_length: int = 800) -> list[str]:
    """
    Splits text into chunks, but never splits WARNING/DANGER blocks.
    """
    chunks = []
    current = ""

    for line in text.splitlines():
        if "WARNING" in line or "DANGER" in line:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.append(line.strip())
        else:
            if len(current) + len(line) > max_length:
                chunks.append(current.strip())
                current = ""
            current += line + " "

    if current.strip():
        chunks.append(current.strip())

    return chunks
