import { useEffect, useMemo, useRef, useState } from "react";
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
import { ApiError, fetchExample, fetchHealth, startExperiment, subscribeRun } from "./api";
import type { CheckView, FlowStatus, Health, RunSnapshot, VariantView } from "./types";

const NODE_LAYOUT: Record<string, { x: number; y: number }> = {
  intake: { x: 430, y: 8 },
  baseline: { x: 40, y: 190 },
  planner: { x: 430, y: 168 },
  author: { x: 670, y: 168 },
  reviewer: { x: 910, y: 168 },
  reviser: { x: 910, y: 330 },
  score: { x: 430, y: 470 },
};

const STATUS_LABELS: Record<FlowStatus, string> = {
  idle: "Sin iniciar",
  queued: "En espera",
  running: "Procesando",
  waiting: "Espera al modelo",
  retrying: "Reintentando",
  done: "Completado",
  failed: "Falló",
  blocked: "Bloqueado",
};

const WINNER_LABEL = {
  baseline: "La línea base cubre más requisitos",
  orchestrated: "La orquestación cubre más requisitos",
  tie: "Empate en la lista determinista",
  incomplete: "Comparación incompleta",
};

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

function FlowBoard({ snapshot }: { snapshot: RunSnapshot | null }) {
  const nodes = useMemo<Node[]>(() => {
    const items = snapshot?.nodes ?? [];
    return items.map((item, index) => ({
      id: item.id,
      position: NODE_LAYOUT[item.id] ?? { x: index * 220, y: 40 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      draggable: false,
      data: {
        label: (
          <div className="flow-node-label">
            <div className="flow-node-topline">
              <span className="node-number">{String(index + 1).padStart(2, "0")}</span>
              <span className={`status-pill status-${item.state}`}>{STATUS_LABELS[item.state]}</span>
            </div>
            <strong>{item.title}</strong>
            <span>{item.detail}</span>
          </div>
        ),
      },
      style: {
        width: 210,
        minHeight: 118,
        padding: 0,
        borderRadius: 18,
        border: `2px solid ${statusColor(item.state)}`,
        background: "#fffdf7",
        boxShadow: "0 14px 36px rgba(15, 23, 42, 0.1)",
      },
    }));
  }, [snapshot]);

  const edges = useMemo<Edge[]>(() => {
    const stateOf = (id: string): FlowStatus =>
      snapshot?.nodes.find((node) => node.id === id)?.state ?? "idle";
    const link = (source: string, target: string): Edge => {
      const sourceState = stateOf(source);
      const targetState = stateOf(target);
      const active = sourceState === "done" && targetState !== "idle";
      return {
        id: `${source}-${target}`,
        source,
        target,
        animated: targetState === "running" || targetState === "queued" || targetState === "waiting",
        markerEnd: { type: MarkerType.ArrowClosed, color: active ? "#0f9f78" : "#cbd5e1" },
        style: { stroke: active ? "#0f9f78" : "#cbd5e1", strokeWidth: active ? 3 : 2 },
      };
    };
    return [
      link("intake", "baseline"),
      link("intake", "planner"),
      link("planner", "author"),
      link("author", "reviewer"),
      link("reviewer", "reviser"),
      link("reviewer", "score"),
      link("reviser", "score"),
      link("baseline", "score"),
    ];
  }, [snapshot]);

  return (
    <div className="flow-canvas orchestration-canvas" aria-label="Grafo de orquestación">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.16 }}
        minZoom={0.4}
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
            const item = snapshot?.nodes.find((entry) => entry.id === node.id);
            return statusColor(item?.state ?? "idle");
          }}
          maskColor="rgba(247, 244, 234, 0.75)"
        />
      </ReactFlow>
    </div>
  );
}

function VariantCard({ title, variant }: { title: string; variant: VariantView | null }) {
  if (!variant) {
    return (
      <article className="compare-card">
        <h4>{title}</h4>
        <p className="preview-text">Esta variante no se ejecutó.</p>
      </article>
    );
  }
  return (
    <article className="compare-card">
      <h4>{title}</h4>
      <dl>
        <dt>Checks</dt>
        <dd>
          {variant.checks_passed}/{variant.checks_total}
        </dd>
        <dt>Gate</dt>
        <dd>{variant.passed ? "Aprobado" : "No aprobado"}</dd>
        <dt>Palabras</dt>
        <dd>{variant.word_count ?? "—"}</dd>
        <dt>Latencia</dt>
        <dd>{variant.latency_ms != null ? `${Math.round(variant.latency_ms)} ms` : "—"}</dd>
        <dt>Corrección</dt>
        <dd>{variant.revision_used ? "Sí, una vez" : "No"}</dd>
        <dt>Revisor LLM</dt>
        <dd>
          {variant.llm_review_available
            ? variant.llm_review_passed
              ? "Dice que sí"
              : "Dice que no"
            : "JSON inválido o ausente"}
        </dd>
      </dl>
    </article>
  );
}

