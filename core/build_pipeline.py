"""Phase 2 static site build pipeline helpers for AI Learning Studio.

This module intentionally implements only the limited Phase 2 pipeline.
It does not aim to be a general Markdown or YAML implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape as escape_html
import json
from pathlib import Path
from shutil import copy2, rmtree
import tempfile
import sys
from typing import Any
from typing import Callable
from uuid import uuid4


PROJECT_NAME = "AI Learning Studio"
BUILD_PHASE = "Phase 2 Static Site Build Pipeline"
GENERATOR_VERSION = "phase-2-build-pipeline-v1"
ALLOWED_FRONT_MATTER_KEYS = {"title", "description", "route", "lang", "status"}
ALLOWED_LANGS = {"ko", "en"}
TOTAL_STAGES = 8


class BuildError(RuntimeError):
    """Raised when the limited Phase 2 build pipeline fails."""

    def __init__(self, stage: str, message: str, *, path: Path | None = None) -> None:
        self.stage = stage
        self.path = path
        self.message = message
        super().__init__(message)

    def format_for_console(self) -> str:
        location = f" [{self.path}]" if self.path else ""
        return f"[{self.stage}]{location} {self.message}"


@dataclass(slots=True)
class PageSource:
    source_path: Path
    title: str
    description: str
    route: str
    lang: str
    status: str
    body_markdown: str


@dataclass(slots=True)
class BuildSummary:
    page_count: int
    asset_count: int
    route_count: int
    output_dir: Path
    generated_routes: list[str]
    generated_output_files: list[str]
    source_page_files: list[str]


def log_stage(index: int, total: int, label: str) -> None:
    print(f"[{index}/{total}] {label}")


def discover_page_sources(pages_dir: Path) -> list[Path]:
    if not pages_dir.is_dir():
        raise BuildError("Discover source pages", "pages/ directory does not exist", path=pages_dir)

    page_sources: list[Path] = []
    for path in sorted(pages_dir.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(pages_dir).parts):
            continue
        if path.name.startswith("."):
            continue
        page_sources.append(path)

    return page_sources


def parse_front_matter(page_path: Path, source_text: str) -> tuple[dict[str, str], str]:
    lines = source_text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise BuildError("Validate page sources", "front matter must start with ---", path=page_path)

    closing_index = next((index for index, raw_line in enumerate(lines[1:], start=1) if raw_line.strip() == "---"), None)
    if closing_index is None:
        raise BuildError("Validate page sources", "missing closing front matter delimiter", path=page_path)

    metadata: dict[str, str] = {}
    for raw_line in lines[1:closing_index]:
        stripped = raw_line.strip()
        if not stripped:
            raise BuildError("Validate page sources", "blank lines are not allowed inside front matter", path=page_path)
        if ":" not in raw_line:
            raise BuildError("Validate page sources", "front matter lines must use key: value format", path=page_path)

        key, _, value = raw_line.partition(":")
        key = key.strip()
        value = value.strip()

        if key not in ALLOWED_FRONT_MATTER_KEYS:
            raise BuildError("Validate page sources", f"unknown front matter field: {key}", path=page_path)
        if key in metadata:
            raise BuildError("Validate page sources", f"duplicate front matter field: {key}", path=page_path)
        metadata[key] = value

    body = "\n".join(lines[closing_index + 1 :])
    return metadata, body


def validate_front_matter(page_path: Path, metadata: dict[str, str]) -> None:
    required_fields = ("title", "description", "route", "lang", "status")
    for field in required_fields:
        value = metadata.get(field, "")
        if not value:
            raise BuildError("Validate page sources", f"missing required front matter field: {field}", path=page_path)

    title = metadata["title"]
    description = metadata["description"]
    route = metadata["route"]
    lang = metadata["lang"]

    if not title.strip():
        raise BuildError("Validate page sources", "title must be a non-empty string", path=page_path)
    if not description.strip():
        raise BuildError("Validate page sources", "description must be a non-empty string", path=page_path)
    validate_route(page_path, route)
    if lang not in ALLOWED_LANGS:
        raise BuildError("Validate page sources", "lang must be ko or en in Phase 2", path=page_path)


def validate_route(page_path: Path, route: str) -> None:
    if not route.startswith("/"):
        raise BuildError("Validate page sources", "route must begin with /", path=page_path)
    if route != "/" and not route.endswith("/"):
        raise BuildError("Validate page sources", "route must end with / unless it is /", path=page_path)
    if any(token in route for token in ("..", "\\", "?", "#", "//")):
        raise BuildError("Validate page sources", "route contains a disallowed path fragment", path=page_path)


def parse_page_source(page_path: Path) -> PageSource:
    source_text = page_path.read_text(encoding="utf-8")
    metadata, body = parse_front_matter(page_path, source_text)
    validate_front_matter(page_path, metadata)
    return PageSource(
        source_path=page_path,
        title=metadata["title"],
        description=metadata["description"],
        route=metadata["route"],
        lang=metadata["lang"],
        status=metadata["status"],
        body_markdown=body,
    )


def render_markdown(markdown_text: str, *, source_path: Path) -> str:
    """Render the limited Phase 2 Markdown subset.

    Supported syntax:
    - level 1 headings
    - level 2 headings
    - paragraphs
    - unordered lists
    - fenced code blocks
    - blank lines
    """

    blocks: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    code_lines: list[str] = []
    in_code_block = False

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        text = " ".join(line.strip() for line in paragraph_lines if line.strip())
        if text:
            blocks.append(f"<p>{escape_html(text)}</p>")
        paragraph_lines.clear()

    def flush_list() -> None:
        if not list_items:
            return
        items = "".join(f"<li>{item}</li>" for item in list_items)
        blocks.append(f"<ul>{items}</ul>")
        list_items.clear()

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if in_code_block:
            if stripped == "```":
                code_html = escape_html("\n".join(code_lines))
                blocks.append(f"<pre><code>{code_html}</code></pre>")
                code_lines.clear()
                in_code_block = False
            else:
                code_lines.append(line)
            continue

        if stripped == "```":
            flush_paragraph()
            flush_list()
            in_code_block = True
            continue
        if stripped.startswith("```"):
            raise BuildError("Render HTML", "only bare triple-backtick fences are supported", path=source_path)
        if not stripped:
            flush_paragraph()
            flush_list()
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h1>{escape_html(stripped[2:].strip())}</h1>")
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h2>{escape_html(stripped[3:].strip())}</h2>")
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            list_items.append(escape_html(stripped[2:].strip()))
            continue

        flush_list()
        paragraph_lines.append(line)

    if in_code_block:
        raise BuildError("Render HTML", "missing closing code fence", path=source_path)

    flush_paragraph()
    flush_list()
    return "\n".join(blocks)


def route_to_output_path(route: str, dist_dir: Path) -> Path:
    if route == "/":
        output_path = dist_dir / "index.html"
    else:
        segments = [segment for segment in route.strip("/").split("/") if segment]
        output_path = dist_dir.joinpath(*segments, "index.html")

    normalized_output = output_path.resolve(strict=False)
    normalized_dist = dist_dir.resolve(strict=False)
    if normalized_dist != normalized_output and normalized_dist not in normalized_output.parents:
        raise BuildError("Render HTML", "route escapes the dist/ directory")
    return output_path


def render_html_document(page: PageSource, rendered_markdown: str) -> str:
    canonical_path = page.route
    return f"""<!doctype html>
