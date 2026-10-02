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
import type { CheckView, FlowStatus, Health, IterationView, RunSnapshot } from "./types";

const NODE_LAYOUT: Record<string, { x: number; y: number }> = {
  intake: { x: 390, y: 8 },
  generate: { x: 40, y: 190 },
  score: { x: 390, y: 190 },
  decide: { x: 740, y: 190 },
  improve: { x: 390, y: 370 },
  best: { x: 740, y: 370 },
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

const STOP_LABEL: Record<string, string> = {
  threshold_reached: "El umbral se alcanzó",
  max_iterations: "Se agotaron las iteraciones",
  max_errors: "Se agotó el presupuesto de errores",
  timeout: "Se agotó el tiempo",
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
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
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
      link("intake", "generate"),
      link("generate", "score"),
      link("score", "decide"),
      link("decide", "improve"),
      link("improve", "generate"),
      link("score", "best"),
      link("decide", "best"),
    ];
  }, [snapshot]);

  return (
    <div className="flow-canvas loop-canvas" aria-label="Grafo del loop">
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

function CheckList({ checks }: { checks: CheckView[] }) {
  if (checks.length === 0) {
    return (
      <div className="empty-state compact">
        <span className="empty-index">✓</span>
        <div>
          <strong>Todavía no hay checks</strong>
          <p>Aparecerán cuando el evaluador puntúe una salida.</p>
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

function IterationList({ iterations }: { iterations: IterationView[] }) {
  if (iterations.length === 0) {
    return (
      <div className="empty-state compact">
        <span className="empty-index">i</span>
        <div>
          <strong>Sin iteraciones todavía</strong>
          <p>Cada vuelta guarda el score, no el prompt completo.</p>
        </div>
      </div>
    );
  }
  return (
    <ol className="iteration-list">
      {iterations.map((item) => (
        <li key={item.iteration} className={item.is_best ? "is-best" : undefined}>
          <strong>
            Iteración {item.iteration}: {item.checks_passed}/{item.checks_total}
          </strong>
          <span>{item.is_best ? "Mejor candidato" : item.passed ? "Umbral" : "Sigue"}</span>
        </li>
      ))}
    </ol>
  );
}

export default function App() {
  const [task, setTask] = useState("");
  const [initialPrompt, setInitialPrompt] = useState("");
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
      setInitialPrompt(example.initial_prompt);
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
        initial_prompt: initialPrompt,
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
          : "Backend no disponible. Confirma que Uvicorn escucha en el puerto 8015.",
      );
    }
  }

  const stopLabel = snapshot?.stop_reason ? STOP_LABEL[snapshot.stop_reason] ?? snapshot.stop_reason : null;

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Volver al inicio">
          <span className="brand-mark" aria-hidden="true">
            05
          </span>
          <span>
            <strong>Loops acotados</strong>
            <small>Laboratorio 05 · BL_Loops</small>
          </span>
        </a>
        <div className="topbar-badges" aria-label="Características de esta parte">
          <span className="badge badge-mint">100 % local</span>
          <span className="badge badge-blue">A0 · loop propio</span>
          <span className="badge badge-outline">{health?.model ?? "Ollama"}</span>
        </div>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <span className="eyebrow">Generar, puntuar, decidir, parar</span>
          <h1>¿Cómo se mejora un resultado sin un ciclo infinito?</h1>
          <p>
            Un prompt débil produce una salida. Un evaluador en código cuenta cinco
            assertions. Si no llegan a 5/5, el mejorador reescribe el prompt. El loop
            guarda el mejor candidato y se detiene al umbral o al presupuesto.
          </p>
          <div className="hero-actions">
            <button className="button primary" type="button" onClick={loadExample}>
              Cargar caso I-LOOP-003
            </button>
            <a className="button ghost" href="#workspace">
              Empezar con tu tarea
            </a>
          </div>
        </div>
        <aside className="concept-card" aria-label="Concepto central">
          <span className="concept-number">05</span>
          <p>Prompt débil</p>
          <span className="concept-arrow" aria-hidden="true">
            ↓
          </span>
          <p>Score 0/5 → 4/5 → 5/5</p>
          <span className="concept-arrow" aria-hidden="true">
            ↓
          </span>
          <p className="concept-result">Parada explícita</p>
          <small>El último intento no gana por ser el último. Gana el de mayor score.</small>
        </aside>
      </section>

      <section className="lesson-strip" aria-label="Las cinco etapas">
        <div>
          <span>01</span>
          <p>Declarar</p>
        </div>
        <div>
          <span>02</span>
          <p>Generar</p>
        </div>
        <div>
          <span>03</span>
          <p>Puntuar</p>
        </div>
        <div>
          <span>04</span>
          <p>Decidir</p>
        </div>
        <div>
          <span>05</span>
          <p>Mejorar</p>
        </div>
      </section>

      <section className="workspace-section" id="workspace">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Taller interactivo</span>
            <h2>Ejecuta el loop acotado</h2>
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
                <h3 id="task-title">Tarea y prompt inicial</h3>
              </div>
              <button
                className="text-button"
                type="button"
                onClick={() => {
                  setTask("");
                  setInitialPrompt("");
                  setSnapshot(null);
                  setLog([]);
                }}
              >
                Limpiar
              </button>
            </div>

            <label className="field full-field">
              <span>Qué debe producir el generador <em>obligatorio</em></span>
              <textarea
                rows={6}
                value={task}
                onChange={(event) => setTask(event.target.value)}
                placeholder="Redacta un briefing operativo…"
              />
              <small>La tarea no cambia. Lo que evoluciona es el prompt.</small>
            </label>

            <label className="field full-field">
              <span>Prompt inicial <em>obligatorio</em></span>
              <textarea
                rows={4}
                value={initialPrompt}
                onChange={(event) => setInitialPrompt(event.target.value)}
                placeholder="Escribe algo útil."
              />
              <small>El caso usa un prompt débil a propósito para ver el score inicial.</small>
            </label>

            <div className="form-actions single">
              <button
                className="button primary"
                type="button"
                disabled={busy || task.trim().length < 20 || initialPrompt.trim().length < 8}
                onClick={handleStart}
              >
                {busy ? "Iterando…" : "Lanzar loop"}
              </button>
            </div>
          </section>

          <div className="middle-column">
            <section className="panel flow-panel" aria-labelledby="flow-title">
              <div className="panel-heading">
                <div>
                  <span className="panel-kicker">Estado derivado de la API</span>
                  <h3 id="flow-title">Mapa del ciclo</h3>
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
                    <strong>El grafo espera un loop</strong>
                    <p>Generar, puntuar y mejorar vuelven a pintarse en cada iteración.</p>
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

          <section className="panel preview-panel" aria-labelledby="score-title">
            <div className="panel-heading">
              <div>
                <span className="panel-kicker">Salida comparable</span>
                <h3 id="score-title">Score y parada</h3>
              </div>
            </div>
            {stopLabel && (
              <div className="winner-banner" role="status">
                <strong>{stopLabel}</strong>
                <p>
                  Inicial {snapshot?.declaration?.initial_score ?? "—"}/5 · Mejor{" "}
                  {snapshot?.declaration?.best_known_score ?? "—"}/5
                </p>
              </div>
            )}
            <div className="compare-grid loop-stats">
              <article className="compare-card">
                <h4>Presupuesto</h4>
                <dl>
                  <dt>Iteraciones</dt>
                  <dd>
                    {snapshot?.iterations.length ?? 0}/
                    {snapshot?.declaration?.budget.max_iterations ?? 5}
                  </dd>
                  <dt>Umbral</dt>
                  <dd>{snapshot?.declaration?.budget.threshold ?? 5}/5</dd>
                  <dt>Tiempo</dt>
                  <dd>{snapshot?.declaration?.budget.timeout_seconds ?? 180}s</dd>
                  <dt>Errores</dt>
                  <dd>máx. {snapshot?.declaration?.budget.max_errors ?? 2}</dd>
                </dl>
              </article>
              <article className="compare-card">
                <h4>Mejor candidato</h4>
                <dl>
                  <dt>Iteración</dt>
                  <dd>{snapshot?.best?.iteration ?? "—"}</dd>
                  <dt>Score</dt>
                  <dd>
                    {snapshot?.best
                      ? `${snapshot.best.checks_passed}/${snapshot.best.checks_total}`
                      : "—"}
                  </dd>
                  <dt>Gate</dt>
                  <dd>
                    {snapshot?.best == null ? "—" : snapshot.best.passed ? "Aprobado" : "No aprobado"}
                  </dd>
                  <dt>Caracteres</dt>
                  <dd>{snapshot?.best?.output_chars ?? "—"}</dd>
                </dl>
              </article>
            </div>
            <IterationList iterations={snapshot?.iterations ?? []} />
            <CheckList checks={snapshot?.best?.checks ?? []} />
            {snapshot?.jsonl_path && (
              <div className="export-success" role="status">
                <strong>JSONL local</strong>
                <code>{snapshot.jsonl_path}</code>
              </div>
            )}
            {snapshot?.best?.preview && <p className="preview-text">{snapshot.best.preview}</p>}
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
            <h3>Declaración</h3>
            <p>Todo loop nombra objetivo, score inicial, presupuesto y condición de parada.</p>
          </article>
          <article>
            <span>02</span>
            <h3>Maker / checker</h3>
            <p>El modelo genera. El código puntúa. El generador no se aprueba a sí mismo.</p>
          </article>
          <article>
            <span>03</span>
            <h3>Mejor candidato</h3>
            <p>Si una iteración posterior baja el score, se conserva la anterior.</p>
          </article>
          <article>
            <span>04</span>
            <h3>Presupuesto</h3>
            <p>Cinco iteraciones, dos errores o tres minutos. Lo que ocurra primero cierra el ciclo.</p>
          </article>
        </div>
      </section>

      <footer>
        <p>A0 · Loop Python tipado · LangGraph y OpenEvolve quedan aplazados.</p>
        <span>Sin telemetría · Sin conectores reales · Sin fallback cloud</span>
      </footer>
    </main>
  );
}
