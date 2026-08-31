"""Tests for prompt audit script (scripts/audit_prompts.py).

Verifies both success path on the real repository and failure paths
(empty preview, missing image, empty source, description mismatch, oversized image,
disallowed option keywords) using temporary directory fixtures.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.audit_prompts import (
    MAX_IMAGE_SIZE_BYTES,
    audit_images,
    audit_prompts,
    audit_three_way_consistency,
    run_audit,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


class AuditPromptsRealRepoTests(unittest.TestCase):
    def test_real_repo_passes_strictly(self) -> None:
        """Ensure the active codebase passes all prompt audits with zero errors and zero warnings."""
        issues, prompt_count, img_count = run_audit(REPO_ROOT, strict=True)
        self.assertGreater(prompt_count, 0, "Should audit multiple markdown prompt pages.")
        self.assertGreater(img_count, 0, "Should audit multiple image assets.")
        errors = [i for i in issues if i.severity == "ERROR"]
        warnings = [i for i in issues if i.severity == "WARNING"]
        self.assertEqual(errors, [], f"Expected 0 errors on real repo, got: {errors}")
        self.assertEqual(warnings, [], f"Expected 0 warnings on real repo, got: {warnings}")


class AuditPromptsFailurePathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.pages_dir = self.base_dir / "pages"
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir = self.base_dir / "assets" / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_empty_preview_fails(self) -> None:
        """Empty preview: key in frontmatter must produce EMPTY_PREVIEW error."""
        md_file = self.pages_dir / "test.md"
        md_file.write_text(
            "---\ntitle: Test\ndescription: Desc\npreview:\n---\n# Title\nBody\n",
            encoding="utf-8",
        )
        issues = []
        audit_prompts(issues, base_dir=self.base_dir)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("EMPTY_PREVIEW", issue_types)

    def test_missing_preview_image_fails(self) -> None:
        """Non-existent preview image path must produce MISSING_PREVIEW_IMAGE error."""
        md_file = self.pages_dir / "test.md"
        md_file.write_text(
            "---\ntitle: Test\ndescription: Desc\npreview: /assets/images/nonexistent.webp\n---\n# Title\nBody\n",
            encoding="utf-8",
        )
        issues = []
        audit_prompts(issues, base_dir=self.base_dir)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("MISSING_PREVIEW_IMAGE", issue_types)

    def test_empty_source_fails(self) -> None:
        """Empty source: key in frontmatter must produce EMPTY_SOURCE error."""
        md_file = self.pages_dir / "test.md"
        md_file.write_text(
            "---\ntitle: Test\ndescription: Desc\nsource:\n---\n# Title\nBody\n",
            encoding="utf-8",
        )
        issues = []
        audit_prompts(issues, base_dir=self.base_dir)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("EMPTY_SOURCE", issue_types)

    def test_oversized_image_fails(self) -> None:
        """Image file exceeding 1MB must produce IMAGE_OVERSIZED error."""
        huge_img = self.images_dir / "huge.webp"
        huge_img.write_bytes(b"\x00" * (MAX_IMAGE_SIZE_BYTES + 2048))
        issues = []
        audit_images(issues, base_dir=self.base_dir)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("IMAGE_OVERSIZED", issue_types)

    def test_disallowed_dropdown_keyword_fails(self) -> None:
        """Dropdown option ending with / 직접 입력 or / 자유 입력 must produce DISALLOWED_OPTION_KEYWORD error."""
        md_file = self.pages_dir / "test.md"
        md_file.write_text(
            "---\ntitle: Test\ndescription: Desc\n---\n# Title\n- 옵션: [옵션1 / 옵션2 / 직접 입력]\n",
            encoding="utf-8",
        )
        issues = []
        audit_prompts(issues, base_dir=self.base_dir)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("DISALLOWED_OPTION_KEYWORD", issue_types)

    def test_section_headers_not_flagged_as_unquoted_chips(self) -> None:
        """Legitimate section headers like [작성 지침], [반드시 확인하세요] must NOT produce warnings."""
        md_file = self.pages_dir / "test.md"
        md_file.write_text(
            "---\ntitle: Test\ndescription: Desc\n---\n# Title\n[작성 지침]\n\n[반드시 확인하세요]\n",
            encoding="utf-8",
        )
        issues = []
        audit_prompts(issues, base_dir=self.base_dir)
        warnings = [i for i in issues if i.severity == "WARNING"]
        self.assertEqual(warnings, [])

    def test_description_mismatch_fails(self) -> None:
        """Markdown description mismatch with page-registry.json must produce DESCRIPTION_MISMATCH error."""
        # 1. Setup valid navigation.json (matching page-registry description)
        nav_json = self.data_dir / "navigation.json"
        nav_json.write_text(
            '{"version": 1, "sections": [{"id": "s1", "label": "S1", "description": "D1", "order": 1, "items": [{"id": "p1", "label": "P1", "description": "Reg Desc", "route": "/test/"}]}]}',
            encoding="utf-8",
        )
        # 2. Setup page-registry.json with section landing and page p1
        reg_json = self.data_dir / "page-registry.json"
        reg_json.write_text(
            '{"version": 1, "pages": ['
            '{"id": "s1", "title": "S1", "description": "D1", "route": "/s1/", "source": "pages/s1.md", "type": "static-prompt", "section": "s1", "order": 1, "navigation": false, "status": "published", "lang": "ko"},'
            '{"id": "p1", "title": "P1", "description": "Reg Desc", "route": "/test/", "source": "pages/test.md", "type": "static-prompt", "section": "s1", "order": 2, "navigation": true, "status": "published", "lang": "ko"}'
            ']}',
            encoding="utf-8",
        )
        # 3. Setup pages/s1.md and pages/test.md (test.md has conflicting description 'MD Desc')
        (self.pages_dir / "s1.md").write_text("---\ntitle: S1\ndescription: D1\n---\n# S1\n", encoding="utf-8")
        (self.pages_dir / "test.md").write_text("---\ntitle: P1\ndescription: MD Desc\n---\n# Title\nBody\n", encoding="utf-8")

        issues = []
        audit_three_way_consistency(issues, base_dir=self.base_dir)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("DESCRIPTION_MISMATCH", issue_types)

    def test_data_consistency_error_fails(self) -> None:
        """Broken navigation/registry consistency must produce DATA_CONSISTENCY_ERROR."""
        # Navigation references route /test/ which is NOT in page-registry
        nav_json = self.data_dir / "navigation.json"
        nav_json.write_text(
            '{"version": 1, "sections": [{"id": "s1", "label": "S1", "description": "D1", "order": 1, "items": [{"id": "p1", "label": "P1", "description": "D1", "route": "/missing/"}]}]}',
            encoding="utf-8",
        )
        reg_json = self.data_dir / "page-registry.json"
        reg_json.write_text(
            '{"version": 1, "pages": [{"id": "p1", "title": "P1", "description": "D1", "route": "/test/", "source": "pages/test.md", "type": "static-prompt", "section": "s1", "order": 1, "navigation": true, "status": "published", "lang": "ko"}]}',
            encoding="utf-8",
        )
        issues = []
        audit_three_way_consistency(issues, base_dir=self.base_dir)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("DATA_CONSISTENCY_ERROR", issue_types)

    def test_unquoted_free_input_slot_produces_warning(self) -> None:
        """Free text input slot without quotes (e.g. - 항목: [직접 입력]) must produce UNQUOTED_FREE_INPUT_SLOT warning."""
        md_file = self.pages_dir / "test.md"
        md_file.write_text(
            "---\ntitle: Test\ndescription: Desc\n---\n# Title\n- 메뉴명: [직접 입력]\n",
            encoding="utf-8",
        )
        issues = []
        audit_prompts(issues, base_dir=self.base_dir)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("UNQUOTED_FREE_INPUT_SLOT", issue_types)

    def test_quoted_free_input_slot_passes(self) -> None:
        """Properly quoted free text slot (e.g. - 메뉴명: \"[직접 입력]\") must NOT produce warning."""
        md_file = self.pages_dir / "test.md"
        md_file.write_text(
            "---\ntitle: Test\ndescription: Desc\n---\n# Title\n- 메뉴명: \"[직접 입력]\"\n",
            encoding="utf-8",
        )
        issues = []
        audit_prompts(issues, base_dir=self.base_dir)
        warnings = [i for i in issues if i.severity == "WARNING"]
        self.assertEqual(warnings, [])

    def test_non_standard_list_marker_in_prompt_block_produces_warning(self) -> None:
        """Using '* ' marker inside ```prompt block must produce NON_STANDARD_LIST_MARKER warning."""
        md_file = self.pages_dir / "test.md"
        md_file.write_text(
            "---\ntitle: Test\ndescription: Desc\n---\n# Title\n```prompt\ntitle: T\n---\n* 항목 1\n* 항목 2\n```\n",
            encoding="utf-8",
        )
        issues = []
        audit_prompts(issues, base_dir=self.base_dir)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("NON_STANDARD_LIST_MARKER", issue_types)


if __name__ == "__main__":
    unittest.main()
