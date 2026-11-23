for (const salida of document.querySelectorAll("[data-volumen]")) {
  const control = document.getElementById(salida.dataset.volumen);
  const actualizar = () => {
    salida.value = `${control.value} %`;
  };

  control.addEventListener("input", actualizar);
  actualizar();
}
