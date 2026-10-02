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
import type {
  CheckView,
  FlowStatus,
  Health,
  LaneView,
  RunSnapshot,
  SourceSummary,
} from "./types";

const NODE_LAYOUT: Record<string, { x: number; y: number }> = {
  intake: { x: 430, y: 8 },
  "seq-a": { x: 40, y: 170 },
  "seq-b": { x: 40, y: 310 },
  "seq-c": { x: 40, y: 450 },
  "seq-join": { x: 40, y: 590 },
  "par-a": { x: 430, y: 170 },
  "par-b": { x: 670, y: 170 },
  "par-c": { x: 910, y: 170 },
  "par-join": { x: 670, y: 360 },
  compare: { x: 430, y: 590 },
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
  sequential: "La línea secuencial gana coherencia o tiempo",
  parallel: "El fan-out redujo el tiempo de pared",
  tie: "Empate en tiempo y coherencia",
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
      sourcePosition: item.id.startsWith("seq-") ? Position.Bottom : Position.Right,
      targetPosition: item.id.startsWith("seq-") ? Position.Top : Position.Left,
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
      link("intake", "seq-a"),
      link("seq-a", "seq-b"),
      link("seq-b", "seq-c"),
      link("seq-c", "seq-join"),
      link("seq-join", "compare"),
      link("intake", "par-a"),
      link("intake", "par-b"),
      link("intake", "par-c"),
      link("par-a", "par-join"),
      link("par-b", "par-join"),
      link("par-c", "par-join"),
      link("par-join", "compare"),
    ];
  }, [snapshot]);

  return (
    <div className="flow-canvas parallel-canvas" aria-label="Grafo de fan-out y fan-in">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.16 }}
        minZoom={0.35}
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

