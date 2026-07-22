"""Theme data models for AI Learning Studio."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


THEME_SOURCE_FILENAME = "design.md"
THEME_CATEGORY_ORDER = (
    "colors",
    "typography",
    "spacing",
    "radius",
    "shadow",
    "layout",
)
THEME_SECTION_ORDER = ("Colors", "Typography", "Spacing", "Radius", "Shadow", "Layout")


@dataclass(slots=True, frozen=True)
class ThemeToken:
    """A normalized token value ready for JSON and CSS generation."""

    category: str
    name: str
    value: str
    css_variable: str


@dataclass(slots=True)
class ThemeDesign:
    """A fully validated human-authored theme design."""

    id: str
    name: str
    description: str
    version: int
    status: str
    lang: str
    source_path: Path
    tokens_by_category: dict[str, tuple[ThemeToken, ...]]

    def token_count(self) -> int:
        return sum(len(tokens) for tokens in self.tokens_by_category.values())

    def categories(self) -> tuple[str, ...]:
        return tuple(self.tokens_by_category.keys())

    def tokens(self) -> tuple[ThemeToken, ...]:
        ordered_tokens: list[ThemeToken] = []
        for category in THEME_CATEGORY_ORDER:
            ordered_tokens.extend(self.tokens_by_category.get(category, ()))
        return tuple(ordered_tokens)

    def to_tokens_payload(self) -> dict[str, object]:
        return {
            "theme": {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "status": self.status,
                "lang": self.lang,
            },
            "tokens": {
                category: {
                    token.name: {
                        "value": token.value,
                        "css_variable": token.css_variable,
                    }
                    for token in self.tokens_by_category.get(category, ())
                }
                for category in THEME_CATEGORY_ORDER
            },
        }

    def to_manifest_payload(self, source_relative_path: str) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "status": self.status,
            "lang": self.lang,
            "source": source_relative_path,
            "files": {
                "tokens": f"themes/{self.id}/tokens.json",
                "style": f"themes/{self.id}/style.css",
                "manifest": f"themes/{self.id}/manifest.json",
            },
            "token_count": self.token_count(),
            "categories": list(self.categories()),
        }


@dataclass(slots=True, frozen=True)
class ThemeRegistryEntry:
    """A public theme registry entry."""

    id: str
    name: str
    description: str
    version: int
    status: str
    lang: str
    manifest: str
    tokens: str
    style: str

    def to_public_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "status": self.status,
            "lang": self.lang,
            "manifest": self.manifest,
            "tokens": self.tokens,
            "style": self.style,
        }


@dataclass(slots=True)
class ThemeRegistry:
    """The generated public themes registry."""

    version: int
    active_theme: str
    themes: tuple[ThemeRegistryEntry, ...]

    def to_public_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "active_theme": self.active_theme,
            "themes": [theme.to_public_dict() for theme in self.themes],
        }

    def theme_by_id(self, theme_id: str) -> ThemeRegistryEntry:
        for theme in self.themes:
            if theme.id == theme_id:
                return theme
        raise KeyError(theme_id)


@dataclass(slots=True)
class ThemeGenerationResult:
    """Details about generated theme files."""

    registry: ThemeRegistry
    discovered_theme_count: int
    active_theme_id: str
    generated_theme_ids: tuple[str, ...]
    generated_theme_files: tuple[str, ...]
    total_theme_token_count: int
    theme_source_files: tuple[str, ...]
    public_registry_output_file: str
