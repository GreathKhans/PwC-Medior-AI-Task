def handle_safety(chunks: list[str]) -> str:
    """
    Ensures that safety-critical information is preserved and highlighted.
    """
    output_lines = []

    for chunk in chunks:
        if "WARNING" in chunk or "DANGER" in chunk:
            output_lines.append("⚠️ SAFETY NOTICE:")
            output_lines.append(chunk)
        else:
            output_lines.append(chunk)

    return "\n".join(output_lines)
