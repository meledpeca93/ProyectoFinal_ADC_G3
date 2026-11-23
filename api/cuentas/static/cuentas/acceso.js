for (const boton of document.querySelectorAll("[data-ver-contrasena]")) {
  const campo = document.getElementById(boton.getAttribute("aria-controls"));
  boton.hidden = false;

  boton.addEventListener("click", () => {
    const mostrar = campo.type === "password";
    campo.type = mostrar ? "text" : "password";
    boton.textContent = mostrar ? "Ocultar" : "Mostrar";
  });
}