<html lang="{escape_html(page.lang)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape_html(page.title)}</title>
  <meta name="description" content="{escape_html(page.description)}">
  <meta name="canonical-path" content="{escape_html(canonical_path)}">
  <style>
    :root {{
      color-scheme: light;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }}

    body {{
      margin: 0;
      padding: 2rem 1rem;
      background: #fafafa;
      color: #1f2937;
    }}

    main {{
      max-width: 64rem;
      margin: 0 auto;
      padding: 1.5rem;
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 1rem;
    }}

    h1, h2, p, ul, pre {{
      margin-top: 0;
    }}

    pre {{
      overflow-x: auto;
      padding: 1rem;
      background: #f3f4f6;
      border-radius: 0.75rem;
    }}

    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}

    ul {{
      padding-left: 1.5rem;
    }}
  </style>
</head>
<body>
  <main>
{rendered_markdown}
  </main>
</body>
</html>
"""


def discover_approved_assets(assets_dir: Path) -> list[Path]:
    if not assets_dir.exists():
        return []

    approved_assets: list[Path] = []
    for path in sorted(assets_dir.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(assets_dir)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if path.suffix == ".pyc":
            continue
        if path.name == ".gitkeep":
            continue
        approved_assets.append(path)
    return approved_assets


def copy_approved_assets(assets_dir: Path, dist_dir: Path) -> tuple[int, list[str]]:
    approved_assets = discover_approved_assets(assets_dir)
    if not approved_assets:
        return 0, []

    copied_files: list[str] = []
    dist_assets_dir = dist_dir / "assets"
    for asset_path in approved_assets:
        relative_path = asset_path.relative_to(assets_dir)
        destination = dist_assets_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        copy2(asset_path, destination)
        copied_files.append(f"dist/{destination.relative_to(dist_dir).as_posix()}")

    return len(copied_files), copied_files


def build_manifest(
    *,
    page_sources: list[PageSource],
    generated_routes: list[str],
    generated_output_files: list[str],
    copied_asset_count: int,
    source_page_files: list[str],
) -> dict[str, Any]:
    return {
        "project_name": PROJECT_NAME,
        "build_phase": BUILD_PHASE,
        "generator_version": GENERATOR_VERSION,
        "generated_page_count": len(page_sources),
        "copied_asset_count": copied_asset_count,
        "generated_routes": generated_routes,
        "generated_output_files": generated_output_files,
        "source_page_files": source_page_files,
        "build_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_manifest(manifest_path: Path, manifest: dict[str, Any]) -> None:
    write_text(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def validate_generated_output(staging_dir: Path, manifest: dict[str, Any], page_sources: list[PageSource]) -> None:
    index_path = staging_dir / "index.html"
    manifest_path = staging_dir / "build-manifest.json"

    if not index_path.is_file():
        raise BuildError("Validate output", "dist/index.html is missing", path=index_path)
    if not manifest_path.is_file():
        raise BuildError("Validate output", "dist/build-manifest.json is missing", path=manifest_path)

    index_html = index_path.read_text(encoding="utf-8")
    first_page = page_sources[0]
    expected_title = f"<title>{escape_html(first_page.title)}</title>"
    expected_description = f'<meta name="description" content="{escape_html(first_page.description)}">'
    if f'lang="{escape_html(first_page.lang)}"' not in index_html:
        raise BuildError("Validate output", "generated HTML does not contain the expected lang attribute", path=index_path)
    if expected_title not in index_html:
        raise BuildError("Validate output", "generated title does not match source front matter", path=index_path)
    if expected_description not in index_html:
        raise BuildError("Validate output", "generated meta description does not match source front matter", path=index_path)
    if "<h1>AI Learning Studio</h1>" not in index_html:
        raise BuildError("Validate output", "rendered Markdown heading is missing", path=index_path)
    if "정적 사이트 생성 파이프라인이 정상적으로 작동하고 있습니다." not in index_html:
        raise BuildError("Validate output", "rendered Markdown paragraph is missing", path=index_path)

    parsed_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if parsed_manifest != manifest:
        raise BuildError("Validate output", "build manifest content changed unexpectedly", path=manifest_path)
    if parsed_manifest.get("generated_page_count") != len(page_sources):
        raise BuildError("Validate output", "manifest page count is incorrect", path=manifest_path)
    if "/" not in parsed_manifest.get("generated_routes", []):
        raise BuildError("Validate output", "manifest does not contain route /", path=manifest_path)
    if parsed_manifest.get("copied_asset_count") != 0:
        asset_dir = staging_dir / "assets"
        if not asset_dir.exists():
            raise BuildError("Validate output", "assets directory is missing despite copied assets", path=staging_dir)


def publish_output(staging_dir: Path, dist_dir: Path) -> None:
    backup_dir = dist_dir.with_name(f".dist-backup-{uuid4().hex}")
    backup_created = False

    if dist_dir.exists():
        dist_dir.rename(backup_dir)
        backup_created = True

    try:
        staging_dir.rename(dist_dir)
    except Exception:
        if backup_created and backup_dir.exists():
            if dist_dir.exists():
                rmtree(dist_dir)
            backup_dir.rename(dist_dir)
        raise
    else:
        if backup_created and backup_dir.exists():
            rmtree(backup_dir)


def cleanup_temp_dir(temp_dir: Path) -> None:
    if temp_dir.exists():
        rmtree(temp_dir)


def build_site(
    repo_root: Path,
    *,
    check_only: bool = False,
    stage_logger: Callable[[int, int, str], None] = log_stage,
) -> BuildSummary:
    pages_dir = repo_root / "pages"
    assets_dir = repo_root / "assets"
    dist_dir = repo_root / "dist"
    temp_root = Path(tempfile.mkdtemp(prefix=".phase2-build-", dir=repo_root))

    try:
        stage_logger(1, TOTAL_STAGES, "Validate environment")
        if sys.version_info < (3, 10):  # pragma: no cover - defensive repeat of the entrypoint check
            raise BuildError("Validate environment", "Python 3.10 or newer is required.")
        print(f"Python version: {sys.version.split()[0]}")
        if not repo_root.is_dir():
            raise BuildError("Validate environment", "repository root does not exist", path=repo_root)
        if not pages_dir.is_dir():
            raise BuildError("Validate environment", "pages/ directory does not exist", path=pages_dir)
        if not assets_dir.is_dir():
            raise BuildError("Validate environment", "assets/ directory does not exist", path=assets_dir)

        stage_logger(2, TOTAL_STAGES, "Discover source pages")
        page_paths = discover_page_sources(pages_dir)
        if not page_paths:
            raise BuildError("Discover source pages", "no page sources were found", path=pages_dir)

        stage_logger(3, TOTAL_STAGES, "Validate page sources")
        page_sources = [parse_page_source(page_path) for page_path in page_paths]
        staging_dir = temp_root
        generated_routes: list[str] = []
        generated_output_files: list[str] = []

        stage_logger(4, TOTAL_STAGES, "Render HTML")
        for page in page_sources:
            output_path = route_to_output_path(page.route, staging_dir)
            rendered_markdown = render_markdown(page.body_markdown, source_path=page.source_path)
            html_document = render_html_document(page, rendered_markdown)
            write_text(output_path, html_document)
            generated_routes.append(page.route)
            generated_output_files.append(f"dist/{output_path.relative_to(staging_dir).as_posix()}")

        stage_logger(5, TOTAL_STAGES, "Copy assets")
        copied_asset_count, copied_asset_files = copy_approved_assets(assets_dir, staging_dir)
        if copied_asset_files:
            generated_output_files.extend(copied_asset_files)

        stage_logger(6, TOTAL_STAGES, "Write build manifest")
        source_page_files = [page.source_path.relative_to(repo_root).as_posix() for page in page_sources]
        manifest = build_manifest(
            page_sources=page_sources,
            generated_routes=generated_routes,
            generated_output_files=sorted(generated_output_files + ["dist/build-manifest.json"]),
            copied_asset_count=copied_asset_count,
            source_page_files=source_page_files,
        )
        write_manifest(staging_dir / "build-manifest.json", manifest)

        stage_logger(7, TOTAL_STAGES, "Validate output")
        validate_generated_output(staging_dir, manifest, page_sources)

        stage_logger(8, TOTAL_STAGES, "Publish dist" if not check_only else "Skip dist publication (--check)")
        if not check_only:
            publish_output(staging_dir, dist_dir)
            output_dir = dist_dir
        else:
            cleanup_temp_dir(staging_dir)
            output_dir = staging_dir

        return BuildSummary(
            page_count=len(page_sources),
            asset_count=copied_asset_count,
            route_count=len(generated_routes),
            output_dir=output_dir,
            generated_routes=generated_routes,
            generated_output_files=sorted(generated_output_files + ["dist/build-manifest.json"]),
            source_page_files=source_page_files,
        )
    except Exception:
        cleanup_temp_dir(temp_root)
        raise
