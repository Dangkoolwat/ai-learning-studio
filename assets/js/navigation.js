/**
 * @fileoverview Navigation & Sidebar Controller for AI Learning Studio.
 * Handles mobile drawer toggle, persistent scroll restoration, route memorization,
 * live client-side search filtering, and smart accordion management.
 */

const COMPACT_MEDIA_QUERY = window.matchMedia("(max-width: 899px)");
const NAV_SCROLL_KEY = "als-nav-scroll-pos";
const LAST_MENU_ROUTE_KEY = "als-last-visited-route";

/**
 * Updates root and toggle button state for mobile navigation drawer.
 * @param {HTMLElement} root - Document root element
 * @param {HTMLButtonElement} toggle - Mobile hamburger button
 * @param {boolean} isOpen - Desired open/closed state
 */
function setNavigationState(root, toggle, isOpen) {
  root.setAttribute("data-navigation-state", isOpen ? "open" : "closed");
  toggle.setAttribute("aria-expanded", String(isOpen));
  toggle.setAttribute("aria-label", isOpen ? "메뉴 닫기" : "메뉴 열기");
  toggle.textContent = isOpen ? "메뉴 닫기" : "메뉴 열기";
}

/**
 * Initializes navigation bar, drawer events, search filtering, and accordion state.
 */
export function initNavigation() {
  const root = document.documentElement;
  const toggle = document.querySelector(".site-nav-toggle");
  const navigation = document.querySelector("#primary-navigation");

  if (!(toggle instanceof HTMLButtonElement) || !(navigation instanceof HTMLElement)) {
    return;
  }

  // 현재 방문한 페이지 경로 기억 (홈/루트가 아닌 실제 메뉴일 때)
  const currentPath = window.location.pathname;
  if (currentPath && currentPath !== "/" && currentPath !== "/index.html") {
    try {
      localStorage.setItem(LAST_MENU_ROUTE_KEY, currentPath);
    } catch {
      // LocalStorage access restricted in private mode
    }
  }

  // 데스크톱 환경에서 사이드바 스크롤 위치 복원
  if (!COMPACT_MEDIA_QUERY.matches) {
    try {
      const savedPos = sessionStorage.getItem(NAV_SCROLL_KEY);
      if (savedPos !== null) {
        navigation.scrollTop = parseInt(savedPos, 10);
      }
    } catch {
      // SessionStorage access restricted
    }

    // 링크 클릭 직전의 스크롤 위치 및 마지막 메뉴 경로 기억
    navigation.addEventListener("click", (e) => {
      const link = e.target.closest("a");
      if (!link) return;

      try {
        sessionStorage.setItem(NAV_SCROLL_KEY, String(navigation.scrollTop));
        const targetPath = link.pathname || link.getAttribute("href");
        if (targetPath && targetPath !== "/" && targetPath !== "/index.html") {
          localStorage.setItem(LAST_MENU_ROUTE_KEY, targetPath);
        }
      } catch {
        // SessionStorage / LocalStorage write restricted
      }
    });

    // 스크롤 변경 시 위치 실시간 기록
    navigation.addEventListener("scroll", () => {
      try {
        sessionStorage.setItem(NAV_SCROLL_KEY, String(navigation.scrollTop));
      } catch {
        // Scroll position persistence restricted
      }
    }, { passive: true });
  }

  // 실시간 사이드바 검색/필터 기능
  const searchInput = navigation.querySelector(".site-nav-search__input");
  const searchClear = navigation.querySelector(".site-nav-search__clear");
  const navItems = navigation.querySelectorAll(".navigation-item");

  if (searchInput instanceof HTMLInputElement) {
    const handleSearch = () => {
      const query = searchInput.value.trim().toLowerCase();
      const isSearching = query.length > 0;
      
      if (searchClear instanceof HTMLButtonElement) {
        searchClear.hidden = !isSearching;
      }

      if (isSearching) {
        navigation.classList.add("is-searching");
      } else {
        navigation.classList.remove("is-searching");
      }

      navItems.forEach((item) => {
        if (!isSearching) {
          item.classList.remove("nav-item--hidden");
          const subItems = item.querySelectorAll(".sub-navigation-item");
          subItems.forEach((sub) => sub.classList.remove("nav-item--hidden"));
          return;
        }

        const mainText = item.querySelector(".navigation-link")?.textContent?.toLowerCase() || "";
        const subItems = item.querySelectorAll(".sub-navigation-item");
        let hasMatchingSub = false;

        subItems.forEach((sub) => {
          const subText = sub.textContent?.toLowerCase() || "";
          if (subText.includes(query)) {
            sub.classList.remove("nav-item--hidden");
            hasMatchingSub = true;
          } else {
            sub.classList.add("nav-item--hidden");
          }
        });

        if (mainText.includes(query) || hasMatchingSub) {
          item.classList.remove("nav-item--hidden");
        } else {
          item.classList.add("nav-item--hidden");
        }
      });
    };

    searchInput.addEventListener("input", handleSearch);

    if (searchClear instanceof HTMLButtonElement) {
      searchClear.addEventListener("click", () => {
        searchInput.value = "";
        searchInput.focus();
        handleSearch();
      });
    }

    // 단축키 (Cmd+K / Ctrl+K) 포커스 지원
    document.addEventListener("keydown", (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
    });
  }

  let isOpen = false;

  const closeNavigation = ({ focusToggle = false } = {}) => {
    isOpen = false;
    setNavigationState(root, toggle, false);
    if (focusToggle) {
      toggle.focus();
    }
  };

  const openNavigation = () => {
    if (!COMPACT_MEDIA_QUERY.matches) {
      closeNavigation();
      return;
    }

    isOpen = true;
    setNavigationState(root, toggle, true);
  };

  const syncToViewport = () => {
    if (!COMPACT_MEDIA_QUERY.matches) {
      closeNavigation();
      return;
    }

    closeNavigation();
  };

  setNavigationState(root, toggle, false);

  toggle.addEventListener("click", () => {
    if (COMPACT_MEDIA_QUERY.matches) {
      if (isOpen) {
        closeNavigation();
      } else {
        openNavigation();
      }
      return;
    }

    closeNavigation();
  });

  navigation.addEventListener("click", (event) => {
    if (!COMPACT_MEDIA_QUERY.matches || !isOpen) {
      return;
    }

    const target = event.target;
    if (target instanceof HTMLAnchorElement) {
      closeNavigation({ focusToggle: true });
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !isOpen) {
      return;
    }

    closeNavigation({ focusToggle: true });
  });

  if (typeof COMPACT_MEDIA_QUERY.addEventListener === "function") {
    COMPACT_MEDIA_QUERY.addEventListener("change", syncToViewport);
  } else if (typeof COMPACT_MEDIA_QUERY.addListener === "function") {
    COMPACT_MEDIA_QUERY.addListener(syncToViewport);
  }
}
