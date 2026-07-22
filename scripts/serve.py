"""Local development server launcher with automatic browser opening for AI Learning Studio."""

from __future__ import annotations

import http.server
import os
from pathlib import Path
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser

PORT = 8000
REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "dist"


def run_build() -> bool:
    print("[1/2] Running build pipeline (python3 scripts/build.py)...")
    result = subprocess.run([sys.executable, "scripts/build.py"], cwd=REPO_ROOT)
    return result.returncode == 0


def open_browser() -> None:
    time.sleep(0.8)
    url = f"http://localhost:{PORT}"
    print(f"Opening browser at {url} ...")
    webbrowser.open(url)


def main() -> None:
    if not run_build():
        print("Build failed. Aborting server launch.", file=sys.stderr)
        sys.exit(1)

    os.chdir(DIST_DIR)
    
    # Avoid address already in use error on rapid restarts
    socketserver.TCPServer.allow_reuse_address = True

    print(f"\n[2/2] Starting local web server on http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server.\n")

    threading.Thread(target=open_browser, daemon=True).start()

    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
