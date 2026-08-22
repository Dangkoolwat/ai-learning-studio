"""Tests for core.page_registry loading and validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.errors import BuildError
from core.page_registry import derive_route_from_source, load_page_registry

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_DATA_DIR = REPO_ROOT / "data"


def _write_registry_dir(payload: object) -> tuple[Path, tempfile.TemporaryDirectory]:
    tmp = tempfile.TemporaryDirectory()
    data_dir = Path(tmp.name)
    (data_dir / "page-registry.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return data_dir, tmp


def _minimal_page(**overrides: object) -> dict[str, object]:
    page: dict[str, object] = {
        "id": "test-page",
        "title": "테스트 페이지",
        "description": "테스트용 페이지 설명",
        "route": "/test-page/",
        "source": "pages/sections/test-page.md",
        "type": "static-prompt",
        "section": "test-section",
        "order": 1,
        "navigation": True,
        "status": "published",
        "lang": "ko",
    }
    page.update(overrides)
    return page


class DeriveRouteTests(unittest.TestCase):
    def test_index_maps_to_root(self) -> None:
        self.assertEqual(derive_route_from_source("pages/index.md"), "/")

    def test_section_landing_maps_without_sections_prefix(self) -> None:
        self.assertEqual(
            derive_route_from_source("pages/sections/ai-practice.md"), "/ai-practice/"
        )

    def test_nested_page_maps_two_levels(self) -> None:
        self.assertEqual(
            derive_route_from_source("pages/sections/ai-practice/summer-vacation-basic.md"),
            "/ai-practice/summer-vacation-basic/",
        )


class LoadPageRegistryRealDataTests(unittest.TestCase):
    def test_real_registry_loads(self) -> None:
        registry = load_page_registry(REAL_DATA_DIR)
        self.assertGreaterEqual(len(registry.pages), 1)
        ids = [page.id for page in registry.pages]
        self.assertEqual(len(ids), len(set(ids)))
        routes = [page.route for page in registry.pages]
        self.assertEqual(len(routes), len(set(routes)))
        for page in registry.pages:
            self.assertEqual(page.route, derive_route_from_source(page.source))


class LoadPageRegistryValidationTests(unittest.TestCase):
    def _assert_load_error(self, payload: object, expected_fragment: str) -> None:
        data_dir, tmp = _write_registry_dir(payload)
        try:
            with self.assertRaises(BuildError) as ctx:
                load_page_registry(data_dir)
        finally:
            tmp.cleanup()
        self.assertIn(expected_fragment, str(ctx.exception))

    def test_missing_file_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(BuildError):
                load_page_registry(Path(tmp))

    def test_wrong_version_raises(self) -> None:
        self._assert_load_error({"version": 2, "pages": []}, "version must be 1")

    def test_empty_pages_raises(self) -> None:
        self._assert_load_error({"version": 1, "pages": []}, "at least one page")

    def test_duplicate_page_id_raises(self) -> None:
        payload = {"version": 1, "pages": [_minimal_page(), _minimal_page(order=2)]}
        self._assert_load_error(payload, "duplicate page id")

    def test_duplicate_source_raises(self) -> None:
        other = _minimal_page(id="other-page", order=2)
        payload = {"version": 1, "pages": [_minimal_page(), other]}
        self._assert_load_error(payload, "duplicate page source")

    def test_route_must_match_source(self) -> None:
        page = _minimal_page(route="/wrong-path/")
        self._assert_load_error({"version": 1, "pages": [page]}, "does not match the route derived")

    def test_source_must_stay_under_pages(self) -> None:
        page = _minimal_page(source="../outside/page.md")
        self._assert_load_error({"version": 1, "pages": [page]}, "repository-relative")

    def test_source_must_be_markdown(self) -> None:
        page = _minimal_page(source="pages/sections/test-page.html")
        self._assert_load_error({"version": 1, "pages": [page]}, "repository-relative")

    def test_unknown_type_raises(self) -> None:
        page = _minimal_page(type="unknown-type")
        self._assert_load_error({"version": 1, "pages": [page]}, "page type must be one of")

    def test_navigation_must_be_bool(self) -> None:
        page = _minimal_page(navigation="yes")
        self._assert_load_error({"version": 1, "pages": [page]}, "must be a boolean")

    def test_order_must_be_non_negative_int(self) -> None:
        page = _minimal_page(order=-1)
        self._assert_load_error({"version": 1, "pages": [page]}, "non-negative integer")

    def test_invalid_status_raises(self) -> None:
        page = _minimal_page(status="archived")
        self._assert_load_error({"version": 1, "pages": [page]}, "page status must be one of")

    def test_missing_key_raises(self) -> None:
        page = _minimal_page()
        del page["lang"]
        self._assert_load_error({"version": 1, "pages": [page]}, "missing keys")


if __name__ == "__main__":
    unittest.main()
