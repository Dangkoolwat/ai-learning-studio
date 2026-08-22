"""Tests for core.navigation loading and validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.errors import BuildError
from core.navigation import load_navigation

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_DATA_DIR = REPO_ROOT / "data"


def _write_nav_dir(payload: object) -> tuple[Path, tempfile.TemporaryDirectory]:
    tmp = tempfile.TemporaryDirectory()
    data_dir = Path(tmp.name)
    (data_dir / "navigation.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return data_dir, tmp


def _minimal_item(**overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "id": "test-item",
        "label": "테스트 아이템",
        "description": "테스트용 아이템 설명",
        "route": "/test-section/test-item/",
    }
    item.update(overrides)
    return item


def _minimal_section(**overrides: object) -> dict[str, object]:
    section: dict[str, object] = {
        "id": "test-section",
        "label": "테스트 섹션",
        "description": "테스트용 섹션 설명",
        "order": 1,
        "items": [_minimal_item()],
    }
    section.update(overrides)
    return section


class LoadNavigationRealDataTests(unittest.TestCase):
    def test_real_navigation_loads(self) -> None:
        navigation = load_navigation(REAL_DATA_DIR)
        self.assertGreaterEqual(len(navigation.sections), 1)
        ids = [section.id for section in navigation.sections]
        self.assertEqual(len(ids), len(set(ids)))


class LoadNavigationValidationTests(unittest.TestCase):
    def _assert_load_error(self, payload: object, expected_fragment: str) -> None:
        data_dir, tmp = _write_nav_dir(payload)
        try:
            with self.assertRaises(BuildError) as ctx:
                load_navigation(data_dir)
        finally:
            tmp.cleanup()
        self.assertIn(expected_fragment, str(ctx.exception))

    def test_missing_file_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(BuildError):
                load_navigation(Path(tmp))

    def test_invalid_json_raises(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        (Path(tmp.name) / "navigation.json").write_text("{broken", encoding="utf-8")
        with self.assertRaises(BuildError):
            load_navigation(Path(tmp.name))

    def test_wrong_version_raises(self) -> None:
        self._assert_load_error({"version": 99, "sections": []}, "version must be 1")

    def test_sections_not_list_raises(self) -> None:
        self._assert_load_error({"version": 1, "sections": {}}, "must be a JSON array")

    def test_empty_sections_raises(self) -> None:
        self._assert_load_error({"version": 1, "sections": []}, "at least one section")

    def test_duplicate_section_id_raises(self) -> None:
        payload = {"version": 1, "sections": [_minimal_section(), _minimal_section()]}
        self._assert_load_error(payload, "duplicate navigation section id")

    def test_missing_section_key_raises(self) -> None:
        section = _minimal_section()
        del section["description"]
        self._assert_load_error({"version": 1, "sections": [section]}, "missing keys")

    def test_unexpected_section_key_raises(self) -> None:
        section = _minimal_section(extra="nope")
        self._assert_load_error({"version": 1, "sections": [section]}, "unexpected keys")

    def test_empty_label_raises(self) -> None:
        section = _minimal_section(label="")
        self._assert_load_error({"version": 1, "sections": [section]}, "non-empty string")

    def test_non_int_order_raises(self) -> None:
        section = _minimal_section(order="1")
        self._assert_load_error({"version": 1, "sections": [section]}, "must be an integer")

    def test_bool_order_raises(self) -> None:
        section = _minimal_section(order=True)
        self._assert_load_error({"version": 1, "sections": [section]}, "must be an integer")

    def test_duplicate_item_id_across_sections_raises(self) -> None:
        other = _minimal_section(id="other-section", order=2)
        payload = {"version": 1, "sections": [_minimal_section(), other]}
        self._assert_load_error(payload, "duplicate navigation sub-item id")

    def test_item_bad_route_shape_raises(self) -> None:
        section = _minimal_section(items=[_minimal_item(route="no-slash-path")])
        self._assert_load_error({"version": 1, "sections": [section]}, "directory path")


if __name__ == "__main__":
    unittest.main()
