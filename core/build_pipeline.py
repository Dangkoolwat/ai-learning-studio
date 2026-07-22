"""Phase 3 static site build pipeline helpers for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape as escape_html
import json
from pathlib import Path
from shutil import copy2, rmtree
import sys
import tempfile
from typing import Any, Callable
from uuid import uuid4

from core.errors import BuildError
from core.navigation import NavigationData, load_navigation
from core.page_registry import PageRegistry, PageRegistryEntry, load_page_registry


PROJECT_NAME = "AI Learning Studio"
BUILD_PHASE = "Phase 3 Page Registry and Content Data Structure"
GENERATOR_VERSION = "phase-3-page-registry-v1"
TOTAL_STAGES = 10
ALLOWED_FRONT_MATTER_KEYS = {"registry_id"}


@dataclass(slots=True)
class PageSource:
    """A parsed page source file."""

    source_path: Path
    registry_id: str
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
        raise BuildError("Validate environment", "pages/ directory does not exist", path=pages_dir)

    page_sources: list[Path] = []
    for path in sorted(pages_dir.rglob("*.md")):
        relative = path.relative_to(pages_dir)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if path.name.startswith("."):
            continue
        page_sources.append(path)

    return page_sources


def parse_front_matter(page_path: Path, source_text: str) -> tuple[dict[str, str], str]:
    lines = source_text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise BuildError("Parse page sources", "front matter must start with ---", path=page_path, source_file=page_path)

    closing_index = next((index for index, raw_line in enumerate(lines[1:], start=1) if raw_line.strip() == "---"), None)
    if closing_index is None:
        raise BuildError(
            "Parse page sources",
            "missing closing front matter delimiter",
            path=page_path,
            source_file=page_path,
        )

    metadata: dict[str, str] = {}
    for raw_line in lines[1:closing_index]:
        stripped = raw_line.strip()
        if not stripped:
            raise BuildError(
                "Parse page sources",
                "blank lines are not allowed inside front matter",
                path=page_path,
                source_file=page_path,
            )
        if ":" not in raw_line:
            raise BuildError(
                "Parse page sources",
                "front matter lines must use key: value format",
                path=page_path,
                source_file=page_path,
            )

        key, _, value = raw_line.partition(":")
        key = key.strip()
        value = value.strip()

        if key not in ALLOWED_FRONT_MATTER_KEYS:
            raise BuildError(
                "Parse page sources",
                f"unknown front matter field: {key}",
                path=page_path,
                source_file=page_path,
                field=key,
            )
        if key in metadata:
            raise BuildError(
                "Parse page sources",
                f"duplicate front matter field: {key}",
                path=page_path,
                source_file=page_path,
                field=key,
            )
        metadata[key] = value

    body = "\n".join(lines[closing_index + 1 :])
    return metadata, body


def validate_front_matter(page_path: Path, metadata: dict[str, str]) -> None:
    if set(metadata) != {"registry_id"}:
        raise BuildError(
            "Parse page sources",
            "front matter must contain only registry_id",
            path=page_path,
            source_file=page_path,
        )

    registry_id = metadata.get("registry_id", "").strip()
    if not registry_id:
        raise BuildError(
            "Parse page sources",
            "registry_id must be a non-empty string",
            path=page_path,
            source_file=page_path,
            field="registry_id",
        )


def parse_page_source(page_path: Path) -> PageSource:
    source_text = page_path.read_text(encoding="utf-8")
    metadata, body = parse_front_matter(page_path, source_text)
    validate_front_matter(page_path, metadata)
    return PageSource(
        source_path=page_path,
        registry_id=metadata["registry_id"].strip(),
        body_markdown=body,
    )


def render_markdown(markdown_text: str, *, source_path: Path) -> str:
    """Render the limited Markdown subset used by the verification pages."""

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


def render_html_document(page: PageRegistryEntry, rendered_markdown: str) -> str:
    canonical_path = page.route
    return f"""<!doctype html>
