function getSliderIndex(slider, slides) {
  const viewport = slider.querySelector(".image-slider__viewport");
  if (!viewport) return 0;

  const viewportRect = viewport.getBoundingClientRect();
  const centerX = viewportRect.left + viewportRect.width / 2;

  let bestIndex = 0;
  let bestDistance = Infinity;

  slides.forEach((slide, index) => {
    const rect = slide.getBoundingClientRect();
    const slideCenter = rect.left + rect.width / 2;
    const distance = Math.abs(centerX - slideCenter);
    if (distance < bestDistance) {
      bestDistance = distance;
      bestIndex = index;
    }
  });

  return bestIndex;
}

function setActiveSlide(slider, index) {
  const slides = Array.from(slider.querySelectorAll("[data-slider-slide]"));
  const dots = Array.from(slider.querySelectorAll("[data-slider-dot]"));
  const prevLinks = Array.from(slider.querySelectorAll("[data-slider-prev]"));
  const nextLinks = Array.from(slider.querySelectorAll("[data-slider-next]"));

  if (!slides.length) return;

  const maxIndex = slides.length - 1;
  const clamped = Math.max(0, Math.min(index, maxIndex));

  slides.forEach((slide, slideIndex) => {
    slide.classList.toggle("is-active", slideIndex === clamped);
  });

  dots.forEach((dot, dotIndex) => {
    dot.classList.toggle("is-active", dotIndex === clamped);
  });

  prevLinks.forEach((link) => {
    link.dataset.index = String(clamped === 0 ? maxIndex : clamped - 1);
  });
  nextLinks.forEach((link) => {
    link.dataset.index = String(clamped === maxIndex ? 0 : clamped + 1);
  });
}

export function initImageSliders() {
  const sliders = document.querySelectorAll(".image-slider");

  sliders.forEach((slider) => {
    const viewport = slider.querySelector(".image-slider__viewport");
    const slides = Array.from(slider.querySelectorAll("[data-slider-slide]"));
    const dots = Array.from(slider.querySelectorAll("[data-slider-dot]"));
    const prevLinks = Array.from(slider.querySelectorAll("[data-slider-prev]"));
    const nextLinks = Array.from(slider.querySelectorAll("[data-slider-next]"));
    if (!viewport || !slides.length) return;

    const sync = () => setActiveSlide(slider, getSliderIndex(slider, slides));
    const goTo = (targetIndex) => {
      const clamped = Math.max(0, Math.min(targetIndex, slides.length - 1));
      const targetSlide = slides[clamped];
      const viewportRect = viewport.getBoundingClientRect();
      const slideRect = targetSlide.getBoundingClientRect();
      const targetLeft = viewport.scrollLeft + (slideRect.left - viewportRect.left);
      viewport.scrollTo({ left: targetLeft, behavior: "smooth" });
    };

    dots.forEach((dot, index) => {
      dot.addEventListener("click", (event) => {
        event.preventDefault();
        goTo(index);
      });
    });

    prevLinks.forEach((prevLink) => {
      prevLink.addEventListener("click", (event) => {
        event.preventDefault();
        const currentIndex = getSliderIndex(slider, slides);
        goTo(currentIndex === 0 ? slides.length - 1 : currentIndex - 1);
      });
    });

    nextLinks.forEach((nextLink) => {
      nextLink.addEventListener("click", (event) => {
        event.preventDefault();
        const currentIndex = getSliderIndex(slider, slides);
        goTo(currentIndex === slides.length - 1 ? 0 : currentIndex + 1);
      });
    });

    viewport.addEventListener("scroll", () => window.requestAnimationFrame(sync), { passive: true });

    window.requestAnimationFrame(sync);
  });
}
