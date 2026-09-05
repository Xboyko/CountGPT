"""Shared CountGPT brain: draft/lookup routing, prompts, Ollama, export.

Used by the FastAPI HTML UI (`app.py`) and the legacy Gradio UI (`chat_gradio.py`).
"""

from __future__ import annotations

import csv
import io
import os
import re
from datetime import datetime, timezone
from typing import Any

import ollama
import requests

import retrieve

OLLAMA_MODEL = "llama3.1:8b"
DEFAULT_OLLAMA_HOST = "http://127.0.0.1:11434"
HISTORY_TURNS = 4
RETRIEVE_K = 4

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

DISCLAIMER_TITLE = "Draft / not assessor-validated"
DISCLAIMER_TEXT = (
    "CountGPT drafts POA&Ms, SSP statements, and control lookups for learning "
    "and analyst assistance only. Outputs are not authorization decisions, "
    "assessor findings, or official eMASS/ATO package content. Always review "
    "against your organization's policy and have a qualified assessor validate "
    "before use."
)
DISCLAIMER_SHORT = (
    "Draft / not assessor-validated. For learning and analyst assistance only. "
    "Not an official ATO/eMASS artifact."
)

EMPTY_RETRIEVAL_MD = (
    "_No retrieval yet. Ask a question or name a control ID (for example `AC-2`)._"
)

STORE_OK = False
STORE_ERROR: str | None = None


class OllamaError(RuntimeError):
    """Raised when the Ollama host is unreachable or returns an error."""


def ollama_host() -> str:
    """Ollama base URL. Default is localhost; set OLLAMA_HOST for WSL→Windows."""
    raw = (os.environ.get("OLLAMA_HOST") or DEFAULT_OLLAMA_HOST).strip()
    if not raw:
        raw = DEFAULT_OLLAMA_HOST
    if "://" not in raw:
        raw = "http://" + raw
    return raw.rstrip("/")


def get_ollama_client() -> ollama.Client:
    return ollama.Client(host=ollama_host())


