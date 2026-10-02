// Cliente Frontend para HyperFrames Video Studio
const API_BASE = window.location.origin;

const btnRun = document.getElementById("btn-run");
const topicInput = document.getElementById("topic-input");
const durationInput = document.getElementById("duration-input");
const modelSelect = document.getElementById("model-select");

const metricDuration = document.getElementById("metric-duration");
const metricTime = document.getElementById("metric-time");
const metricSize = document.getElementById("metric-size");
const metricStatus = document.getElementById("metric-status");

const outputVideo = document.getElementById("output-video");
const htmlFrame = document.getElementById("html-preview-frame");
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
    "GENERATING_SCRIPT",
    "BUILDING_COMPOSITION",
    "VALIDATING_LINT",
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

// SSE Connection
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
        metricTime.textContent = `${event.data.render.render_elapsed_seconds}s`;
        metricSize.textContent = `${(event.data.render.file_size_bytes / 1024).toFixed(1)} KB`;
      }
      // Actualizar video e iframe
      outputVideo.src = `${API_BASE}/api/video?t=${Date.now()}`;
      outputVideo.load();
      htmlFrame.src = `${API_BASE}/api/composition/html?t=${Date.now()}`;
    } else if (event.state === "FAILED") {
      btnRun.disabled = false;
      metricStatus.textContent = "Error";
      metricStatus.style.color = "#ef4444";
    }
  };
  eventSource.onerror = () => {
    setTimeout(connectEvents, 3000);
  };
}

btnRun.addEventListener("click", async () => {
  btnRun.disabled = true;
  metricStatus.textContent = "Renderizando...";
  metricStatus.className = "";
  log("Iniciando generación con IA local...", "info");

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
      throw new Error(`HTTP error: ${res.status}`);
    }
  } catch (err) {
    log(`Error al iniciar pipeline: ${err.message}`, "error");
    btnRun.disabled = false;
  }
});

connectEvents();
