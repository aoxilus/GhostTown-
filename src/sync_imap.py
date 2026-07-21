"""IMAP sync → data/index.json + attachments."""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from imap_tools import AND, MailBox

from .config import DATA, INDEX, STATE, get_settings

SAFE = re.compile(r"[^\w.\-]+", re.UNICODE)


def _load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def _save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _safe_name(name: str, fallback: str) -> str:
    name = SAFE.sub("_", name or fallback).strip("._") or fallback
    return name[:120]


def verify() -> dict:
    """Try IMAP login only. Returns {'ok': bool, 'error': str, 'user': str}."""
    s = get_settings()
    if not s.imap_user or not s.imap_password:
        return {"ok": False, "error": "Faltan IMAP_USER / IMAP_PASSWORD", "user": s.imap_user}
    try:
        with MailBox(s.imap_host).login(s.imap_user, s.imap_password):
            pass
        return {"ok": True, "error": "", "user": s.imap_user}
    except Exception as e:
        msg = str(e)
        if "AUTHENTICATIONFAILED" in msg.upper() or "Invalid credentials" in msg:
            msg = "Login rechazado: usa un App Password de 16 letras (no tu contrasena normal) y activa IMAP en Gmail."
        return {"ok": False, "error": msg, "user": s.imap_user}


def sync(folders: list[str] | None = None, limit: int | None = None) -> dict:
    s = get_settings()
    if not s.imap_user or not s.imap_password:
        raise SystemExit("Set IMAP_USER and IMAP_PASSWORD in .env (Gmail App Password)")

    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "attachments").mkdir(exist_ok=True)
    index: dict = _load_json(INDEX, {"messages": {}})
    state: dict = _load_json(STATE, {"uids": {}})
    fetched = 0
    errors: list[str] = []

    with MailBox(s.imap_host).login(s.imap_user, s.imap_password) as mb:
        available_list = [f.name for f in mb.folder.list()]
        available = set(available_list)
        folder_totals = state.setdefault("folder_totals", {})
        for name in available_list:
            try:
                folder_totals[name] = mb.folder.status(name, ["MESSAGES"])["MESSAGES"]
            except Exception:
                continue

        if not folders:
            custom = [name for name in available_list if not name.startswith("[Gmail]/")]
            preferred = ["[Gmail]/All Mail", "INBOX", "[Gmail]/Sent Mail"]
            folders = list(dict.fromkeys([name for name in preferred + custom if name in available]))

        for folder in folders:
            if folder not in available:
                errors.append(f"skip missing folder: {folder}")
                continue
            mb.folder.set(folder)
            seen = set(state.setdefault("uids", {}).setdefault(folder, []))
            all_uids = mb.uids(AND(all=True))
            new_uids = [u for u in all_uids if u not in seen]
            new_uids.reverse()  # newest first
            if limit:
                new_uids = new_uids[: limit - fetched]
            print(f"{folder}: {len(new_uids)} nuevos de {len(all_uids)}", flush=True)

            CHUNK = 50
            for start in range(0, len(new_uids), CHUNK):
                chunk = new_uids[start : start + CHUNK]
                for msg in mb.fetch(AND(uid=",".join(chunk)), mark_seen=False, bulk=True):
                    key = f"{folder}:{msg.uid}"
                    att_dir = DATA / "attachments" / _safe_name(key.replace(":", "_"), msg.uid)
                    att_meta = []
                    if msg.attachments:
                        att_dir.mkdir(parents=True, exist_ok=True)
                        for i, att in enumerate(msg.attachments):
                            fname = _safe_name(att.filename or f"att_{i}", f"att_{i}")
                            fpath = att_dir / fname
                            fpath.write_bytes(att.payload)
                            att_meta.append(
                                {
                                    "filename": fname,
                                    "path": str(fpath.relative_to(DATA / "attachments")).replace("\\", "/"),
                                }
                            )

                    date_iso = None
                    if msg.date:
                        dt = msg.date
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        date_iso = dt.isoformat()

                    index["messages"][key] = {
                        "id": key,
                        "uid": msg.uid,
                        "folder": folder,
                        "subject": msg.subject or "(no subject)",
                        "from": str(msg.from_) if msg.from_ else "",
                        "to": [str(x) for x in (msg.to or [])],
                        "date": date_iso,
                        "text": (msg.text or "")[:50000],
                        "html": (msg.html or "")[:100000],
                        "attachments": att_meta,
                    }
                    seen.add(msg.uid)
                    fetched += 1
                print(f"  {fetched} bajados...", flush=True)
            state["uids"][folder] = sorted(seen)
            if limit and fetched >= limit:
                break

    state["last_sync"] = datetime.now(timezone.utc).isoformat()
    _save_json(INDEX, index)
    _save_json(STATE, state)
    return {"fetched": fetched, "total": len(index["messages"]), "errors": errors}
