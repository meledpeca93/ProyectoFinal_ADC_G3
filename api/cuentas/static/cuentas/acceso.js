const selectorFormulario = "[data-formulario-acceso]";
const portada = document.querySelector(".portada");
let formularioActual = document.querySelector(selectorFormulario);
let solicitudFormulario;

function ajustarPortada() {
  portada.style.removeProperty("--escala-portada");
  const altoDisponible = window.innerHeight;
  let escala = 1;
  for (let intento = 0; intento < 3; intento += 1) {
    const altoContenido = Math.ceil(portada.getBoundingClientRect().height);
    if (altoContenido <= altoDisponible) break;
    escala *= (altoDisponible - 1) / altoContenido;
    portada.style.setProperty("--escala-portada", escala);
  }
}

function prepararFormulario(formulario) {
  for (const boton of formulario.querySelectorAll("[data-ver-contrasena]")) {
    const campo = formulario.querySelector(`#${CSS.escape(boton.getAttribute("aria-controls"))}`);
    boton.hidden = false;

    boton.addEventListener("click", () => {
      const mostrar = campo.type === "password";
      campo.type = mostrar ? "text" : "password";
      boton.textContent = mostrar ? "Ocultar" : "Mostrar";
    });
  }
}

async function cambiarFormulario(url, agregarAlHistorial) {
  solicitudFormulario?.abort();
  const solicitud = new AbortController();
  solicitudFormulario = solicitud;

  try {
    const respuesta = await fetch(url, { signal: solicitud.signal });
    if (!respuesta.ok) throw new Error("No se pudo cargar el formulario");

    const pagina = new DOMParser().parseFromString(await respuesta.text(), "text/html");
    if (solicitud.signal.aborted) return;
    const formulario = pagina.querySelector(selectorFormulario);
    if (!formulario) throw new Error("La página no contiene un formulario de acceso");

    prepararFormulario(formulario);
    if (agregarAlHistorial) history.pushState(null, "", url);
    formularioActual.replaceWith(formulario);
    formularioActual = formulario;
    document.title = pagina.title;
    ajustarPortada();
    formulario.querySelector("h2").focus({ preventScroll: true });
  } catch {
    if (!solicitud.signal.aborted) location.href = url;
  }
}

if (formularioActual) {
  prepararFormulario(formularioActual);
  ajustarPortada();
  window.addEventListener("resize", ajustarPortada);

  document.addEventListener("click", (evento) => {
    const enlace = evento.target.closest("[data-cambiar-formulario]");
    if (!enlace || evento.defaultPrevented || evento.button !== 0 ||
        evento.metaKey || evento.ctrlKey || evento.shiftKey || evento.altKey) return;

    evento.preventDefault();
    cambiarFormulario(enlace.href, true);
  });

  window.addEventListener("popstate", () => cambiarFormulario(location.href, false));
}

const mina = document.querySelector(".portada__arte");

if (mina) {
  try {
    const preferencia = localStorage.getItem("buscaminas.movimientoMina");
    if (preferencia === "activo" || preferencia === "pausa") {
      mina.dataset.movimiento = preferencia;
    }
  } catch {
    // Sin almacenamiento local se usa la preferencia de movimiento del sistema.
  }
}
