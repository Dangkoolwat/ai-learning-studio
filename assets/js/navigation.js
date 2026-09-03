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
 * Highlights matching query in text element, restoring original if empty.
 * @param {Element|null} element
 * @param {string} query
 */
function highlightText(element, query) {
  if (!(element instanceof HTMLElement)) return;
  const originalText = element.getAttribute("data-nav-original-text") || element.textContent;
  if (!element.hasAttribute("data-nav-original-text")) {
    element.setAttribute("data-nav-original-text", originalText);
  }

  if (!query) {
    element.textContent = originalText;
    return;
  }

  const lower = originalText.toLowerCase();
  const qLower = query.toLowerCase();
  const index = lower.indexOf(qLower);

  if (index === -1) {
    element.textContent = originalText;
    return;
  }

  const before = originalText.slice(0, index);
  const match = originalText.slice(index, index + query.length);
  const after = originalText.slice(index + query.length);

  element.textContent = "";
  if (before) element.appendChild(document.createTextNode(before));
  const mark = document.createElement("mark");
  mark.className = "search-highlight";
  mark.textContent = match;
  element.appendChild(mark);
  if (after) element.appendChild(document.createTextNode(after));
}

/**
 * Initializes navigation bar, drawer events, search filtering, and accordion state.
 */
export function initNavigation() {
  const root = document.documentElement;
  const toggle = document.querySelector(".site-nav-toggle");
  const navigation = document.querySelector("#primary-navigation");
  const brandLink = document.querySelector(".site-brand");

  // 현재 방문한 페이지 경로 실시간 기억
  const currentPath = window.location.pathname.replace(/\/index\.html$/, "/");
  if (currentPath && currentPath !== "/" && currentPath !== "") {
    try {
      localStorage.setItem(LAST_MENU_ROUTE_KEY, currentPath);
    } catch (e) {}
  }

  // 상단 로고(홈) 클릭 시 마지막 방문 경로를 홈('/')으로 갱신
  if (brandLink instanceof HTMLAnchorElement) {
    brandLink.addEventListener("click", () => {
      try {
        localStorage.setItem(LAST_MENU_ROUTE_KEY, "/");
      } catch (e) {}
    });
  }

  if (!(toggle instanceof HTMLButtonElement) || !(navigation instanceof HTMLElement)) {
    return;
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
        } else if (targetPath === "/" || targetPath === "/index.html") {
          localStorage.setItem(LAST_MENU_ROUTE_KEY, "/");
        }
      } catch {
        // SessionStorage write restricted
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
        const groupHeaders = item.querySelectorAll(".sub-nav-group-header");
        const subItems = item.querySelectorAll(".sub-navigation-item");

        if (!isSearching) {
          item.classList.remove("nav-item--hidden");
          highlightText(item.querySelector(".navigation-link"), "");
          groupHeaders.forEach((gh) => gh.classList.remove("nav-item--hidden"));
          subItems.forEach((sub) => {
            sub.classList.remove("nav-item--hidden");
            highlightText(sub.querySelector("a") || sub, "");
          });
          return;
        }

        const mainLink = item.querySelector(".navigation-link");
        const mainText = mainLink?.getAttribute("data-nav-original-text") || mainLink?.textContent?.toLowerCase() || "";
        let hasMatchingSub = false;

        subItems.forEach((sub) => {
          const subLink = sub.querySelector("a") || sub;
          const subText = subLink.getAttribute("data-nav-original-text") || subLink.textContent || "";
          if (subText.toLowerCase().includes(query)) {
            sub.classList.remove("nav-item--hidden");
            highlightText(subLink, query);
            hasMatchingSub = true;
          } else {
            sub.classList.add("nav-item--hidden");
            highlightText(subLink, "");
          }
        });

        // 그룹 헤더별로 다음 그룹 헤더 전까지 매칭되는 아이템이 하나라도 있으면 그룹 헤더 표시
        groupHeaders.forEach((gh) => {
          let nextEl = gh.nextElementSibling;
          let groupHasMatch = false;
          while (nextEl && !nextEl.classList.contains("sub-nav-group-header")) {
            if (nextEl.classList.contains("sub-navigation-item") && !nextEl.classList.contains("nav-item--hidden")) {
              groupHasMatch = true;
              break;
            }
            nextEl = nextEl.nextElementSibling;
          }
          if (groupHasMatch || gh.textContent?.toLowerCase().includes(query)) {
            gh.classList.remove("nav-item--hidden");
          } else {
            gh.classList.add("nav-item--hidden");
          }
        });

        if (mainText.includes(query) || hasMatchingSub) {
          item.classList.remove("nav-item--hidden");
          highlightText(mainLink, query);
        } else {
          item.classList.add("nav-item--hidden");
          highlightText(mainLink, "");
        }
      });

      // 검색 결과 0건 안내 (Empty State)
      const visibleItems = Array.from(navItems).filter((item) => !item.classList.contains("nav-item--hidden"));
      let emptyEl = navigation.querySelector(".site-nav-search__empty");
      if (isSearching && visibleItems.length === 0) {
        if (!emptyEl) {
          emptyEl = document.createElement("div");
          emptyEl.className = "site-nav-search__empty";
          emptyEl.setAttribute("role", "status");
          emptyEl.textContent = "일치하는 메뉴가 없습니다.";
          const searchContainer = navigation.querySelector(".site-nav-search");
          if (searchContainer) {
            searchContainer.after(emptyEl);
          } else {
            navigation.prepend(emptyEl);
          }
        }
        emptyEl.hidden = false;
      } else if (emptyEl) {
        emptyEl.hidden = true;
      }
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

  const getFocusableElements = () => {
    return Array.from(
      navigation.querySelectorAll(
        'button:not([disabled]):not([hidden]), [href]:not([tabindex="-1"]), input:not([disabled]):not([hidden]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )
    ).filter((el) => el.offsetParent !== null);
  };

  const closeNavigation = ({ focusToggle = true } = {}) => {
    isOpen = false;
    setNavigationState(root, toggle, false);
    if (focusToggle) {
      toggle.focus();
    }
  };

  const openNavigation = () => {
    if (!COMPACT_MEDIA_QUERY.matches) {
      closeNavigation({ focusToggle: false });
      return;
    }

    isOpen = true;
    setNavigationState(root, toggle, true);
    requestAnimationFrame(() => {
      const focusables = getFocusableElements();
      if (focusables.length > 0) {
        focusables[0].focus();
      }
    });
  };

  const syncToViewport = () => {
    if (!COMPACT_MEDIA_QUERY.matches) {
      closeNavigation({ focusToggle: false });
      return;
    }

    closeNavigation({ focusToggle: false });
  };

  setNavigationState(root, toggle, false);

  toggle.addEventListener("click", () => {
    if (COMPACT_MEDIA_QUERY.matches) {
      if (isOpen) {
        closeNavigation({ focusToggle: true });
      } else {
        openNavigation();
      }
      return;
    }

    closeNavigation({ focusToggle: false });
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
    if (!isOpen) {
      return;
    }

    if (event.key === "Escape") {
      closeNavigation({ focusToggle: true });
      return;
    }

    if (event.key === "Tab" && COMPACT_MEDIA_QUERY.matches) {
      const focusables = [toggle, ...getFocusableElements()];
      if (focusables.length === 0) return;

      const firstEl = focusables[0];
      const lastEl = focusables[focusables.length - 1];

      if (event.shiftKey && document.activeElement === firstEl) {
        event.preventDefault();
        lastEl.focus();
      } else if (!event.shiftKey && document.activeElement === lastEl) {
        event.preventDefault();
        firstEl.focus();
      }
    }
  });

  if (typeof COMPACT_MEDIA_QUERY.addEventListener === "function") {
    COMPACT_MEDIA_QUERY.addEventListener("change", syncToViewport);
  } else if (typeof COMPACT_MEDIA_QUERY.addListener === "function") {
    COMPACT_MEDIA_QUERY.addListener(syncToViewport);
  }
}
