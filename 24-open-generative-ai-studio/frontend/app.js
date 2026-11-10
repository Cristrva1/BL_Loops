// Panel de Open Generative AI Studio. Todo texto que viene del modelo se inserta con textContent:
// se trata como datos, nunca como HTML.
const API_BASE = window.location.origin;
const NODES = ["ANALYZING_CONCEPT", "GENERATING_STORYBOARD", "RENDERING_ANIMATIC", "EVALUATING"];
const HEX = /^#[0-9a-fA-F]{6}$/;

const $ = (id) => document.getElementById(id);
const btnRun = $("btn-run");
const btnExport = $("btn-export");
const btnExpand = $("btn-expand");
const consoleLogs = $("console-logs");

// --- Pestañas -----------------------------------------------------------------------------
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => showTab(tab.dataset.tab));
});

function showTab(targetId) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === targetId));
  document.querySelectorAll(".tab-content").forEach((c) => c.classList.toggle("active", c.id === targetId));
}

// --- Utilidades ---------------------------------------------------------------------------
function log(message, type = "info") {
  const line = document.createElement("div");
  line.className = `log-line ${type}`;
  line.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
  consoleLogs.appendChild(line);
  consoleLogs.scrollTop = consoleLogs.scrollHeight;
}

function setPill(id, text, ok) {
  const pill = $(id);
  pill.textContent = text;
  pill.className = `pill ${ok ? "ok" : "warn"}`;
}

function setBanner(element, source, reason, okText) {
  element.hidden = false;
  if (source === "ollama") {
    element.textContent = okText;
    element.className = "banner ok";
  } else {
    element.textContent = `Fallback visible: ${reason || "motivo desconocido"}. Se muestran datos calibrados, no una decisión del modelo.`;
    element.className = "banner warn";
  }
}

async function errorDetail(response) {
  try {
    const body = await response.json();
    if (Array.isArray(body.detail)) return body.detail.map((d) => d.msg).join("; ");
    return body.detail || `HTTP ${response.status}`;
  } catch {
    return `HTTP ${response.status}`;
  }
}

// --- Nodos del pipeline -------------------------------------------------------------------
function updateNodes(state) {
  if (state === "COMPLETED") {
    NODES.forEach((n) => $(`node-${n}`).className = "node completed");
    return;
  }
  if (state === "FAILED") {
    const active = document.querySelector(".node.active");
    if (active) active.className = "node failed";
    return;
  }
  const index = NODES.indexOf(state);
  if (index === -1) return;
  NODES.forEach((n, i) => {
    $(`node-${n}`).className = i < index ? "node completed" : i === index ? "node active" : "node";
  });
}

// --- Storyboard ---------------------------------------------------------------------------
function renderShots(shots) {
  const container = $("shots");
  container.replaceChildren();
  shots.forEach((shot) => {
    const card = document.createElement("article");
    card.className = "shot";
    card.style.borderLeftColor = HEX.test(shot.accent_color) ? shot.accent_color : "#6366f1";

    const header = document.createElement("header");
    const number = document.createElement("strong");
    number.textContent = `Plano ${shot.shot_number}`;
    const meta = document.createElement("span");
    meta.textContent = `${shot.shot_type} · ${shot.camera_movement} · ${shot.duration_seconds} s`;
    header.append(number, meta);

    const title = document.createElement("h3");
    title.textContent = shot.headline;
    const description = document.createElement("p");
    description.textContent = shot.description || "(sin descripción)";
    const lighting = document.createElement("p");
    lighting.className = "hint";
    lighting.textContent = `Luz: ${shot.lighting}`;
    const prompt = document.createElement("p");
    prompt.className = "mono";
    prompt.textContent = shot.prompt_expansion || "(el modelo no entregó prompt)";

    card.append(header, title, description, lighting, prompt);
    container.appendChild(card);
  });
}

// --- Métricas -----------------------------------------------------------------------------
function showRender(render, evaluation) {
  $("metric-duration").textContent = `${render.duration} s`;
  $("metric-res").textContent = `${render.width}×${render.height} a ${render.fps} fps`;
  $("metric-size").textContent = `${(render.file_size_bytes / 1024).toFixed(1)} KB`;
  $("metric-time").textContent = `${render.render_elapsed_seconds} s`;
  if (evaluation) {
    const delta = evaluation.metrics.duration_delta_seconds;
    $("metric-eval").textContent = `${evaluation.success ? "Aprobada" : "No aprobada"} (desvío ${delta} s)`;
    $("metric-eval").className = evaluation.success ? "ok-text" : "warn-text";
    $("metric-source").textContent = evaluation.metrics.director_source;
    btnExport.disabled = false;
  }
  const video = $("output-video");
  video.src = `${API_BASE}/api/video?t=${Date.now()}`;
  video.load();
  $("video-hint").textContent = "Cada plano muestra tipo, movimiento, luz y prompt durante su duración real.";
}

function setStatus(text, kind = "") {
  $("metric-status").textContent = text;
  $("metric-status").className = kind;
}

