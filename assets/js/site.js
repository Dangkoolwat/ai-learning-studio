/**
 * @fileoverview Application Entry Point for AI Learning Studio Client Scripts.
 * Bootstraps theme manager, navigation/search, prompt copy engines, sliders, and lightboxes.
 */

import { initNavigation } from "./navigation.js";
import { initPromptCopy } from "./prompt-copy.js";
import { initPromptBuilder } from "./prompt-builder.js";
import { initImageSliders } from "./image-slider.js";
import { initImageLightbox } from "./image-lightbox.js";
import { initThemeToggle } from "./theme-toggle.js";

// Progressive Enhancement: Mark JavaScript as enabled on HTML root
document.documentElement.classList.add("js");

/**
 * Executes all UI component initializers.
 */
function runInitializers() {
  initThemeToggle();
  initNavigation();
  initPromptCopy();
  initPromptBuilder();
  initImageSliders();
  initImageLightbox();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", runInitializers);
} else {
  runInitializers();
}
