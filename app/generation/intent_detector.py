from __future__ import annotations

def detect_intent(question: str) -> str:
    q = question.lower()

    if any(k in q for k in [
        "avoid", "must not", "do not", "danger", "warning", "prohibited"
    ]):
        return "SAFETY"

    if any(k in q for k in [
        "before", "prepare", "preparing"
    ]):
        return "PREPARATION"

    if any(k in q for k in [
        "how", "steps", "replace", "remove", "disassemble", "install"
    ]):
        return "PROCEDURE"

    if any(k in q for k in [
        "which parts", "components", "parts are"
    ]):
        return "PARTS"

    if any(k in q for k in [
        "check", "inspect", "verify"
    ]):
        return "CHECKS"

    return "GENERAL"
