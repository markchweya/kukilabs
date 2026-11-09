"""Run Kuki: `python -m kuki`.

Binds to 127.0.0.1 only. Kuki holds personal study material and has no login,
so it must never be reachable from the network by default.
"""

from __future__ import annotations

import argparse
import logging

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(prog="kuki", description="Kuki, your private study companion")
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind (default: localhost only)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--reload", action="store_true", help="Auto-reload on code changes (development)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    if args.host not in ("127.0.0.1", "localhost"):
        logging.warning("Kuki is listening on %s. Anyone on your network can read your notes.", args.host)
    uvicorn.run("kuki.api.app:create_app", factory=True, host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
