"""Local GhostTown server + AI clean API."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .ai_clean import chat as ai_chat
from .ai_clean import trash_ids
from .config import DATA, GHOST, INDEX, get_settings
from .export_html import build
from .sync_imap import sync

app = FastAPI(title="GmailGhostTown")


class ChatIn(BaseModel):
    message: str
    history: list[dict] = []


class ConfirmIn(BaseModel):
    ids: list[str]


@app.on_event("startup")
def _ensure_build():
    GHOST.mkdir(parents=True, exist_ok=True)
    if INDEX.exists() and not (GHOST / "index.html").exists():
        build()


@app.get("/api/stats")
def stats():
    n = 0
    if INDEX.exists():
        n = len(json.loads(INDEX.read_text(encoding="utf-8")).get("messages", {}))
    return {"messages": n, "ghost_ready": (GHOST / "index.html").exists()}


@app.post("/api/sync")
def api_sync(limit: int | None = None):
    result = sync(limit=limit)
    build()
    return result


@app.post("/api/build")
def api_build():
    return build()


@app.post("/api/chat")
def api_chat(body: ChatIn):
    return ai_chat(body.message, body.history)


@app.post("/api/confirm-trash")
def api_confirm(body: ConfirmIn):
    if not body.ids:
        raise HTTPException(400, "ids required")
    result = trash_ids(body.ids)
    build()
    return result


@app.get("/")
def home():
    index = GHOST / "index.html"
    if not index.exists():
        return HTMLResponse(
            "<h1>GmailGhostTown</h1><p>Empty. Run <code>python -m src.cli sync</code> then refresh.</p>",
            status_code=200,
        )
    return FileResponse(index)


def mount_static():
    if GHOST.exists():
        app.mount("/static-ghost", StaticFiles(directory=str(GHOST)), name="ghost")
        att = GHOST / "attachments"
        if att.exists():
            app.mount("/attachments", StaticFiles(directory=str(att)), name="att")
        threads = GHOST / "threads"
        if threads.exists():
            app.mount("/threads", StaticFiles(directory=str(threads)), name="threads")


mount_static()


# serve css/js from ghost root
@app.get("/styles.css")
def css():
    p = GHOST / "styles.css"
    if p.exists():
        return FileResponse(p)
    raise HTTPException(404)


@app.get("/app.js")
def js():
    p = GHOST / "app.js"
    if p.exists():
        return FileResponse(p)
    raise HTTPException(404)
