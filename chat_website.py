"""CountGPT Gradio UI: chat + retrieval side panel + draft export."""

from __future__ import annotations

import csv
import os
import re
import tempfile
from datetime import datetime, timezone

import gradio as gr
import ollama

import retrieve

OLLAMA_MODEL = "llama3.1:8b"
HISTORY_TURNS = 4
RETRIEVE_K = 4


def _patch_gradio_bool_schema_bug() -> None:
    """Gradio 5.9 crashes page load when a JSON schema has additionalProperties: true.

    gradio_client treats that bool as a nested schema and does ``\"const\" in True``.
    """
    import gradio_client.utils as gu

    if getattr(gu, "_countgpt_bool_patch", False):
        return
    _orig = gu._json_schema_to_python_type

    def _safe(schema, defs):
        if isinstance(schema, bool):
            return "Any"
        return _orig(schema, defs)

    gu._json_schema_to_python_type = _safe
    gu._countgpt_bool_patch = True


_patch_gradio_bool_schema_bug()

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

DISCLAIMER_HTML = """
<div style="
  border: 1px solid #b45309;
  background: #fffbeb;
  color: #78350f;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 8px;
  font-family: system-ui, sans-serif;
  font-size: 14px;
  line-height: 1.45;
">
  <strong style="display:block; margin-bottom:4px;">
    Draft / not assessor-validated
  </strong>
  CountGPT drafts POA&amp;Ms, SSP statements, and control lookups for learning
  and analyst assistance only. Outputs are <em>not</em> authorization decisions,
  assessor findings, or official eMASS/ATO package content. Always review against
  your organization's policy and have a qualified assessor validate before use.
</div>
"""

EMPTY_RETRIEVAL_MD = (
    "_No retrieval yet. Ask a question or name a control ID (for example `AC-2`)._"
)

STORE_OK = False
_LAST_EXPORT: dict = {}
try:
    print("Loading saved rules and fingerprints...")
    retrieve.load_store()
    print("Loading the embedding model...")
    retrieve.get_model()
    STORE_OK = True
except FileNotFoundError:
    print(retrieve.pkl_missing_message())
    STORE_OK = False


def _set_last_export(payload: dict) -> None:
    """Keep export payload in-process (avoids Gradio State schema bug on 5.9)."""
    global _LAST_EXPORT
    _LAST_EXPORT = payload or {}


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


def generate_answer(question: str, history) -> tuple[str, list]:
    """Return (assistant_text, matches)."""
    if not STORE_OK:
        return (
            retrieve.pkl_missing_message() + " Then reload this chat.",
            [],
        )
    question = (question or "").strip()
    if not question:
        return (
            "Ask a NIST 800-53 question, or request a POA&M / implementation-statement draft.",
            [],
        )

    matches = retrieve.retrieve(question, k=RETRIEVE_K)
    prompt = build_prompt(question, history, matches)
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"], matches