def dry_run_enabled() -> bool:
    return os.environ.get("COUNTGPT_DRY_RUN", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def dry_run_answer(question: str, matches: list) -> str:
    """Deterministic grounded stub used when COUNTGPT_DRY_RUN is set."""
    drafting = is_drafting_task(question)
    mode = "drafting" if drafting else "lookup"
    if not matches:
        return (
            "I could not find a confident NIST 800-53 match for this question. "
            "Name a control ID (for example AC-2) or rephrase. "
            f"({DISCLAIMER_TITLE}.)"
        )
    cited = ", ".join(m.get("id", "") for m in matches if m.get("id"))
    first = matches[0]
    snippet = (first.get("text") or "").strip()
    if len(snippet) > 280:
        snippet = snippet[:280].rstrip() + "…"
    lead = (
        f"Draft based on retrieved controls {cited}."
        if drafting
        else f"From retrieved NIST SP 800-53 controls {cited}:"
    )
    caveat = (
        "This is a draft, not assessor-validated."
        if drafting
        else DISCLAIMER_SHORT
    )
    return (
        f"{lead}\n\n"
        f"**{first.get('id', '')} — {first.get('title', '')}**\n\n"
        f"{snippet}\n\n"
        f"_Mode: {mode}. {caveat}_"
    )


def init_store() -> bool:
    """Load the pickled NIST index and MiniLM encoder. Safe to call more than once."""
    global STORE_OK, STORE_ERROR
    if STORE_OK:
        return True
    try:
        print("Loading saved rules and fingerprints...")
        retrieve.load_store()
        print("Loading the embedding model...")
        retrieve.get_model()
        STORE_OK = True
        STORE_ERROR = None
        return True
    except FileNotFoundError:
        STORE_OK = False
        STORE_ERROR = retrieve.pkl_missing_message()
        print(STORE_ERROR)
        return False
    except Exception as exc:  # noqa: BLE001 — surface any load failure in /api/health
        STORE_OK = False
        STORE_ERROR = f"Failed to load retrieval store: {exc}"
        print(STORE_ERROR)
        return False


def reset_store_state() -> None:
    """Test helper: forget a previous init_store() result."""
    global STORE_OK, STORE_ERROR
    STORE_OK = False
    STORE_ERROR = None


def is_drafting_task(question: str) -> bool:
    q = question or ""
    if DRAFT_HINT.search(q):
        return True
    if LOOKUP_HINT.search(q) and not DRAFT_HINT.search(q):
        return False
    return False


def history_to_text(history, max_turns=HISTORY_TURNS) -> str:
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


def format_matches_markdown(matches: list) -> str:
    if not matches:
        return (
            "**Retrieved controls**\n\n"
            "_No NIST 800-53 controls met the ID match or similarity floor "
            f"({retrieve.DEFAULT_MIN_SCORE})._"
        )
    lines = [
        "**Retrieved controls**",
        "",
        "| ID | Score | Source | Title |",
        "| --- | --- | --- | --- |",
    ]
    for m in matches:
        cid = (m.get("id") or "").replace("|", "\\|")
        title = (m.get("title") or "").replace("|", "\\|")
        source = (m.get("source") or "").replace("|", "\\|")
        score = f"{float(m.get('score') or 0):.2f}"
        lines.append(f"| `{cid}` | {score} | {source} | {title} |")
    lines.extend(["", "### Control text", ""])
    for m in matches:
        text = (m.get("text") or "").strip()
        if len(text) > 500:
            text = text[:500].rstrip() + "…"
        lines.append(f"**`{m.get('id', '')}` — {m.get('title', '')}**")
        lines.append("")
        lines.append(text or "_No statement text._")
        lines.append("")
    return "\n".join(lines)


def matches_to_rows(matches: list) -> list[list]:
    rows = []
    for m in matches:
        rows.append(
            [
                m.get("id", ""),
                round(float(m.get("score") or 0), 4),
                m.get("source", ""),
                m.get("title", ""),
            ]
        )
    return rows


def serialize_match(match: dict) -> dict[str, Any]:
    return {
        "id": match.get("id", ""),
        "title": match.get("title", ""),
        "text": match.get("text", ""),
        "score": float(match.get("score") or 0),
        "source": match.get("source", ""),
    }


def generate_answer(question: str, history) -> tuple[str, list]:
    """Return (assistant_text, matches)."""
    if not STORE_OK:
        return (
            (STORE_ERROR or retrieve.pkl_missing_message()) + " Then reload this chat.",
            [],
        )
    question = (question or "").strip()
    if not question:
        return (
            "Ask a NIST 800-53 question, or request a POA&M / implementation-statement draft.",
            [],
        )

    matches = retrieve.retrieve(question, k=RETRIEVE_K)
    if dry_run_enabled():
        return dry_run_answer(question, matches), matches

    prompt = build_prompt(question, history, matches)
    try:
        response = get_ollama_client().chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:  # noqa: BLE001 — surface host/model failures to the API
        raise OllamaError(
            f"Ollama at {ollama_host()} failed ({OLLAMA_MODEL}): {exc}"
        ) from exc
    content = ""
    if isinstance(response, dict):
        content = ((response.get("message") or {}).get("content")) or ""
    else:
        message = getattr(response, "message", None)
        content = getattr(message, "content", "") or ""
    return content, matches


def chat_turn(message: str, history=None) -> dict[str, Any]:
    """Run one retrieve + generate turn and return the API payload."""
    history = history or []
    message = (message or "").strip()
    drafting = is_drafting_task(message)
    answer, matches = generate_answer(message, history)
    return {
        "answer": answer,
        "matches": [serialize_match(m) for m in matches],
        "drafting": drafting,
        "question": message,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def export_basename(state: dict, when: datetime | None = None) -> str:
    stamp = (when or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S")
    kind = "poam-draft" if state.get("drafting") else "lookup"
    return f"countgpt-{kind}-{stamp}"


def build_export_markdown(state: dict) -> str:
    matches = state.get("matches") or []
    lines = [
        "# CountGPT export",
        "",
        f"> **{DISCLAIMER_TITLE}.** {DISCLAIMER_SHORT}",
        "",
        f"- Generated (UTC): `{state.get('generated_at', '')}`",
        f"- Mode: `{'drafting' if state.get('drafting') else 'lookup'}`",
        f"- Model: `{OLLAMA_MODEL}`",
        "",
        "## Question",
        "",
        state.get("question") or "",
        "",
        "## Answer",
        "",
        state.get("answer") or "",
        "",
        "## Retrieved NIST 800-53 controls",
        "",
    ]
    if not matches:
        lines.append("_No controls retrieved._")
    else:
        lines.extend(
            [
                "| ID | Score | Source | Title |",
                "| --- | --- | --- | --- |",
            ]
        )
        for m in matches:
            lines.append(
                f"| {m.get('id', '')} | {float(m.get('score') or 0):.4f} | "
                f"{m.get('source', '')} | {m.get('title', '')} |"
            )
        lines.append("")
        for m in matches:
            lines.append(f"### {m.get('id', '')} — {m.get('title', '')}")
            lines.append("")
            lines.append(m.get("text") or "")
            lines.append("")
    return "\n".join(lines)


def build_export_csv(state: dict) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "row_type",
            "control_id",
            "score",
            "source",
            "title",
            "text",
            "question",
            "answer",
            "mode",
            "generated_at_utc",
            "disclaimer",
        ]
    )
    writer.writerow(
        [
            "draft",
            "",
            "",
            "",
            "",
            "",
            state.get("question") or "",
            state.get("answer") or "",
            "drafting" if state.get("drafting") else "lookup",
            state.get("generated_at") or "",
            DISCLAIMER_SHORT,
        ]
    )
    for m in state.get("matches") or []:
        writer.writerow(
            [
                "retrieved_control",
                m.get("id", ""),
                f"{float(m.get('score') or 0):.4f}",
                m.get("source", ""),
                m.get("title", ""),
                m.get("text", ""),
                "",
                "",
                "",
                "",
                "",
            ]
        )
    return buf.getvalue()


def check_ollama(timeout: float = 2.0) -> dict[str, Any]:
    host = ollama_host()
    info: dict[str, Any] = {
        "host": host,
        "reachable": False,
        "model": OLLAMA_MODEL,
        "model_available": False,
        "error": None,
    }
    try:
        resp = requests.get(f"{host}/api/tags", timeout=timeout)
        resp.raise_for_status()
        info["reachable"] = True
        names = []
        for item in (resp.json() or {}).get("models") or []:
            names.append(item.get("name") or item.get("model") or "")
        # Exact name, or a longer local tag that starts with the configured model.
        info["model_available"] = any(
            name == OLLAMA_MODEL or name.startswith(f"{OLLAMA_MODEL}")
            for name in names
            if name
        )
    except Exception as exc:  # noqa: BLE001
        info["error"] = str(exc)
    return info


def health_status() -> dict[str, Any]:
    ollama_info = check_ollama()
    store_loaded = bool(STORE_OK)
    ok = store_loaded and bool(ollama_info.get("reachable"))
    return {
        "ok": ok,
        "store_loaded": store_loaded,
        "store_error": None if store_loaded else STORE_ERROR or retrieve.pkl_missing_message(),
        "ollama": ollama_info,
        "model": OLLAMA_MODEL,
    }
