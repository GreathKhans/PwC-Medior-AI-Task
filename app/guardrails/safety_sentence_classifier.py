from typing import List
import re

SAFETY_ACTION_KEYWORDS = [
    "do not",
    "never",
    "must not",
    "unplug",
    "disconnect",
    "use only",
    "connect ground",
    "grounding",
]

EXCLUDE_KEYWORDS = [
    "may cause",
    "indicates possibility",
    "symbol",
    "means",
    "warning indicates",
    "caution indicates",
    "risk of",
    "can result in",
]


def split_sentences(text: str) -> List[str]:
    return re.split(r'(?<=[.!?])\s+', text)


def is_safety_instruction(sentence: str) -> bool:
    s = sentence.lower()

    if any(ex in s for ex in EXCLUDE_KEYWORDS):
        return False

    if any(k in s for k in SAFETY_ACTION_KEYWORDS):
        return True

    return False


def extract_safety_instructions(text: str) -> List[str]:
    sentences = split_sentences(text)
    return [s.strip() for s in sentences if is_safety_instruction(s)]
