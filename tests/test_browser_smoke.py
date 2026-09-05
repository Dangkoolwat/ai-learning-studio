"""Browser smoke tests for AI Learning Studio core client-side interactions.

Verifies:
1. Chip option selection, live preview update, and clipboard synchronization.
2. Keyboard focus restoration to triggering chip on dropdown Escape.
3. Mobile drawer open/close toggle and ARIA state management.
"""

from functools import partial
import http.server
from pathlib import Path
import socketserver
import threading
import unittest

try:
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


@unittest.skipUnless(PLAYWRIGHT_AVAILABLE, "Playwright is not installed. Skipping browser smoke tests.")
class TestBrowserSmoke(unittest.TestCase):
    """End-to-end browser smoke test suite using Playwright."""

    server: socketserver.TCPServer
    server_thread: threading.Thread
    port: int
    dist_dir: Path

    @classmethod
    def setUpClass(cls) -> None:
        if not PLAYWRIGHT_AVAILABLE:
            return

        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.dist_dir = cls.repo_root / "dist"

        if not (cls.dist_dir / "index.html").exists():
            raise RuntimeError("dist/index.html not found. Run python3 scripts/build.py before running browser tests.")

        handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(cls.dist_dir))
        cls.server = socketserver.TCPServer(("127.0.0.1", 0), handler)
        cls.port = cls.server.server_address[1]

        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "server"):
            cls.server.shutdown()
            cls.server.server_close()

    def test_chip_preview_and_clipboard_sync(self) -> None:
        """Verify selecting chip option updates preview and copy button text."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
            page = context.new_page()

            page.goto(f"http://127.0.0.1:{self.port}/ai-practice/vacation-plan-basic/", wait_until="networkidle")

            # Locate first combo chip
            chip = page.locator(".itc[data-type='combo']").first
            chip.click()

            dropdown = page.locator(".itc-dropdown")
            dropdown.wait_for(state="visible", timeout=5000)
            self.assertTrue(dropdown.is_visible())

            # Select an option
            option_btn = page.locator(".itc-dropdown__option").nth(1)
            option_text = option_btn.text_content().strip()
            option_btn.click()

            # Verify dropdown closed and chip value updated
            dropdown.wait_for(state="detached", timeout=5000)
            self.assertFalse(dropdown.is_visible())
            self.assertIn(option_text, chip.text_content())

            prompt_item = chip.locator(
                "xpath=ancestor::*[contains(concat(' ', normalize-space(@class), ' '), ' prompt-item ')][1]"
            )

            # 1. Verify live preview text matches expected prompt
            preview_code = prompt_item.locator(".prompt-item__preview-code")
            expected_prompt = f"{option_text} 휴가 계획을 세워 줘."
            self.assertEqual(preview_code.text_content().strip(), expected_prompt)

            # 2. Click copy button
            copy_btn = prompt_item.locator("[data-prompt-copy]").first
            copy_btn.click()

            # 3. Wait for asynchronous copy success feedback ('복사되었습니다!')
            success_btn = prompt_item.locator("[data-prompt-copy]").filter(has_text="복사되었습니다!")
            success_btn.wait_for(state="visible", timeout=5000)
            self.assertTrue(success_btn.is_visible())
            btn_class = copy_btn.get_attribute("class") or ""
            self.assertIn("is-copied", btn_class)
            self.assertNotIn("is-copy-failed", btn_class)
            self.assertEqual(prompt_item.locator(".is-copy-failed").count(), 0)

            # 4. Verify actual clipboard content matches expected prompt text
            clipboard_text = page.evaluate("navigator.clipboard.readText()")
            self.assertEqual(clipboard_text.strip(), expected_prompt)

            browser.close()

    def test_dropdown_escape_focus_restoration(self) -> None:
        """Verify pressing Escape in dropdown restores keyboard focus to triggering chip."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(f"http://127.0.0.1:{self.port}/ai-practice/vacation-plan-basic/", wait_until="networkidle")

            chip = page.locator(".itc[data-type='combo']").first
            chip.click()

            dropdown = page.locator(".itc-dropdown")
            dropdown.wait_for(state="visible", timeout=5000)
            self.assertTrue(dropdown.is_visible())

            # Press Escape to close
            page.keyboard.press("Escape")
            dropdown.wait_for(state="detached", timeout=5000)
            self.assertFalse(dropdown.is_visible())

            # Focus must be restored to the chip
            is_chip_focused = page.evaluate("document.activeElement.classList.contains('itc')")
            self.assertTrue(is_chip_focused, "Keyboard focus was not restored to the .itc chip after Escape")

            browser.close()

    def test_mobile_navigation_toggle(self) -> None:
        """Verify mobile hamburger toggle opens and closes drawer with proper ARIA attributes."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Mobile viewport 375x667
            context = browser.new_context(viewport={"width": 375, "height": 667})
            page = context.new_page()

            page.goto(f"http://127.0.0.1:{self.port}/", wait_until="networkidle")

            toggle = page.locator(".site-nav-toggle")
            self.assertTrue(toggle.is_visible())

            # Initially closed
            nav_state = page.evaluate("document.documentElement.getAttribute('data-navigation-state')")
            self.assertEqual(nav_state, "closed")
            self.assertEqual(toggle.get_attribute("aria-expanded"), "false")

            # Click to open
            toggle.click()
            page.wait_for_function("document.documentElement.getAttribute('data-navigation-state') === 'open'")
            self.assertEqual(toggle.get_attribute("aria-expanded"), "true")

            # Click to close
            toggle.click()
            page.wait_for_function("document.documentElement.getAttribute('data-navigation-state') === 'closed'")
            self.assertEqual(toggle.get_attribute("aria-expanded"), "false")

            browser.close()


if __name__ == "__main__":
    unittest.main()
