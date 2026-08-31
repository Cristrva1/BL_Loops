import { useMemo, useState } from "react";
import {
  Background,
  BackgroundVariant,
  Controls,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";
import { ApiError, analyzeIntake, buildDraft, exportArtifact } from "./api";
import type {
  Artifact,
  ArtifactType,
  ExportResult,
  FactoryIntake,
  FlowEvent,
  FlowStatus,
  GuidanceResult,
} from "./types";

const EMPTY_INTAKE: FactoryIntake = {
  artifact_type: "prompt",
  idea: "",
  title: null,
  audience: null,
  context: null,
  input_name: null,
  output_format: null,
  success_criteria: [],
  constraints: [],
  source_refs: [],
  allowed_tools: [],
  tools_confirmed: false,
  requires_human_approval: true,
};

const EXAMPLE_INTAKE: FactoryIntake = {
  artifact_type: "prompt",
  idea: "Crear una instrucción que identifique posibles archivos duplicados sin modificar el sistema de archivos.",
  title: "Detector seguro de duplicados",
  audience: "Persona con conocimientos básicos de PowerShell",
  context:
    "Se analizará un inventario sintético de archivos locales y la revisión será exclusivamente de lectura.",
  input_name: "folder_inventory",
  output_format: "json",
  success_criteria: [
    "Cada candidato incluye sus rutas y la evidencia de coincidencia",
    "Los casos inciertos quedan marcados para revisión humana",
    "La salida no propone borrar ni mover archivos",
  ],
  constraints: [
    "Solo lectura",
    "No borrar, mover ni sobrescribir",
    "No asumir que dos nombres iguales implican contenido igual",
  ],
  source_refs: ["docs/CASOS_DE_EVALUACION.md#F-PROMPT-001"],
  allowed_tools: [],
  tools_confirmed: false,
  requires_human_approval: true,
};

const STAGES: Array<Pick<FlowEvent, "node_id" | "title" | "detail">> = [
  {
    node_id: "capture",
    title: "Capturar intención",
    detail: "La idea es un dato, no una orden ejecutable.",
  },
  {
    node_id: "clarify",
    title: "Cerrar huecos",
    detail: "Preguntas explicadas antes de construir.",
  },
  {
    node_id: "contract",
    title: "Construir contrato",
    detail: "PromptSpec, AgentSpec o SkillSpec.",
  },
  {
    node_id: "validate",
    title: "Validar esquema",
    detail: "Tipos, límites, permisos y parada.",
  },
  {
    node_id: "export",
    title: "Exportar local",
    detail: "JSON con huella dentro de .local.",
  },
];

const STATUS_LABELS: Record<FlowStatus, string> = {
  idle: "Sin iniciar",
  queued: "En espera",
  running: "Procesando",
  waiting: "Falta información",
  retrying: "Reintentando",
  done: "Completado",
  failed: "Falló",
  blocked: "Bloqueado",
};

type BusyAction = "analyze" | "build" | "export" | null;

function toLines(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function initialEvents(): FlowEvent[] {
  return STAGES.map((stage, index) => ({
    ...stage,
    sequence: index + 1,
    status: "idle",
  }));
}

function statusColor(status: FlowStatus): string {
  const colors: Record<FlowStatus, string> = {
    idle: "#94a3b8",
    queued: "#3b82f6",
    running: "#f59e0b",
    waiting: "#8b5cf6",
    retrying: "#f97316",
    done: "#0f9f78",
    failed: "#dc3545",
    blocked: "#8b1e3f",
  };
  return colors[status];
}

function FlowBoard({ events }: { events: FlowEvent[] }) {
  const nodes = useMemo<Node[]>(
    () =>
      events.map((event, index) => ({
        id: event.node_id,
        position: { x: index * 270, y: index % 2 === 0 ? 40 : 170 },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
        draggable: false,
        selectable: true,
        data: {
          label: (
            <div className="flow-node-label">
              <div className="flow-node-topline">
                <span className="node-number">0{event.sequence}</span>
                <span className={`status-pill status-${event.status}`}>
                  {STATUS_LABELS[event.status]}
                </span>
              </div>
              <strong>{event.title}</strong>
              <span>{event.detail}</span>
            </div>
          ),
        },
        style: {
          width: 220,
          minHeight: 126,
          padding: 0,
          borderRadius: 18,
          border: `2px solid ${statusColor(event.status)}`,
          background: "#fffdf7",
          boxShadow: "0 14px 36px rgba(15, 23, 42, 0.1)",
        },
      })),
    [events],
  );

  const edges = useMemo<Edge[]>(
    () =>
      events.slice(0, -1).map((event, index) => {
        const next = events[index + 1];
        const active = event.status === "done" && next.status !== "idle";
        return {
          id: `${event.node_id}-${next.node_id}`,
          source: event.node_id,
          target: next.node_id,
          animated: next.status === "running" || next.status === "queued",
          markerEnd: { type: MarkerType.ArrowClosed, color: active ? "#0f9f78" : "#cbd5e1" },
          style: {
            stroke: active ? "#0f9f78" : "#cbd5e1",
            strokeWidth: active ? 3 : 2,
          },
        };
      }),
    [events],
  );

  return (
    <div className="flow-canvas" aria-label="Mapa visual de la fábrica">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.18 }}
        minZoom={0.45}
        maxZoom={1.3}
        nodesConnectable={false}
        elementsSelectable
        proOptions={{ hideAttribution: false }}
      >
        <Background variant={BackgroundVariant.Dots} gap={18} size={1.4} color="#d8ded8" />
        <Controls showInteractive={false} />
        <MiniMap
          pannable
          zoomable
          nodeColor={(node) => {
            const event = events.find((item) => item.node_id === node.id);
            return statusColor(event?.status ?? "idle");
          }}
          maskColor="rgba(247, 244, 234, 0.75)"
        />
      </ReactFlow>
    </div>
  );
}

