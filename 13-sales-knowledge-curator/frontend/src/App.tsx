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
import { ApiError, buildRelease, fetchHealth, getCurrentRelease, getRun, startAudit, submitReview } from "./api";
import type { ClaimRecord, Health, RunSnapshot, WorkflowState } from "./types";

const GRAPH_NODES = [
  { id: "ingest", title: "Ingesta y cuarentena", states: ["scope_draft", "inventory_running"] },
  { id: "registry", title: "Registro de fuentes", states: ["sources_normalized"] },
  { id: "extraction", title: "Extracción", states: ["claims_extracted"] },
  { id: "ledger", title: "Ledger de claims", states: ["claims_extracted"] },
  { id: "research", title: "Plan e investigación", states: ["gaps_ready", "research_planned", "awaiting_external_authorization", "collecting_local"] },
  { id: "verification", title: "Verificación", states: ["verification_running", "conflicts_open"] },
  { id: "review", title: "Revisión humana", states: ["review_pending", "changes_requested", "approved", "rejected"] },
  { id: "staging", title: "Staging", states: ["staging"] },
  { id: "gate", title: "Gate reproducible", states: ["validating"] },
  { id: "release", title: "KnowledgeRelease", states: ["published", "failed"] },
] as const;

type NodeVisual = "idle" | "running" | "done" | "failed" | "blocked";

function visualFor(state: WorkflowState | null, nodeId: string): NodeVisual {
  if (!state) return "idle";
  if (state === "failed" && nodeId === "release") return "failed";
  const current = GRAPH_NODES.find((item) => item.states.includes(state as never));
  const currentIndex = GRAPH_NODES.findIndex((item) => item.id === current?.id);
  const thisIndex = GRAPH_NODES.findIndex((item) => item.id === nodeId);
  if (thisIndex < currentIndex) return "done";
  if (thisIndex === currentIndex) {
    if (state === "awaiting_external_authorization") return "blocked";
    if (state === "published") return "done";
    return "running";
  }
  return "idle";
}

const VISUAL_COLOR: Record<NodeVisual, string> = {
  idle: "#94a3b8",
  running: "#f59e0b",
  done: "#0f9f78",
  failed: "#dc3545",
  blocked: "#8b5cf6",
};

const VISUAL_LABEL: Record<NodeVisual, string> = {
  idle: "Sin iniciar",
  running: "Activo",
  done: "Hecho",
  failed: "Falló",
  blocked: "Bloqueado",
};

function FlowBoard({ state }: { state: WorkflowState | null }) {
  const nodes = useMemo<Node[]>(
    () =>
      GRAPH_NODES.map((item, index) => {
        const visual = visualFor(state, item.id);
        return {
          id: item.id,
          position: { x: (index % 5) * 250, y: index < 5 ? 24 : 190 },
          sourcePosition: Position.Right,
          targetPosition: Position.Left,
          draggable: false,
          data: {
            label: (
              <div className="flow-node-label">
                <div className="flow-node-topline">
                  <span className="node-number">{String(index + 1).padStart(2, "0")}</span>
                  <span className={`status-pill status-${visual}`}>{VISUAL_LABEL[visual]}</span>
                </div>
                <strong>{item.title}</strong>
              </div>
            ),
          },
          style: {
            width: 220,
            minHeight: 96,
            borderRadius: 18,
            border: `2px solid ${VISUAL_COLOR[visual]}`,
            background: "#fffdf7",
          },
        };
      }),
    [state],
  );
  const edges = useMemo<Edge[]>(() => {
    const pairs: Array<[string, string]> = [
      ["ingest", "registry"],
      ["ingest", "research"],
      ["registry", "extraction"],
      ["extraction", "ledger"],
      ["research", "verification"],
      ["ledger", "verification"],
      ["verification", "review"],
      ["review", "staging"],
      ["staging", "gate"],
      ["gate", "release"],
    ];
    return pairs.map(([source, target]) => ({
      id: `${source}-${target}`,
      source,
      target,
      markerEnd: { type: MarkerType.ArrowClosed, color: "#cbd5e1" },
      style: { stroke: "#cbd5e1", strokeWidth: 2 },
    }));
  }, []);
  return (
    <div className="flow-canvas" aria-label="Grafo del curador">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.16 }}
        minZoom={0.4}
        maxZoom={1.2}
        nodesConnectable={false}
        proOptions={{ hideAttribution: false }}
      >
        <Background variant={BackgroundVariant.Dots} gap={18} size={1.4} color="#d8ded8" />
        <Controls showInteractive={false} />
        <MiniMap pannable zoomable maskColor="rgba(247, 244, 234, 0.75)" />
      </ReactFlow>
    </div>
  );
}

