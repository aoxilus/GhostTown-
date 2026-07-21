"""Build static GhostTown pages from data/index.json."""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

import bleach
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import DATA, GHOST, INDEX, TEMPLATES


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

    GHOST.mkdir(parents=True, exist_ok=True)
    threads = GHOST / "threads"
    _wipe(threads)
    threads.mkdir(parents=True, exist_ok=True)
    att_out = GHOST / "attachments"
    _wipe(att_out)
    src_att = DATA / "attachments"
    if src_att.exists():
        shutil.copytree(src_att, att_out, dirs_exist_ok=True)

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
        body = m.get("text") or ""
        if m.get("html"):
            body_html = bleach.clean(m["html"], tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
        else:
            body_html = bleach.clean(body.replace("\n", "<br>\n"), tags=ALLOWED_TAGS, strip=True)
        safe_id = m["id"].replace(":", "_").replace("/", "_")
        (threads / f"{safe_id}.html").write_text(
            thread_t.render(m=m, body_html=body_html, safe_id=safe_id),
            encoding="utf-8",
        )
        m["href"] = f"threads/{safe_id}.html"

    folder_names = {"INBOX": "Recibidos", "[Gmail]/All Mail": "Todos los correos", "[Gmail]/Sent Mail": "Enviados"}
    counts: dict[str, int] = {}
    for m in msgs:
        counts[m["folder"]] = counts.get(m["folder"], 0) + 1
    folders = [
        {"id": f, "name": folder_names.get(f, f), "count": c}
        for f, c in sorted(counts.items(), key=lambda x: -x[1])
    ]

    index_t = env.get_template("index.html")
    (GHOST / "index.html").write_text(
        index_t.render(messages=msgs, total=len(msgs), folders=folders), encoding="utf-8"
    )
    return {"pages": len(msgs)}
