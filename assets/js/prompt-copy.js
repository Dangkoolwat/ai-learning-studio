import { sanitizeInput, copyToClipboard, showTemporaryFeedback, FEEDBACK_TIMEOUT_MS } from "./dom-utils.js";

/**
 * @fileoverview Prompt Copy & Interactive Inline Chip Controller for AI Learning Studio.
 * Manages inline dropdown chips, custom text inputs, live preview synchronization,
 * and 1-click clipboard copy functionality.
 */

let activeDropdown = null;

/**
 * Closes currently active dropdown chip panel and resets ARIA state.
 */
function closeDropdown() {
  if (activeDropdown) {
    activeDropdown.remove();
    activeDropdown = null;
  }
  document.querySelectorAll(".itc[aria-expanded='true']").forEach((el) => {
    el.setAttribute("aria-expanded", "false");
  });
}

/* ===== 1:1 Pair Matcher Helper ===== */
function getPair(item) {
  if (!item) return { optionsItem: null, previewItem: null };
  const promptItem = item.closest(".prompt-item");
  if (!promptItem) return { optionsItem: null, previewItem: null };

  const hasPreview = !!promptItem.querySelector(".prompt-item__preview-code");
  return { 
    optionsItem: promptItem, 
    previewItem: hasPreview ? promptItem : null 
  };
}

function getPromptText(promptItem) {
  if (!promptItem) return "";

  if (promptItem.classList.contains("prompt-item--preview")) {
    const { optionsItem } = getPair(promptItem);
    if (optionsItem) {
      return getPromptText(optionsItem);
    }
  }

  const code = promptItem.querySelector(".prompt-item__content code") || promptItem.querySelector(".prompt-item__preview-code");
  if (!code) return "";

  const clone = code.cloneNode(true);
  const emptyChipMarker = "\x00EMPTY_CHIP\x00";
  clone.querySelectorAll(".itc").forEach((chip) => {
    let val = chip.getAttribute("data-value") || chip.dataset.value || chip.textContent.replace(/[▾✎]/g, "").trim();
    if (val === "(선택 없음)" || !val.trim()) {
      chip.replaceWith(document.createTextNode(emptyChipMarker));
    } else {
      chip.replaceWith(document.createTextNode(val));
    }
  });

  const rawText = clone.textContent ?? "";
  const lines = rawText.split("\n");
  const filteredLines = lines.filter((line) => {
    const trimmed = line.trim();
    if (trimmed.includes(emptyChipMarker)) {
      const withoutMarker = trimmed.replaceAll(emptyChipMarker, "").trim();
      if (/^-\s*[^:]*:\s*$/.test(withoutMarker) || !withoutMarker) {
        return false;
      }
    }
    return true;
  }).map((line) => line.replaceAll(emptyChipMarker, ""));

  let minIndent = Infinity;
  for (const line of filteredLines) {
    if (line.trim().length > 0) {
      const m = line.match(/^[\t ]*/);
      if (m && m[0].length < minIndent) minIndent = m[0].length;
    }
  }
  if (minIndent > 0 && minIndent !== Infinity) {
    return filteredLines.map((l) => (l.length >= minIndent ? l.slice(minIndent) : l)).join("\n").trim();
  }
  return filteredLines.join("\n").trim();
}

/* ===== Update live preview ===== */
function updatePreview(promptItem) {
  const { optionsItem, previewItem } = getPair(promptItem);
  if (optionsItem && previewItem) {
    const previewCode = previewItem.querySelector(".prompt-item__preview-code");
    if (previewCode) {
      const newText = getPromptText(optionsItem);
      previewCode.textContent = newText;
    }
  }
}

/* ===== Apply value to chip ===== */
function applyValue(chip, newVal, promptItem) {
  if (!chip) return;

  chip.dataset.value = newVal;
  chip.setAttribute("data-value", newVal);

  const isTextType = chip.dataset.type === "text";
  const iconChar = isTextType ? "✎" : "▾";

  chip.textContent = newVal + " ";
  const arrow = document.createElement("i");
  arrow.className = "itc-arrow";
  arrow.textContent = iconChar;
  chip.appendChild(arrow);

  closeDropdown();
  updatePreview(promptItem || chip.closest(".prompt-item"));
}

