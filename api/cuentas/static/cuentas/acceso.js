for (const boton of document.querySelectorAll("[data-ver-contrasena]")) {
  const campo = document.getElementById(boton.getAttribute("aria-controls"));
  boton.hidden = false;

  boton.addEventListener("click", () => {
    const mostrar = campo.type === "password";
    campo.type = mostrar ? "text" : "password";
    boton.textContent = mostrar ? "Ocultar" : "Mostrar";
  });
}

const controlMina = document.querySelector("[data-control-mina]");

if (controlMina) {
  const mina = document.querySelector(".portada__arte");
  const movimientoReducido = matchMedia("(prefers-reduced-motion: reduce)");
  const claveMovimiento = "buscaminas.movimientoMina";

  try {
    const preferencia = localStorage.getItem(claveMovimiento);
    if (preferencia === "activo" || preferencia === "pausa") {
      mina.dataset.movimiento = preferencia;
    }
  } catch {
    // Algunas vistas previas restringen el almacenamiento local.
  }

  const pausada = () => mina.dataset.movimiento === "pausa" ||
    (movimientoReducido.matches && mina.dataset.movimiento !== "activo");
  const actualizarControl = () => {
    controlMina.textContent = pausada() ? "Animar mina" : "Pausar mina";
  };

  controlMina.addEventListener("click", () => {
    mina.dataset.movimiento = pausada() ? "activo" : "pausa";
    try {
      localStorage.setItem(claveMovimiento, mina.dataset.movimiento);
    } catch {
      // La elección sigue funcionando durante esta visita.
    }
    actualizarControl();
  });
  movimientoReducido.addEventListener("change", actualizarControl);
  actualizarControl();
  controlMina.hidden = false;
}
