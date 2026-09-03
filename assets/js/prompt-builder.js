import { copyToClipboard, showTemporaryFeedback, FEEDBACK_TIMEOUT_MS } from "./dom-utils.js";

/**
 * @fileoverview Interactive prompt-builder handler for AI Learning Studio.
 * Supports Help Modal Popups (?) and Live Dynamic Prompt Assembly with parameter controls.
 */

let lastActiveElement = null;

function createHelpModal() {
  let modalBg = document.getElementById("als-help-modal-bg");
  if (!modalBg) {
    modalBg = document.createElement("div");
    modalBg.id = "als-help-modal-bg";
    modalBg.className = "als-modal-bg";
    modalBg.setAttribute("role", "dialog");
    modalBg.setAttribute("aria-modal", "true");
    modalBg.setAttribute("aria-labelledby", "als-modal-title");
    modalBg.innerHTML = `
      <div class="als-modal">
        <div class="als-modal__header">
          <div class="als-modal__title-group">
            <span class="als-modal__badge">💡 학습 팁</span>
            <h3 id="als-modal-title" class="als-modal__title">항목 도움말</h3>
          </div>
          <button id="als-modal-close" class="als-modal__close-btn" aria-label="닫기">×</button>
        </div>
        <div id="als-modal-body" class="als-modal__body"></div>
      </div>
    `;
    document.body.appendChild(modalBg);

    const closeBtn = modalBg.querySelector("#als-modal-close");
    const closeModal = () => {
      modalBg.classList.remove("is-visible");
      if (lastActiveElement instanceof HTMLElement) {
        lastActiveElement.focus();
        lastActiveElement = null;
      }
    };

    closeBtn.onclick = closeModal;
    modalBg.onclick = (e) => {
      if (e.target === modalBg) closeModal();
    };
    document.addEventListener("keydown", (e) => {
      if (!modalBg.classList.contains("is-visible")) return;
      if (e.key === "Escape") {
        closeModal();
        return;
      }
      if (e.key === "Tab") {
        const focusable = modalBg.querySelectorAll("button, [href], input, [tabindex='0']");
        if (focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    });
  }
  return modalBg;
}

function showHelpPopup(title, description, detailText = "", triggerEl = null) {
  lastActiveElement = triggerEl || (document.activeElement instanceof HTMLElement ? document.activeElement : null);
  const modalBg = createHelpModal();
  const titleEl = modalBg.querySelector("#als-modal-title");
  const bodyEl = modalBg.querySelector("#als-modal-body");
  const closeBtn = modalBg.querySelector("#als-modal-close");

  titleEl.textContent = title;
  bodyEl.innerHTML = `
    <div class="als-modal__section">
      <h4>📌 쉬운 설명</h4>
      <p>${description}</p>
    </div>
    ${detailText ? `<div class="als-modal__section"><h4>🔍 활용 가이드</h4><p>${detailText}</p></div>` : ""}
  `;
  modalBg.classList.add("is-visible");
  requestAnimationFrame(() => {
    closeBtn?.focus();
  });
}

export function initPromptBuilder() {
  const builders = document.querySelectorAll(".prompt-builder");

  // Global Setup for ? Help Buttons across all prompt fields
  const allFields = document.querySelectorAll(".prompt-field");
  allFields.forEach((field) => {
    const labelEl = field.querySelector(".prompt-field__label");
    const descEl = field.querySelector(".prompt-field__description");

    if (labelEl && descEl && descEl.textContent.trim()) {
      if (!field.querySelector(".prompt-field__help-btn")) {
        const helpBtn = document.createElement("button");
        helpBtn.className = "prompt-field__help-btn";
        helpBtn.type = "button";
        helpBtn.setAttribute("aria-label", `${labelEl.textContent.trim()} 도움말 보기`);
        helpBtn.setAttribute("title", "도움말 및 설명 보기");
        helpBtn.textContent = "?";

        helpBtn.onclick = (e) => {
          e.preventDefault();
          e.stopPropagation();
          showHelpPopup(labelEl.textContent.trim(), descEl.textContent.trim(), "", helpBtn);
        };

        labelEl.appendChild(helpBtn);
      }
    }
  });

  builders.forEach((builder) => {
    const generateBtn = builder.querySelector(".prompt-builder__generate-btn");
    const resultBox = builder.querySelector(".prompt-builder__result");
    const resultCode = builder.querySelector(".prompt-builder__result-code");
    const copyBtn = builder.querySelector("[data-builder-copy]");

    if (!resultBox || !resultCode) return;

    function updateLivePrompt() {
      const fields = builder.querySelectorAll(".prompt-field");
      const values = {};

      fields.forEach((field) => {
        const fieldId = field.dataset.fieldId || field.getAttribute("data-field-id") || "";
        const select = field.querySelector("select");
        const customInput = field.querySelector("input[data-custom-input]");

        let val = "";
        const checkboxes = field.querySelectorAll("input[type='checkbox']");
        if (checkboxes.length > 0) {
          const checked = Array.from(checkboxes).filter((cb) => cb.checked).map((cb) => cb.value.trim());
          val = checked.length > 0 ? checked.join(", ") : "";
        } else {
          if (select && select.value === "__custom__") {
            val = (customInput && customInput.value.trim() !== "") ? customInput.value.trim() : "";
          } else if (select) {
            val = select.value ? select.value.trim() : "";
          }
        }

        if (val === "(선택 없음)") val = "";

        if (fieldId) {
          values[fieldId] = val;
        }
      });

      let generatedPrompt = "";
      const templateEl = builder.querySelector("#prompt-builder-template");

      if (templateEl && templateEl.innerHTML.trim() !== "") {
        let text = templateEl.innerHTML;
        const temp = document.createElement("textarea");
        temp.innerHTML = text;
        text = temp.value; // Decode HTML entities
        
        Object.keys(values).forEach((key) => {
          let val = values[key];
          if (!val) {
            const field = builder.querySelector(`.prompt-field[data-field-id="${key}"]`);
            const label = field ? field.querySelector(".prompt-field__label").textContent.trim() : key;
            val = `[${label}]`;
          }
          text = text.replaceAll(`[[${key}]]`, val);
        });
        generatedPrompt = text.trim();
      } else {
        generatedPrompt = Object.entries(values)
          .filter(([, v]) => v)
          .map(([k, v]) => `${k}: ${v}`)
          .join("\n");
      }

      resultCode.textContent = generatedPrompt;
      resultBox.classList.remove("is-hidden");
      resultBox.style.display = "block";
    }

    // Attach real-time input listeners
    const allFields = builder.querySelectorAll(".prompt-field");
    allFields.forEach((field) => {
      const select = field.querySelector("select");
      const customInputWrapper = field.querySelector(".prompt-field__custom-input-wrapper");
      const customInput = field.querySelector("input[data-custom-input]");
      if (select && customInput && customInputWrapper) {
        select.addEventListener("change", () => {
          if (select.value === "__custom__") {
            customInputWrapper.classList.remove("is-hidden");
            customInput.focus();
          } else {
            customInputWrapper.classList.add("is-hidden");
            customInput.value = "";
          }
          updateLivePrompt();
        });
        customInput.addEventListener("input", () => {
          updateLivePrompt();
        });
      }
    });

    const allControls = builder.querySelectorAll("select, input");
    allControls.forEach((control) => {
      control.addEventListener("input", updateLivePrompt);
      control.addEventListener("change", updateLivePrompt);
    });

    // Initial render
    updateLivePrompt();

    if (generateBtn) {
      generateBtn.onclick = (e) => {
        if (e) e.preventDefault();
        updateLivePrompt();
        resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
      };
    }

    if (copyBtn) {
      copyBtn.onclick = async (e) => {
        if (e) e.preventDefault();
        const text = resultCode?.textContent?.trim();
        if (!text) return;

        const statusEl = builder.querySelector(".prompt-builder__status");
        const ok = await copyToClipboard(text);
        if (ok) {
          showTemporaryFeedback(copyBtn, "복사되었습니다!", "프롬프트 복사", "is-copied", FEEDBACK_TIMEOUT_MS);
          if (statusEl) {
            statusEl.textContent = "프롬프트가 클립보드에 복사되었습니다.";
            setTimeout(() => {
              statusEl.textContent = "";
            }, FEEDBACK_TIMEOUT_MS);
          }
        } else {
          showTemporaryFeedback(copyBtn, "복사 실패", "프롬프트 복사", "is-error", FEEDBACK_TIMEOUT_MS);
          if (statusEl) {
            statusEl.textContent = "프롬프트 복사에 실패했습니다.";
            setTimeout(() => {
              statusEl.textContent = "";
            }, FEEDBACK_TIMEOUT_MS);
          }
        }
      };
    }
  });
}
