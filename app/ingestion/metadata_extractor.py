from __future__ import annotations
import re

SAFETY_KEYWORDS_DANGER = [
    r"\bDANGER\b",
]

SAFETY_KEYWORDS_WARNING = [
    r"\bWARNING\b",
    r"\bCAUTION\b",
    r"\bIMPORTANT\b",
    r"\bUNPLUG\b",
    r"\bDISCONNECT\b",
    r"electric shock",
    r"\bshock\b",
    r"\bfire\b",
    r"\binjury\b",
    r"\bhazard\b",
    r"\brisk\b",
]

def extract_metadata(text: str) -> dict:
    t = text.strip()
    t_low = t.lower()

    severity = "NORMAL"
    if any(re.search(p, t, re.IGNORECASE) for p in SAFETY_KEYWORDS_DANGER):
        severity = "DANGER"
    elif any(re.search(p, t, re.IGNORECASE) for p in SAFETY_KEYWORDS_WARNING):
        severity = "WARNING"

    section = "General"
    for line in t.splitlines():
        line = line.strip()
        if line.isupper() and 3 <= len(line) <= 80:
            section = line
            break

    return {"severity": severity, "section": section}