def respond(message, history):
    history = list(history or [])
    message = (message or "").strip()
    if not message:
        _set_last_export({})
        return (
            history,
            EMPTY_RETRIEVAL_MD,
            [],
            gr.update(interactive=False),
            gr.update(interactive=False),
        )

    answer, matches = generate_answer(message, history)
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": answer})

    _set_last_export(
        {
            "question": message,
            "answer": answer,
            "matches": matches,
            "drafting": is_drafting_task(message),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    can_export = bool(answer.strip())
    return (
        history,
        format_matches_markdown(matches),
        matches_to_rows(matches),
        gr.update(interactive=can_export),
        gr.update(interactive=can_export),
    )


def _export_basename(state: dict) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    kind = "poam-draft" if state.get("drafting") else "lookup"
    return f"countgpt-{kind}-{stamp}"


def export_markdown():
    state = _LAST_EXPORT
    if not state or not (state.get("answer") or "").strip():
        raise gr.Error("Nothing to export yet. Send a question first.")

    matches = state.get("matches") or []
    lines = [
        "# CountGPT export",
        "",
        "> **Draft / not assessor-validated.** "
        "For learning and analyst assistance only. Not an official ATO/eMASS artifact.",
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

    path = os.path.join(tempfile.gettempdir(), f"{_export_basename(state)}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def export_csv():
    state = _LAST_EXPORT
    if not state or not (state.get("answer") or "").strip():
        raise gr.Error("Nothing to export yet. Send a question first.")

    path = os.path.join(tempfile.gettempdir(), f"{_export_basename(state)}.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
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
        disclaimer = "Draft / not assessor-validated. Not official ATO/eMASS content."
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
                disclaimer,
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
    return path


def clear_chat():
    _set_last_export({})
    return (
        [],
        EMPTY_RETRIEVAL_MD,
        [],
        gr.update(interactive=False),
        gr.update(interactive=False),
        "",
    )


CSS = """
#retrieval-panel {
  max-height: 70vh;
  overflow-y: auto;
}
"""

_GRADIO_MAJOR = int(gr.__version__.split(".", 1)[0])


def _chatbot():
    """Gradio 5 uses type=/show_copy_button; Gradio 6 uses buttons=."""
    kwargs = {"label": "Chat", "height": 480}
    if _GRADIO_MAJOR >= 6:
        kwargs["buttons"] = ["copy", "copy_all"]
    else:
        kwargs["type"] = "messages"
        kwargs["show_copy_button"] = True
    return gr.Chatbot(**kwargs)


def _blocks():
    """theme/css belong on Blocks in Gradio 5, on launch() in Gradio 6."""
    if _GRADIO_MAJOR >= 6:
        return gr.Blocks(title="CountGPT")
    return gr.Blocks(title="CountGPT", css=CSS, theme=gr.themes.Soft())


with _blocks() as demo:
    gr.Markdown("# CountGPT")
    gr.Markdown(
        "Local NIST SP 800-53 assistant for control lookup and POA&M / "
        "implementation-statement drafting. Answers cite retrieved rule IDs."
    )
    gr.HTML(DISCLAIMER_HTML)

    if not STORE_OK:
        gr.HTML(
            "<div style='border:1px solid #b91c1c;background:#fef2f2;color:#7f1d1d;"
            "padding:10px 14px;border-radius:8px;margin:8px 0;'>"
            f"<strong>Setup needed:</strong> {retrieve.pkl_missing_message()}"
            "</div>"
        )

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = _chatbot()
            with gr.Row():
                msg = gr.Textbox(
                    placeholder=(
                        "Ask about a control (e.g. What does AC-2 require?) "
                        "or draft a POA&M…"
                    ),
                    label="Message",
                    scale=5,
                    autofocus=True,
                )
                send = gr.Button("Send", variant="primary", scale=1)
            clear = gr.Button("Clear chat", variant="secondary")

        with gr.Column(scale=2, elem_id="retrieval-panel"):
            gr.Markdown("## Sources")
            retrieval_md = gr.Markdown(EMPTY_RETRIEVAL_MD)
            retrieval_table = gr.Dataframe(
                headers=["ID", "Score", "Source", "Title"],
                datatype=["str", "number", "str", "str"],
                label="Retrieval scores",
                interactive=False,
                wrap=True,
            )
            gr.Markdown("### Export last answer")
            gr.Markdown(
                "Downloads include the disclaimer, your question, the model "
                "answer, and retrieved controls (Markdown report or CSV rows)."
            )
            with gr.Row():
                btn_md = gr.Button(
                    "Export Markdown",
                    variant="secondary",
                    interactive=False,
                )
                btn_csv = gr.Button(
                    "Export CSV",
                    variant="secondary",
                    interactive=False,
                )
            file_md = gr.File(label="Markdown file", interactive=False)
            file_csv = gr.File(label="CSV file", interactive=False)

    outputs = [
        chatbot,
        retrieval_md,
        retrieval_table,
        btn_md,
        btn_csv,
    ]

    def _submit(message, history):
        new_history, md, rows, md_upd, csv_upd = respond(message, history)
        return new_history, md, rows, md_upd, csv_upd, ""

    msg.submit(_submit, [msg, chatbot], outputs + [msg])
    send.click(_submit, [msg, chatbot], outputs + [msg])
    clear.click(
        clear_chat,
        inputs=None,
        outputs=outputs + [msg],
    )

    btn_md.click(export_markdown, inputs=None, outputs=[file_md])
    btn_csv.click(export_csv, inputs=None, outputs=[file_csv])

    gr.Examples(
        examples=[
            "What does AC-2 require?",
            "Draft a POA&M for a Moderate finding: weak cipher suite on a web server.",
            "Write an SSP implementation statement for AU-2 Event Logging.",
            "Explain IA-2 identification and authentication.",
        ],
        inputs=msg,
    )


if __name__ == "__main__":
    # Windows / corporate networks often break Gradio's localhost self-check
    # (IPv6 localhost or proxy). Bind to 127.0.0.1 and exempt it from proxies.
    os.environ.setdefault("NO_PROXY", "127.0.0.1,localhost,::1")
    os.environ.setdefault("no_proxy", "127.0.0.1,localhost,::1")
    # None = let Gradio pick the first free port (avoids stale 7860 conflicts).
    port_env = os.environ.get("GRADIO_SERVER_PORT", "").strip()
    server_port = int(port_env) if port_env.isdigit() else None
    launch_kwargs = {
        "server_name": "127.0.0.1",
        "server_port": server_port,
        "inbrowser": True,
        "show_api": False,
    }
    if _GRADIO_MAJOR >= 6:
        launch_kwargs["theme"] = gr.themes.Soft()
        launch_kwargs["css"] = CSS
    try:
        demo.launch(**launch_kwargs)
    except ValueError as exc:
        if "shareable link" not in str(exc).lower() and "share=True" not in str(exc):
            raise
        print(
            "Localhost self-check failed; retrying with share=True "
            "(temporary public Gradio link). Open the printed URL."
        )
        launch_kwargs["share"] = True
        demo.launch(**launch_kwargs)
