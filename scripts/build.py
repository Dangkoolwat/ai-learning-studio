#!/usr/bin/env python3
"""Minimal bootstrap build for AI Learning Studio."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def log_stage(message: str) -> None:
    print(f"Stage: {message}")


def verify_python_version() -> None:
    log_stage("verify Python version")
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10 or newer is required.")
    print(f"Python version: {sys.version.split()[0]}")


def get_repo_root() -> Path:
    log_stage("resolve repository root")
    repo_root = Path(__file__).resolve().parent.parent
    if not repo_root.is_dir():
        raise RuntimeError(f"Repository root not found: {repo_root}")
    return repo_root


def reset_dist_directory(repo_root: Path) -> Path:
    log_stage("create clean dist directory")
    dist_dir = repo_root / "dist"
    if dist_dir.exists():
        if dist_dir.is_dir():
            shutil.rmtree(dist_dir)
        else:
            dist_dir.unlink()
    dist_dir.mkdir(parents=True, exist_ok=True)
    return dist_dir


def build_bootstrap_index(dist_dir: Path) -> None:
    log_stage("generate bootstrap index")
    index_html = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Learning Studio | Project Bootstrap</title>
  <meta name="description" content="AI Learning Studio는 프로젝트 부트스트랩 단계의 배포 검증용 페이지입니다.">
</head>
<body>
  <main>
    <h1>AI Learning Studio 프로젝트 부트스트랩 단계</h1>
    <p>이 페이지는 배포 검증용 임시 페이지입니다.</p>
  </main>
</body>
</html>
"""
    (dist_dir / "index.html").write_text(index_html, encoding="utf-8")


def main() -> int:
    try:
        log_stage("bootstrap build start")
        verify_python_version()
        repo_root = get_repo_root()
        dist_dir = reset_dist_directory(repo_root)
        build_bootstrap_index(dist_dir)
        log_stage("bootstrap build complete")
        return 0
    except Exception as exc:  # noqa: BLE001 - bootstrap must report a clear fatal error
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
