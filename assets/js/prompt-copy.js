const COPY_FEEDBACK_TIMEOUT_MS = 1800;
const feedbackTimers = new WeakMap();

function getPromptText(button) {
  const promptItem = button.closest(".prompt-item");
  const code = promptItem?.querySelector(".prompt-item__content code");
  return code?.textContent?.trim() ?? "";
}

function getPromptStatus(button) {
  const promptItem = button.closest(".prompt-item");
  return promptItem?.querySelector(".prompt-item__copy-status") ?? null;
}

async function copyText(text) {
  if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
    await navigator.clipboard.writeText(text);
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "true");
  textarea.style.position = "fixed";
  textarea.style.inset = "0";
  textarea.style.opacity = "0";
  document.body.append(textarea);
  textarea.select();

  const copied = document.execCommand("copy");
  textarea.remove();

  if (!copied) {
    throw new Error("copy failed");
  }
}

function flashFeedback(button, status, message, defaultLabel) {
  button.textContent = message;
  button.setAttribute("aria-label", message);
  if (status) {
    status.textContent = message;
  }

  const existingTimer = feedbackTimers.get(button);
  if (existingTimer) {
    window.clearTimeout(existingTimer);
  }

  const nextTimer = window.setTimeout(() => {
    button.textContent = defaultLabel;
    button.setAttribute("aria-label", defaultLabel);
    if (status) {
      status.textContent = "";
    }
    feedbackTimers.delete(button);
  }, COPY_FEEDBACK_TIMEOUT_MS);

  feedbackTimers.set(button, nextTimer);
}

export function initPromptCopy() {
  const buttons = document.querySelectorAll("[data-prompt-copy]");

  buttons.forEach((button) => {
    if (!(button instanceof HTMLButtonElement)) {
      return;
    }

    const defaultLabel = button.textContent?.trim() || "프롬프트 복사";
    const status = getPromptStatus(button);

    button.addEventListener("click", async () => {
      const promptText = getPromptText(button);
      if (!promptText) {
        flashFeedback(button, status, "복사하지 못했습니다", defaultLabel);
        return;
      }

      try {
        await copyText(promptText);
        flashFeedback(button, status, "복사됨", defaultLabel);
      } catch {
        flashFeedback(button, status, "복사하지 못했습니다", defaultLabel);
      }
    });
  });
}