<html lang="{escape_html(page.lang)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="generator" content="{escape_html(GENERATOR_VERSION)}">
  <meta name="description" content="{escape_html(page.description)}">
  <link rel="canonical" href="{escape_html(canonical_path)}">
  <title>{escape_html(page.title)}</title>
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

    h1,
    h2,
    p,
    ul,
    pre {{
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
  <main data-page-id="{escape_html(page.id)}" data-page-type="{escape_html(page.type)}">
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


def validate_page_sources_against_registry(
    page_paths: list[Path],
    page_sources: list[PageSource],
    registry: PageRegistry,
    repo_root: Path,
) -> None:
    discovered_sources = {path.relative_to(repo_root).as_posix() for path in page_paths}
    expected_sources = set(registry.source_files())
    if discovered_sources != expected_sources:
        missing = sorted(expected_sources - discovered_sources)
        extra = sorted(discovered_sources - expected_sources)
        details = []
        if missing:
            details.append(f"missing sources: {', '.join(missing)}")
        if extra:
            details.append(f"unregistered sources: {', '.join(extra)}")
        raise BuildError(
            "Validate registered sources",
            "page source files do not match the page registry"
            + (" (" + "; ".join(details) + ")" if details else ""),
        )

    sources_by_id = {source.registry_id: source for source in page_sources}
    for page in registry.pages:
        source = sources_by_id.get(page.id)
        if source is None:
            raise BuildError(
                "Validate registered sources",
                f"missing page source for registry entry {page.id}",
                source_file=page.source,
                page_id=page.id,
            )
        if source.source_path.relative_to(repo_root).as_posix() != page.source:
            raise BuildError(
                "Validate registered sources",
                f"page source path must be {page.source}",
                source_file=source.source_path,
                page_id=page.id,
            )
        if source.registry_id != page.id:
            raise BuildError(
                "Validate registered sources",
                "registry_id must match the page registry entry id",
                source_file=source.source_path,
                page_id=page.id,
                field="registry_id",
            )


def build_public_registry_data(registry: PageRegistry) -> dict[str, object]:
    return registry.to_public_dict()


def build_public_navigation_data(navigation: NavigationData) -> dict[str, object]:
    return navigation.to_public_dict()


def build_manifest(
    *,
    registry: PageRegistry,
    navigation: NavigationData,
    published_pages: list[PageRegistryEntry],
    draft_pages: list[PageRegistryEntry],
    generated_routes: list[str],
    generated_output_files: list[str],
    copied_asset_count: int,
    source_page_files: list[str],
    public_registry_output_file: str,
    public_navigation_output_file: str,
) -> dict[str, Any]:
    return {
        "project_name": PROJECT_NAME,
        "build_phase": BUILD_PHASE,
        "generator_version": GENERATOR_VERSION,
        "registry_version": registry.version,
        "navigation_version": navigation.version,
        "registered_page_count": len(registry.pages),
        "published_page_count": len(published_pages),
        "draft_page_count": len(draft_pages),
        "generated_page_count": len(published_pages),
        "copied_asset_count": copied_asset_count,
        "registered_page_ids": [page.id for page in registry.pages],
        "published_page_ids": [page.id for page in published_pages],
        "generated_routes": generated_routes,
        "source_page_files": source_page_files,
        "public_registry_output_file": public_registry_output_file,
        "public_navigation_output_file": public_navigation_output_file,
        "generated_output_files": generated_output_files,
        "build_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def validate_json_file(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BuildError("Validate output", f"{path.name} is not valid JSON: {exc.msg}", path=path) from exc
    if not isinstance(payload, dict):
        raise BuildError("Validate output", f"{path.name} must contain a JSON object", path=path)
    return payload


def validate_generated_output(
    staging_dir: Path,
    manifest: dict[str, Any],
    registry: PageRegistry,
    navigation: NavigationData,
    public_registry: dict[str, Any],
    public_navigation: dict[str, Any],
) -> None:
    manifest_path = staging_dir / "build-manifest.json"
    registry_path = staging_dir / "page-registry.json"
    navigation_path = staging_dir / "navigation.json"

    for required_path, label in (
        (staging_dir / "index.html", "dist/index.html"),
        (manifest_path, "dist/build-manifest.json"),
        (registry_path, "dist/page-registry.json"),
        (navigation_path, "dist/navigation.json"),
    ):
        if not required_path.is_file():
            raise BuildError("Validate output", f"{label} is missing", path=required_path)

    parsed_manifest = validate_json_file(manifest_path)
    parsed_registry = validate_json_file(registry_path)
    parsed_navigation = validate_json_file(navigation_path)

    if parsed_manifest != manifest:
        raise BuildError("Validate output", "build manifest content changed unexpectedly", path=manifest_path)
    if parsed_registry != public_registry:
        raise BuildError("Validate output", "public page registry content changed unexpectedly", path=registry_path)
    if parsed_navigation != public_navigation:
        raise BuildError("Validate output", "public navigation content changed unexpectedly", path=navigation_path)

    published_pages = registry.published_pages()
    draft_pages = registry.draft_pages()
    expected_routes = [page.route for page in published_pages]
    expected_html_files = {route_to_output_path(page.route, staging_dir).relative_to(staging_dir).as_posix() for page in published_pages}
    actual_html_files = {
        path.relative_to(staging_dir).as_posix()
        for path in staging_dir.rglob("*.html")
    }
    if actual_html_files != expected_html_files:
        missing = sorted(expected_html_files - actual_html_files)
        extra = sorted(actual_html_files - expected_html_files)
        details = []
        if missing:
            details.append(f"missing html: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected html: {', '.join(extra)}")
        raise BuildError(
            "Validate output",
            "generated HTML files do not match the published page registry"
            + (" (" + "; ".join(details) + ")" if details else ""),
            path=staging_dir,
        )

    if [page.route for page in published_pages] != parsed_manifest.get("generated_routes", []):
        raise BuildError("Validate output", "manifest routes do not match the published registry", path=manifest_path)
    if [page.id for page in published_pages] != parsed_manifest.get("published_page_ids", []):
        raise BuildError("Validate output", "manifest published page ids are incorrect", path=manifest_path)
    if [page.id for page in registry.pages] != parsed_manifest.get("registered_page_ids", []):
        raise BuildError("Validate output", "manifest registered page ids are incorrect", path=manifest_path)
    if parsed_manifest.get("published_page_count") != len(published_pages):
        raise BuildError("Validate output", "manifest published page count is incorrect", path=manifest_path)
    if parsed_manifest.get("draft_page_count") != len(draft_pages):
        raise BuildError("Validate output", "manifest draft page count is incorrect", path=manifest_path)
    if parsed_manifest.get("registered_page_count") != len(registry.pages):
        raise BuildError("Validate output", "manifest registered page count is incorrect", path=manifest_path)

    if parsed_manifest.get("public_registry_output_file") != "dist/page-registry.json":
        raise BuildError("Validate output", "manifest public registry output file is incorrect", path=manifest_path)
    if parsed_manifest.get("public_navigation_output_file") != "dist/navigation.json":
        raise BuildError("Validate output", "manifest public navigation output file is incorrect", path=manifest_path)

    public_registry_pages = parsed_registry.get("pages")
    if not isinstance(public_registry_pages, list):
        raise BuildError("Validate output", "public registry pages must be an array", path=registry_path)
    if len(public_registry_pages) != len(published_pages):
        raise BuildError("Validate output", "public registry must only include published pages", path=registry_path)
    if [page.id for page in published_pages] != [page_data.get("id") for page_data in public_registry_pages]:
        raise BuildError("Validate output", "public registry page ids are incorrect", path=registry_path)
    if any(page_data.get("status") != "published" for page_data in public_registry_pages):
        raise BuildError("Validate output", "public registry contains a non-published page", path=registry_path)

    if parsed_navigation != public_navigation:
        raise BuildError("Validate output", "navigation output changed unexpectedly", path=navigation_path)
    if parsed_navigation.get("version") != navigation.version:
        raise BuildError("Validate output", "navigation version is incorrect", path=navigation_path)

    navigation_sections = parsed_navigation.get("sections")
    if not isinstance(navigation_sections, list):
        raise BuildError("Validate output", "navigation sections must be an array", path=navigation_path)
    if [section.id for section in navigation.sections] != [section_data.get("id") for section_data in navigation_sections]:
        raise BuildError("Validate output", "navigation section ids are incorrect", path=navigation_path)

    navigation_page_ids = {page.id for page in published_pages if page.navigation}
    expected_navigation_ids = {section.id for section in navigation.sections}
    if navigation_page_ids != expected_navigation_ids:
        raise BuildError("Validate output", "navigation does not reference the published section pages", path=navigation_path)

    for json_payload, label in (
        (parsed_manifest, "build-manifest.json"),
        (parsed_registry, "page-registry.json"),
        (parsed_navigation, "navigation.json"),
    ):
        if contains_absolute_filesystem_path(json_payload):
            raise BuildError("Validate output", f"{label} contains an absolute filesystem path", path=staging_dir)

    for relative_path in parsed_manifest.get("generated_output_files", []):
        output_path = staging_dir / Path(relative_path).relative_to("dist")
        resolved_output = output_path.resolve(strict=False)
        resolved_dist = staging_dir.resolve(strict=False)
        if resolved_dist != resolved_output and resolved_dist not in resolved_output.parents:
            raise BuildError("Validate output", f"generated output escapes dist/: {relative_path}", path=staging_dir)
        if not output_path.exists():
            raise BuildError("Validate output", f"generated output is missing: {relative_path}", path=staging_dir)

    if draft_pages:
        for draft_page in draft_pages:
            draft_output_path = route_to_output_path(draft_page.route, staging_dir)
            if draft_output_path.exists():
                raise BuildError(
                    "Validate output",
                    f"draft page unexpectedly generated HTML: {draft_page.route}",
                    path=draft_output_path,
                )


def contains_absolute_filesystem_path(payload: Any) -> bool:
    if isinstance(payload, dict):
        return any(contains_absolute_filesystem_path(value) for value in payload.values())
    if isinstance(payload, list):
        return any(contains_absolute_filesystem_path(item) for item in payload)
    if isinstance(payload, str):
        return payload.startswith("/Users/") or payload.startswith("/private/") or payload.startswith("/var/") or payload.startswith("/tmp/")
    return False


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
    data_dir = repo_root / "data"
    dist_dir = repo_root / "dist"
    temp_root = Path(tempfile.mkdtemp(prefix=".phase3-build-", dir=repo_root))

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
        if not data_dir.is_dir():
            raise BuildError("Validate environment", "data/ directory does not exist", path=data_dir)

        stage_logger(2, TOTAL_STAGES, "Load navigation data")
        navigation = load_navigation(data_dir)

        stage_logger(3, TOTAL_STAGES, "Load page registry")
        registry = load_page_registry(data_dir)

        stage_logger(4, TOTAL_STAGES, "Validate registered sources")
        page_paths = discover_page_sources(pages_dir)
        if not page_paths:
            raise BuildError("Validate registered sources", "no page sources were found", path=pages_dir)
        discovered_source_paths = {path.relative_to(repo_root).as_posix() for path in page_paths}
        expected_source_paths = set(registry.source_files())
        if discovered_source_paths != expected_source_paths:
            missing = sorted(expected_source_paths - discovered_source_paths)
            extra = sorted(discovered_source_paths - expected_source_paths)
            details = []
            if missing:
                details.append(f"missing sources: {', '.join(missing)}")
            if extra:
                details.append(f"unregistered sources: {', '.join(extra)}")
            raise BuildError(
                "Validate registered sources",
                "page source files do not match the page registry"
                + (" (" + "; ".join(details) + ")" if details else ""),
                path=pages_dir,
            )

        stage_logger(5, TOTAL_STAGES, "Parse page sources")
        parsed_sources = [parse_page_source(page_path) for page_path in page_paths]
        parsed_sources_by_id = {source.registry_id: source for source in parsed_sources}
        if len(parsed_sources_by_id) != len(parsed_sources):
            raise BuildError("Parse page sources", "duplicate registry_id values were found", path=pages_dir)

        for page in registry.pages:
            source = parsed_sources_by_id.get(page.id)
            if source is None:
                raise BuildError(
                    "Parse page sources",
                    f"missing page source for registry entry {page.id}",
                    source_file=page.source,
                    page_id=page.id,
                )
            if source.source_path.relative_to(repo_root).as_posix() != page.source:
                raise BuildError(
                    "Parse page sources",
                    f"page source path must be {page.source}",
                    source_file=source.source_path,
                    page_id=page.id,
                )

        validate_page_sources_against_registry(page_paths, parsed_sources, registry, repo_root)

        staging_dir = temp_root
        published_pages = list(registry.published_pages())
        draft_pages = list(registry.draft_pages())
        generated_routes: list[str] = []
        generated_output_files: list[str] = []

        stage_logger(6, TOTAL_STAGES, "Render published pages")
        for page in published_pages:
            source = parsed_sources_by_id[page.id]
            output_path = route_to_output_path(page.route, staging_dir)
            rendered_markdown = render_markdown(source.body_markdown, source_path=source.source_path)
            html_document = render_html_document(page, rendered_markdown)
            write_text(output_path, html_document)
            generated_routes.append(page.route)
            generated_output_files.append(f"dist/{output_path.relative_to(staging_dir).as_posix()}")

        stage_logger(7, TOTAL_STAGES, "Copy approved assets")
        copied_asset_count, copied_asset_files = copy_approved_assets(assets_dir, staging_dir)
        generated_output_files.extend(copied_asset_files)

        stage_logger(8, TOTAL_STAGES, "Write public data and manifest")
        public_registry = build_public_registry_data(registry)
        public_navigation = build_public_navigation_data(navigation)
        public_registry_path = staging_dir / "page-registry.json"
        public_navigation_path = staging_dir / "navigation.json"
        write_json(public_registry_path, public_registry)
        write_json(public_navigation_path, public_navigation)

        source_page_files = [page.source for page in registry.pages]
        manifest = build_manifest(
            registry=registry,
            navigation=navigation,
            published_pages=published_pages,
            draft_pages=draft_pages,
            generated_routes=generated_routes,
            generated_output_files=sorted(
                generated_output_files
                + [
                    "dist/build-manifest.json",
                    "dist/page-registry.json",
                    "dist/navigation.json",
                ]
            ),
            copied_asset_count=copied_asset_count,
            source_page_files=source_page_files,
            public_registry_output_file="dist/page-registry.json",
            public_navigation_output_file="dist/navigation.json",
        )
        write_json(staging_dir / "build-manifest.json", manifest)

        stage_logger(9, TOTAL_STAGES, "Validate generated output")
        validate_generated_output(
            staging_dir,
            manifest,
            registry,
            navigation,
            public_registry,
            public_navigation,
        )

        stage_logger(10, TOTAL_STAGES, "Publish dist" if not check_only else "Skip dist publication (--check)")
        if not check_only:
            publish_output(staging_dir, dist_dir)
            output_dir = dist_dir
        else:
            cleanup_temp_dir(staging_dir)
            output_dir = staging_dir

        return BuildSummary(
            page_count=len(published_pages),
            asset_count=copied_asset_count,
            route_count=len(generated_routes),
            output_dir=output_dir,
            generated_routes=generated_routes,
            generated_output_files=sorted(generated_output_files),
            source_page_files=source_page_files,
        )
    except Exception:
        cleanup_temp_dir(temp_root)
        raise
