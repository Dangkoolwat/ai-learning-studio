"""Tests for cross-file consistency validation between navigation and registry."""

from __future__ import annotations

import unittest
from pathlib import Path

from core.data_consistency import validate_navigation_registry_consistency
from core.errors import BuildError
from core.navigation import NavigationData, NavigationSection, NavigationSubItem, load_navigation
from core.page_registry import PageRegistry, PageRegistryEntry, load_page_registry

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_DATA_DIR = REPO_ROOT / "data"


def _entry(**overrides: object) -> PageRegistryEntry:
    values: dict[str, object] = {
        "id": "section-a",
        "title": "섹션 A",
        "description": "섹션 A 설명",
        "route": "/section-a/",
        "source": "pages/sections/section-a.md",
        "type": "static-prompt",
        "section": "section-a",
        "order": 0,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    }
    values.update(overrides)
    return PageRegistryEntry(**values)  # type: ignore[arg-type]


def _item(item_id: str, label: str, description: str, route: str) -> NavigationSubItem:
    return NavigationSubItem(id=item_id, label=label, description=description, route=route)


def _nav(sections: list[NavigationSection]) -> NavigationData:
    return NavigationData(version=1, sections=tuple(sections))


class RealDataConsistencyTests(unittest.TestCase):
    def test_real_data_is_consistent(self) -> None:
        navigation = load_navigation(REAL_DATA_DIR)
        registry = load_page_registry(REAL_DATA_DIR)
        validate_navigation_registry_consistency(navigation, registry)


class SyntheticConsistencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.landing = _entry()
        self.child = _entry(
            id="section-a-child",
            title="자식 페이지",
            description="자식 설명",
            route="/section-a/child/",
            source="pages/sections/section-a/child.md",
            order=1,
        )
        self.registry = PageRegistry(version=1, pages=(self.landing, self.child))
        self.section = NavigationSection(
            id="section-a",
            label="섹션 A",
            description="섹션 A 설명",
            order=1,
            items=(
                _item("section-a-child", "자식 페이지", "자식 설명", "/section-a/child/"),
            ),
        )

    def test_consistent_data_passes(self) -> None:
        validate_navigation_registry_consistency(_nav([self.section]), self.registry)

    def test_label_mismatch_raises(self) -> None:
        section = NavigationSection(
            id="section-a",
            label="섹션 A",
            description="섹션 A 설명",
            order=1,
            items=(_item("section-a-child", "다른 라벨", "자식 설명", "/section-a/child/"),),
        )
        with self.assertRaises(BuildError) as ctx:
            validate_navigation_registry_consistency(_nav([section]), self.registry)
        self.assertIn("label", str(ctx.exception))

    def test_description_mismatch_raises(self) -> None:
        section = NavigationSection(
            id="section-a",
            label="섹션 A",
            description="섹션 A 설명",
            order=1,
            items=(_item("section-a-child", "자식 페이지", "다른 설명", "/section-a/child/"),),
        )
        with self.assertRaises(BuildError):
            validate_navigation_registry_consistency(_nav([section]), self.registry)

    def test_route_mismatch_raises(self) -> None:
        section = NavigationSection(
            id="section-a",
            label="섹션 A",
            description="섹션 A 설명",
            order=1,
            items=(_item("section-a-child", "자식 페이지", "자식 설명","/다른-경로/"),),
        )
        with self.assertRaises(BuildError):
            validate_navigation_registry_consistency(_nav([section]), self.registry)

    def test_item_missing_from_registry_raises(self) -> None:
        empty_registry = PageRegistry(version=1, pages=(self.landing,))
        with self.assertRaises(BuildError) as ctx:
            validate_navigation_registry_consistency(_nav([self.section]), empty_registry)
        self.assertIn("does not exist in the page registry", str(ctx.exception))

    def test_section_without_pages_raises(self) -> None:
        orphan_section = NavigationSection(
            id="orphan", label="고아", description="고아 섹션", order=2, items=()
        )
        with self.assertRaises(BuildError) as ctx:
            validate_navigation_registry_consistency(_nav([orphan_section]), self.registry)
        self.assertIn("no registered pages", str(ctx.exception))

    def test_navigation_flagged_page_missing_from_nav_raises(self) -> None:
        hidden = _entry(
            id="hidden-page",
            title="숨김 페이지",
            description="숨김 설명",
            route="/section-a/hidden/",
            source="pages/sections/section-a/hidden.md",
            order=2,
        )
        registry = PageRegistry(version=1, pages=(self.landing, self.child, hidden))
        with self.assertRaises(BuildError) as ctx:
            validate_navigation_registry_consistency(_nav([self.section]), registry)
        self.assertIn("missing from navigation data", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
