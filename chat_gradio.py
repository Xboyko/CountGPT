"""CountGPT Gradio UI (legacy): chat + retrieval side panel + draft export."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone

import gradio as gr

import countgpt
import retrieve

OLLAMA_MODEL = countgpt.OLLAMA_MODEL


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

DISCLAIMER_HTML = f"""
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
    {countgpt.DISCLAIMER_TITLE}
  </strong>
  {countgpt.DISCLAIMER_TEXT}
</div>
"""

EMPTY_RETRIEVAL_MD = countgpt.EMPTY_RETRIEVAL_MD

countgpt.init_store()
STORE_OK = countgpt.STORE_OK
_LAST_EXPORT: dict = {}


def _set_last_export(payload: dict) -> None:
    """Keep export payload in-process (avoids Gradio State schema bug on 5.9)."""
    global _LAST_EXPORT
    _LAST_EXPORT = payload or {}


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

    try:
        result = countgpt.chat_turn(message, history)
    except countgpt.OllamaError as exc:
        result = {
            "answer": str(exc),
            "matches": [],
            "drafting": countgpt.is_drafting_task(message),
            "question": message,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    answer = result["answer"]
    matches = result["matches"]
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": answer})

    _set_last_export(
        {
            "question": message,
            "answer": answer,
            "matches": matches,
            "drafting": result["drafting"],
            "generated_at": result.get("generated_at")
            or datetime.now(timezone.utc).isoformat(),
        }
    )
    can_export = bool(answer.strip())
    return (
        history,
        countgpt.format_matches_markdown(matches),
        countgpt.matches_to_rows(matches),
        gr.update(interactive=can_export),
        gr.update(interactive=can_export),
    )


def export_markdown():
    state = _LAST_EXPORT
    if not state or not (state.get("answer") or "").strip():
        raise gr.Error("Nothing to export yet. Send a question first.")
    path = os.path.join(tempfile.gettempdir(), f"{countgpt.export_basename(state)}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(countgpt.build_export_markdown(state))
    return path


def export_csv():
    state = _LAST_EXPORT
    if not state or not (state.get("answer") or "").strip():
        raise gr.Error("Nothing to export yet. Send a question first.")
    path = os.path.join(tempfile.gettempdir(), f"{countgpt.export_basename(state)}.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(countgpt.build_export_csv(state))
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
