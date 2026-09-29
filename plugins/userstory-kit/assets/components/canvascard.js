(() => {
  const root = document.querySelector(".ukcards");
  const slides = [...root.querySelectorAll(".ukcards-slide")];
  const counter = root.querySelector(".ukcards-counter");
  root.style.setProperty("--ukcards-pages", slides.length > 1 ? slides.length + 1 : 1);

  function update() {
    const distance = Math.max(0, root.offsetHeight - window.innerHeight);
    const progress = distance ? -root.getBoundingClientRect().top / distance : 0;
    const index = Math.min(slides.length - 1, Math.floor(Math.max(0, Math.min(1, progress)) * slides.length));
    slides.forEach((slide, number) => {
      slide.classList.toggle("active", number === index);
      slide.setAttribute("aria-hidden", String(number !== index));
    });
    counter.textContent = `${index + 1}/${slides.length}`;
  }

  // Read the native scroll position; never move the page or intercept input.
  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update, { passive: true });
  update();
})();
