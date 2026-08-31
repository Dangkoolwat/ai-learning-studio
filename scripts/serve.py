"""Local development server launcher with automatic browser opening for AI Learning Studio."""

from __future__ import annotations

import argparse
import http.server
import os
from pathlib import Path
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser

DEFAULT_PORT = 8000
REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "dist"


def run_build() -> bool:
    print("[1/2] Running build pipeline (python3 scripts/build.py)...")
    result = subprocess.run([sys.executable, "scripts/build.py"], cwd=REPO_ROOT)
    return result.returncode == 0


def normalize_target_path(raw_path: str) -> str:
    """Normalize input path to standard URL path with leading slash."""
    if not raw_path:
        return "/"

    path = raw_path.strip().replace("\\", "/")
    if path.startswith("pages/sections/"):
        path = path[len("pages/sections/"):]
    elif path.startswith("/pages/sections/"):
        path = path[len("/pages/sections/"):]

    if path.endswith(".md"):
        path = path[:-3]
    elif path.endswith(".html"):
        path = path[:-5]
    if path.endswith("/index"):
        path = path[:-6]

    path = path.strip("/")
    if not path:
        return "/"

    return f"/{path}/"


def open_browser(port: int, target_path: str) -> None:
    time.sleep(0.8)
    url = f"http://localhost:{port}{target_path}"
    print(f"Opening browser at {url} ...")
    webbrowser.open(url)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Local development server for AI Learning Studio"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="",
        help="Optional relative path or route to open (e.g. image-ai/crayon-travel-poster)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port number to listen on (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "-P",
        "--path-opt",
        dest="path_flag",
        default="",
        help="Target page path (alternative to positional argument)",
    )
    parser.add_argument(
        "-n",
        "--no-browser",
        action="store_true",
        help="Do not open web browser automatically",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Skip build step before starting server",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.no_build:
        if not run_build():
            print("Build failed. Aborting server launch.", file=sys.stderr)
            sys.exit(1)

    os.chdir(DIST_DIR)

    # Avoid address already in use error on rapid restarts
    socketserver.TCPServer.allow_reuse_address = True

    target_path = normalize_target_path(args.path_flag or args.path)
    print(f"\n[2/2] Starting local web server on http://localhost:{args.port}")
    if target_path != "/":
        print(f"Target page: http://localhost:{args.port}{target_path}")
    print("Press Ctrl+C to stop the server.\n")

    if not args.no_browser:
        threading.Thread(
            target=open_browser,
            args=(args.port, target_path),
            daemon=True,
        ).start()

    with socketserver.TCPServer(("", args.port), http.server.SimpleHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
