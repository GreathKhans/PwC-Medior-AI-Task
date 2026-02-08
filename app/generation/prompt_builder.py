from __future__ import annotations
from app.guardrails.safety_sentence_classifier import extract_safety_instructions
from app.generation.intent_detector import detect_intent
from typing import List, Dict, Any
import re


SYSTEM_PROMPT = """You are a technical documentation assistant for field mechanics.

NON-NEGOTIABLE SAFETY RULES:
- Use ONLY the provided excerpts as source of truth.
- NEVER invent steps, parts, values, or safety procedures.
- If the excerpts do not contain the answer, say exactly:
  Not found in the provided documentation.

SAFETY STATEMENT IDENTIFICATION (CRITICAL):
- A safety statement is ONLY a direct instruction or prohibition addressed to a technician or user.
- It MUST contain a clear action or prohibition.

SAFETY STATEMENT HANDLING:
- Safety statements MUST be copied VERBATIM.
- Do NOT paraphrase safety statements.
- One instruction per bullet.
- Show safety BEFORE any steps.
- Every safety statement MUST include a citation in the format:
  "<verbatim statement>" (source: <file>, page: <n>)

PROCEDURE HANDLING:
- Procedural steps may be listed ONLY if explicitly supported by the provided excerpts.
- Do NOT rewrite or paraphrase safety statements as procedural steps.
- Each procedural step MUST include a citation in the format:
  <instruction> (source: <file>, page: <n>)
- Do NOT invent missing steps.

OUTPUT FORMAT RULES:
- ALWAYS include [SAFETY WARNINGS] if any safety statements exist.
- Include [STEP-BY-STEP] ONLY IF procedural actions are explicitly provided.
- If no procedural actions are provided, DO NOT include [STEP-BY-STEP] at all.
- NEVER include empty sections.
- [SAFETY WARNINGS] may appear alone.
- If any safety instructions are present, the answer MUST start with:

[SAFETY WARNINGS]

followed by the list of verbatim safety instructions.

OUTPUT STRUCTURE (WHEN APPLICABLE):
- "<verbatim safety statement>" (source: <file>, page: <n>)
- ...

[STEP-BY-STEP]
1. <procedural instruction> (source: <file>, page: <n>)
2. <procedural instruction> (source: <file>, page: <n>)
"""


# ---------- helpers ----------

def normalize_for_dedup(text: str) -> str:
    t = text.lower()
    t = re.sub(r'\bthe\b', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()


def is_non_instruction_text(text: str) -> bool:
    blacklist = [
        "symbol meaning",
        "indicates possibility of",
        "specific instruction is followed by",
        "electric shock indicates",
        "means secondary damages"
    ]
    t = text.lower()
    return any(b in t for b in blacklist)

def extract_parts_sentences(text: str) -> List[str]:
    """
    Extract sentences that mention physical components / parts.
    PoC-level heuristic.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)

    part_keywords = [
        # grounding / electrical safety
        "ground", "grounding", "ground wire", "earth", "earthing",
        "shell plate", "metal frame", "frame", "chassis",
        "terminal", "ground terminal", "ground pin",

        # electrical components
        "power cord", "power cable", "plug", "socket",
        "connector", "wiring", "harness",

        # mechanical components (relevant to service)
        "door", "door lock", "lock", "hinge",
        "panel", "front panel", "rear panel",
        "cover", "lower cover",
        "gasket", "seal", "clamp",
        "screw", "bolt", "bracket",

        # control / internal
        "motor", "pump", "drum", "tub",
        "sensor", "switch", "board", "pcb"
    ]

    result = []
    for s in sentences:
        s_low = s.lower()
        if any(k in s_low for k in part_keywords):
            if not is_non_instruction_text(s):
                result.append(s.strip())

    return result

def extract_procedure_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)

    action_verbs = [
        # core actions
        "open", "close", "remove", "install", "replace", "attach", "detach",
        "loosen", "tighten", "unscrew", "screw", "pull", "push",
        "lift", "lower", "slide", "move",

        # disassembly / assembly
        "take off", "take down", "disassemble", "assemble",
        "release", "lock", "unlock",

        # electrical / checks
        "disconnect", "connect", "measure", "check", "inspect",
        "verify", "confirm", "test",

        # safety-adjacent but still actions
        "turn off", "shut off", "isolate", "ground", "grounding",

        # plumbing / hoses
        "drain", "flush", "seal", "unseal"
    ]

    exclude_phrases = [
        "during operation",
        "during washing",
        "before starting washing",
        "for normal operation",
        "when using",
        "user should",
        "customer should",
        "installation",
        "installing",
        "environment",
        "location",
        "ventilation",
        "drainage pipe",
        "sewage",
        "floor",
        "room",
        "water pressure",
        "power supply requirement"
    ]

    result = []

    for s in sentences:
        s_low = s.lower()
        if not any(v in s_low for v in action_verbs):
            continue

        if any(p in s_low for p in exclude_phrases):
            continue
        if is_non_instruction_text(s):
            continue

        result.append(s.strip())
    return result


# ---------- main builder ----------

def build_messages(
    question: str,
    retrieved: List[Dict[str, Any]]
) -> List[Dict[str, str]]:

    intent = detect_intent(question)

    seen = set()
    safety_lines: List[str] = []
    procedure_lines: List[str] = []
    parts_lines: List[str] = []

    for r in retrieved:
        md = r.get("metadata", {}) or {}
        source = md.get("source", "unknown")
        page = md.get("page", "unknown")
        raw_text = (r.get("text") or "").strip()

        # ---- SAFETY (always extracted) ----
        safety_instr = extract_safety_instructions(raw_text)
        safety_set = set(safety_instr)

        for s in safety_instr:
            key = normalize_for_dedup(s)
            if key in seen:
                continue
            seen.add(key)
            safety_lines.append(
                f'- "{s}" (source: {source}, page: {page})'
            )

        # ---- PROCEDURES / PREPARATION / CHECKS ----
        if intent in ("PROCEDURE", "PREPARATION", "CHECKS"):
            for s in extract_procedure_sentences(raw_text):
                if s in safety_set:
                    continue
                key = normalize_for_dedup(s)
                if key in seen:
                    continue
                seen.add(key)
                procedure_lines.append(
                    f'- {s} (source: {source}, page: {page})'
                )

        # ---- PARTS ----
        if intent == "PARTS":
            for s in extract_parts_sentences(raw_text):
                key = normalize_for_dedup(s)
                if key in seen:
                    continue
                seen.add(key)
                parts_lines.append(
                    f'- {s} (source: {source}, page: {page})'
                )

    # ---- NO ANSWER ----
    if not safety_lines and not procedure_lines and not parts_lines:
        return [{
            "role": "assistant",
            "content": "Not found in the provided documentation."
        }]

    # ---- PROMPT ----
    user_prompt = f"""User question:
{question}

Documentation excerpts:

[SAFETY EXCERPTS]
{chr(10).join(safety_lines)}

{"[PROCEDURE EXCERPTS]\n" + chr(10).join(procedure_lines) if intent in ("PROCEDURE", "PREPARATION", "CHECKS") else ""}

{"[PARTS EXCERPTS]\n" + chr(10).join(parts_lines) if intent == "PARTS" else ""}

Task:
Answer using ONLY the provided excerpts.
"""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
