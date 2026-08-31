#!/usr/bin/env python3
"""Prompt audit and health check script for AI Learning Studio.

Audits markdown prompt files, frontmatter consistency, asset references,
3-way title/description synchronization, and prompt authoring rules.
Reuses core domain modules for cross-file data consistency checks.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Add project root to sys.path to enable core imports
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.data_consistency import validate_navigation_registry_consistency  # noqa: E402
from core.errors import BuildError  # noqa: E402
from core.navigation import load_navigation  # noqa: E402
from core.page_registry import load_page_registry  # noqa: E402
from core.renderers.static_prompt import _is_section_header  # noqa: E402

PAGES_DIR = REPO_ROOT / "pages"
DATA_DIR = REPO_ROOT / "data"
ASSETS_IMAGES_DIR = REPO_ROOT / "assets" / "images"

MAX_IMAGE_SIZE_BYTES = 1024 * 1024  # 1MB
MARKDOWN_IMAGE_RE = re.compile(r"!\[.*?\]\((/assets/images/[^)\s]+)")
STANDALONE_BRACKET_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")
DISALLOWED_DROPDOWN_OPTION_RE = re.compile(r"\[[^\]]*[/|]\s*(?:자유\s*입력|직접\s*입력)\s*\]")


@dataclass
class AuditIssue:
    file_path: str
    issue_type: str
    message: str
    severity: str = "ERROR"  # "ERROR" or "WARNING"


def parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Extract frontmatter and body from markdown content."""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    front_text = parts[1]
    body = parts[2]
    meta: dict[str, str] = {}
    for line in front_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip()
    return meta, body


def audit_images(issues: list[AuditIssue], base_dir: Path = REPO_ROOT) -> int:
    """Check image sizes and formats."""
    checked = 0
    images_dir = base_dir / "assets" / "images"
    if not images_dir.exists():
        return checked

    for img_path in sorted(images_dir.rglob("*")):
        if not img_path.is_file() or img_path.name.startswith("."):
            continue
        checked += 1
        suffix = img_path.suffix.lower()
        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
            size = img_path.stat().st_size
            if size > MAX_IMAGE_SIZE_BYTES:
                issues.append(
                    AuditIssue(
                        file_path=str(img_path.relative_to(base_dir)),
                        issue_type="IMAGE_OVERSIZED",
                        message=f"Image size {size / 1024:.1f}KB exceeds 1MB limit.",
                    )
                )
    return checked


def audit_prompts(issues: list[AuditIssue], base_dir: Path = REPO_ROOT) -> int:
    """Audit markdown prompt frontmatter, rules, and image references."""
    checked = 0
    pages_dir = base_dir / "pages"
    if not pages_dir.exists():
        return checked

    for md_path in sorted(pages_dir.rglob("*.md")):
        checked += 1
        rel_path = str(md_path.relative_to(base_dir))
        content = md_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(content)

        # 1. Check preview images
        if "preview" in meta:
            raw_preview = meta["preview"]
            if not raw_preview:
                issues.append(
                    AuditIssue(
                        file_path=rel_path,
                        issue_type="EMPTY_PREVIEW",
                        message="Frontmatter 'preview:' key exists but is empty.",
                    )
                )
            else:
                entries = [item.strip() for item in raw_preview.split(",") if item.strip()]
                for entry in entries:
                    clean_path = entry.lstrip("/")
                    disk_path = base_dir / clean_path
                    if not disk_path.exists():
                        issues.append(
                            AuditIssue(
                                file_path=rel_path,
                                issue_type="MISSING_PREVIEW_IMAGE",
                                message=f"Preview image '{entry}' not found on disk at '{clean_path}'.",
                            )
                        )
                    elif not clean_path.lower().endswith(".webp") and not clean_path.lower().endswith(".svg"):
                        issues.append(
                            AuditIssue(
                                file_path=rel_path,
                                issue_type="NON_WEBP_PREVIEW",
                                message=f"Preview image '{entry}' should be WebP format.",
                                severity="WARNING",
                            )
                        )

        # 2. Check source field
        if "source" in meta and not meta["source"]:
            issues.append(
                AuditIssue(
                    file_path=rel_path,
                    issue_type="EMPTY_SOURCE",
                    message="Frontmatter 'source:' key exists but is empty.",
                )
            )

        # 3. Check inline markdown images
        for match in MARKDOWN_IMAGE_RE.finditer(body):
            img_src = match.group(1).split("#")[0].strip()
            clean_path = img_src.lstrip("/")
            disk_path = base_dir / clean_path
            if not disk_path.exists():
                issues.append(
                    AuditIssue(
                        file_path=rel_path,
                        issue_type="MISSING_INLINE_IMAGE",
                        message=f"Inline image '{img_src}' not found on disk at '{clean_path}'.",
                    )
                )

        # 4. Check prompt authoring rules
        in_prompt_block = False
        for line_no, line in enumerate(body.splitlines(), start=1):
            line_stripped = line.strip()

            if line_stripped.startswith("```prompt"):
                in_prompt_block = True
                continue
            elif in_prompt_block and line_stripped.startswith("```"):
                in_prompt_block = False
                continue

            # Check disallowed placeholder option keywords at the end of dropdown choices
            if DISALLOWED_DROPDOWN_OPTION_RE.search(line):
                issues.append(
                    AuditIssue(
                        file_path=f"{rel_path}:{line_no}",
                        issue_type="DISALLOWED_OPTION_KEYWORD",
                        message="Disallowed placeholder option keyword ('직접 입력'/'자유 입력') found in dropdown options. Use verified presets.",
                    )
                )

            # Check standalone unquoted chips while correctly excluding genuine section headers
            m = STANDALONE_BRACKET_RE.match(line_stripped)
            if m and not line_stripped.startswith("#"):
                bracket_content = m.group(1).strip()
                full_match_str = f"[{bracket_content}]"
                # If it is NOT a section header, it's an unquoted chip that should be quoted
                if not _is_section_header(line_stripped, full_match_str, bracket_content):
                    issues.append(
                        AuditIssue(
                            file_path=f"{rel_path}:{line_no}",
                            issue_type="STANDALONE_UNQUOTED_CHIP",
                            message=f"Standalone bracket chip '[{bracket_content}]' should be enclosed in quotes (e.g. \"[{bracket_content}]\").",
                            severity="WARNING",
                        )
                    )

            # Check unquoted free text input slot in list items (e.g. "- 항목: [직접 입력]" without quotes)
            # Free text input slots (containing keywords like '입력', '작성', '붙여넣기') require quotes: "- 항목: \"[직접 입력]\""
            if line_stripped.startswith("- ") and ":" in line_stripped:
                key_part, val_part = line_stripped.split(":", 1)
                val_trimmed = val_part.strip()
                if val_trimmed.startswith("[") and val_trimmed.endswith("]") and not val_trimmed.startswith("[["):
                    inner = val_trimmed[1:-1].strip()
                    if "/" not in inner and "|" not in inner:
                        # Only flag if it represents a free text placeholder
                        if any(kw in inner for kw in ("입력", "작성", "붙여넣기", "자유", "내용을", "텍스트")):
                            issues.append(
                                AuditIssue(
                                    file_path=f"{rel_path}:{line_no}",
                                    issue_type="UNQUOTED_FREE_INPUT_SLOT",
                                    message=f"Free text input slot '{val_trimmed}' should be enclosed in quotes (e.g. \"{val_trimmed}\").",
                                    severity="WARNING",
                                )
                            )

            # Check non-standard list markers within prompt blocks (e.g. '* ' instead of '- ')
            if in_prompt_block and line_stripped.startswith("* "):
                issues.append(
                    AuditIssue(
                        file_path=f"{rel_path}:{line_no}",
                        issue_type="NON_STANDARD_LIST_MARKER",
                        message="Use '- ' instead of '* ' for list markers inside prompt blocks.",
                        severity="WARNING",
                    )
                )
    return checked