// --- Eventos SSE --------------------------------------------------------------------------
function connectEvents() {
  // EventSource se reconecta solo; no se crean conexiones duplicadas.
  const source = new EventSource(`${API_BASE}/api/pipeline/events`);
  source.onopen = () => setPill("events-status", "Eventos: en vivo", true);
  source.onerror = () => setPill("events-status", "Eventos: reconectando…", false);
  source.onmessage = (message) => {
    const event = JSON.parse(message.data);
    const isFallback = event.data && event.data.director_source === "fallback";
    log(`[${event.node}] ${event.message}`, event.state === "FAILED" ? "error" : isFallback ? "warn" : "info");
    updateNodes(event.state);

    if (event.data && event.data.director_source) {
      setBanner($("source-banner"), event.data.director_source, event.data.fallback_reason, "Planos generados por Ollama y validados contra el contrato.");
      $("metric-source").textContent = event.data.director_source;
    }
    if (event.state === "RENDERING_ANIMATIC" && event.data && event.data.shots) {
      renderShots(event.data.shots);
      setStatus("Renderizando con FFmpeg…");
    }
    if (event.state === "COMPLETED") {
      btnRun.disabled = false;
      setStatus("Completado", "ok-text");
      showRender(event.data.render, event.data.eval);
    } else if (event.state === "FAILED") {
      btnRun.disabled = false;
      setStatus("Error", "warn-text");
      $("video-hint").textContent = event.message;
    }
  };
}

// --- Acciones -----------------------------------------------------------------------------
$("project-form").addEventListener("submit", async (submitEvent) => {
  submitEvent.preventDefault();
  btnRun.disabled = true;
  btnExport.disabled = true;
  $("export-result").textContent = "";
  setStatus("En curso…");
  const project = {
    title: $("title-input").value,
    narrative_concept: $("concept-input").value,
    total_duration_target: parseFloat($("duration-input").value),
  };
  if ($("model-select").value) project.model = $("model-select").value;
  try {
    const response = await fetch(`${API_BASE}/api/pipeline/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(project),
    });
    if (!response.ok) throw new Error(await errorDetail(response));
    const body = await response.json();
    log(`Pipeline iniciado con el modelo ${body.model}.`);
  } catch (err) {
    log(`No se pudo iniciar el pipeline: ${err.message}`, "error");
    setStatus("Rechazado", "warn-text");
    btnRun.disabled = false;
  }
});

btnExport.addEventListener("click", async () => {
  const response = await fetch(`${API_BASE}/api/export`, { method: "POST" });
  $("export-result").textContent = response.ok
    ? `Añadido a ${(await response.json()).path}`
    : `No se pudo exportar: ${await errorDetail(response)}`;
});

$("prompt-form").addEventListener("submit", async (submitEvent) => {
  submitEvent.preventDefault();
  btnExpand.disabled = true;
  btnExpand.textContent = "Expandiendo…";
  const request = { raw_idea: $("idea-input").value, style: $("style-input").value };
  if ($("model-select").value) request.model = $("model-select").value;
  try {
    const response = await fetch(`${API_BASE}/api/prompt/expand`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error(await errorDetail(response));
    const body = await response.json();
    $("prompt-result").hidden = false;
    setBanner($("prompt-source"), body.source, body.fallback_reason, `Prompt expandido por ${body.model}.`);
    $("prompt-positive").textContent = body.result.positive_prompt;
    $("prompt-negative").textContent = body.result.negative_prompt || "(vacío)";
    $("prompt-camera").textContent = body.result.camera_settings || "(vacío)";
    const palette = $("prompt-palette");
    palette.replaceChildren();
    body.result.mood_palette.forEach((color) => {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.textContent = color;
      if (HEX.test(color)) chip.style.setProperty("--swatch", color);
      palette.appendChild(chip);
    });
    log(`[PromptStudio] Origen: ${body.source}${body.fallback_reason ? ` (${body.fallback_reason})` : ""}`, body.source === "ollama" ? "info" : "warn");
  } catch (err) {
    log(`No se pudo expandir el prompt: ${err.message}`, "error");
  } finally {
    btnExpand.disabled = false;
    btnExpand.textContent = "Expandir prompt";
  }
});

// --- Estado real del backend: las píldoras solo muestran lo que se ha comprobado ------------
async function refreshStatus() {
  try {
    const status = await (await fetch(`${API_BASE}/api/status`)).json();
    setPill("ollama-status", status.ollama_reachable ? `Ollama: conectado (${status.model})` : "Ollama: no disponible (habrá fallback visible)", status.ollama_reachable);
    setPill("ffmpeg-status", status.ffmpeg_available && status.ffprobe_available ? "FFmpeg: disponible" : "FFmpeg/ffprobe: no encontrado", status.ffmpeg_available && status.ffprobe_available);
    if (status.run_in_progress) {
      btnRun.disabled = true;
      setStatus("En curso…");
    }
    if (!status.run_in_progress && status.last_render && status.last_render.success) {
      showRender(status.last_render, status.last_eval);
      setStatus("Último render completado", "ok-text");
    }
    // Al recargar la página se recupera el último storyboard que sigue en memoria del servidor.
    const storyboard = await fetch(`${API_BASE}/api/storyboard`);
    if (storyboard.ok) {
      const body = await storyboard.json();
      renderShots(body.shots);
      setBanner($("source-banner"), body.director_source, body.fallback_reason, "Planos generados por Ollama y validados contra el contrato.");
      $("metric-source").textContent = body.director_source;
    }
  } catch {
    setPill("ollama-status", "API no disponible", false);
  }
}

log("Panel listo. Pulsa «Generar storyboard y animatic» o prueba el Prompt Studio.");
refreshStatus();
connectEvents();
