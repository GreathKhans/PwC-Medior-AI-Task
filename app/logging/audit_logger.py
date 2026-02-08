from datetime import datetime


def log_interaction(question: str, answer: str) -> None:
    timestamp = datetime.now().isoformat()

    log_entry = (
        f"[{timestamp}]\n"
        f"QUESTION: {question}\n"
        f"ANSWER: {answer}\n"
        f"{'-'*50}\n"
    )

    with open("audit.log", "a", encoding="utf-8") as f:
        f.write(log_entry)
