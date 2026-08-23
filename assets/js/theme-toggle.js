/**
 * AI Learning Studio - Dark Mode & Theme Toggle
 * Supports system preference, localStorage persistence, and instant toggle without flash.
 */

const STORAGE_KEY = "als-theme-preference";

export function initThemeToggle() {
  const toggleBtn = document.querySelector(".site-theme-toggle");
  if (!toggleBtn) return;

  function getEffectiveTheme() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === "dark" || saved === "light") {
        return saved;
      }
    } catch {
      // Storage access may fail under strict sandboxing or disabled storage policies
    }

    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    if (theme === "dark") {
      document.documentElement.setAttribute("data-theme-mode", "dark");
      toggleBtn.setAttribute("aria-pressed", "true");
      toggleBtn.setAttribute("aria-label", "라이트 모드로 전환");
      toggleBtn.setAttribute("title", "라이트 모드로 전환");
    } else {
      document.documentElement.setAttribute("data-theme-mode", "light");
      toggleBtn.setAttribute("aria-pressed", "false");
      toggleBtn.setAttribute("aria-label", "다크 모드로 전환");
      toggleBtn.setAttribute("title", "다크 모드로 전환");
    }
  }

  // 초기 테마 적용
  const currentTheme = getEffectiveTheme();
  applyTheme(currentTheme);

  // 클릭 이벤트 핸들러
  toggleBtn.addEventListener("click", () => {
    const isDark = document.documentElement.getAttribute("data-theme-mode") === "dark";
    const nextTheme = isDark ? "light" : "dark";
    try {
      localStorage.setItem(STORAGE_KEY, nextTheme);
    } catch {
      // Storage write may fail under strict sandboxing
    }
    applyTheme(nextTheme);
  });

  // 시스템 테마 변경 감지
  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      try {
        if (!localStorage.getItem(STORAGE_KEY)) {
          applyTheme(e.matches ? "dark" : "light");
        }
      } catch {
        applyTheme(e.matches ? "dark" : "light");
      }
    });
  }
}
