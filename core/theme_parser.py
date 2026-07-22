"""Theme discovery helpers for AI Learning Studio."""

from __future__ import annotations

from pathlib import Path

from core.errors import BuildError
from core.theme_models import THEME_SOURCE_FILENAME, ThemeDesign
from core.theme_validation import parse_theme_design


def discover_theme_design_paths(design_dir: Path) -> list[Path]:
    if not design_dir.is_dir():
        raise BuildError(
            "Discover themes",
            "design/ directory does not exist",
            path=design_dir,
        )

    theme_design_paths: list[Path] = []
    for child in sorted(design_dir.iterdir()):
        if child.name.startswith("."):
            continue
        if not child.is_dir():
            continue

        direct_design_path = child / THEME_SOURCE_FILENAME
        nested_design_paths = [
            path
            for path in child.rglob(THEME_SOURCE_FILENAME)
            if path.parent != child
        ]
        if nested_design_paths:
            raise BuildError(
                "Discover themes",
                "nested theme directories are not allowed",
                path=child,
                theme_id=child.name,
            )

        if direct_design_path.is_file():
            theme_design_paths.append(direct_design_path)
            continue

        if any(not entry.name.startswith(".") for entry in child.iterdir()):
            raise BuildError(
                "Discover themes",
                "theme directory is missing design.md",
                path=child,
                theme_id=child.name,
            )

    if not theme_design_paths:
        raise BuildError(
            "Discover themes",
            "no theme found",
            path=design_dir,
        )

    return theme_design_paths


def load_theme_designs(design_dir: Path) -> list[ThemeDesign]:
    theme_design_paths = discover_theme_design_paths(design_dir)
    return [parse_theme_design(theme_path) for theme_path in theme_design_paths]
