document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("galleryLightbox");
  const modalImage = document.getElementById("lightboxImage");
  const modalTitle = document.getElementById("lightboxTitle");
  const modalTag = document.getElementById("lightboxTag");
  const modalDescription = document.getElementById("lightboxDescription");

  if (!modal || !modalImage || !modalTitle || !modalTag || !modalDescription) {
    return;
  }

  const cards = document.querySelectorAll(".gallery-card--clickable");
  const closeElements = modal.querySelectorAll("[data-lightbox-close]");

  function openLightbox(card) {
    const image = card.getAttribute("data-lightbox-image") || "";
    const title = card.getAttribute("data-lightbox-title") || "";
    const tag = card.getAttribute("data-lightbox-tag") || "";
    const description = card.getAttribute("data-lightbox-description") || "";

    modalImage.src = image;
    modalImage.alt = title;
    modalTitle.textContent = title;
    modalTag.textContent = tag;
    modalDescription.textContent = description;

    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("lightbox-open");
  }

  function closeLightbox() {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("lightbox-open");

    modalImage.src = "";
    modalImage.alt = "";
    modalTitle.textContent = "";
    modalTag.textContent = "";
    modalDescription.textContent = "";
  }

  cards.forEach((card) => {
    card.addEventListener("click", () => openLightbox(card));
    card.addEventListener("keypress", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openLightbox(card);
      }
    });
    card.setAttribute("tabindex", "0");
  });

  closeElements.forEach((element) => {
    element.addEventListener("click", closeLightbox);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal.classList.contains("is-open")) {
      closeLightbox();
    }
  });
});
