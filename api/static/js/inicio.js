document.addEventListener("DOMContentLoaded", () => {
  const cards = Array.from(document.querySelectorAll("[data-difficulty-card]"));
  const playButton = document.getElementById("btn-jugar-ahora");
  if (!cards.length) {
    return;
  }

  let selectedLevel =
    cards.find((card) => card.classList.contains("difficulty-card--active"))?.dataset.nivel ||
    "normal";

  const syncPlayHref = () => {
    if (!playButton) {
      return;
    }
    const playBase = playButton.dataset.playBase || "";
    if (playBase) {
      playButton.href = `${playBase}?nivel=${encodeURIComponent(selectedLevel)}`;
    }
  };

  cards.forEach((card) => {
    card.addEventListener("click", () => {
      selectedLevel = card.dataset.nivel || "normal";
      cards.forEach((item) => {
        const active = item === card;
        item.classList.toggle("difficulty-card--active", active);
        item.setAttribute("aria-pressed", active ? "true" : "false");
      });
      syncPlayHref();
    });
  });

  syncPlayHref();
});
