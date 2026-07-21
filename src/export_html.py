"""Build static GhostTown pages from data/index.json."""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

import bleach
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import DATA, GHOST, INDEX, STATE, TEMPLATES


ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union(
    {"p", "br", "div", "span", "pre", "code", "h1", "h2", "h3", "table", "tr", "td", "th", "thead", "tbody", "img", "hr"}
)
ALLOWED_ATTRS = {"*": ["class"], "a": ["href", "title"], "img": ["src", "alt"]}


def _load_index() -> dict:
    if not INDEX.exists():
        return {"messages": {}}
    return json.loads(INDEX.read_text(encoding="utf-8"))


def _wipe(path: Path) -> None:
    if not path.exists():
        return
    for attempt in range(5):
        try:
            shutil.rmtree(path)
            return
        except PermissionError:
            time.sleep(0.4 * (attempt + 1))
    # last resort: empty contents
    for child in path.rglob("*"):
        if child.is_file():
            try:
                child.unlink()
            except PermissionError:
                pass


def build() -> dict:
    idx = _load_index()
    msgs = list(idx.get("messages", {}).values())
    msgs.sort(key=lambda m: m.get("date") or "", reverse=True)
    state = {}
    if STATE.exists():
        state = json.loads(STATE.read_text(encoding="utf-8"))

    GHOST.mkdir(parents=True, exist_ok=True)
    threads = GHOST / "threads"
    threads.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    # copy css/js
    for name in ("styles.css", "app.js"):
        src = TEMPLATES / name
        if src.exists():
            shutil.copy2(src, GHOST / name)

    thread_t = env.get_template("thread.html")
    for m in msgs:
        safe_id = m["id"].replace(":", "_").replace("/", "_")
        thread_path = threads / f"{safe_id}.html"
        if not thread_path.exists():
            body = m.get("text") or ""
            if m.get("html"):
                body_html = bleach.clean(m["html"], tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
            else:
                body_html = bleach.clean(body.replace("\n", "<br>\n"), tags=ALLOWED_TAGS, strip=True)
            thread_path.write_text(
                thread_t.render(m=m, body_html=body_html, safe_id=safe_id),
                encoding="utf-8",
            )
        m["href"] = f"threads/{safe_id}.html"

    folder_names = {
        "INBOX": "Recibidos",
        "[Gmail]/All Mail": "Todos los correos",
        "[Gmail]/Sent Mail": "Enviados",
        "[Gmail]/Drafts": "Borradores",
        "[Gmail]/Spam": "Spam",
        "[Gmail]/Trash": "Papelera",
        "[Gmail]/Starred": "Destacados",
        "[Gmail]/Important": "Importantes",
    }
    counts: dict[str, int] = {}
    for m in msgs:
        counts[m["folder"]] = counts.get(m["folder"], 0) + 1
    remote_counts = state.get("folder_totals", {})
    all_folders = set(counts) | set(remote_counts)
    # Sidebar: hide All Mail (shown as "Todos"); prefer Gmail system folders then custom
    priority = {
        "INBOX": 0,
        "[Gmail]/Sent Mail": 1,
        "[Gmail]/Drafts": 2,
        "[Gmail]/Starred": 3,
        "[Gmail]/Important": 4,
        "[Gmail]/Spam": 5,
        "[Gmail]/Trash": 6,
    }
    folders = [
        {
            "id": f,
            "name": folder_names.get(f, f),
            "count": counts.get(f, 0),
            "remote_count": remote_counts.get(f, counts.get(f, 0)),
        }
        for f in sorted(
            (name for name in all_folders if name != "[Gmail]/All Mail"),
            key=lambda name: (priority.get(name, 50), -remote_counts.get(name, counts.get(name, 0)), name),
        )
    ]

    canonical = [m for m in msgs if m.get("folder") == "[Gmail]/All Mail"]
    downloaded = len(canonical) or len(msgs)
    remote_total = remote_counts.get("[Gmail]/All Mail") or len(
        state.get("uids", {}).get("[Gmail]/All Mail", [])
    ) or downloaded
    percent = round(min(100, downloaded * 100 / remote_total), 1) if remote_total else 0
    stats = {
        "downloaded": downloaded,
        "remote_total": remote_total,
        "percent": percent,
        "last_sync": state.get("last_sync", "Nunca"),
    }

    message_rows = [
        {
            "id": m["id"],
            "folder": m.get("folder", ""),
            "from": m.get("from", ""),
            "subject": m.get("subject", "(sin asunto)"),
            "snippet": (m.get("text") or "")[:160],
            "date": (m.get("date") or "")[:10],
            "href": m["href"],
            "has_attachments": bool(m.get("attachments")),
        }
        for m in msgs
    ]
    (GHOST / "messages.json").write_text(
        json.dumps(message_rows, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    index_t = env.get_template("index.html")
    (GHOST / "index.html").write_text(
        index_t.render(total=downloaded, folders=folders, stats=stats), encoding="utf-8"
    )
    return {"pages": len(msgs), "unique": downloaded, "percent": percent}
