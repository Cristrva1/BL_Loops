import { useEffect, useMemo, useState } from "react";
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
import {
  ApiError,
  buildRelease,
  fetchHealth,
  fetchLibrary,
  getCurrentRelease,
  getRun,
  publishRelease,
  startAudit,
  submitReview,
} from "./api";
import type { ClaimRecord, Health, LibraryIndex, RunSnapshot, WorkflowState } from "./types";

const GRAPH_NODES = [
  { id: "ingest", title: "Ingesta y cuarentena" },
  { id: "registry", title: "Registro de fuentes" },
  { id: "extraction", title: "Extracción" },
  { id: "ledger", title: "Ledger de claims" },
  { id: "research", title: "Plan e investigación" },
  { id: "verification", title: "Verificación" },
  { id: "review", title: "Revisión humana" },
  { id: "staging", title: "Staging" },
  { id: "gate", title: "Gate reproducible" },
  { id: "release", title: "KnowledgeRelease" },
] as const;

const NODE_FOR_STATE: Record<WorkflowState, string> = {
  scope_draft: "ingest",
  inventory_running: "ingest",
  gaps_ready: "research",
  research_planned: "research",
  awaiting_external_authorization: "research",
  collecting_local: "research",
  sources_normalized: "registry",
  claims_extracted: "extraction",
  verification_running: "verification",
  conflicts_open: "verification",
  review_pending: "review",
  changes_requested: "review",
  approved: "review",
  rejected: "review",
  staging: "staging",
  validating: "gate",
  published: "release",
  failed: "release",
};

const STATE_RANK: Record<WorkflowState, number> = {
  scope_draft: 0,
  inventory_running: 1,
  gaps_ready: 2,
  research_planned: 3,
  awaiting_external_authorization: 4,
  collecting_local: 5,
  sources_normalized: 6,
  claims_extracted: 7,
  verification_running: 8,
  conflicts_open: 9,
  review_pending: 10,
  changes_requested: 10,
  approved: 12,
  rejected: 10,
  staging: 13,
  validating: 14,
  published: 15,
  failed: 99,
};

const NODE_DONE_AT: Record<string, number> = {
  ingest: 2,
  research: 6,
  registry: 7,
  extraction: 8,
  ledger: 8,
  verification: 10,
  review: 13,
  staging: 14,
  gate: 15,
  release: 16,
};

type NodeVisual = "idle" | "running" | "done" | "failed" | "blocked";