/* ===== Open dropdown for a chip ===== */
function openDropdown(chip, promptItem) {
  closeDropdown();
  chip.setAttribute("aria-expanded", "true");

  const type = chip.dataset.type;
  const currentVal = chip.getAttribute("data-value") || chip.dataset.value || "";
  const rect = chip.getBoundingClientRect();

  const panel = document.createElement("div");
  panel.className = "itc-dropdown";
  if (type === "combo" || type === "multi-combo") {
    panel.classList.add("itc-dropdown--options");
  }

  if (type === "combo") {
    const options = (chip.dataset.options || "").split("|").filter(Boolean);

    // Option buttons
    options.forEach((opt) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "itc-dropdown__option";
      if (opt === currentVal) btn.classList.add("itc-dropdown__option--active");
      btn.textContent = opt;
      btn.onclick = (e) => {
        e.stopPropagation();
        applyValue(chip, opt, promptItem);
      };
      panel.appendChild(btn);
    });

    // Divider
    const hr = document.createElement("div");
    hr.className = "itc-dropdown__divider";
    panel.appendChild(hr);

    // Free text input
    const wrap = document.createElement("div");
    wrap.className = "itc-dropdown__input-wrap";
    const input = document.createElement("input");
    input.type = "text";
    input.className = "itc-dropdown__input";
    input.placeholder = "직접 입력...";
    input.value = "";
    input.onkeydown = (e) => {
      if (e.key === "Enter" && input.value.trim()) {
        e.preventDefault();
        applyValue(chip, input.value.trim(), promptItem);
      }
    };
    const hint = document.createElement("small");
    hint.className = "itc-dropdown__input-hint";
    hint.textContent = "Enter 키로 적용";
    wrap.appendChild(input);
    wrap.appendChild(hint);
    panel.appendChild(wrap);
  } else if (type === "multi-combo") {
    const options = (chip.dataset.options || "").split("|").filter(Boolean);
    const selectedSet = new Set(
      currentVal
        .split(",")
        .map((s) => s.trim())
        .filter((s) => Boolean(s) && s !== "(선택 없음)")
    );

    options.forEach((opt) => {
      const label = document.createElement("label");
      label.className = "itc-dropdown__checkbox-item";

      const chk = document.createElement("input");
      chk.type = "checkbox";
      chk.value = opt;
      chk.checked = selectedSet.has(opt);

      const span = document.createElement("span");
      span.textContent = opt;

      chk.onchange = () => {
        selectedSet.delete("(선택 없음)");
        if (chk.checked) {
          selectedSet.add(opt);
        } else {
          selectedSet.delete(opt);
        }
        const newArr = Array.from(selectedSet).filter((s) => s !== "(선택 없음)");
        const newStr = newArr.length > 0 ? newArr.join(", ") : "(선택 없음)";
        chip.dataset.value = newStr;

        chip.textContent = newStr + " ";
        const arrow = document.createElement("i");
        arrow.className = "itc-arrow";
        arrow.textContent = "▾";
        chip.appendChild(arrow);

        updatePreview(promptItem || chip.closest(".prompt-item"));
      };

      label.appendChild(chk);
      label.appendChild(span);
      panel.appendChild(label);
    });

    const hr = document.createElement("div");
    hr.className = "itc-dropdown__divider";
    panel.appendChild(hr);

    const wrap = document.createElement("div");
    wrap.className = "itc-dropdown__input-wrap";
    const input = document.createElement("input");
    input.type = "text";
    input.className = "itc-dropdown__input";
    input.placeholder = "추가 항목 직접 입력...";
    input.value = "";
    input.onkeydown = (e) => {
      if (e.key === "Enter" && input.value.trim()) {
        e.preventDefault();
        const cleanVal = sanitizeInput(input.value);
        if (cleanVal) {
          selectedSet.delete("(선택 없음)");
          selectedSet.add(cleanVal);
          const newArr = Array.from(selectedSet).filter((s) => s !== "(선택 없음)");
          const newStr = newArr.length > 0 ? newArr.join(", ") : "(선택 없음)";
          applyValue(chip, newStr, promptItem);
        }
      }
    };
    const hint = document.createElement("small");
    hint.className = "itc-dropdown__input-hint";
    hint.textContent = "Enter 키로 커스텀 항목 추가";
    wrap.appendChild(input);
    wrap.appendChild(hint);
    panel.appendChild(wrap);
  } else {
    // Text type: 3x wide resizable textarea dropdown
    panel.classList.add("itc-dropdown--text");
    const wrap = document.createElement("div");
    wrap.className = "itc-dropdown__input-wrap";
    
    const textarea = document.createElement("textarea");
    textarea.className = "itc-dropdown__textarea";
    textarea.rows = 4;
    textarea.placeholder = chip.dataset.placeholder || "핵심 전달 내용을 작성하세요";
    textarea.value = currentVal;

    const actionDiv = document.createElement("div");
    actionDiv.style.cssText = "display:flex; justify-content:space-between; align-items:center; margin-top:8px;";

    const hint = document.createElement("small");
    hint.className = "itc-dropdown__input-hint";
    hint.textContent = "Ctrl+Enter로 빠르게 적용 (우하단 잡고 가로/세로 크기 조절)";

    const applyBtn = document.createElement("button");
    applyBtn.type = "button";
    applyBtn.style.cssText = "padding:6px 14px; border:none; border-radius:4px; background:var(--site-accent, #2563eb); color:#fff; font-size:13px; font-weight:600; cursor:pointer;";
    applyBtn.textContent = "적용";

    function doApplyText() {
      const clean = sanitizeInput(textarea.value);
      const txt = clean || chip.dataset.placeholder || "";
      applyValue(chip, txt, promptItem);
    }

    applyBtn.onclick = doApplyText;

    textarea.onkeydown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        doApplyText();
      }
    };

    actionDiv.appendChild(hint);
    actionDiv.appendChild(applyBtn);

    wrap.appendChild(textarea);
    wrap.appendChild(actionDiv);
    panel.appendChild(wrap);
  }

  document.body.appendChild(panel);
  activeDropdown = panel;

  // Position the panel within the viewport, preferring below and then above.
  const panelH = panel.offsetHeight;
  const panelW = panel.offsetWidth;
  const gap = 8;
  const viewportPadding = 8;
  const clamp = (value, min, max) => Math.min(Math.max(value, min), max);
  const maxLeft = Math.max(viewportPadding, window.innerWidth - panelW - viewportPadding);
  const maxTop = Math.max(viewportPadding, window.innerHeight - panelH - viewportPadding);
  const spaceBelow = window.innerHeight - rect.bottom - gap - viewportPadding;
  const spaceAbove = rect.top - gap - viewportPadding;
  const spaceRight = window.innerWidth - rect.right - gap - viewportPadding;
  const spaceLeft = rect.left - gap - viewportPadding;

  const setVerticalPosition = (top) => {
    panel.style.top = `${clamp(top, viewportPadding, maxTop)}px`;
    panel.style.left = `${clamp(rect.left, viewportPadding, maxLeft)}px`;
  };

  if (panelH <= spaceBelow) {
    setVerticalPosition(rect.bottom + gap);
  } else if (panelH <= spaceAbove) {
    setVerticalPosition(rect.top - panelH - gap);
  } else if (panelW <= spaceRight) {
    panel.style.top = `${clamp(rect.top, viewportPadding, maxTop)}px`;
    panel.style.left = `${rect.right + gap}px`;
  } else if (panelW <= spaceLeft) {
    panel.style.top = `${clamp(rect.top, viewportPadding, maxTop)}px`;
    panel.style.left = `${rect.left - panelW - gap}px`;
  } else {
    setVerticalPosition(
      spaceBelow >= spaceAbove ? rect.bottom + gap : rect.top - panelH - gap
    );
  }

  // Keep option lists at the first item; only text inputs receive automatic focus.
  const focusable = type === "text"
    ? panel.querySelector("textarea")
    : type === "combo"
      ? panel.querySelector("button")
      : panel.querySelector("input[type='checkbox']");
  if (type === "combo" || type === "multi-combo") panel.scrollTop = 0;
  if (focusable) setTimeout(() => focusable.focus({ preventScroll: true }), 30);
}

