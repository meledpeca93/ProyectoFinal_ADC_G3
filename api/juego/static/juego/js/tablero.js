/* Tablero jugable - Integrante 04: 
 * El servidor Django es la única autoridad sobre minas, victoria y tiempo.
 */
(() => {
  "use strict";
  const root = document.getElementById("bmGame");
  if (!root) return;

  const $ = (id) => document.getElementById(id);
  const board = $("bmBoard");
  const message = $("bmMessage");
  const csrf = root.querySelector("input[name=csrfmiddlewaretoken]")?.value || getCookie("csrftoken");
  const placeholder = "00000000-0000-0000-0000-000000000000";
  const urls = {
    nueva: root.dataset.nuevaUrl,
    estado: root.dataset.estadoUrl,
    accion: root.dataset.accionUrl,
    abandonar: root.dataset.abandonarUrl
  };
  const storageKey = `buscaminas:partida:${root.dataset.usuario || "jugador"}`;
  const levels = {
    FACIL: { label: "Fácil", rows: 8, cols: 8, mines: 10, seconds: 240 },
    NORMAL: { label: "Normal", rows: 10, cols: 10, mines: 18, seconds: 360 },
    DIFICIL: { label: "Difícil", rows: 12, cols: 12, mines: 30, seconds: 480 }
  };
  let state = null;
  let selectedLevel = (root.dataset.nivelInicial || "NORMAL").toUpperCase();
  let flagMode = false;
  let busy = false;
  let pollHandle = null;
  let pressHandle = null;
  let longPressTriggered = false;
  let focusedIndex = 0;

  function getCookie(name) {
    const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
    return match ? decodeURIComponent(match[1]) : "";
  }
  function endpoint(template, id) { return template.replace(placeholder, encodeURIComponent(id)); }
  function formatTime(seconds) {
    const n = Math.max(0, Number(seconds) || 0);
    return `${String(Math.floor(n / 60)).padStart(2, "0")}:${String(n % 60).padStart(2, "0")}`;
  }
  function say(text, kind = "info") {
    message.textContent = text;
    message.dataset.kind = kind;
  }
  async function request(url, options = {}) {
    const headers = { "Accept": "application/json", ...(options.headers || {}) };
    if (options.method && options.method !== "GET") {
      headers["Content-Type"] = "application/json";
      if (csrf) headers["X-CSRFToken"] = csrf;
    }
    const response = await fetch(url, { credentials: "same-origin", ...options, headers });
    let data;
    try { data = await response.json(); } catch (_) { data = {}; }
    if (!response.ok && response.status !== 409) {
      const error = new Error(data.error || `Error del servidor (${response.status})`);
      error.status = response.status;
      error.data = data;
      throw error;
    }
    return { data, status: response.status };
  }
  function saveSession() {
    if (!state?.partida_id) return;
    try { localStorage.setItem(storageKey, JSON.stringify({ id: state.partida_id, nivel: state.dificultad || selectedLevel })); } catch (_) { /* almacenamiento opcional */ }
  }
  function clearSession() {
    try { localStorage.removeItem(storageKey); } catch (_) { /* almacenamiento opcional */ }
  }
  function stopPolling() {
    if (pollHandle) window.clearInterval(pollHandle);
    pollHandle = null;
  }
  function startPolling() {
    stopPolling();
    pollHandle = window.setInterval(() => {
      if (state?.partida_id && !busy && state.estado === "EN_CURSO") refreshState(true);
    }, 3000);
  }
  function isFinished() { return !state || state.estado !== "EN_CURSO"; }
  function render() {
    if (!state) return;
    const matrix = Array.isArray(state.tablero) ? state.tablero : [];
    const rows = matrix.length || Number(state.filas) || levels[selectedLevel].rows;
    const cols = matrix[0]?.length || Number(state.columnas) || levels[selectedLevel].cols;
    const cfg = levels[(state.dificultad || selectedLevel).toUpperCase()] || levels.NORMAL;
    const totalMines = Number(state.minas ?? cfg.mines);
    const flags = Number(state.banderas || 0);
    const revealedSafe = matrix.flat().filter(v => typeof v === "number" && v >= 0).length;
    const safeTotal = rows * cols - totalMines;
    const remaining = Math.max(0, Number(state.segundos_restantes ?? cfg.seconds));
    const elapsed = Math.max(0, cfg.seconds - remaining);
    $("bmLevelName").textContent = cfg.label;
    $("bmMineCount").textContent = totalMines;
    $("bmFlagCount").textContent = flags;
    $("bmTimer").textContent = formatTime(remaining);
    $("bmElapsed").textContent = formatTime(elapsed);
    $("bmProgress").textContent = `${revealedSafe} / ${safeTotal}`;
    $("bmMoves").textContent = Number(state.movimientos || 0);
    $("bmRemaining").textContent = Math.max(0, totalMines - flags);
    $("bmStatus").textContent = state.estado || "EN_CURSO";
    board.style.setProperty("--bm-cols", cols);
    board.setAttribute("aria-label", `Tablero ${rows} por ${cols}`);
    board.replaceChildren();

    matrix.forEach((row, f) => row.forEach((value, c) => {
      const cell = document.createElement("button");
      const index = f * cols + c;
      cell.type = "button";
      cell.className = "bm-cell";
      cell.dataset.row = f;
      cell.dataset.col = c;
      cell.dataset.index = index;
      cell.setAttribute("aria-label", cellLabel(value, f, c));
      if (value === "B") {
        cell.textContent = "🚩";
        cell.classList.add("is-flag");
      } else if (value === -1) {
        cell.textContent = "💣";
        cell.classList.add("is-open", "is-mine");
      } else if (typeof value === "number") {
        cell.textContent = value === 0 ? "" : String(value);
        cell.classList.add("is-open");
        cell.dataset.number = value;
        if (value === 0) cell.setAttribute("aria-label", `Fila ${f + 1}, columna ${c + 1}, casilla vacía descubierta`);
      }
      cell.disabled = isFinished() || (value !== null && value !== "B");
      if (state.estado === "PERDIDA" && value === -1) cell.classList.add("is-exploded");
      board.appendChild(cell);
    }));

    document.querySelectorAll("[data-level]").forEach(button => {
      const active = button.dataset.level === (state.dificultad || selectedLevel).toUpperCase();
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    $("bmFlagMode").setAttribute("aria-pressed", String(flagMode));
    $("bmNewGame").disabled = busy;
    $("bmAbandon").disabled = busy || isFinished();
    $("bmFlagMode").disabled = isFinished();
    if (isFinished()) {
      stopPolling();
      if (state.resultado_url) {
        clearSession();
        say(resultMessage(state.estado), state.estado);
        // El usuario puede ver el tablero final unos instantes antes de ir al resumen.
        window.setTimeout(() => { window.location.assign(state.resultado_url); }, 1800);
      } else {
        say(resultMessage(state.estado), state.estado);
      }
    }
  }
  function cellLabel(value, f, c) {
    const pos = `Fila ${f + 1}, columna ${c + 1}`;
    if (value === "B") return `${pos}, bandera`;
    if (value === -1) return `${pos}, mina`;
    if (typeof value === "number") return `${pos}, ${value ? `${value} minas cercanas` : "sin minas cercanas"}`;
    return `${pos}, oculta`;
  }
  function resultMessage(status) {
    return ({ GANADA: "¡Felicidades! Has ganado la partida.", PERDIDA: "Has encontrado una mina. Fin de la partida.", TIEMPO_AGOTADO: "Se agotó el tiempo de la partida.", ABANDONADA: "Has abandonado la partida." })[status] || "La partida ha finalizado.";
  }
  async function createGame(level = selectedLevel) {
    if (busy) return;
    busy = true; stopPolling(); selectedLevel = levels[level] ? level : "NORMAL";
    say("Creando una nueva partida…");
    try {
      const { data } = await request(urls.nueva, { method: "POST", body: JSON.stringify({ nivel: selectedLevel }) });
      state = { ...data, dificultad: data.nivel, tablero: [], banderas: 0, descubiertas: 0, movimientos: 0, segundos_restantes: data.tiempo };
      saveSession();
      render();
      say("Partida lista. El primer clic será seguro.");
      await refreshState(false);
      startPolling();
    } catch (error) {
      say(`${error.message}. Comprueba que hayas iniciado sesión y que Django esté funcionando.`, "error");
    } finally { busy = false; renderIfReady(); }
  }
  function renderIfReady() { if (state) render(); }
  async function restoreOrCreate() {
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem(storageKey) || "null"); } catch (_) { saved = null; }
    if (saved?.id) {
      selectedLevel = (saved.nivel || selectedLevel).toUpperCase();
      state = { partida_id: saved.id, dificultad: selectedLevel, estado: "EN_CURSO", tablero: [] };
      say("Recuperando tu partida…");
      try { await refreshState(false); if (!isFinished()) startPolling(); return; }
      catch (_) { clearSession(); state = null; }
    }
    await createGame(selectedLevel);
  }
  async function refreshState(silent = false) {
    if (!state?.partida_id) return;
    try {
      const { data } = await request(endpoint(urls.estado, state.partida_id), { method: "GET" });
      state = { ...state, ...data };
      saveSession(); render();
    } catch (error) {
      if (!silent) say(`No se pudo recuperar el estado: ${error.message}`, "error");
      throw error;
    }
  }
  async function performAction(f, c, type) {
    if (!state?.partida_id || busy || isFinished()) return;
    const row = state.tablero?.[f];
    const current = row?.[c];
    if (type === "DESCUBRIR" && current !== null && current !== undefined) return;
    if (type === "BANDERA" && typeof current === "number") return;
    busy = true;
    const number = Number(state.movimientos || 0) + 1;
    const payload = { numero: number, tipo: type, f, c };
    try {
      // El mismo número y payload se conservan si hay un fallo de red: el endpoint es idempotente.
      const { data } = await request(endpoint(urls.accion, state.partida_id), { method: "POST", body: JSON.stringify(payload) });
      state = { ...state, ...data };
      saveSession(); render();
      if (state.estado === "EN_CURSO") say(type === "BANDERA" ? "Bandera actualizada." : "Casilla descubierta.");
    } catch (error) {
      say(error.message || "No se pudo registrar el movimiento.", "error");
      if (error.status === 409 || error.status >= 500) {
        // Reconciliar con el servidor antes de aceptar otra jugada.
        try { await refreshState(true); } catch (_) { /* se conserva la sesión para reintentar */ }
      }
    } finally { busy = false; renderIfReady(); }
  }
  async function abandonGame() {
    if (!state?.partida_id || busy || isFinished()) return;
    if (!window.confirm("¿Seguro que deseas abandonar esta partida?")) return;
    busy = true;
    try {
      const { data } = await request(endpoint(urls.abandonar, state.partida_id), { method: "POST", body: "{}" });
      state = { ...state, ...data }; clearSession(); render();
      if (state.resultado_url) window.setTimeout(() => window.location.assign(state.resultado_url), 900);
    } catch (error) { say(error.message, "error"); }
    finally { busy = false; renderIfReady(); }
  }
  function toggleFlagMode() {
    flagMode = !flagMode;
    $("bmFlagMode").setAttribute("aria-pressed", String(flagMode));
    say(flagMode ? "Modo bandera activado. Selecciona una casilla." : "Modo bandera desactivado.");
  }
  function coordsFrom(target) {
    const cell = target.closest(".bm-cell");
    if (!cell || !board.contains(cell)) return null;
    return { f: Number(cell.dataset.row), c: Number(cell.dataset.col), cell };
  }
  board.addEventListener("click", event => {
    const pos = coordsFrom(event.target); if (!pos) return;
    if (longPressTriggered) { longPressTriggered = false; event.preventDefault(); return; }
    performAction(pos.f, pos.c, flagMode ? "BANDERA" : "DESCUBRIR");
  });
  board.addEventListener("contextmenu", event => {
    const pos = coordsFrom(event.target); if (!pos) return;
    event.preventDefault(); performAction(pos.f, pos.c, "BANDERA");
  });
  board.addEventListener("pointerdown", event => {
    const pos = coordsFrom(event.target);
    if (!pos || event.pointerType === "mouse" || event.button !== 0) return;
    longPressTriggered = false;
    pressHandle = window.setTimeout(() => {
      longPressTriggered = true;
      performAction(pos.f, pos.c, "BANDERA");
    }, 500);
  });
  ["pointerup", "pointerleave", "pointercancel"].forEach(name => board.addEventListener(name, () => {
    if (pressHandle) window.clearTimeout(pressHandle);
    pressHandle = null;
  }));
  board.addEventListener("keydown", event => {
    const pos = coordsFrom(event.target); if (!pos) return;
    const buttons = [...board.querySelectorAll(".bm-cell")];
    const rows = state?.tablero?.length || 0; const cols = state?.tablero?.[0]?.length || 0;
    let next = pos.f * cols + pos.c;
    if (event.key === "ArrowRight") next++;
    else if (event.key === "ArrowLeft") next--;
    else if (event.key === "ArrowDown") next += cols;
    else if (event.key === "ArrowUp") next -= cols;
    else if (event.key.toLowerCase() === "f") { event.preventDefault(); performAction(pos.f, pos.c, "BANDERA"); return; }
    else return;
    event.preventDefault();
    next = Math.max(0, Math.min(rows * cols - 1, next));
    buttons[next]?.focus();
  });
  document.querySelectorAll("[data-level]").forEach(button => button.addEventListener("click", () => {
    const level = button.dataset.level;
    if (level && level !== selectedLevel && window.confirm("¿Iniciar una nueva partida con esta dificultad?")) createGame(level);
  }));
  $("bmNewGame").addEventListener("click", () => {
    if (window.confirm("¿Deseas iniciar una nueva partida? Se cerrará la partida actual.")) createGame(selectedLevel);
  });
  $("bmFlagMode").addEventListener("click", toggleFlagMode);
  $("bmAbandon").addEventListener("click", abandonGame);
  window.addEventListener("online", () => { if (state?.partida_id) refreshState(true).catch(() => {}); });
  restoreOrCreate();
})();
