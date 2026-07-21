"""Local GhostTown server + AI clean API."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import threading

from .ai_clean import chat as ai_chat
from .ai_clean import trash_ids
from .config import DATA, GHOST, INDEX, ROOT, TEMPLATES, get_settings
from .export_html import build
from .sync_imap import PROGRESS, _write_progress, sync, verify

_sync_thread: threading.Thread | None = None

app = FastAPI(title="GmailGhostTown")


class ChatIn(BaseModel):
    message: str
    history: list[dict] = []


class ConfirmIn(BaseModel):
    ids: list[str]


class SetupIn(BaseModel):
    user: str
    password: str
    openai_key: str = ""


def _configured() -> bool:
    s = get_settings()
    return bool(s.imap_user and s.imap_password and "@" in s.imap_user and s.imap_user != "tu@gmail.com")


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


def _sync_job(limit: int | None):
    try:
        sync(limit=limit)
        build()
        _write_progress(status="done")
    except Exception as e:
        _write_progress(status="error", error=str(e))


@app.post("/api/sync")
def api_sync(limit: int | None = None):
    """Launch sync in background; UI polls /api/sync-status."""
    global _sync_thread
    if _sync_thread and _sync_thread.is_alive():
        return {"started": False, "running": True}
    _sync_thread = threading.Thread(target=_sync_job, args=(limit,), daemon=True)
    _sync_thread.start()
    return {"started": True, "running": True}


@app.get("/api/sync-status")
def api_sync_status():
    if PROGRESS.exists():
        return json.loads(PROGRESS.read_text(encoding="utf-8"))
    return {"status": "idle"}


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


@app.post("/api/setup")
def api_setup(body: SetupIn):
    """Write .env from the web wizard, then test the IMAP login."""
    s = get_settings()
    lines = [
        "IMAP_HOST=imap.gmail.com",
        f"IMAP_USER={body.user.strip()}",
        f"IMAP_PASSWORD={body.password.strip()}",
        f"OPENAI_API_KEY={body.openai_key.strip() or s.openai_api_key}",
        f"OPENAI_MODEL={s.openai_model}",
        f"PORT={s.port}",
    ]
    (ROOT / ".env").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return verify()


@app.get("/")
def home():
    if not _configured():
        return FileResponse(TEMPLATES / "setup.html")
    index = GHOST / "index.html"
    if not index.exists():
        return FileResponse(TEMPLATES / "setup.html")
    return FileResponse(index)


@app.get("/messages.json")
def messages_index():
    path = GHOST / "messages.json"
    if path.exists():
        return FileResponse(path, media_type="application/json")
    raise HTTPException(404)


def mount_static():
    if GHOST.exists():
        app.mount("/static-ghost", StaticFiles(directory=str(GHOST)), name="ghost")
        att = DATA / "attachments"
        if att.exists():
            app.mount("/attachments", StaticFiles(directory=str(att)), name="att")
        threads = GHOST / "threads"
        if threads.exists():
            app.mount("/threads", StaticFiles(directory=str(threads)), name="threads")


mount_static()


# serve css/js from ghost root, falling back to templates (setup page before first build)
@app.get("/styles.css")
def css():
    for p in (GHOST / "styles.css", TEMPLATES / "styles.css"):
        if p.exists():
            return FileResponse(p)
    raise HTTPException(404)


@app.get("/app.js")
def js():
    for p in (GHOST / "app.js", TEMPLATES / "app.js"):
        if p.exists():
            return FileResponse(p)
    raise HTTPException(404)