function CheckList({ checks }: { checks: CheckView[] }) {
  if (checks.length === 0) {
    return (
      <div className="empty-state compact">
        <span className="empty-index">✓</span>
        <div>
          <strong>Todavía no hay checks</strong>
          <p>Aparecerán cuando una variante produzca Markdown.</p>
        </div>
      </div>
    );
  }
  return (
    <ul className="check-list">
      {checks.map((check) => (
        <li key={check.check_id}>
          <span className={check.passed ? "ok" : "ko"}>{check.passed ? "OK" : "NO"}</span>
          <span>
            <strong>{check.title}</strong>
            <br />
            {check.evidence}
          </span>
        </li>
      ))}
    </ul>
  );
}

export default function App() {
  const [task, setTask] = useState("");
  const [includeBaseline, setIncludeBaseline] = useState(true);
  const [includeOrchestrated, setIncludeOrchestrated] = useState(true);
  const [health, setHealth] = useState<Health | null>(null);
  const [snapshot, setSnapshot] = useState<RunSnapshot | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [log, setLog] = useState<string[]>([]);
  const closeStream = useRef<(() => void) | null>(null);
  const terminal = useRef(false);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
    return () => closeStream.current?.();
  }, []);

  async function loadExample() {
    setError(null);
    try {
      const example = await fetchExample();
      setTask(example.task);
      setIncludeBaseline(true);
      setIncludeOrchestrated(true);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "No se pudo cargar el ejemplo.");
    }
  }

  async function handleStart() {
    closeStream.current?.();
    terminal.current = false;
    setBusy(true);
    setError(null);
    setLog([]);
    setSnapshot(null);
    try {
      const started = await startExperiment({
        task,
        include_baseline: includeBaseline,
        include_orchestrated: includeOrchestrated,
      });
      closeStream.current = subscribeRun(
        started.run_id,
        (envelope) => {
          setSnapshot(envelope.snapshot);
          const node = envelope.event.node?.id ?? "run";
          setLog((current) => [
            ...current.slice(-24),
            `${envelope.event.sequence}. ${envelope.event.event_type} · ${node}`,
          ]);
          if (envelope.snapshot.status === "completed" || envelope.snapshot.status === "failed") {
            terminal.current = true;
            closeStream.current?.();
            setBusy(false);
          }
        },
        (message) => {
          if (terminal.current) return;
          setError(message);
          setBusy(false);
        },
      );
    } catch (caught) {
      setBusy(false);
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Backend no disponible. Confirma que Uvicorn escucha en el puerto 8012.",
      );
    }
  }

  const checks =
    snapshot?.orchestrated?.checks.length
      ? snapshot.orchestrated.checks
      : snapshot?.baseline?.checks ?? [];

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Volver al inicio">
          <span className="brand-mark" aria-hidden="true">
            03
          </span>
          <span>
            <strong>Orquestación local</strong>
            <small>Laboratorio 03 · BL_Loops</small>
          </span>
        </a>
        <div className="topbar-badges" aria-label="Características de esta parte">
          <span className="badge badge-mint">100 % local</span>
          <span className="badge badge-blue">A0 · orquestador propio</span>
          <span className="badge badge-outline">{health?.model ?? "Ollama"}</span>
        </div>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <span className="eyebrow">Planificar, escribir, comprobar</span>
          <h1>¿Mejora algo al separar una tarea entre agentes?</h1>
          <p>
            Un agente único escribe la guía de un tirón. El pipeline parte el trabajo en
            planificador, autor y revisor. La misma lista determinista puntúa las dos salidas.
          </p>
          <div className="hero-actions">
            <button className="button primary" type="button" onClick={loadExample}>
              Cargar caso I-ORCH-001
            </button>
            <a className="button ghost" href="#workspace">
              Empezar con tu tarea
            </a>
          </div>
        </div>
        <aside className="concept-card" aria-label="Concepto central">
          <span className="concept-number">03</span>
          <p>Agente único</p>
          <span className="concept-arrow" aria-hidden="true">
            ↓
          </span>
          <p>Plan → autor → revisor</p>
          <span className="concept-arrow" aria-hidden="true">
            ↓
          </span>
          <p className="concept-result">Misma lista de checks</p>
          <small>Sin esa línea base no se puede afirmar que la orquestación mejoró el resultado.</small>
        </aside>
      </section>

      <section className="lesson-strip" aria-label="Las cinco etapas">
        <div>
          <span>01</span>
          <p>Tarea</p>
        </div>
        <div>
          <span>02</span>
          <p>Línea base</p>
        </div>
        <div>
          <span>03</span>
          <p>Handoffs</p>
        </div>
        <div>
          <span>04</span>
          <p>Gate</p>
        </div>
        <div>
          <span>05</span>
          <p>Comparar</p>
        </div>
      </section>

      <section className="workspace-section" id="workspace">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Taller interactivo</span>
            <h2>Ejecuta las dos variantes</h2>
          </div>
        </div>

        {error && (
          <div className="error-banner" role="alert">
            <strong>No pudimos completar el paso</strong>
            <span>{error}</span>
          </div>
        )}

        <div className="workspace-grid">
          <section className="panel form-panel" aria-labelledby="task-title">
            <div className="panel-heading">
              <div>
                <span className="panel-kicker">Entrada humana</span>
                <h3 id="task-title">Tarea</h3>
              </div>
              <button
                className="text-button"
                type="button"
                onClick={() => {
                  setTask("");
                  setSnapshot(null);
                  setLog([]);
                }}
              >
                Limpiar
              </button>
            </div>

            <label className="field full-field">
              <span>Qué debe producir el sistema <em>obligatorio</em></span>
              <textarea
                rows={8}
                value={task}
                onChange={(event) => setTask(event.target.value)}
                placeholder="Produce una guía breve para ejecutar un agente local…"
              />
              <small>La misma entrada alimenta al agente único y al pipeline.</small>
            </label>

            <div className="variant-toggle">
              <label>
                <input
                  type="checkbox"
                  checked={includeBaseline}
                  onChange={(event) => setIncludeBaseline(event.target.checked)}
                />
                Agente único
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={includeOrchestrated}
                  onChange={(event) => setIncludeOrchestrated(event.target.checked)}
                />
                Pipeline orquestado
              </label>
            </div>

            <div className="form-actions">
              <button
                className="button primary"
                type="button"
                disabled={busy || task.trim().length < 20}
                onClick={handleStart}
              >
                {busy ? "Orquestando…" : "Lanzar experimento"}
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
                  <i /> {snapshot ? snapshot.status : "Sin corrida"}
                </span>
              </div>
              <FlowBoard snapshot={snapshot} />
              <div className="legend" aria-label="Leyenda de estados">
                {(["idle", "running", "waiting", "done", "failed"] as FlowStatus[]).map((status) => (
                  <span key={status}>
                    <i style={{ backgroundColor: statusColor(status) }} />
                    {STATUS_LABELS[status]}
                  </span>
                ))}
              </div>
            </section>

            <section className="panel explanation-panel">
              <div className="panel-heading">
                <div>
                  <span className="panel-kicker">Eventos reales</span>
                  <h3>Bitácora</h3>
                </div>
                <span className="count-badge">{snapshot?.event_count ?? 0} eventos</span>
              </div>
              {log.length === 0 ? (
                <div className="empty-state compact">
                  <span className="empty-index">i</span>
                  <div>
                    <strong>El grafo espera un experimento</strong>
                    <p>Cada nodo cambia de color cuando el backend emite un evento.</p>
                  </div>
                </div>
              ) : (
                <ol className="event-log">
                  {log.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
              )}
            </section>
          </div>

          <section className="panel preview-panel" aria-labelledby="compare-title">
            <div className="panel-heading">
              <div>
                <span className="panel-kicker">Salida comparable</span>
                <h3 id="compare-title">Checks y ganador</h3>
              </div>
            </div>
            {snapshot?.comparison && (
              <div className="winner-banner" role="status">
                <strong>{WINNER_LABEL[snapshot.comparison.winner]}</strong>
                <p>{snapshot.comparison.explanation[0]}</p>
              </div>
            )}
            <div className="compare-grid">
              <VariantCard title="Agente único" variant={snapshot?.baseline ?? null} />
              <VariantCard title="Orquestada" variant={snapshot?.orchestrated ?? null} />
            </div>
            <CheckList checks={checks} />
            {snapshot?.jsonl_path && (
              <div className="export-success" role="status">
                <strong>JSONL local</strong>
                <code>{snapshot.jsonl_path}</code>
              </div>
            )}
            {snapshot?.orchestrated?.preview && (
              <p className="preview-text">{snapshot.orchestrated.preview}</p>
            )}
          </section>
        </div>
      </section>

      <section className="learning-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Mapa mental</span>
            <h2>Cuatro ideas que debes poder explicar</h2>
          </div>
        </div>
        <div className="learning-grid">
          <article>
            <span>01</span>
            <h3>Handoff</h3>
            <p>Un contrato JSON o Markdown que un rol entrega al siguiente. Sin él, solo hay charla.</p>
          </article>
          <article>
            <span>02</span>
            <h3>Línea base</h3>
            <p>El mismo caso, un solo agente. Si no existe, no hay mejora que medir.</p>
          </article>
          <article>
            <span>03</span>
            <h3>Gate determinista</h3>
            <p>El revisor modelo puede opinar. Aprueba o no el código que busca headings y límites.</p>
          </article>
          <article>
            <span>04</span>
            <h3>Una corrección</h3>
            <p>Si el gate falla, el autor corrige una vez. Un loop con presupuesto es otro laboratorio.</p>
          </article>
        </div>
      </section>

      <footer>
        <p>A0 · Orquestador propio · LangGraph, CrewAI y AG2 quedan aplazados.</p>
        <span>Sin telemetría · Sin conectores reales · Sin fallback cloud</span>
      </footer>
    </main>
  );
}
