const COMPACT_MEDIA_QUERY = window.matchMedia("(max-width: 899px)");

function setNavigationState(root, toggle, isOpen) {
  root.setAttribute("data-navigation-state", isOpen ? "open" : "closed");
  toggle.setAttribute("aria-expanded", String(isOpen));
  toggle.setAttribute("aria-label", isOpen ? "메뉴 닫기" : "메뉴 열기");
  toggle.textContent = isOpen ? "메뉴 닫기" : "메뉴 열기";
}

export function initNavigation() {
  const root = document.documentElement;
  const toggle = document.querySelector(".site-nav-toggle");
  const navigation = document.querySelector("#primary-navigation");

  if (!(toggle instanceof HTMLButtonElement) || !(navigation instanceof HTMLElement)) {
    return;
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