def audit_three_way_consistency(issues: list[AuditIssue], base_dir: Path = REPO_ROOT) -> None:
    """Audit 3-way synchronization between markdown files, page-registry, and navigation.

    Reuses core data_consistency, page_registry, and navigation validation.
    """
    data_dir = base_dir / "data"
    if not data_dir.exists():
        issues.append(
            AuditIssue(
                file_path="data/",
                issue_type="MISSING_DATA_DIR",
                message="Data directory does not exist.",
            )
        )
        return

    try:
        navigation = load_navigation(data_dir)
        registry = load_page_registry(data_dir)
        validate_navigation_registry_consistency(navigation, registry)
    except BuildError as e:
        issues.append(
            AuditIssue(
                file_path=str(e.path or "data/"),
                issue_type="DATA_CONSISTENCY_ERROR",
                message=f"Data consistency validation failed: {e.message}",
            )
        )
        return

    # Check markdown frontmatter description vs page-registry description
    for page in registry.pages:
        src_path = base_dir / page.source
        if not src_path.exists():
            issues.append(
                AuditIssue(
                    file_path=str(page.source),
                    issue_type="MISSING_SOURCE_FILE",
                    message=f"Page '{page.id}' source file '{page.source}' not found.",
                )
            )
            continue

        content = src_path.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(content)
        if "description" in meta:
            md_desc = meta["description"].strip()
            reg_desc = page.description.strip()
            if md_desc != reg_desc:
                issues.append(
                    AuditIssue(
                        file_path=str(src_path.relative_to(base_dir)),
                        issue_type="DESCRIPTION_MISMATCH",
                        message=f"Markdown description does not match page-registry.json:\n  MD: '{md_desc}'\n  REG: '{reg_desc}'",
                    )
                )


def run_audit(base_dir: Path = REPO_ROOT, strict: bool = False) -> tuple[list[AuditIssue], int, int]:
    """Execute all audit checks and return (issues, prompt_count, image_count)."""
    issues: list[AuditIssue] = []
    img_count = audit_images(issues, base_dir=base_dir)
    prompt_count = audit_prompts(issues, base_dir=base_dir)
    audit_three_way_consistency(issues, base_dir=base_dir)
    return issues, prompt_count, img_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit prompt health and metadata consistency.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    args = parser.parse_args()

    print("[*] Auditing AI Learning Studio prompts and assets...")
    issues, prompt_count, img_count = run_audit(REPO_ROOT, strict=args.strict)

    errors = [i for i in issues if i.severity == "ERROR"]
    warnings = [i for i in issues if i.severity == "WARNING"]

    print(f"[*] Audited {prompt_count} markdown pages and {img_count} image assets.")

    if warnings:
        print(f"\n[!] Found {len(warnings)} warning(s):")
        for w in warnings:
            print(f"  [{w.issue_type}] {w.file_path}: {w.message}")

    if errors:
        print(f"\n[X] Found {len(errors)} error(s):")
        for e in errors:
            print(f"  [{e.issue_type}] {e.file_path}: {e.message}")
        print("\nAudit FAILED.")
        return 1

    if args.strict and warnings:
        print("\nAudit FAILED (strict mode enabled with warnings).")
        return 1

    print("\n[OK] All prompt audits passed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
