"""CountGPT FastAPI server: local HTML chat UI + NIST RAG API."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import countgpt

STATIC_DIR = Path(__file__).resolve().parent / "static"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 7860


@asynccontextmanager
async def lifespan(_app: FastAPI):
    countgpt.init_store()
    yield


app = FastAPI(
    title="CountGPT",
    description="Local NIST SP 800-53 compliance assistant.",
    lifespan=lifespan,
)


class HistoryMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[HistoryMessage] = Field(default_factory=list)


class MatchOut(BaseModel):
    id: str = ""
    title: str = ""
    text: str = ""
    score: float = 0.0
    source: str = ""


class ChatResponse(BaseModel):
    answer: str
    matches: list[MatchOut]
    drafting: bool


class ExportRequest(BaseModel):
    question: str = ""
    answer: str = ""
    draft: str = ""
    matches: list[dict] = Field(default_factory=list)
    drafting: bool = False
    mode: str = ""
    fields: dict = Field(default_factory=dict)
    format: str = "md"


class PoamRequest(BaseModel):
    finding: str
    severity: str = "Moderate"
    system_name: str = ""
    poc: str = ""
    detector_source: str = ""
    plugin_id: str = ""
    discovery_date: str = ""
    control_id: str = ""
    vendor_dependency: str = "no"
    vendor_notes: str = ""
    status: str = "Open"
    guidance: str = ""


class SspRequest(BaseModel):
    control_id: str
    system_name: str = ""
    system_context: str = ""
    guidance: str = ""


class WorkbenchResponse(BaseModel):
    draft: str
    matches: list[MatchOut]
    meta: dict


@app.get("/api/health")
def health():
    return countgpt.health_status()


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    message = (req.message or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")
    history = [m.model_dump() for m in req.history]
    try:
        result = countgpt.chat_turn(message, history)
    except countgpt.OllamaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ChatResponse(
        answer=result["answer"],
        matches=[MatchOut(**m) for m in result["matches"]],
        drafting=result["drafting"],
    )


def _workbench_response(mode: str, fields: dict) -> WorkbenchResponse:
    try:
        result = countgpt.workbench_turn(mode, fields)
    except countgpt.WorkbenchError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except countgpt.OllamaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return WorkbenchResponse(
        draft=result["draft"],
        matches=[MatchOut(**m) for m in result["matches"]],
        meta=result["meta"],
    )


@app.post("/api/poam", response_model=WorkbenchResponse)
def poam_draft(req: PoamRequest) -> WorkbenchResponse:
    return _workbench_response("poam", req.model_dump())


@app.post("/api/ssp", response_model=WorkbenchResponse)
def ssp_draft(req: SspRequest) -> WorkbenchResponse:
    return _workbench_response("ssp", req.model_dump())


@app.post("/api/export")
def export_last_turn(req: ExportRequest):
    answer = (req.answer or req.draft or "").strip()
    if not answer:
        raise HTTPException(status_code=400, detail="Nothing to export yet.")
    fmt = (req.format or "md").strip().lower()
    if fmt not in {"md", "markdown", "csv"}:
        raise HTTPException(status_code=400, detail="format must be md or csv")
    state = {
        "question": req.question,
        "answer": answer,
        "draft": answer,
        "matches": req.matches,
        "drafting": req.drafting or (req.mode in {"poam", "ssp"}),
        "mode": req.mode,
        "fields": req.fields,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    basename = countgpt.export_basename(state)
    if fmt == "csv":
        body = countgpt.build_export_csv(state)
        return Response(
            content=body,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{basename}.csv"'
            },
        )
    body = countgpt.build_export_markdown(state)
    return PlainTextResponse(
        content=body,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{basename}.md"'},
    )


@app.get("/")
def index():
    index_path = STATIC_DIR / "index.html"
    if not index_path.is_file():
        raise HTTPException(status_code=500, detail="static/index.html is missing")
    return FileResponse(index_path)


@app.get("/workbench")
def workbench():
    page = STATIC_DIR / "workbench.html"
    if not page.is_file():
        raise HTTPException(status_code=500, detail="static/workbench.html is missing")
    return FileResponse(page)


if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def main() -> None:
    import uvicorn

    host = os.environ.get("COUNTGPT_HOST", DEFAULT_HOST)
    port = int(os.environ.get("COUNTGPT_PORT", str(DEFAULT_PORT)))
    uvicorn.run("app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