function LaneCard({ title, lane }: { title: string; lane: LaneView | null }) {
  if (!lane) {
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
        <dt>Gate</dt>
        <dd>{lane.passed ? "Aprobado" : "No aprobado"}</dd>
        <dt>Fuentes</dt>
        <dd>
          {lane.completed_sources.length}/3 completas
        </dd>
        <dt>Fallidas</dt>
        <dd>{lane.failed_sources.length === 0 ? "Ninguna" : lane.failed_sources.join(", ")}</dd>
        <dt>Hechos</dt>
        <dd>{lane.fact_count}</dd>
        <dt>Tiempo</dt>
        <dd>{lane.wall_ms != null ? `${Math.round(lane.wall_ms)} ms` : "—"}</dd>
        <dt>Overlap</dt>
        <dd>{lane.overlap_observed ? "Sí" : "No"}</dd>
        <dt>In flight</dt>
        <dd>{lane.max_in_flight ?? "—"}</dd>
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
          <p>Aparecerán cuando una variante una la tabla.</p>
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
  const [includeSequential, setIncludeSequential] = useState(true);
  const [includeParallel, setIncludeParallel] = useState(true);
  const [health, setHealth] = useState<Health | null>(null);
  const [sources, setSources] = useState<SourceSummary[]>([]);
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
      setSources(example.sources);
      setIncludeSequential(true);
      setIncludeParallel(true);
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
        include_sequential: includeSequential,
        include_parallel: includeParallel,
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
          : "Backend no disponible. Confirma que Uvicorn escucha en el puerto 8014.",
      );
    }
  }

  const checks =
    snapshot?.parallel?.checks.length
      ? snapshot.parallel.checks
      : snapshot?.sequential?.checks ?? [];

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Volver al inicio">
          <span className="brand-mark" aria-hidden="true">
            04
          </span>
          <span>
            <strong>Agentes en paralelo</strong>
            <small>Laboratorio 04 · BL_Loops</small>
          </span>
        </a>
        <div className="topbar-badges" aria-label="Características de esta parte">
          <span className="badge badge-mint">100 % local</span>
          <span className="badge badge-blue">A · fan-out asyncio</span>
          <span className="badge badge-outline">{health?.model ?? "Ollama"}</span>
        </div>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <span className="eyebrow">Tres fuentes, una tabla</span>
          <h1>¿El paralelismo ahorra tiempo sin perder coherencia?</h1>
          <p>
            La misma extracción corre en serie y en fan-out. El agregador espera resultados o un
            timeout explícito. Una rama fallida no entra en la tabla.
          </p>
          <div className="hero-actions">
            <button className="button primary" type="button" onClick={loadExample}>
              Cargar caso I-PARALLEL-002
            </button>
            <a className="button ghost" href="#workspace">
              Empezar con tu tarea
            </a>
          </div>
        </div>
        <aside className="concept-card" aria-label="Concepto central">
          <span className="concept-number">04</span>
          <p>A → B → C</p>
          <span className="concept-arrow" aria-hidden="true">
            ↓
          </span>
          <p>A, B y C a la vez</p>
          <span className="concept-arrow" aria-hidden="true">
            ↓
          </span>
          <p className="concept-result">Misma tabla, menos reloj</p>
          <small>Un solo modelo compartido. Varios pesos a la vez quedan aplazados.</small>
        </aside>
      </section>

      <section className="lesson-strip" aria-label="Las cinco etapas">
        <div>
          <span>01</span>
          <p>Fuentes</p>
        </div>
        <div>
          <span>02</span>
          <p>Secuencial</p>
        </div>
        <div>
          <span>03</span>
          <p>Fan-out</p>
        </div>
        <div>
          <span>04</span>
          <p>Fan-in</p>
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
                  setSources([]);
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
                rows={7}
                value={task}
                onChange={(event) => setTask(event.target.value)}
                placeholder="Extrae hechos de tres documentos independientes…"
              />
              <small>La misma entrada alimenta la línea secuencial y el fan-out.</small>
            </label>

            {sources.length > 0 && (
              <ul className="source-list">
                {sources.map((source) => (
                  <li key={source.source_id}>
                    <strong>{source.source_id}</strong>
                    <span>{source.title}</span>
                  </li>
                ))}
              </ul>
            )}

            <div className="variant-toggle">
              <label>
                <input
                  type="checkbox"
                  checked={includeSequential}
                  onChange={(event) => setIncludeSequential(event.target.checked)}
                />
                Secuencial
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={includeParallel}
                  onChange={(event) => setIncludeParallel(event.target.checked)}
                />
                Paralelo
              </label>
            </div>

            <div className="form-actions">
              <button
                className="button primary"
                type="button"
                disabled={busy || task.trim().length < 20}
                onClick={handleStart}
              >
                {busy ? "Extrayendo…" : "Lanzar experimento"}
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
                {(["idle", "queued", "running", "waiting", "done", "failed"] as FlowStatus[]).map(
                  (status) => (
                    <span key={status}>
                      <i style={{ backgroundColor: statusColor(status) }} />
                      {STATUS_LABELS[status]}
                    </span>
                  ),
                )}
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
                    <p>Las tres ramas paralelas deben pasar a queued antes de running.</p>
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
                <h3 id="compare-title">Tiempos y tabla</h3>
              </div>
            </div>
            {snapshot?.comparison && (
              <div className="winner-banner" role="status">
                <strong>{WINNER_LABEL[snapshot.comparison.winner]}</strong>
                <p>
                  {snapshot.comparison.speedup
                    ? `Speedup ${snapshot.comparison.speedup}×. ${snapshot.comparison.explanation[0]}`
                    : snapshot.comparison.explanation[0]}
                </p>
              </div>
            )}
            <div className="compare-grid">
              <LaneCard title="Secuencial" lane={snapshot?.sequential ?? null} />
              <LaneCard title="Paralelo" lane={snapshot?.parallel ?? null} />
            </div>
            <CheckList checks={checks} />
            {snapshot?.jsonl_path && (
              <div className="export-success" role="status">
                <strong>JSONL local</strong>
                <code>{snapshot.jsonl_path}</code>
              </div>
            )}
            {snapshot?.parallel?.preview && (
              <p className="preview-text">{snapshot.parallel.preview}</p>
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
            <h3>Fan-out</h3>
            <p>Tres documentos independientes se lanzan a la vez. No hay dependencia de datos entre ellos.</p>
          </article>
          <article>
            <span>02</span>
            <h3>Fan-in</h3>
            <p>El agregador espera. No inventa la fila de una rama que hizo timeout.</p>
          </article>
          <article>
            <span>03</span>
            <h3>Procedencia</h3>
            <p>Cada hecho recuerda su source_id. Mezclar tarifas con el horario sería un error de unión.</p>
          </article>
          <article>
            <span>04</span>
            <h3>Un modelo</h3>
            <p>Se comparten pesos. Si Ollama serializa, el reloj lo dice. max_in_flight=1 lo demuestra.</p>
          </article>
        </div>
      </section>

      <footer>
        <p>A · Fan-out asyncio · LangGraph y varios modelos quedan aplazados.</p>
        <span>Sin telemetría · Sin conectores reales · Sin fallback cloud</span>
      </footer>
    </main>
  );
}
