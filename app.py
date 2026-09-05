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
    matches: list[dict] = Field(default_factory=list)
    drafting: bool = False
    format: str = "md"


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


@app.post("/api/export")
def export_last_turn(req: ExportRequest):
    if not (req.answer or "").strip():
        raise HTTPException(status_code=400, detail="Nothing to export yet.")
    fmt = (req.format or "md").strip().lower()
    if fmt not in {"md", "markdown", "csv"}:
        raise HTTPException(status_code=400, detail="format must be md or csv")
    state = {
        "question": req.question,
        "answer": req.answer,
        "matches": req.matches,
        "drafting": req.drafting,
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


if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def main() -> None:
    import uvicorn

    host = os.environ.get("COUNTGPT_HOST", DEFAULT_HOST)
    port = int(os.environ.get("COUNTGPT_PORT", str(DEFAULT_PORT)))
    uvicorn.run("app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
