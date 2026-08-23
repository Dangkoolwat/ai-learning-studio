import { initNavigation } from "./navigation.js";
import { initPromptCopy } from "./prompt-copy.js";
import { initPromptBuilder } from "./prompt-builder.js";
import { initImageSliders } from "./image-slider.js";
import { initImageLightbox } from "./image-lightbox.js";
import { initThemeToggle } from "./theme-toggle.js";

document.documentElement.classList.add("js");

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
