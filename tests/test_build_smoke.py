"""Full-pipeline smoke test: validate and render without touching dist/."""

from __future__ import annotations

import unittest
from pathlib import Path

from core.build_pipeline import build_site

REPO_ROOT = Path(__file__).resolve().parent.parent


class BuildSmokeTests(unittest.TestCase):
    def test_check_only_build_passes(self) -> None:
        summary = build_site(REPO_ROOT, check_only=True)
        self.assertGreaterEqual(summary.page_count, 1)
        self.assertGreaterEqual(summary.route_count, 1)


if __name__ == "__main__":
    unittest.main()
