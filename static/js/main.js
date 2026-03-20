document.addEventListener("DOMContentLoaded", () => {
  /* ===== Mostrar / ocultar contraseña ===== */
  const toggleButtons = document.querySelectorAll("[data-toggle-password]");

  toggleButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetId = button.getAttribute("data-password-target");
      const input = document.getElementById(targetId);

      if (!input) return;

      const isHidden = input.type === "password";
      input.type = isHidden ? "text" : "password";
      button.textContent = isHidden ? "Ocultar" : "Ver";
    });
  });

  /* ===== Lightbox de galería ===== */
  const modal = document.getElementById("galleryLightbox");
  const modalImage = document.getElementById("lightboxImage");
  const modalTitle = document.getElementById("lightboxTitle");
  const modalTag = document.getElementById("lightboxTag");
  const modalDescription = document.getElementById("lightboxDescription");

  if (modal && modalImage && modalTitle && modalTag && modalDescription) {
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
  }
});
