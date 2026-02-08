def clean_text(text: str) -> str:
    """
    Normalizes PDF text: whitespace, line breaks, warnings formatting.
    """
    text = text.replace("\r", "\n")
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

    # Normalize safety keywords
    text = text.replace("WARNING :", "WARNING:")
    text = text.replace("DANGER :", "DANGER:")

    return text