// Cliente Frontend para Remotion Superpowers Studio
const API_BASE = window.location.origin;

const btnRun = document.getElementById("btn-run");
const topicInput = document.getElementById("topic-input");
const durationInput = document.getElementById("duration-input");
const modelSelect = document.getElementById("model-select");

const metricDuration = document.getElementById("metric-duration");
const metricFrames = document.getElementById("metric-frames");
const metricTime = document.getElementById("metric-time");
const metricSize = document.getElementById("metric-size");
const metricStatus = document.getElementById("metric-status");

const outputVideo = document.getElementById("output-video");
const scenesCodeBlock = document.getElementById("scenes-code-block");
const consoleLogs = document.getElementById("console-logs");

// Tabs
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    tab.classList.add("active");
    const targetId = tab.getAttribute("data-tab");
    document.getElementById(targetId).classList.add("active");
  });
});

function log(message, type = "info") {
  const line = document.createElement("div");
  line.className = `log-line ${type}`;
  line.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
  consoleLogs.appendChild(line);
  consoleLogs.scrollTop = consoleLogs.scrollHeight;
}

function updateNodeState(activeState) {
  const nodes = [
    "ANALYZING_BRIEF",
    "PLANNING_SCENES",
    "CALCULATING_FRAMES",
    "WRITING_REACT_PROPS",
    "RENDERING_VIDEO",
    "EVALUATING"
  ];
  let found = false;
  nodes.forEach(node => {
    const el = document.getElementById(`node-${node}`);
    if (!el) return;
    if (node === activeState) {
      el.classList.add("active");
      el.classList.remove("completed");
      found = true;
    } else if (!found) {
      el.classList.add("completed");
      el.classList.remove("active");
    } else {
      el.classList.remove("active", "completed");
    }
  });

  if (activeState === "COMPLETED") {
    nodes.forEach(node => {
      const el = document.getElementById(`node-${node}`);
      if (el) {
        el.classList.remove("active");
        el.classList.add("completed");
      }
    });
  }
}

async function loadScenes() {
  try {
    const res = await fetch(`${API_BASE}/api/scenes`);
    if (res.ok) {
      const data = await res.json();
      scenesCodeBlock.textContent = JSON.stringify(data, null, 2);
    }
  } catch (e) {
    // ignore
  }
}

// SSE Connection
let eventsLost = false;

function connectEvents() {
  const eventSource = new EventSource(`${API_BASE}/api/pipeline/events`);
  eventSource.onmessage = (e) => {
    const event = JSON.parse(e.data);
    log(`[${event.node}] ${event.message}`, event.state === "FAILED" ? "error" : "info");
    updateNodeState(event.state);

    if (event.state === "COMPLETED") {
      btnRun.disabled = false;
      metricStatus.textContent = "Completado";
      metricStatus.className = "status-ready";
      if (event.data.render) {
        metricDuration.textContent = `${event.data.render.duration}s`;
        metricFrames.textContent = `${event.data.render.total_frames}`;
        metricTime.textContent = `${event.data.render.render_elapsed_seconds}s`;
        metricSize.textContent = `${(event.data.render.file_size_bytes / 1024).toFixed(1)} KB`;
      }
      outputVideo.src = `${API_BASE}/api/video?t=${Date.now()}`;
      outputVideo.load();
      loadScenes();
    } else if (event.state === "FAILED") {
      btnRun.disabled = false;
      metricStatus.textContent = "Error";
      metricStatus.style.color = "#ef4444";
    }
  };
  // EventSource se reconecta solo: abrir otra conexión aquí duplicaría cada evento.
  eventSource.onopen = () => {
    eventsLost = false;
  };
  eventSource.onerror = () => {
    if (!eventsLost) log("Conexión de eventos perdida; el navegador reintentará automáticamente.", "error");
    eventsLost = true;
  };
}

btnRun.addEventListener("click", async () => {
  btnRun.disabled = true;
  metricStatus.textContent = "Renderizando...";
  metricStatus.className = "";
  log("Iniciando pipeline Remotion Superpowers con Ollama...", "info");

  const brief = {
    topic: topicInput.value,
    target_duration: parseFloat(durationInput.value),
    model: modelSelect.value,
  };

  try {
    const res = await fetch(`${API_BASE}/api/pipeline/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(brief)
    });
    if (!res.ok) {
      // 409: ya hay un render en curso; 422: el brief no cumple el contrato (p. ej. modelo cloud).
      const body = await res.json().catch(() => ({}));
      const detail = Array.isArray(body.detail) ? body.detail.map((d) => d.msg).join("; ") : body.detail;
      throw new Error(detail || `HTTP ${res.status}`);
    }
  } catch (err) {
    log(`Error al iniciar pipeline: ${err.message}`, "error");
    btnRun.disabled = false;
  }
});

// Estado real del backend: las píldoras no muestran nada que no se haya comprobado.
async function refreshStatus() {
  const ollamaPill = document.getElementById("ollama-status");
  const rendererPill = document.getElementById("remotion-status");
  try {
    const res = await fetch(`${API_BASE}/api/status`);
    const status = await res.json();
    ollamaPill.textContent = status.ollama_reachable
      ? "Ollama: conectado"
      : "Ollama: no disponible (se usarán escenas calibradas)";
    ollamaPill.className = `status-pill ${status.ollama_reachable ? "status-ready" : "status-warning"}`;
    rendererPill.textContent = status.npx_available ? "npx: disponible" : "npx: no encontrado";
    rendererPill.className = `status-pill ${status.npx_available ? "status-ready" : "status-warning"}`;
  } catch (err) {
    ollamaPill.textContent = "API no disponible";
    ollamaPill.className = "status-pill status-warning";
  }
}

refreshStatus();
connectEvents();
loadScenes();
