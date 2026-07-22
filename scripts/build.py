#!/usr/bin/env python3
"""Phase 2 build entry point for AI Learning Studio."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import traceback


def resolve_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def add_repo_root_to_sys_path(repo_root: Path) -> None:
    repo_root_text = str(repo_root)
    if repo_root_text not in sys.path:
        sys.path.insert(0, repo_root_text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the AI Learning Studio static site.")
    parser.add_argument("--check", action="store_true", help="Validate and render without replacing dist/")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root()
    add_repo_root_to_sys_path(repo_root)

    from core.build_pipeline import BuildError, build_site  # noqa: WPS433

    try:
        summary = build_site(repo_root, check_only=args.check)

        print("Build complete")
        print(f"Pages: {summary.page_count}")
        print(f"Assets: {summary.asset_count}")
        print(f"Routes: {summary.route_count}")
        print(f"Output directory: {summary.output_dir}")
        return 0
    except BuildError as exc:
        print(f"Build failed: {exc.format_for_console()}", file=sys.stderr)
        if os.environ.get("AI_STUDIO_DEBUG") == "1":
            traceback.print_exc()
        return 1
    except Exception as exc:  # pragma: no cover - defensive fallback for unexpected failures
        print(f"Build failed: {exc}", file=sys.stderr)
        if os.environ.get("AI_STUDIO_DEBUG") == "1":
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