function visualFor(state: WorkflowState | null, nodeId: string): NodeVisual {
  if (!state) return "idle";
  const currentId = NODE_FOR_STATE[state];
  if (state === "failed") return nodeId === "release" ? "failed" : "idle";
  if (nodeId === currentId) {
    if (state === "awaiting_external_authorization") return "blocked";
    if (state === "published") return "done";
    return "running";
  }
  if (STATE_RANK[state] >= (NODE_DONE_AT[nodeId] ?? 99)) return "done";
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

const LIBRARY_NODES = [
  { id: "inventory", title: "Inventario de fichas" },
  { id: "catalogs", title: "Catálogos" },
  { id: "rights", title: "Gate de derechos" },
  { id: "copy", title: "Copia legal o dossier" },
  { id: "export", title: "Exportación explícita" },
] as const;

function libraryVisual(
  library: LibraryIndex,
  nodeId: string,
): NodeVisual {
  if (!library.loop_id) return "idle";
  const hasCopy = library.works.some((item) => item.has_legal_copy);
  const hasFailed = library.works.some((item) => item.status === "failed");
  const hasReady = library.works.some(
    (item) => item.status === "dossier_ready" || item.status === "copy_acquired",
  );
  if (nodeId === "inventory") return library.inventory_count > 0 || library.works.length > 0 ? "done" : "idle";
  if (nodeId === "catalogs") return library.works.some((item) => item.offers_count > 0) ? "done" : "running";
  if (nodeId === "rights") return hasReady || hasFailed ? "done" : "running";
  if (nodeId === "copy") {
    if (hasFailed) return "failed";
    if (hasCopy) return "done";
    return hasReady ? "done" : "running";
  }
  return "blocked";
}

function LibraryBoard({ library }: { library: LibraryIndex }) {
  const nodes = useMemo<Node[]>(
    () =>
      LIBRARY_NODES.map((item, index) => {
        const visual = libraryVisual(library, item.id);
        return {
          id: item.id,
          position: { x: index * 250, y: 24 },
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
    [library],
  );
  const edges = useMemo<Edge[]>(() => {
    const pairs: Array<[string, string]> = [
      ["inventory", "catalogs"],
      ["catalogs", "rights"],
      ["rights", "copy"],
      ["copy", "export"],
    ];
    return pairs.map(([source, target]) => ({
      id: `${source}-${target}`,
      source,
      target,
      markerEnd: { type: MarkerType.ArrowClosed, color: "#cbd5e1" },
      style: { stroke: "#cbd5e1", strokeWidth: 2 },
    }));
  }, []);
  const copies = library.works.filter((item) => item.has_legal_copy).length;
  return (
    <div>
      <div className="flow-canvas" aria-label="Grafo del loop de biblioteca">
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
        </ReactFlow>
      </div>
      <p className="library-summary">
        {library.loop_id
          ? `${library.works.length} fichas · ${copies} copias legales · loop ${library.loop_id}`
          : "Sin índice en .local/library. Ejecuta sales-curator library research."}
      </p>
      <div className="table-list">
        {library.works.map((work) => (
          <article key={work.work_id}>
            <strong>{work.title}</strong>
            <p>
              {work.author ?? "sin autor"} · {work.status} · ofertas {work.offers_count} ·{" "}
              {work.has_legal_copy ? "copia legal" : "sin PDF legal"}
            </p>
            <small>{work.gaps[0] ?? "sin huecos"}</small>
          </article>
        ))}
      </div>
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
  const [tab, setTab] = useState<"sources" | "claims" | "conflicts" | "events" | "release">(
    "sources",
  );
  const [library, setLibrary] = useState<LibraryIndex>({
    loop_id: null,
    inventory_count: 0,
    works: [],
  });

  async function refreshExtras() {
    const info = await fetchHealth();
    setHealth(info);
    const pointer = await getCurrentRelease();
    setCurrent(pointer);
    const libraryIndex = await fetchLibrary();
    setLibrary(libraryIndex);
  }

  useEffect(() => {
    refreshExtras().catch(() => {
      setError("No se pudo conectar al backend en el puerto 8013.");
    });
  }, []);

  const runId = run?.run_id;

  useEffect(() => {
    if (!runId) return;
    const source = new EventSource(`/api/runs/${runId}/events`);
    const onTerminal = () => {
      getRun(runId)
        .then(setRun)
        .catch(() => undefined);
      source.close();
    };
    source.addEventListener("run.terminal", onTerminal);
    source.onerror = () => source.close();
    return () => {
      source.removeEventListener("run.terminal", onTerminal);
      source.close();
    };
  }, [runId]);

  async function handleAudit() {
    setBusy(true);
    setError(null);
    try {
      const snapshot = await startAudit();
      setRun(snapshot);
      await refreshExtras();
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

  async function handleApprovePublishable() {
    if (!run) return;
    setBusy(true);
    setError(null);
    try {
      let approvedCount = 0;
      for (const claim of run.claims) {
        if (
          claim.status === "human_approved" ||
          claim.status === "published" ||
          claim.status === "disputed"
        ) {
          continue;
        }
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
          approvedCount += 1;
        } catch {
          // El gate técnico rechaza claims no publicables; se dejan visibles.
        }
      }
      const snapshot = await getRun(run.run_id);
      setRun(snapshot);
      if (approvedCount === 0) {
        setError("Ninguna afirmación nueva pasó el gate técnico.");
      }
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
      await refreshExtras();
      setTab("release");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "No se pudo construir el staging");
    } finally {
      setBusy(false);
    }
  }

  async function handlePublish() {
    if (!run?.candidate_id || !run.candidate_hash) return;
    setBusy(true);
    setError(null);
    try {
      const snapshot = await publishRelease({
        run_id: run.run_id,
        candidate_id: run.candidate_id,
        expected_hash: run.candidate_hash,
        reviewer,
        reason,
      });
      setRun(snapshot);
      await refreshExtras();
      setTab("release");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "No se pudo publicar el candidato");
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
          <span className="badge badge-mint">
            {health?.model_configured ? "Modelo Ollama configurado" : "Extractor determinista"}
          </span>
          <span className="badge badge-outline">
            {health?.network_enabled ? "red habilitada" : "NETWORK_ENABLED=false"}
          </span>
          {health && <span className="badge badge-blue">{health.phase}</span>}
        </div>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Laboratorio 13 · corte vertical local</p>
          <h1>Auditar, contrastar y publicar sin inventar evidencia.</h1>
          <p>
            El dashboard pinta estados reales del backend. Una cita demuestra procedencia, no verdad. La red,
            el CRM y el laboratorio 09 permanecen fuera de este corte. Publicar exige el hash exacto del
            candidato en staging.
          </p>
          <div className="hero-actions">
            <button type="button" className="button primary" onClick={handleAudit} disabled={busy}>
              Auditar fixtures
            </button>
            <button
              type="button"
              className="button ghost"
              onClick={handleApprovePublishable}
              disabled={busy || !run || run.state !== "review_pending"}
            >
              Aprobar claims publicables
            </button>
            <button
              type="button"
              className="button secondary"
              onClick={handleBuild}
              disabled={busy || run?.state !== "review_pending"}
            >
              Construir staging
            </button>
            <button
              type="button"
              className="button primary"
              onClick={handlePublish}
              disabled={busy || run?.state !== "staging" || !run?.candidate_hash}
            >
              Publicar hash exacto
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
            <div>
              <dt>Claims aprobados</dt>
              <dd>{approved.length}</dd>
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

      <section className="workspace-section" id="library">
        <div className="section-heading">
          <div>
            <p className="panel-kicker">Biblioteca</p>
            <h2>El loop de fichas vive en CLI; aquí solo se lee el índice local.</h2>
          </div>
        </div>
        <LibraryBoard library={library} />
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
          {(["sources", "claims", "conflicts", "events", "release"] as const).map((item) => (
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
        {tab === "events" && (
          <div className="table-list">
            <div className="metrics-grid">
              {Object.entries(run?.metrics ?? {}).map(([key, value]) => (
                <article key={key}>
                  <strong>{key}</strong>
                  <p>{value ?? "—"}</p>
                </article>
              ))}
            </div>
            {(run?.events ?? []).map((event) => (
              <article key={`${event.node_id}-${event.sequence}`}>
                <strong>
                  {event.sequence}. {event.node_id}
                </strong>
                <p>
                  {event.state}
                  {event.error ? ` · ${event.error}` : ""}
                </p>
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
            <p>
              Incluidas {run?.candidate_diff?.included_claim_ids.length ?? 0} afirmaciones;
              excluidas {run?.candidate_diff?.excluded_claim_ids.length ?? 0}.
            </p>
            <p>
              Publicadas ahora: {run?.claims.filter((item) => item.status === "published").length ?? 0}.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
