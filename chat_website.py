import re

import gradio as gr
import ollama

import retrieve

OLLAMA_MODEL = "llama3.1:8b"
HISTORY_TURNS = 4

DRAFT_HINT = re.compile(
    r"\b("
    r"poa\s*&\s*m|poam|p\.o\.a\.m|"
    r"implementation statement|control implementation|"
    r"emass|soc\s+triage|triage|"
    r"draft|write\s+a|generate\s+a|create\s+a|fill\s+out"
    r")\b",
    re.IGNORECASE,
)

LOOKUP_HINT = re.compile(
    r"\b("
    r"what\s+is|what\s+does|explain|summarize|requirements?\s+for|"
    r"tell\s+me\s+about|define|meaning\s+of|does\s+[a-z]{2,3}-?\d+"
    r")\b",
    re.IGNORECASE,
)

STORE_OK = False
try:
    print("Loading saved rules and fingerprints...")
    retrieve.load_store()
    print("Loading the embedding model...")
    retrieve.get_model()
    STORE_OK = True
except FileNotFoundError:
    print(retrieve.pkl_missing_message())
    STORE_OK = False


def is_drafting_task(question):
    q = question or ""
    if DRAFT_HINT.search(q):
        return True
    if LOOKUP_HINT.search(q) and not DRAFT_HINT.search(q):
        return False
    return False


def history_to_text(history, max_turns=HISTORY_TURNS):
    if not history:
        return ""
    pairs = []
    if history and isinstance(history[0], dict):
        pending_user = None
        for msg in history:
            role = (msg.get("role") or "").lower()
            content = msg.get("content") or ""
            if role == "user":
                pending_user = content
            elif role == "assistant" and pending_user is not None:
                pairs.append((pending_user, content))
                pending_user = None
    else:
        for item in history:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                user_msg, bot_msg = item[0], item[1]
                if user_msg or bot_msg:
                    pairs.append((user_msg or "", bot_msg or ""))
    recent = pairs[-max_turns:]
    if not recent:
        return ""
    lines = []
    for user_msg, bot_msg in recent:
        lines.append(f"User: {user_msg}")
        lines.append(f"Assistant: {bot_msg}")
    return "\n".join(lines)


def build_prompt(question, history, matches):
    history_text = history_to_text(history)
    history_block = (
        f"Recent conversation:\n{history_text}\n\n" if history_text else ""
    )

    if not matches:
        return (
            "You are CountGPT, a cybersecurity analyst assistant.\n"
            "Retrieval found no NIST 800-53 controls that match this question "
            "closely enough (no control ID in the question matched the catalog, "
            "and no embedding scored above the similarity floor).\n"
            "Do NOT invent control IDs, quotes, or requirements. Say clearly that "
            "you could not find a confident NIST match, and suggest naming a "
            "control ID (for example AC-2) or rephrasing.\n\n"
            f"{history_block}"
            f"Question: {question}\n\nAnswer:"
        )

    context_text = retrieve.format_matches(matches)
    cited = ", ".join(sorted({m["id"] for m in matches if m.get("id")}))

    if is_drafting_task(question):
        return f"""You are CountGPT, a cybersecurity analyst assistant for NIST SP 800-53 and related drafting (POA&M, control implementation statements, SOC triage, eMASS packages).

Use the retrieved NIST rules below as the control source of truth. Cite rule IDs ({cited}).

Drafting instructions:
- Produce a practical draft the analyst can paste into a ticket or package.
- Use placeholders such as [System Name], [ISSO Name], and [date] whenever a specific value was not provided.
- Never claim a specific organizational tool, scanner, SIEM, or GRC product is in use unless the user named it.
- Do not invent findings, plugin IDs, or scan dates.
- End with a one-line caveat that this is a draft, not assessor-validated.

{history_block}NIST rules:
{context_text}

Question: {question}

Answer:"""

    return f"""You are CountGPT, a cybersecurity analyst assistant.

Answer ONLY from the retrieved NIST SP 800-53 rules below. Cite the rule ID(s) you used.
If the rules do not cover the question, say so. Do not invent controls or requirements.

{history_block}NIST rules:
{context_text}

Question: {question}

Answer:"""


def answer_question(question, history):
    if not STORE_OK:
        return (
            retrieve.pkl_missing_message()
            + " Then reload this chat."
        )
    question = (question or "").strip()
    if not question:
        return "Ask a NIST 800-53 question, or request a POA&M / implementation-statement draft."

    matches = retrieve.retrieve(question, k=4)
    prompt = build_prompt(question, history, matches)
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]


demo = gr.ChatInterface(
    fn=answer_question,
    title="CountGPT",
    description=(
        "Cybersecurity analyst assistant: look up NIST SP 800-53 controls "
        "and draft POA&M / implementation-statement / SOC notes. "
        "Answers cite retrieved rule IDs. Drafts use placeholders and are not assessor-validated."
    ),
)

if __name__ == "__main__":
    demo.launch()
