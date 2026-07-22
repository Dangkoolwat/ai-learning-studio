#!/usr/bin/env python3
"""Minimal bootstrap build for AI Learning Studio."""

from __future__ import annotations

import sys
from pathlib import Path


def verify_python_version() -> None:
    print("Stage: verify Python version")
    if sys.version_info < (3, 11):
        raise SystemExit("Python 3.11 or newer is required.")
    print(f"Python version: {sys.version.split()[0]}")


def ensure_dist_directory() -> None:
    print("Stage: ensure dist directory")
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    print(f"Created or verified: {dist_dir}")


def main() -> int:
    print("Stage: bootstrap build start")
    verify_python_version()
    ensure_dist_directory()
    print("Stage: bootstrap build complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
