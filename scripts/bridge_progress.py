"""Puente temporal: lee la salida del sync viejo (terminal) y escribe
data/sync_progress.json para que la barra del GUI muestre el avance real.
Se borra solo cuando el sync termina. Uso:
  python scripts/bridge_progress.py <ruta_terminal_txt>
"""
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROG = ROOT / "data" / "sync_progress.json"
TERM = Path(sys.argv[1])

RE_FOLDER = re.compile(r"^(.+?): (\d+) nuevos de (\d+)", re.M)
RE_COUNT = re.compile(r"^\s+(\d+) bajados", re.M)


def write(**kw):
    kw["updated_at"] = datetime.now(timezone.utc).isoformat()
    PROG.write_text(json.dumps(kw, ensure_ascii=False), encoding="utf-8")


while True:
    text = TERM.read_text(encoding="utf-8", errors="ignore")
    folders = list(RE_FOLDER.finditer(text))
    counts = list(RE_COUNT.finditer(text))
    fetched = int(counts[-1].group(1)) if counts else 0

    if "exit_code:" in text:
        write(status="done", folder="", fetched=fetched, errors=[])
        break

    if folders:
        cur = folders[-1]
        folder, new_total = cur.group(1), int(cur.group(3))
        # bajados acumulados antes de que empezara esta carpeta
        before = [c for c in counts if c.start() < cur.start()]
        base = int(before[-1].group(1)) if before else 0
        write(
            status="running",
            folder=folder,
            folder_done=max(0, fetched - base),
            folder_total=new_total,
            fetched=fetched,
            errors=[],
        )
    time.sleep(3)

print("bridge done")
