const musica = document.querySelector("[data-musica-fondo]");

if (musica) {
  const gestos = new AbortController();
  let iniciandoMusica = false;

  async function iniciarMusica() {
    if (iniciandoMusica || musica.muted || !musica.paused) return;
    iniciandoMusica = true;
    try {
      await musica.play();
      gestos.abort();
    } catch {
      // Si el navegador bloquea este intento, prueba con el siguiente gesto.
    } finally {
      iniciandoMusica = false;
    }
  }

  function aplicarPreferenciasMusica() {
    musica.volume = Number(musica.dataset.volumenMusica) / 100;
    musica.muted = musica.dataset.silenciado === "true" || musica.volume === 0;
    iniciarMusica();
  }

  const opciones = { capture: true, signal: gestos.signal };
  document.addEventListener("click", iniciarMusica, opciones);
  document.addEventListener("keydown", iniciarMusica, opciones);
  musica.addEventListener("preferencias-musica", aplicarPreferenciasMusica);
  aplicarPreferenciasMusica();
}
