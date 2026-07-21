"""CLI: sync | build | serve"""
from __future__ import annotations

import argparse
import json
import sys
import webbrowser

import uvicorn

from .config import get_settings
from .export_html import build
from .sync_imap import sync, verify


def main():
    p = argparse.ArgumentParser(prog="gmailghosttown")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sync", help="IMAP pull")
    s.add_argument("--limit", type=int, default=None)
    s.add_argument("--folder", action="append", default=None)

    sub.add_parser("build", help="Rebuild GhostTown HTML")
    sub.add_parser("verify", help="Test IMAP login only")
    srv = sub.add_parser("serve", help="Open GhostTown + AI chat")
    srv.add_argument("--no-browser", action="store_true")

    args = p.parse_args()
    if args.cmd == "verify":
        r = verify()
        print(json.dumps(r))
        sys.exit(0 if r["ok"] else 1)
    elif args.cmd == "sync":
        r = sync(folders=args.folder, limit=args.limit)
        print(r)
        print(build())
    elif args.cmd == "build":
        print(build())
    elif args.cmd == "serve":
        # remount after build
        from . import server as srvmod

        srvmod.mount_static()
        settings = get_settings()
        url = f"http://127.0.0.1:{settings.port}"
        if not args.no_browser:
            webbrowser.open(url)
        uvicorn.run("src.server:app", host="127.0.0.1", port=settings.port, reload=False)


if __name__ == "__main__":
    main()