function ClaimRow({
  claim,
  onApprove,
  busy,
}: {
  claim: ClaimRecord;
  onApprove: (claim: ClaimRecord) => void;
  busy: boolean;
}) {
  return (
    <article className={`claim-card status-${claim.status}`}>
      <header>
        <strong>{claim.claim_id}</strong>
        <span>{claim.status}</span>
      </header>
      <p>{claim.canonical_text}</p>
      <small>
        {claim.topic} · {claim.claim_type} · {claim.evidence[0]?.locator ?? "sin localizador"}
      </small>
      <code>{claim.identity_hash.slice(0, 16)}…</code>
      {claim.status !== "human_approved" && claim.status !== "published" && claim.status !== "disputed" && (
        <button type="button" className="button ghost" disabled={busy} onClick={() => onApprove(claim)}>
          Aprobar este hash
        </button>
      )}
    </article>
  );
}

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [run, setRun] = useState<RunSnapshot | null>(null);
  const [current, setCurrent] = useState<Record<string, string>>({});
  const [reviewer, setReviewer] = useState("operador-local");
  const [reason, setReason] = useState("Aprobacion humana sobre el hash visible");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"sources" | "claims" | "conflicts" | "release">("sources");

  async function refreshExtras(runId?: string) {
    const info = await fetchHealth();
    setHealth(info);
    const pointer = await getCurrentRelease();
    setCurrent(pointer);
    if (runId) {
      // SSE replay is pulled with the snapshot already in hand.
    }
  }

  async function handleAudit() {
    setBusy(true);
    setError(null);
    try {
      const snapshot = await startAudit();
      setRun(snapshot);
      await refreshExtras(snapshot.run_id);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "No se pudo auditar. ¿El backend está en el puerto 8013?");
    } finally {
      setBusy(false);
    }
  }

  async function handleApproveClaim(claim: ClaimRecord) {
    if (!run) return;
    setBusy(true);
    setError(null);
    try {
      await submitReview({
        run_id: run.run_id,
        object_type: "claim",
        object_id: claim.claim_id,
        decision: "approved",
        reviewer,
        reason,
        expected_hash: claim.identity_hash,
      });
      const snapshot = await getRun(run.run_id);
      setRun(snapshot);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "La revisión falló");
    } finally {
      setBusy(false);
    }
  }

  async function handleBuild() {
    if (!run) return;
    setBusy(true);
    setError(null);
    try {
      const snapshot = await buildRelease({ run_id: run.run_id, reviewer, reason });
      setRun(snapshot);
      await refreshExtras(snapshot.run_id);
      setTab("release");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "No se pudo publicar");
    } finally {
      setBusy(false);
    }
  }

  const approved = run?.claims.filter((item) => item.status === "human_approved" || item.status === "published") ?? [];

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#workspace">
          <span className="brand-mark">13</span>
          <span>
            <strong>Curador de conocimiento</strong>
            <small>Afirmaciones trazables · red apagada</small>
          </span>
        </a>
        <div className="topbar-badges">
          <span className="badge badge-mint">Ollama local</span>
          <span className="badge badge-outline">NETWORK_ENABLED=false</span>
          {health && <span className="badge badge-blue">{health.phase}</span>}
        </div>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Laboratorio 13 · corte vertical local</p>
          <h1>Auditar, contrastar y publicar sin inventar evidencia.</h1>
          <p>
            El dashboard pinta estados reales del backend. Una cita demuestra procedencia, no verdad. La red,
            el CRM y el laboratorio 09 permanecen fuera de este corte.
          </p>
          <div className="hero-actions">
            <button type="button" className="button primary" onClick={handleAudit} disabled={busy}>
              Auditar fixtures
            </button>
            <button type="button" className="button secondary" onClick={handleBuild} disabled={busy || !run}>
              Construir release
            </button>
          </div>
        </div>
        <aside className="budget-card">
          <p className="panel-kicker">Presupuesto</p>
          <dl>
            <div>
              <dt>Red</dt>
              <dd>{run?.network_enabled ? "habilitada" : "apagada"}</dd>
            </div>
            <div>
              <dt>URLs usadas</dt>
              <dd>{run?.urls_used ?? 0}</dd>
            </div>
            <div>
              <dt>Estado</dt>
              <dd>{run?.state ?? "sin corrida"}</dd>
            </div>
            <div>
              <dt>Release actual</dt>
              <dd>{current.release_id ?? "ninguno"}</dd>
            </div>
          </dl>
        </aside>
      </section>

      <section className="workspace-section" id="workspace">
        <div className="section-heading">
          <div>
            <p className="panel-kicker">Grafo vivo</p>
            <h2>El nodo solo se marca hecho si el backend llegó ahí.</h2>
          </div>
        </div>
        <FlowBoard state={run?.state ?? null} />
        {error && (
          <p className="error-banner" role="alert">
            {error}
          </p>
        )}
      </section>

      <section className="panels">
        <form
          className="reviewer-form"
          onSubmit={(event) => {
            event.preventDefault();
          }}
        >
          <label>
            Revisor humano
            <input value={reviewer} onChange={(event) => setReviewer(event.target.value)} />
          </label>
          <label>
            Razón
            <input value={reason} onChange={(event) => setReason(event.target.value)} />
          </label>
          <p>
            La aprobación exige el hash exacto. No existe `--approve=true`. Aprobadas: {approved.length}.
          </p>
        </form>

        <div className="tab-bar" role="tablist">
          {(["sources", "claims", "conflicts", "release"] as const).map((item) => (
            <button
              key={item}
              type="button"
              role="tab"
              className={tab === item ? "active" : ""}
              onClick={() => setTab(item)}
            >
              {item}
            </button>
          ))}
        </div>

        {tab === "sources" && (
          <div className="table-list">
            {(run?.sources ?? []).map((source) => (
              <article key={source.source_id}>
                <strong>{source.title}</strong>
                <p>
                  {source.source_id} · {source.independence} · {source.quarantine_status}
                </p>
                <code>{source.content_sha256.slice(0, 16)}…</code>
              </article>
            ))}
          </div>
        )}
        {tab === "claims" && (
          <div className="claim-grid">
            {(run?.claims ?? []).map((claim) => (
              <ClaimRow key={claim.claim_id} claim={claim} onApprove={handleApproveClaim} busy={busy} />
            ))}
          </div>
        )}
        {tab === "conflicts" && (
          <div className="table-list">
            {(run?.conflicts ?? []).map((conflict) => (
              <article key={conflict.conflict_id}>
                <strong>{conflict.topic}</strong>
                <p>
                  {conflict.claim_ids.join(" vs ")} · {conflict.materiality}
                </p>
                <p>{conflict.resolution ?? "Sin resolver: no se publica como hecho."}</p>
              </article>
            ))}
            <h3>Huecos</h3>
            {(run?.gaps ?? []).map((gap) => (
              <article key={gap.gap_id}>
                <strong>{gap.topic}</strong>
                <p>{gap.reason}</p>
              </article>
            ))}
          </div>
        )}
        {tab === "release" && (
          <div className="release-panel">
            <p>
              Candidato: <code>{run?.candidate_id ?? "—"}</code>
            </p>
            <p>
              Hash: <code>{run?.candidate_hash ?? "—"}</code>
            </p>
            <p>
              Publicación: <code>{run?.release_id ?? current.release_id ?? "—"}</code>
            </p>
            <p>
              JSONL: <code>{run?.jsonl_path ?? "—"}</code>
            </p>
            <p>Incluidas {run?.claims.filter((item) => item.status === "published").length ?? 0} afirmaciones publicadas.</p>
          </div>
        )}
      </section>
    </div>
  );
}
