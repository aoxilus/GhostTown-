"""gpt-4.1-mini helper: propose commercial trash batches + execute IMAP trash."""
from __future__ import annotations

import json
from pathlib import Path

from imap_tools import MailBox
from openai import OpenAI

from .config import INDEX, get_settings

SYSTEM = """You help clean a Gmail inbox archive (GhostTown).
Classify and propose deletions of commercial spam, ads, newsletters, sales.
Keep real human conversations.
Reply ONLY with JSON:
{"reply":"short spanish explanation","actions":[{"id":"folder:uid","reason":"..."}]}
ids must be exact message ids from the catalog. Max 40 actions per turn.
If user is just chatting, actions can be []."""


def _catalog(limit: int = 400) -> list[dict]:
    if not INDEX.exists():
        return []
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    msgs = list(data.get("messages", {}).values())
    msgs.sort(key=lambda m: m.get("date") or "", reverse=True)
    out = []
    for m in msgs[:limit]:
        out.append(
            {
                "id": m["id"],
                "subject": m.get("subject"),
                "from": m.get("from"),
                "date": m.get("date"),
                "snippet": (m.get("text") or "")[:200],
            }
        )
    return out


def chat(user_message: str, history: list[dict] | None = None) -> dict:
    s = get_settings()
    if not s.openai_api_key:
        return {"reply": "Falta OPENAI_API_KEY en .env", "actions": []}
    client = OpenAI(api_key=s.openai_api_key)
    catalog = _catalog()
    messages = [
        {"role": "system", "content": SYSTEM},
        {
            "role": "user",
            "content": "CATALOG JSON:\n" + json.dumps(catalog, ensure_ascii=False)[:120000],
        },
    ]
    for h in history or []:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_message})

    resp = client.chat.completions.create(
        model=s.openai_model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    raw = resp.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"reply": raw, "actions": []}
    return {
        "reply": parsed.get("reply") or "",
        "actions": parsed.get("actions") or [],
    }


def trash_ids(ids: list[str]) -> dict:
    s = get_settings()
    if not INDEX.exists():
        return {"trashed": 0, "errors": ["no index"]}
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    msgs = data.get("messages", {})
    by_folder: dict[str, list[str]] = {}
    errors = []
    for mid in ids:
        m = msgs.get(mid)
        if not m:
            errors.append(f"missing {mid}")
            continue
        by_folder.setdefault(m["folder"], []).append(m["uid"])

    trashed = 0
    with MailBox(s.imap_host).login(s.imap_user, s.imap_password) as mb:
        folders = {f.name for f in mb.folder.list()}
        trash_name = "[Gmail]/Trash" if "[Gmail]/Trash" in folders else "Trash"
        for folder, uids in by_folder.items():
            if folder not in folders:
                errors.append(f"no folder {folder}")
                continue
            mb.folder.set(folder)
            try:
                mb.move(uids, trash_name)
                trashed += len(uids)
                for uid in uids:
                    mid = f"{folder}:{uid}"
                    msgs.pop(mid, None)
            except Exception as e:
                errors.append(f"{folder}: {e}")

    INDEX.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"trashed": trashed, "errors": errors}
