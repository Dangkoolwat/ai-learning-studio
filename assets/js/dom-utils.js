/**
 * @fileoverview Shared DOM and UI utilities for AI Learning Studio.
 * Provides helper functions for input sanitization, clipboard handling,
 * feedback timer management, and element querying.
 */

/**
 * Default feedback display duration in milliseconds.
 * @type {number}
 */
export const FEEDBACK_TIMEOUT_MS = 1800;

/**
 * WeakMap to track active feedback timer IDs per HTML element.
 * @type {WeakMap<HTMLElement, number>}
 */
export const feedbackTimers = new WeakMap();

/**
 * Sanitizes user input string by stripping unprintable control characters.
 * Preserves all valid prompt characters, punctuation, and Unicode symbols.
 * XSS prevention is guaranteed via safe DOM text node insertion (textContent/createTextNode).
 * 
 * @param {string|null|undefined} text - Raw input string
 * @returns {string} Sanitized string
 */
export function sanitizeInput(text) {
  if (!text) return "";
  return text.replace(/[\x00-\x09\x0B\x0C\x0E-\x1F\x7F]/g, "").trim();
}

/**
 * Copies plain text to the clipboard with modern Async Clipboard API and legacy fallback.
 * 
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} True if copy succeeded, false otherwise
 */
export async function copyToClipboard(text) {
  if (!text) return false;

  if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      // Fallback on permission/context error
    }
  }

  // Fallback for older browsers or restricted iframe environments
  try {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    textarea.style.pointerEvents = "none";
    document.body.appendChild(textarea);
    textarea.select();
    const successful = document.execCommand("copy");
    textarea.remove();
    return successful;
  } catch (err) {
    return false;
  }
}

/**
 * Shows temporary feedback message/state on a button or container.
 * 
 * @param {HTMLElement} element - Target button or indicator element
 * @param {string} feedbackText - Text to display during feedback
 * @param {string} [originalText] - Original text to restore (optional)
 * @param {string} [feedbackClass="is-copied"] - CSS class to toggle
 * @param {number} [timeoutMs=FEEDBACK_TIMEOUT_MS] - Duration to display feedback
 */
export function showTemporaryFeedback(
  element, 
  feedbackText, 
  originalText = null, 
  feedbackClass = "is-copied", 
  timeoutMs = FEEDBACK_TIMEOUT_MS
) {
  if (!element) return;

  const prevTimer = feedbackTimers.get(element);
  if (prevTimer) {
    clearTimeout(prevTimer);
  }

  const initialText = originalText !== null ? originalText : element.textContent;
  element.textContent = feedbackText;
  element.classList.add(feedbackClass);

  const timerId = window.setTimeout(() => {
    element.textContent = initialText;
    element.classList.remove(feedbackClass);
    feedbackTimers.delete(element);
  }, timeoutMs);

  feedbackTimers.set(element, timerId);
}