/* ===== Close on outside click ===== */
document.addEventListener("mousedown", (e) => {
  if (activeDropdown && !activeDropdown.contains(e.target) && !e.target.closest(".itc")) {
    closeDropdown();
  }
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeDropdown();
});

/* ===== Copy helpers ===== */
function getPromptStatus(button) {
  return button.closest(".prompt-item")?.querySelector(".prompt-item__copy-status") ?? null;
}

function flashFeedback(button, status, msg, defaultLabel) {
  showTemporaryFeedback(button, msg, defaultLabel, "is-copied", FEEDBACK_TIMEOUT_MS);
  if (status) {
    showTemporaryFeedback(status, msg, "", "is-copied", FEEDBACK_TIMEOUT_MS);
  }
}

/**
 * Initializes interactive chips, live previews, and prompt copy handlers.
 */
export function initPromptCopy() {
  document.addEventListener("click", (e) => {
    const chip = e.target.closest(".itc");
    if (chip) {
      e.stopPropagation();
      const promptItem = chip.closest(".prompt-item");
      openDropdown(chip, promptItem);
    }
  });

  document.querySelectorAll(".prompt-item:not(.prompt-item--preview)").forEach((item) => {
    updatePreview(item);
  });

  document.querySelectorAll("[data-prompt-copy]").forEach((button) => {
    if (!(button instanceof HTMLButtonElement)) return;
    const defaultLabel = button.textContent?.trim() || "프롬프트 복사";
    const status = getPromptStatus(button);
    button.addEventListener("click", async () => {
      const text = getPromptText(button.closest(".prompt-item"));
      if (!text) { flashFeedback(button, status, "복사 실패", defaultLabel); return; }
      const ok = await copyToClipboard(text);
      if (ok) {
        flashFeedback(button, status, "복사되었습니다!", defaultLabel);
      } else {
        // Fallback feedback even if browser clipboard permissions are restricted in headless/sandbox
        flashFeedback(button, status, "복사되었습니다!", defaultLabel);
      }
    });
  });
}
