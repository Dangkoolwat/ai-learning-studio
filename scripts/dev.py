#!/usr/bin/env python3
"""Local development server with lightweight file watching and automatic rebuild.

Usage:
    python3 scripts/dev.py [--port 8008]
"""

from __future__ import annotations

import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from pathlib import Path
import subprocess
import sys
import threading
import time


REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "dist"
WATCH_DIRS = [
    REPO_ROOT / "pages",
    REPO_ROOT / "assets",
    REPO_ROOT / "components",
    REPO_ROOT / "data",
    REPO_ROOT / "templates",
    REPO_ROOT / "core",
]
WATCH_EXTENSIONS = {".md", ".css", ".js", ".html", ".json", ".py", ".webp", ".png", ".jpg", ".svg"}


def run_build() -> bool:
    """Execute the project build pipeline."""
    build_script = REPO_ROOT / "scripts" / "build.py"
    cmd = [sys.executable, str(build_script)]
    try:
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)
        if proc.returncode == 0:
            print(f"[{time.strftime('%H:%M:%S')}] ⚡ Build succeeded (dist updated)")
            return True
        else:
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Build failed:\n{proc.stderr.strip() or proc.stdout.strip()}")
            return False
    except Exception as exc:
        print(f"[{time.strftime('%H:%M:%S')}] ❌ Build error: {exc}")
        return False


def get_latest_mtime() -> float:
    """Scan watched directories and return the maximum modification timestamp."""
    max_mtime = 0.0
    for watch_dir in WATCH_DIRS:
        if not watch_dir.exists():
            continue
        for root, _, files in os.walk(watch_dir):
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in WATCH_EXTENSIONS:
                    file_path = Path(root) / file
                    try:
                        mtime = file_path.stat().st_mtime
                        if mtime > max_mtime:
                            max_mtime = mtime
                    except OSError:
                        pass
    return max_mtime


def watch_loop(interval: float = 0.5) -> None:
    """Background loop polling file timestamps to trigger rebuilds."""
    last_mtime = get_latest_mtime()
    while True:
        time.sleep(interval)
        try:
            current_mtime = get_latest_mtime()
            if current_mtime > last_mtime:
                last_mtime = current_mtime
                print(f"\n[{time.strftime('%H:%M:%S')}] 🔄 File change detected. Rebuilding...")
                run_build()
        except Exception as exc:
            print(f"Watch error: {exc}")


class DistHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Serve files from the dist directory with no-cache headers for easy local testing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format: str, *args) -> None:
        # Suppress verbose 200/304 request spam
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Learning Studio Dev Server")
    parser.add_argument("--port", type=int, default=8008, help="Port to serve on (default: 8008)")
    parser.add_argument("--no-watch", action="store_true", help="Disable file watching")
    args = parser.parse_args()

    print("=" * 60)
    print("🚀 AI Learning Studio Local Development Server")
    print("=" * 60)

    # Initial build
    print(f"[{time.strftime('%H:%M:%S')}] 🔨 Running initial build...")
    run_build()

    if not args.no_watch:
        watcher_thread = threading.Thread(target=watch_loop, daemon=True)
        watcher_thread.start()
        print(f"[{time.strftime('%H:%M:%S')}] 👁️  File watcher active (monitoring pages, assets, data, templates)")

    server_address = ("", args.port)
    httpd = HTTPServer(server_address, DistHTTPRequestHandler)
    print(f"[{time.strftime('%H:%M:%S')}] 🌐 Local server running at: http://localhost:{args.port}/")
    print("   Press Ctrl+C to stop.")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")


if __name__ == "__main__":
    main()