function QuestionPanel({ guidance }: { guidance: GuidanceResult | null }) {
  if (!guidance) {
    return (
      <div className="empty-state compact">
        <span className="empty-index">?</span>
        <div>
          <strong>Las preguntas aún no se calculan</strong>
          <p>Completa lo que sepas y pulsa “Analizar intención”.</p>
        </div>
      </div>
    );
  }

  if (guidance.ready) {
    return (
      <div className="ready-message" role="status">
        <span aria-hidden="true">✓</span>
        <div>
          <strong>Briefing completo</strong>
          <p>Ya puede convertirse en un contrato tipado.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="question-list" aria-live="polite">
      {guidance.questions.map((question, index) => (
        <article className="question-card" key={question.question_id}>
          <span className="question-number">{index + 1}</span>
          <div>
            <strong>{question.prompt}</strong>
            <p>{question.why}</p>
            <small>Ejemplo: {question.example}</small>
          </div>
        </article>
      ))}
    </div>
  );
}

function ArtifactPreview({
  artifact,
  exportResult,
}: {
  artifact: Artifact | null;
  exportResult: ExportResult | null;
}) {
  if (!artifact) {
    return (
      <div className="empty-state preview-empty">
        <span className="empty-index">{`{ }`}</span>
        <div>
          <strong>Aquí aparecerá el contrato</strong>
          <p>No es una respuesta del modelo: es una estructura validada.</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="artifact-summary">
        <div>
          <span>Tipo</span>
          <strong>{artifact.artifact_type} spec</strong>
        </div>
        <div>
          <span>Huella</span>
          <code>{artifact.content_hash.slice(0, 12)}…</code>
        </div>
      </div>
      {exportResult && (
        <div className="export-success" role="status">
          <strong>Exportación local completada</strong>
          <code>{exportResult.relative_path}</code>
        </div>
      )}
      <pre className="json-preview" tabIndex={0}>
        {JSON.stringify(artifact, null, 2)}
      </pre>
    </>
  );
}

export default function App() {
  const [intake, setIntake] = useState<FactoryIntake>(EMPTY_INTAKE);
  const [guidance, setGuidance] = useState<GuidanceResult | null>(null);
  const [events, setEvents] = useState<FlowEvent[]>(initialEvents);
  const [artifact, setArtifact] = useState<Artifact | null>(null);
  const [exportResult, setExportResult] = useState<ExportResult | null>(null);
  const [explanation, setExplanation] = useState<string[]>([]);
  const [busy, setBusy] = useState<BusyAction>(null);
  const [error, setError] = useState<string | null>(null);

  const readiness = Math.round((guidance?.readiness ?? 0) * 100);
  const needsToolDecision = intake.artifact_type !== "prompt";

  function resetResult() {
    setGuidance(null);
    setEvents(initialEvents());
    setArtifact(null);
    setExportResult(null);
    setExplanation([]);
    setError(null);
  }

  function updateIntake(patch: Partial<FactoryIntake>) {
    setIntake((current) => ({ ...current, ...patch }));
    resetResult();
  }

  function loadExample() {
    setIntake({ ...EXAMPLE_INTAKE });
    resetResult();
  }

  async function handleAnalyze() {
    setBusy("analyze");
    setError(null);
    try {
      const result = await analyzeIntake(intake);
      setGuidance(result);
      setEvents(result.events);
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Backend no disponible. Confirma que Uvicorn escucha en el puerto 8011.",
      );
    } finally {
      setBusy(null);
    }
  }

  async function handleBuild() {
    setBusy("build");
    setError(null);
    try {
      const result = await buildDraft(intake);
      setArtifact(result.artifact);
      setEvents(result.events);
      setExplanation(result.explanation);
      setExportResult(null);
    } catch (caught) {
      if (caught instanceof ApiError) {
        const detail = caught.problem.detail;
        if (!Array.isArray(detail) && typeof detail === "object" && detail?.guidance) {
          setGuidance(detail.guidance);
          setEvents(detail.guidance.events);
        }
        setError(caught.message);
      } else {
        setError("No fue posible construir el contrato.");
      }
    } finally {
      setBusy(null);
    }
  }

  async function handleExport() {
    if (!artifact) return;
    setBusy("export");
    setError(null);
    try {
      const result = await exportArtifact(artifact);
      setExportResult(result);
      setEvents(result.events);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "No fue posible exportar el JSON.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Volver al inicio">
          <span className="brand-mark" aria-hidden="true">
            BL
          </span>
          <span>
            <strong>Prompt & Agent Factory</strong>
            <small>Laboratorio 01 · BL_Loops</small>
          </span>
        </a>
        <div className="topbar-badges" aria-label="Características de esta parte">
          <span className="badge badge-mint">100 % local</span>
          <span className="badge badge-blue">Parte 1</span>
          <span className="badge badge-outline">Sin IA todavía</span>
        </div>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <span className="eyebrow">Contratos antes de inferencia</span>
          <h1>Aprende a construir el plano antes de pedirle ayuda al modelo.</h1>
          <p>
            Una idea puede ser inspiradora y seguir siendo ambigua. Esta fábrica la convierte en
            un contrato que podemos leer, validar, exportar y —después— comparar entre modelos.
          </p>
          <div className="hero-actions">
            <button className="button primary" type="button" onClick={loadExample}>
              Cargar ejemplo didáctico
            </button>
            <a className="button ghost" href="#workspace">
              Empezar desde cero
            </a>
          </div>
        </div>
        <aside className="concept-card" aria-label="Concepto central">
          <span className="concept-number">01</span>
          <p>Idea</p>
          <span className="concept-arrow" aria-hidden="true">
            ↓
          </span>
          <p>Briefing</p>
          <span className="concept-arrow" aria-hidden="true">
            ↓
          </span>
          <p className="concept-result">Contrato verificable</p>
          <small>La IA local se incorpora después de esta frontera.</small>
        </aside>
      </section>

      <section className="lesson-strip" aria-label="Las cinco etapas">
        {STAGES.map((stage, index) => (
          <div key={stage.node_id}>
            <span>0{index + 1}</span>
            <p>{stage.title}</p>
          </div>
        ))}
      </section>

      <section className="workspace-section" id="workspace">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Taller interactivo</span>
            <h2>Construye tu primer contrato</h2>
          </div>
          <div className="progress-block" aria-label={`Preparación ${readiness} por ciento`}>
            <span>Preparación</span>
            <strong>{readiness}%</strong>
            <div className="progress-track">
              <span style={{ width: `${readiness}%` }} />
            </div>
          </div>
        </div>

        {error && (
          <div className="error-banner" role="alert">
            <strong>No pudimos completar el paso</strong>
            <span>{error}</span>
          </div>
        )}

        <div className="workspace-grid">
          <section className="panel form-panel" aria-labelledby="briefing-title">
            <div className="panel-heading">
              <div>
                <span className="panel-kicker">Entrada humana</span>
                <h3 id="briefing-title">Briefing</h3>
              </div>
              <button className="text-button" type="button" onClick={() => {
                setIntake(EMPTY_INTAKE);
                resetResult();
              }}>
                Limpiar
              </button>
            </div>

            <fieldset className="type-selector">
              <legend>¿Qué quieres diseñar?</legend>
              {(["prompt", "agent", "skill"] as ArtifactType[]).map((type) => (
                <button
                  type="button"
                  key={type}
                  className={intake.artifact_type === type ? "selected" : ""}
                  aria-pressed={intake.artifact_type === type}
                  onClick={() => updateIntake({
                    artifact_type: type,
                    tools_confirmed: type === "prompt" ? false : intake.tools_confirmed,
                  })}
                >
                  {type}
                </button>
              ))}
            </fieldset>

            <label className="field full-field">
              <span>Intención <em>obligatorio</em></span>
              <textarea
                rows={3}
                value={intake.idea}
                onChange={(event) => updateIntake({ idea: event.target.value })}
                placeholder="Quiero crear una instrucción que…"
              />
              <small>Describe el resultado, no el personaje del modelo.</small>
            </label>

            <div className="form-columns">
              <label className="field">
                <span>Título</span>
                <input
                  value={intake.title ?? ""}
                  onChange={(event) => updateIntake({ title: event.target.value || null })}
                  placeholder="Nombre reconocible"
                />
              </label>
              <label className="field">
                <span>Audiencia</span>
                <input
                  value={intake.audience ?? ""}
                  onChange={(event) => updateIntake({ audience: event.target.value || null })}
                  placeholder="Quién usará la salida"
                />
              </label>
            </div>

            <label className="field full-field">
              <span>Contexto</span>
              <textarea
                rows={3}
                value={intake.context ?? ""}
                onChange={(event) => updateIntake({ context: event.target.value || null })}
                placeholder="Situación, datos conocidos y alcance…"
              />
            </label>

            <div className="form-columns">
              <label className="field">
                <span>Nombre de entrada</span>
                <input
                  value={intake.input_name ?? ""}
                  onChange={(event) => updateIntake({ input_name: event.target.value || null })}
                  placeholder="input_document"
                  pattern="[a-z][a-z0-9_]*"
                />
                <small>Inglés, minúsculas y guion bajo.</small>
              </label>
              <label className="field">
                <span>Formato de salida</span>
                <select
                  value={intake.output_format ?? ""}
                  onChange={(event) =>
                    updateIntake({
                      output_format: (event.target.value || null) as FactoryIntake["output_format"],
                    })
                  }
                >
                  <option value="">Selecciona…</option>
                  <option value="json">JSON</option>
                  <option value="markdown">Markdown</option>
                  <option value="text">Texto</option>
                  <option value="yaml">YAML</option>
                  <option value="code">Código</option>
                </select>
              </label>
            </div>

            <label className="field full-field">
              <span>Criterios de éxito <em>uno por línea</em></span>
              <textarea
                rows={4}
                value={intake.success_criteria.join("\n")}
                onChange={(event) => updateIntake({ success_criteria: toLines(event.target.value) })}
                placeholder="Cada hallazgo incluye evidencia verificable"
              />
            </label>

            <label className="field full-field">
              <span>Restricciones <em>una por línea</em></span>
              <textarea
                rows={4}
                value={intake.constraints.join("\n")}
                onChange={(event) => updateIntake({ constraints: toLines(event.target.value) })}
                placeholder="Solo lectura\nNo inventar fuentes"
              />
            </label>

            {needsToolDecision && (
              <div className="tool-box">
                <label className="field full-field">
                  <span>Tools permitidas <em>una por línea</em></span>
                  <textarea
                    rows={3}
                    value={intake.allowed_tools.join("\n")}
                    onChange={(event) => updateIntake({ allowed_tools: toLines(event.target.value) })}
                    placeholder="local_file_reader"
                  />
                </label>
                <label className="checkbox-field">
                  <input
                    type="checkbox"
                    checked={intake.tools_confirmed}
                    onChange={(event) => updateIntake({ tools_confirmed: event.target.checked })}
                  />
                  <span>
                    <strong>Confirmo esta lista explícitamente</strong>
                    <small>Puede estar vacía; confirmar elimina la ambigüedad.</small>
                  </span>
                </label>
                <label className="checkbox-field">
                  <input
                    type="checkbox"
                    checked={intake.requires_human_approval}
                    onChange={(event) =>
                      updateIntake({ requires_human_approval: event.target.checked })
                    }
                  />
                  <span>
                    <strong>Requerir aprobación humana</strong>
                    <small>Seguro por defecto para cada tool declarada.</small>
                  </span>
                </label>
              </div>
            )}

            <details className="advanced-fields">
              <summary>Fuentes de dominio opcionales</summary>
              <label className="field full-field">
                <span>Referencias <em>una por línea</em></span>
                <textarea
                  rows={3}
                  value={intake.source_refs.join("\n")}
                  onChange={(event) => updateIntake({ source_refs: toLines(event.target.value) })}
                  placeholder="docs/mi_fuente.md#seccion"
                />
              </label>
            </details>

            <div className="form-actions">
              <button
                className="button secondary"
                type="button"
                disabled={busy !== null || intake.idea.trim().length < 15}
                onClick={handleAnalyze}
              >
                {busy === "analyze" ? "Analizando…" : "1. Analizar intención"}
              </button>
              <button
                className="button primary"
                type="button"
                disabled={busy !== null || !guidance?.ready}
                onClick={handleBuild}
              >
                {busy === "build" ? "Construyendo…" : "2. Construir borrador"}
              </button>
            </div>
          </section>

          <div className="middle-column">
            <section className="panel flow-panel" aria-labelledby="flow-title">
              <div className="panel-heading">
                <div>
                  <span className="panel-kicker">Estado derivado de la API</span>
                  <h3 id="flow-title">Mapa del flujo</h3>
                </div>
                <span className="live-label">
                  <i /> Real, no simulado
                </span>
              </div>
              <FlowBoard events={events} />
              <div className="legend" aria-label="Leyenda de estados">
                {(["idle", "waiting", "queued", "done"] as FlowStatus[]).map((status) => (
                  <span key={status}>
                    <i style={{ backgroundColor: statusColor(status) }} />
                    {STATUS_LABELS[status]}
                  </span>
                ))}
              </div>
            </section>

            <section className="panel question-panel" aria-labelledby="questions-title">
              <div className="panel-heading">
                <div>
                  <span className="panel-kicker">Tutor determinista</span>
                  <h3 id="questions-title">Preguntas y razones</h3>
                </div>
                {guidance && (
                  <span className="count-badge">
                    {guidance.questions.length} pendiente{guidance.questions.length === 1 ? "" : "s"}
                  </span>
                )}
              </div>
              <QuestionPanel guidance={guidance} />
            </section>

            {explanation.length > 0 && (
              <section className="panel explanation-panel">
                <div className="panel-heading">
                  <div>
                    <span className="panel-kicker">Qué ocurrió</span>
                    <h3>Explicación de la transformación</h3>
                  </div>
                </div>
                <ol>
                  {explanation.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
              </section>
            )}
          </div>

          <section className="panel preview-panel" aria-labelledby="preview-title">
            <div className="panel-heading">
              <div>
                <span className="panel-kicker">Salida portable</span>
                <h3 id="preview-title">Contrato JSON</h3>
              </div>
              <button
                className="export-button"
                type="button"
                onClick={handleExport}
                disabled={!artifact || busy !== null}
              >
                {busy === "export" ? "Exportando…" : "Exportar JSON"}
              </button>
            </div>
            <ArtifactPreview artifact={artifact} exportResult={exportResult} />
          </section>
        </div>
      </section>

      <section className="learning-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Mapa mental</span>
            <h2>Cuatro palabras que debes poder explicar</h2>
          </div>
        </div>
        <div className="learning-grid">
          <article>
            <span>01</span>
            <h3>PromptSpec</h3>
            <p>Plano de una instrucción: propósito, datos, reglas y salida verificable.</p>
          </article>
          <article>
            <span>02</span>
            <h3>AgentSpec</h3>
            <p>Añade tools, memoria, permisos, supervisión y límites de ejecución.</p>
          </article>
          <article>
            <span>03</span>
            <h3>Validación</h3>
            <p>Comprueba estructura. No garantiza que el contenido sea verdadero o útil.</p>
          </article>
          <article>
            <span>04</span>
            <h3>Content hash</h3>
            <p>Detecta cambios del contenido; no certifica calidad, autoría ni seguridad total.</p>
          </article>
        </div>
      </section>

      <footer>
        <p>
          Parte 1 · Contratos deterministas · Siguiente frontera: propuestas con Ollama y eventos
          SSE.
        </p>
        <span>Sin telemetría · Sin conectores reales · Sin fallback cloud</span>
      </footer>
    </main>
  );
}

