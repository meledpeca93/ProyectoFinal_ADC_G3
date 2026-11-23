const perfil = document.querySelector(".perfil");

function actualizarVolumen(control) {
  const salida = perfil.querySelector(`[data-volumen="${CSS.escape(control.id)}"]`);
  if (salida) salida.value = `${control.value} %`;
}

function mostrarVolumenes(formulario) {
  for (const control of formulario.querySelectorAll('input[type="range"]')) {
    actualizarVolumen(control);
  }
}

mostrarVolumenes(perfil.querySelector("[data-formulario-perfil]"));
perfil.addEventListener("input", (evento) => {
  if (evento.target.matches('input[type="range"]')) actualizarVolumen(evento.target);
});

perfil.addEventListener("submit", async (evento) => {
  const formulario = evento.target;
  if (!formulario.matches("[data-formulario-perfil]")) return;
  evento.preventDefault();

  const boton = formulario.querySelector('button[type="submit"]');
  if (boton.disabled) return;
  const error = perfil.querySelector("[data-error-guardado]");
  error.hidden = true;
  boton.disabled = true;

  try {
    const respuesta = await fetch(formulario.action, {
      method: "POST",
      body: new FormData(formulario),
    });
    if (!respuesta.ok) throw new Error("No se pudo guardar el perfil");

    const pagina = new DOMParser().parseFromString(await respuesta.text(), "text/html");
    const preferencias = pagina.querySelector("#preferencias");
    if (!preferencias && respuesta.redirected) {
      location.assign(respuesta.url);
      return;
    }
    if (!preferencias) throw new Error("La respuesta no contiene las preferencias");

    const titulo = pagina.querySelector("#mi-perfil h1");
    perfil.querySelector("#mi-perfil h1").textContent = titulo.textContent;
    perfil.querySelector("#preferencias").replaceWith(preferencias);
    mostrarVolumenes(preferencias);

    const reproductor = document.querySelector("[data-musica-fondo]");
    const musicaGuardada = pagina.querySelector("[data-musica-fondo]");
    reproductor.dataset.volumenMusica = musicaGuardada.dataset.volumenMusica;
    reproductor.dataset.silenciado = musicaGuardada.dataset.silenciado;
    reproductor.dispatchEvent(new Event("preferencias-musica"));

    const destino = preferencias.querySelector('[aria-invalid="true"], [role="status"]');
    if (destino) {
      destino.tabIndex = -1;
      destino.focus({ preventScroll: true });
    }
  } catch {
    error.textContent = "No se pudo confirmar el guardado. Vuelve a intentarlo.";
    error.hidden = false;
  } finally {
    boton.disabled = false;
  }
});
