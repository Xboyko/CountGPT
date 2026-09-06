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


def generate_answer(
    question: str, history, *, retrieve_query: str | None = None
) -> tuple[str, list]:
    """Return (assistant_text, matches).

    ``retrieve_query`` optionally overrides the NIST search string so workbench
    forms can retrieve on a control ID / finding without stuffing the full
    drafting instructions into the embed query. Chat and Gradio omit it.
    """
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

    query_for_retrieve = (retrieve_query or question).strip() or question
    matches = retrieve.retrieve(query_for_retrieve, k=RETRIEVE_K)
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


SEVERITIES = ("High", "Moderate", "Low")
SEVERITY_TIMELINE_DAYS = {"High": 30, "Moderate": 90, "Low": 180}
POAM_STATUSES = (
    "Open",
    "Pending",
    "Delayed",
    "Risk Accepted",
    "False Positive",
    "Closed",
)
VENDOR_DEPENDENCY_VALUES = ("yes", "no")


class WorkbenchError(ValueError):
    """Invalid workbench form input."""


def _clean_field(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def placeholder_or(value: Any, placeholder: str) -> str:
    cleaned = _clean_field(value)
    return cleaned if cleaned else placeholder


def normalize_severity(value: Any) -> str:
    raw = _clean_field(value).lower()
    aliases = {
        "med": "moderate",
        "medium": "moderate",
        "mod": "moderate",
        "hi": "high",
        "lo": "low",
    }
    raw = aliases.get(raw, raw)
    for label in SEVERITIES:
        if label.lower() == raw:
            return label
    return "Moderate"


def normalize_yes_no(value: Any) -> str:
    raw = _clean_field(value).lower()
    if raw in {"1", "true", "yes", "y"}:
        return "yes"
    return "no"


def normalize_status(value: Any) -> str:
    cleaned = _clean_field(value)
    if not cleaned:
        return "Open"
    for label in POAM_STATUSES:
        if label.lower() == cleaned.lower():
            return label
    return cleaned


def severity_timeline_days(severity: str) -> int:
    return SEVERITY_TIMELINE_DAYS[normalize_severity(severity)]


def normalize_poam_fields(fields: dict | None) -> dict[str, str]:
    src = fields or {}
    finding = _clean_field(src.get("finding"))
    if not finding:
        raise WorkbenchError("finding is required")
    return {
        "finding": finding,
        "severity": normalize_severity(src.get("severity")),
        "system_name": _clean_field(src.get("system_name")),
        "poc": _clean_field(src.get("poc")),
        "detector_source": _clean_field(src.get("detector_source")),
        "plugin_id": _clean_field(src.get("plugin_id")),
        "discovery_date": _clean_field(src.get("discovery_date")),
        "control_id": _clean_field(src.get("control_id")),
        "vendor_dependency": normalize_yes_no(src.get("vendor_dependency")),
        "vendor_notes": _clean_field(src.get("vendor_notes")),
        "status": normalize_status(src.get("status")),
        "guidance": _clean_field(src.get("guidance")),
    }


def normalize_ssp_fields(fields: dict | None) -> dict[str, str]:
    src = fields or {}
    control_id = _clean_field(src.get("control_id"))
    if not control_id:
        raise WorkbenchError("control_id is required")
    return {
        "control_id": control_id,
        "system_name": _clean_field(src.get("system_name")),
        "system_context": _clean_field(src.get("system_context")),
        "guidance": _clean_field(src.get("guidance")),
    }


def workbench_retrieval_query(mode: str, fields: dict) -> str:
    """Focused NIST search string: control ID plus finding/context when present."""
    mode = (mode or "").strip().lower()
    control_id = _clean_field(fields.get("control_id"))
    if mode == "ssp":
        extra = _clean_field(fields.get("system_context"))
        return " ".join(part for part in (control_id, extra) if part)
    finding = _clean_field(fields.get("finding"))
    return " ".join(part for part in (control_id, finding) if part)


def build_poam_question(fields: dict) -> str:
    """Assemble a drafting question from POA&M workbench fields."""
    data = normalize_poam_fields(fields)
    days = severity_timeline_days(data["severity"])
    vendor = "Yes" if data["vendor_dependency"] == "yes" else "No"
    lines = [
        "Draft a POA&M entry suitable for an eMASS ticket or package.",
        "",
        "Use ONLY the facts in \"Provided fields\" below. Do not invent plugin IDs, "
        "CVE numbers, scan dates, tools, products, or organizational processes that "
        "are not listed. Keep any [bracketed placeholders] in the draft. Cite "
        "retrieved NIST control IDs when they are relevant.",
        "",
        "Required sections:",
        "1. Weakness",
        "2. Point of Contact",
        "3. Vendor Dependency",
        f"4. Required Action — apply the {data['severity']} remediation timeline "
        f"of {days} days from discovery",
        f"5. Milestones — include interim checkpoints that fit the {days}-day window",
        "6. Status",
        "",
        "Provided fields:",
        f"- Finding / weakness: {data['finding']}",
        f"- Severity: {data['severity']} ({days}-day timeline)",
        f"- System name: {placeholder_or(data['system_name'], '[System Name]')}",
        f"- Point of contact / ISSO: {placeholder_or(data['poc'], '[ISSO Name]')}",
        f"- Detector source: {placeholder_or(data['detector_source'], '[detector source]')}",
        f"- Plugin / finding ID: {placeholder_or(data['plugin_id'], '[plugin ID if known]')}",
        f"- Discovery date: {placeholder_or(data['discovery_date'], '[discovery date]')}",
        f"- Control ID: {placeholder_or(data['control_id'], '[control ID if applicable]')}",
        f"- Vendor dependency: {vendor}",
        f"- Vendor notes: {placeholder_or(data['vendor_notes'], '[none provided]')}",
        f"- Status: {data['status']}",
    ]
    if data["guidance"]:
        lines.append(f"- Analyst guidance: {data['guidance']}")
    lines.extend(
        [
            "",
            "If Plugin / finding ID is the placeholder [plugin ID if known], omit a "
            "concrete plugin number rather than inventing one.",
            "End with a one-line caveat that this is a draft, not assessor-validated.",
        ]
    )
    return "\n".join(lines)


def build_ssp_question(fields: dict) -> str:
    """Assemble a drafting question from SSP workbench fields."""
    data = normalize_ssp_fields(fields)
    system = placeholder_or(data["system_name"], "[System Name]")
    context = placeholder_or(
        data["system_context"],
        "[system context — environment, users, and known implementing mechanisms]",
    )
    lines = [
        f"Write an SSP control implementation statement for {data['control_id']}.",
        "",
        "Use ONLY the facts in \"Provided fields\" below. Do not invent tools, "
        "products, logging platforms, scanners, or dates that are not listed. "
        f"Use the system name {system} when referring to the system. Use "
        "placeholders such as [SIEM], [identity provider], [backup solution], "
        "and [policy version] whenever a specific product or version was not "
        "provided. Ground the statement in the retrieved NIST control text.",
        "",
        "Suggested sections:",
        "- Implementation summary",
        "- How the control is met (mechanisms, frequency, responsible role)",
        "- Evidence / review",
        "- Customer responsibility (or Not applicable)",
        "",
        "Provided fields:",
        f"- Control ID: {data['control_id']}",
        f"- System name: {system}",
        f"- System context: {context}",
    ]
    if data["guidance"]:
        lines.append(f"- Analyst guidance: {data['guidance']}")
    lines.extend(
        [
            "",
            "End with a one-line caveat that this is a draft, not assessor-validated.",
        ]
    )
    return "\n".join(lines)


def workbench_turn(mode: str, fields: dict | None = None) -> dict[str, Any]:
    """Generate a POA&M or SSP draft using the shared retrieve + prompt path."""
    mode = _clean_field(mode).lower()
    if mode not in {"poam", "ssp"}:
        raise WorkbenchError("mode must be poam or ssp")
    fields = fields or {}
    if mode == "poam":
        normalized = normalize_poam_fields(fields)
        question = build_poam_question(normalized)
        timeline = severity_timeline_days(normalized["severity"])
    else:
        normalized = normalize_ssp_fields(fields)
        question = build_ssp_question(normalized)
        timeline = None
    retrieve_query = workbench_retrieval_query(mode, normalized)
    answer, matches = generate_answer(
        question, history=[], retrieve_query=retrieve_query or None
    )
    generated_at = datetime.now(timezone.utc).isoformat()
    return {
        "draft": answer,
        "matches": [serialize_match(m) for m in matches],
        "meta": {
            "mode": mode,
            "drafting": True,
            "question": question,
            "retrieve_query": retrieve_query,
            "generated_at": generated_at,
            "severity_timeline_days": timeline,
            "fields": normalized,
            "disclaimer": DISCLAIMER_SHORT,
            "model": OLLAMA_MODEL,
            "dry_run": dry_run_enabled(),
        },
        "answer": answer,
        "question": question,
        "drafting": True,
        "generated_at": generated_at,
        "mode": mode,
        "fields": normalized,
    }


def export_mode_label(state: dict) -> str:
    mode = _clean_field(state.get("mode")).lower()
    if mode in {"poam", "ssp", "lookup", "drafting"}:
        return mode
    return "drafting" if state.get("drafting") else "lookup"


def export_basename(state: dict, when: datetime | None = None) -> str:
    stamp = (when or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S")
    mode = _clean_field(state.get("mode")).lower()
    if mode == "ssp":
        kind = "ssp-draft"
    elif mode == "poam" or state.get("drafting"):
        kind = "poam-draft"
    else:
        kind = "lookup"
    return f"countgpt-{kind}-{stamp}"


def build_export_markdown(state: dict) -> str:
    matches = state.get("matches") or []
    lines = [
        "# CountGPT export",
        "",
        f"> **{DISCLAIMER_TITLE}.** {DISCLAIMER_SHORT}",
        "",
        f"- Generated (UTC): `{state.get('generated_at', '')}`",
        f"- Mode: `{export_mode_label(state)}`",
        f"- Model: `{OLLAMA_MODEL}`",
        "",
    ]
    fields = state.get("fields") or {}
    if fields:
        lines.extend(["## Workbench fields", ""])
        for key, value in fields.items():
            lines.append(f"- {key}: {value}")
        lines.append("")
    lines.extend(
        [
            "## Question",
            "",
            state.get("question") or "",
            "",
            "## Answer",
            "",
            state.get("answer") or state.get("draft") or "",
            "",
            "## Retrieved NIST 800-53 controls",
            "",
        ]
    )
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
            state.get("answer") or state.get("draft") or "",
            export_mode_label(state),
            state.get("generated_at") or "",
            DISCLAIMER_SHORT,
        ]
    )
    for key, value in (state.get("fields") or {}).items():
        writer.writerow(
            [
                "form_field",
                "",
                "",
                "",
                key,
                value,
                "",
                "",
                "",
                "",
                "",
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
    dry = dry_run_enabled()
    ok = store_loaded and (bool(ollama_info.get("reachable")) or dry)
    return {
        "ok": ok,
        "store_loaded": store_loaded,
        "store_error": None if store_loaded else STORE_ERROR or retrieve.pkl_missing_message(),
        "ollama": ollama_info,
        "dry_run": dry,
        "model": OLLAMA_MODEL,
    }
