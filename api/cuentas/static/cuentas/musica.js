const musica = document.querySelector("[data-musica-fondo]");

if (musica && musica.dataset.silenciado !== "true" && Number(musica.dataset.volumenMusica) > 0) {
  musica.volume = Number(musica.dataset.volumenMusica) / 100;
  const gestos = new AbortController();
  let iniciandoMusica = false;

  async function iniciarMusica() {
    if (iniciandoMusica) return;
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

  const opciones = { capture: true, signal: gestos.signal };
  document.addEventListener("click", iniciarMusica, opciones);
  document.addEventListener("keydown", iniciarMusica, opciones);
  iniciarMusica();
}
