/**
 * Pure JavaScript Image Slider Module for AI Learning Studio
 * Built with CSS transform (translateX) for 100% reliable, smooth slide transitions across all browsers.
 */

export function initImageSliders() {
  const sliders = document.querySelectorAll(".image-slider");

  sliders.forEach((slider) => {
    const track = slider.querySelector("[data-slider-track]");
    const slides = Array.from(slider.querySelectorAll("[data-slider-slide]"));
    const dots = Array.from(slider.querySelectorAll("[data-slider-dot]"));
    const prevLink = slider.querySelector("[data-slider-prev]");
    const nextLink = slider.querySelector("[data-slider-next]");

    if (!track || !slides.length) return;

    let currentIndex = 0;
    const maxIndex = slides.length - 1;

    function updateSlider(index) {
      currentIndex = Math.max(0, Math.min(index, maxIndex));

      // Translate track smoothly
      track.style.transform = `translateX(-${currentIndex * 100}%)`;

      // Update slide active state
      slides.forEach((slide, i) => {
        slide.classList.toggle("is-active", i === currentIndex);
      });

      // Update dots active state
      dots.forEach((dot, i) => {
        dot.classList.toggle("is-active", i === currentIndex);
        dot.setAttribute("aria-current", i === currentIndex ? "true" : "false");
      });
    }

    function nextSlide() {
      const nextIndex = currentIndex >= maxIndex ? 0 : currentIndex + 1;
      updateSlider(nextIndex);
    }

    function prevSlide() {
      const prevIndex = currentIndex <= 0 ? maxIndex : currentIndex - 1;
      updateSlider(prevIndex);
    }

    // Event Listeners for Arrow Navigation
    if (prevLink) {
      prevLink.addEventListener("click", (event) => {
        event.preventDefault();
        prevSlide();
      });
    }

    if (nextLink) {
      nextLink.addEventListener("click", (event) => {
        event.preventDefault();
        nextSlide();
      });
    }

    // Event Listeners for Dots Navigation
    dots.forEach((dot, index) => {
      dot.addEventListener("click", (event) => {
        event.preventDefault();
        updateSlider(index);
      });
    });

    // Touch / Swipe Support
    let startX = 0;
    let currentX = 0;
    let isDragging = false;

    track.addEventListener("touchstart", (e) => {
      startX = e.touches[0].clientX;
      isDragging = true;
    }, { passive: true });

    track.addEventListener("touchmove", (e) => {
      if (!isDragging) return;
      currentX = e.touches[0].clientX;
    }, { passive: true });

    track.addEventListener("touchend", () => {
      if (!isDragging) return;
      isDragging = false;
      const diffX = startX - currentX;
      if (Math.abs(diffX) > 40) {
        if (diffX > 0) {
          nextSlide();
        } else {
          prevSlide();
        }
      }
      startX = 0;
      currentX = 0;
    });

    // Initialize to index 0
    updateSlider(0);
  });
}
