from __future__ import annotations
from typing import List, Dict, Any
import re
from app.guardrails.safety_sentence_classifier import extract_safety_instructions

def is_non_instruction_text(text: str) -> bool:
    blacklist = [
        "symbol meaning",
        "indicates possibility of",
        "specific instruction is followed by",
        "electric shock indicates",
        "means secondary damages"
    ]
    t = text.lower()

    verbs = ["unplug", "disconnect", "do not", "never", "check", "use", "connect", "avoid"]
    if any(v in t for v in verbs):
        return False

    return any(b in t for b in blacklist)


def extract_safety_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)

    verbs = [
        "unplug", "disconnect", "do not", "never",
        "check", "use", "connect", "avoid",
        "remove", "install"
    ]

    result = []
    for s in sentences:
        s_low = s.lower()

        if not any(v in s_low for v in verbs):
            continue

        if is_non_instruction_text(s):
            continue

        result.append(s.strip())

    return result


def extract_mandatory_safety_sentences(
    retrieved: List[Dict[str, Any]]
) -> List[str]:
    mandatory = []

    for r in retrieved:
        md = r.get("metadata", {}) or {}
        if md.get("severity") not in ("WARNING", "DANGER"):
            continue

        text = (r.get("text") or "").strip()
        mandatory.extend(extract_safety_instructions(text))

    # dedup
    seen = set()
    result = []
    for s in mandatory:
        if s not in seen:
            seen.add(s)
            result.append(s)

    return result



def validate_safety_verbatim(answer: str, retrieved: List[Dict[str, Any]]) -> bool:
    mandatory = extract_mandatory_safety_sentences(retrieved)

    if not mandatory:
        return True

    for s in mandatory:
        if s not in answer:
            return False

    return True
