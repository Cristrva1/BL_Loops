import React, { useEffect, useState } from "react";
import {
  askMeetingQuestion,
  fetchFixtures,
  fetchHealth,
  fetchMeetingDetail,
  fetchMeetings,
  fetchModels,
  parsePreview,
  summarizeStreamSSE,
} from "./api";
import type {
  ChatMessage,
  FixtureSample,
  MeetingListItem,
  MeetingMetadata,
  MeetingSummaryReport,
  PipelineEvent,
} from "./types";

export default function App() {
  // Config & Status
  const [ollamaOnline, setOllamaOnline] = useState<boolean>(true);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("qwen3.5:9b");
  const [selectedMode, setSelectedMode] = useState<string>("completo");

  // Input & Previews
  const [title, setTitle] = useState<string>("");
  const [transcriptText, setTranscriptText] = useState<string>("");
  const [fixtures, setFixtures] = useState<FixtureSample[]>([]);
  const [previewMeta, setPreviewMeta] = useState<MeetingMetadata | null>(null);

  // Pipeline Execution
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [currentEvent, setCurrentEvent] = useState<PipelineEvent | null>(null);
  const [activeTab, setActiveTab] = useState<string>("summary");

  // Output
  const [report, setReport] = useState<MeetingSummaryReport | null>(null);
  const [copiedNotice, setCopiedNotice] = useState<string | null>(null);

  // History & Chat
  const [historyMeetings, setHistoryMeetings] = useState<MeetingListItem[]>([]);
  const [showHistory, setShowHistory] = useState<boolean>(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatQuestion, setChatQuestion] = useState<string>("");
  const [chatLoading, setChatLoading] = useState<boolean>(false);

  // Load initial data
  useEffect(() => {
    fetchHealth()
      .then((h) => {
        setOllamaOnline(h.ollama_available);
        if (h.default_model) setSelectedModel(h.default_model);
      })
      .catch(() => setOllamaOnline(false));

    fetchModels()
      .then((m) => {
        if (m.models && m.models.length > 0) {
          setAvailableModels(m.models);
          if (!m.models.includes(selectedModel)) {
            setSelectedModel(m.models[0]);
          }
        }
      })
      .catch(() => {});

    fetchFixtures()
      .then((f) => {
        setFixtures(f);
        if (f.length > 0 && !transcriptText) {
          setTranscriptText(f[0].content);
          setTitle(f[0].title);
        }
      })
      .catch(() => {});

    loadHistory();
  }, []);

  // Update preview when text changes
  useEffect(() => {
    if (!transcriptText || transcriptText.trim().length < 20) {
      setPreviewMeta(null);
      return;
    }
    const timer = setTimeout(() => {
      parsePreview(transcriptText, title)
        .then((res) => setPreviewMeta(res.metadata))
        .catch(() => {});
    }, 400);
    return () => clearTimeout(timer);
  }, [transcriptText, title]);

  const loadHistory = () => {
    fetchMeetings()
      .then(setHistoryMeetings)
      .catch(() => {});
  };

  const handleLoadFixture = (fixture: FixtureSample) => {
    setTranscriptText(fixture.content);
    setTitle(fixture.title);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setTranscriptText(content);
      setTitle(file.name.replace(/\.[^/.]+$/, "").replace(/_/g, " ").toUpperCase());
    };
    reader.readAsText(file);
  };

  const handleGenerateSummary = async () => {
    if (!transcriptText.trim()) return;
    setIsProcessing(true);
    setCurrentEvent({
      stage: "init",
      progress: 5,
      message: "Iniciando análisis...",
    });

    await summarizeStreamSSE(
      {
        transcript_text: transcriptText,
        title: title.trim() || undefined,
        model: selectedModel,
        mode: selectedMode,
        save_to_db: true,
      },
      (event) => {
        setCurrentEvent(event);
        if (event.stage === "completed" && event.payload?.report) {
          setReport(event.payload.report);
          setIsProcessing(false);
          loadHistory();
        }
      },
      (err) => {
        alert("Error en el procesamiento: " + err.message);
        setIsProcessing(false);
      },
      () => {
        setIsProcessing(false);
      }
    );
  };

  const handleSelectHistoryItem = async (meetingId: string) => {
    try {
      const detail = await fetchMeetingDetail(meetingId);
      if (detail.report) {
        setReport(detail.report);
        setTitle(detail.meeting.title);
        setTranscriptText(detail.meeting.raw_transcript);
        setChatMessages(detail.chat_history || []);
        setShowHistory(false);
      }
    } catch (err: any) {
      alert("Error cargando reunión del historial: " + err.message);
    }
  };

  const handleCopy = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedNotice(label);
    setTimeout(() => setCopiedNotice(null), 2500);
  };

  const handleDownloadMarkdown = () => {
    if (!report) return;
    const md = `# Minuta: ${report.title}
Fecha: ${new Date(report.created_at).toLocaleDateString()}
Modelo: ${report.model_used}
Participantes: ${report.metadata.participants.join(", ")}

## Resumen Ejecutivo
${report.executive_summary}

## Decisiones Clave
${report.decisions.map((d) => `- **${d.decision}** (Motivo: ${d.rationale || "Consenso"})`).join("\n")}

## Compromisos y Tareas
| Tarea | Responsable | Plazo | Prioridad |
|---|---|---|---|
${report.action_items.map((a) => `| ${a.task} | ${a.assignee} | ${a.deadline || "Por definir"} | ${a.priority.toUpperCase()} |`).join("\n")}

## Minuta de Correo / Slack
${report.email_followup}
`;
    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `minuta_${report.title.toLowerCase().replace(/\s+/g, "_")}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleSendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatQuestion.trim() || !report) return;
    const q = chatQuestion.trim();
    setChatQuestion("");
    setChatMessages((prev) => [...prev, { question: q, answer: "Pensando..." }]);
    setChatLoading(true);

    try {
      const res = await askMeetingQuestion(report.meeting_id, q, selectedModel);
      setChatMessages((prev) =>
        prev.map((msg, i) => (i === prev.length - 1 ? { question: q, answer: res.answer } : msg))
      );
    } catch (err: any) {
      setChatMessages((prev) =>
        prev.map((msg, i) =>
          i === prev.length - 1 ? { question: q, answer: "Error: " + err.message } : msg
        )
      );
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand">
          <div className="brand-icon">M</div>
          <div>
            <div className="brand-title">BL_Loops · 25 Resúmenes de Videollamadas</div>
            <div className="brand-subtitle">IA Local con Ollama · Google Meet · Zoom · Teams</div>
          </div>
        </div>

        <div className="header-status">
          <div className={`status-pill ${ollamaOnline ? "" : "offline"}`}>
            <span className="status-dot"></span>
            <span>{ollamaOnline ? "Ollama Conectado (127.0.0.1:11434)" : "Ollama Desconectado"}</span>
          </div>

          <button className="btn-secondary" onClick={() => setShowHistory(!showHistory)}>
            📂 Historial ({historyMeetings.length})
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <main className="main-grid">
        {/* Left Column: Intake */}
        <section className="intake-column">
          <div className="card">
            <div className="card-title">
              <span>📥 Entrada de Transcripción</span>
              <label className="btn-secondary" style={{ padding: "0.3rem 0.6rem", fontSize: "0.75rem", cursor: "pointer" }}>
                📎 Subir archivo (.txt, .vtt, .srt)
                <input type="file" accept=".txt,.vtt,.srt" onChange={handleFileUpload} style={{ display: "none" }} />
              </label>
            </div>

            <div className="form-group">
              <label className="form-label">Título de la videollamada</label>
              <input
                type="text"
                placeholder="Ej. Planificación Sprint 4 / Standup Semanal"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>

            <div className="form-group">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
                <label className="form-label">Transcripción (pega aquí el texto de tu llamada)</label>
              </div>

              {fixtures.length > 0 && (
                <div className="quick-samples">
                  <span style={{ fontSize: "0.75rem", color: "var(--text-dim)", alignSelf: "center" }}>Ejemplos:</span>
                  {fixtures.map((fix) => (
                    <button key={fix.name} className="btn-sample" onClick={() => handleLoadFixture(fix)}>
                      {fix.title}
                    </button>
                  ))}
                </div>
              )}

              <textarea
                className="transcript-textarea"
                placeholder="00:00:10 Carlos: Buenos días equipo, hoy revisaremos los entregables..."
                value={transcriptText}
                onChange={(e) => setTranscriptText(e.target.value)}
              />
            </div>

            {/* Live Metadata Pre-check */}
            {previewMeta && (
              <div className="preview-pill-bar">
                <span className="badge badge-format">{previewMeta.detected_format}</span>
                <span className="badge badge-words">{previewMeta.total_words} palabras</span>
                <span className="badge badge-time">~{Math.round(previewMeta.duration_seconds / 60)} min</span>
                <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
                  👥 {previewMeta.participants.length} participantes: {previewMeta.participants.slice(0, 3).join(", ")}
                  {previewMeta.participants.length > 3 ? "..." : ""}
                </span>
              </div>
            )}

            {/* Model & Mode Controls */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
              <div className="form-group">
                <label className="form-label">Modelo Ollama</label>
                <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
                  {availableModels.length > 0 ? (
                    availableModels.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))
                  ) : (
                    <>
                      <option value="qwen3.5:9b">qwen3.5:9b (Recomendado)</option>
                      <option value="qwen3.5:4b">qwen3.5:4b (Rápido)</option>
                    </>
                  )}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Estilo de Análisis</label>
                <select value={selectedMode} onChange={(e) => setSelectedMode(e.target.value)}>
                  <option value="completo">Minuta Completa</option>
                  <option value="ejecutivo">Ejecutivo (TL;DR)</option>
                  <option value="tareas">Solo Compromisos y Tareas</option>
                  <option value="tecnico">Técnico y Arquitectura</option>
                </select>
              </div>
            </div>

            <button
              className="btn-primary"
              disabled={isProcessing || !transcriptText.trim()}
              onClick={handleGenerateSummary}
            >
              {isProcessing ? "⏳ Analizando con Ollama..." : "⚡ Generar Resumen Inteligente"}
            </button>
          </div>

          {/* SSE Live Streaming Monitor */}
          {isProcessing && currentEvent && (
            <div className="pipeline-monitor">
              <div className="progress-header">
                <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Pipeline en Ejecución</span>
                <span className="progress-pct">{currentEvent.progress}%</span>
              </div>
              <div className="progress-track">
                <div className="progress-bar-fill" style={{ width: `${currentEvent.progress}%` }}></div>
              </div>
              <div className="progress-message">{currentEvent.message}</div>
            </div>
          )}

          {/* History Drawer Modal / Popup */}
          {showHistory && (
            <div className="card" style={{ borderColor: "var(--primary)" }}>
              <div className="card-title">
                <span>Reuniones Guardadas ({historyMeetings.length})</span>
                <button className="btn-sample" onClick={() => setShowHistory(false)}>✕ Cerrar</button>
              </div>
              <div style={{ maxHeight: "250px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {historyMeetings.map((m) => (
                  <div
                    key={m.meeting_id}
                    onClick={() => handleSelectHistoryItem(m.meeting_id)}
                    style={{
                      padding: "0.6rem 0.8rem",
                      borderRadius: "6px",
                      backgroundColor: "var(--bg-input)",
                      cursor: "pointer",
                      fontSize: "0.82rem",
                      border: "1px solid var(--border-color)",
                    }}
                  >
                    <div style={{ fontWeight: 600, color: "var(--text-main)" }}>{m.title}</div>
                    <div style={{ color: "var(--text-dim)", fontSize: "0.75rem", marginTop: "0.2rem" }}>
                      {m.format.toUpperCase()} · {m.total_words} palabras · {new Date(m.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* Right Column: Structured Output */}
        <section className="results-column">
          <div className="tabs-bar">
            <button
              className={`tab-btn ${activeTab === "summary" ? "active" : ""}`}
              onClick={() => setActiveTab("summary")}
            >
              📌 Resumen Ejecutivo
            </button>
            <button
              className={`tab-btn ${activeTab === "decisions" ? "active" : ""}`}
              onClick={() => setActiveTab("decisions")}
            >
              🎯 Decisiones ({report ? report.decisions.length : 0})
            </button>
            <button
              className={`tab-btn ${activeTab === "actions" ? "active" : ""}`}
              onClick={() => setActiveTab("actions")}
            >
              ✅ Tareas y Compromisos ({report ? report.action_items.length : 0})
            </button>
            <button
              className={`tab-btn ${activeTab === "email" ? "active" : ""}`}
              onClick={() => setActiveTab("email")}
            >
              ✉️ Minuta para Correo / Slack
            </button>
            <button
              className={`tab-btn ${activeTab === "participants" ? "active" : ""}`}
              onClick={() => setActiveTab("participants")}
            >
              👥 Participantes & Métricas
            </button>
            <button
              className={`tab-btn ${activeTab === "chat" ? "active" : ""}`}
              onClick={() => setActiveTab("chat")}
            >
              💬 Preguntar a la Reunión
            </button>
          </div>

          <div className="tab-content">
            {!report ? (
              <div style={{ textAlign: "center", padding: "4rem 1rem", color: "var(--text-dim)" }}>
                <div style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>📋</div>
                <h3 style={{ color: "var(--text-muted)", marginBottom: "0.5rem" }}>
                  Aún no has procesado ninguna videollamada
                </h3>
                <p style={{ maxWidth: "450px", margin: "0 auto", fontSize: "0.88rem" }}>
                  Pega la transcripción en el panel izquierdo o selecciona un ejemplo de prueba y presiona
                  <strong> "Generar Resumen Inteligente"</strong>.
                </p>
              </div>
            ) : (
              <>
                {/* Actions Toolbar */}
                <div className="actions-toolbar">
                  {copiedNotice && (
                    <span style={{ fontSize: "0.8rem", color: "var(--accent-emerald)", alignSelf: "center" }}>
                      ✓ {copiedNotice}
                    </span>
                  )}
                  <button className="btn-secondary" onClick={() => handleCopy(report.email_followup, "Minuta copiada")}>
                    📋 Copiar Minuta
                  </button>
                  <button className="btn-secondary" onClick={handleDownloadMarkdown}>
                    ⬇️ Descargar .md
                  </button>
                  <button
                    className="btn-secondary"
                    onClick={() => {
                      const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `report_${report.meeting_id}.json`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                  >
                    ⬇️ Descargar JSON
                  </button>
                </div>

                {/* Tab: Summary */}
                {activeTab === "summary" && (
                  <div>
                    <div className="section-title">📌 Resumen Ejecutivo de la Reunión</div>
                    <div className="exec-summary-box">{report.executive_summary}</div>

                    {report.topics.length > 0 && (
                      <>
                        <div className="section-title">Temas Clave Abordados</div>
                        <div className="topics-grid">
                          {report.topics.map((top, idx) => (
                            <div key={idx} className="topic-card">
                              <div className="topic-title">{top.topic}</div>
                              <div className="topic-summary">{top.summary}</div>
                              {top.participants_involved.length > 0 && (
                                <div style={{ marginTop: "0.5rem", fontSize: "0.75rem", color: "var(--text-dim)" }}>
                                  Liderado por: {top.participants_involved.join(", ")}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </>
                    )}

                    {report.open_questions.length > 0 && (
                      <div style={{ marginTop: "1rem" }}>
                        <div className="section-title" style={{ color: "var(--accent-amber)" }}>
                          ⚠️ Dudas Abiertas o Bloqueos Pendientes
                        </div>
                        <ul style={{ paddingLeft: "1.25rem", color: "var(--text-muted)", fontSize: "0.88rem" }}>
                          {report.open_questions.map((q, idx) => (
                            <li key={idx} style={{ marginBottom: "0.35rem" }}>{q}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Tab: Decisions */}
                {activeTab === "decisions" && (
                  <div>
                    <div className="section-title">🎯 Decisiones y Acuerdos Adoptados</div>
                    {report.decisions.length === 0 ? (
                      <p style={{ color: "var(--text-dim)" }}>No se identificaron decisiones explícitas en esta llamada.</p>
                    ) : (
                      <div className="decisions-list">
                        {report.decisions.map((d, idx) => (
                          <div key={idx} className="decision-item">
                            <div className="decision-text">✓ {d.decision}</div>
                            {d.rationale && (
                              <div className="decision-meta">
                                <strong>Motivo:</strong> {d.rationale}
                              </div>
                            )}
                            {d.impact && (
                              <div className="decision-meta">
                                <strong>Impacto:</strong> {d.impact}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Tab: Action Items */}
                {activeTab === "actions" && (
                  <div>
                    <div className="section-title">✅ Matriz de Compromisos y Tareas</div>
                    {report.action_items.length === 0 ? (
                      <p style={{ color: "var(--text-dim)" }}>No se detectaron compromisos específicos en la llamada.</p>
                    ) : (
                      <div className="table-container">
                        <table className="action-table">
                          <thead>
                            <tr>
                              <th>Tarea / Compromiso</th>
                              <th>Responsable</th>
                              <th>Plazo / Fecha</th>
                              <th>Prioridad</th>
                            </tr>
                          </thead>
                          <tbody>
                            {report.action_items.map((act, idx) => (
                              <tr key={idx}>
                                <td>
                                  <div style={{ fontWeight: 500, color: "var(--text-main)" }}>{act.task}</div>
                                  {act.context && (
                                    <div style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>{act.context}</div>
                                  )}
                                </td>
                                <td>
                                  <span className="assignee-tag">👤 {act.assignee}</span>
                                </td>
                                <td>
                                  <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>
                                    {act.deadline || "Por definir"}
                                  </span>
                                </td>
                                <td>
                                  <span className={`priority-badge priority-${act.priority}`}>
                                    {act.priority}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}

                {/* Tab: Email / Slack */}
                {activeTab === "email" && (
                  <div>
                    <div className="section-title">✉️ Minuta Lista para Compartir (Slack / Teams / Correo)</div>
                    <div className="email-card">{report.email_followup}</div>
                  </div>
                )}

                {/* Tab: Participants & Metrics */}
                {activeTab === "participants" && (
                  <div>
                    <div className="section-title">👥 Participantes y Métricas de la Sesión</div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
                      <div className="card" style={{ padding: "1rem" }}>
                        <div style={{ color: "var(--text-dim)", fontSize: "0.75rem" }}>Duración Total</div>
                        <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--accent-cyan)" }}>
                          {Math.round(report.metadata.duration_seconds / 60)} minutos
                        </div>
                      </div>
                      <div className="card" style={{ padding: "1rem" }}>
                        <div style={{ color: "var(--text-dim)", fontSize: "0.75rem" }}>Total Palabras</div>
                        <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--accent-purple)" }}>
                          {report.metadata.total_words}
                        </div>
                      </div>
                      <div className="card" style={{ padding: "1rem" }}>
                        <div style={{ color: "var(--text-dim)", fontSize: "0.75rem" }}>Intervenciones (Turnos)</div>
                        <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--accent-amber)" }}>
                          {report.metadata.total_turns}
                        </div>
                      </div>
                    </div>

                    <div className="section-title">Distribución de Intervenciones por Hablante</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                      {Object.entries(report.metadata.speaker_turn_counts || {}).map(([speaker, count]) => {
                        const pct = Math.round((count / (report.metadata.total_turns || 1)) * 100);
                        return (
                          <div key={speaker} style={{ background: "var(--bg-input)", padding: "0.6rem 0.8rem", borderRadius: "6px" }}>
                            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem", marginBottom: "0.25rem" }}>
                              <span><strong>{speaker}</strong></span>
                              <span>{count} turnos ({pct}%)</span>
                            </div>
                            <div style={{ height: "6px", backgroundColor: "var(--bg-card)", borderRadius: "4px", overflow: "hidden" }}>
                              <div style={{ height: "100%", width: `${pct}%`, background: "var(--primary)" }}></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Tab: Chat with Meeting */}
                {activeTab === "chat" && (
                  <div className="chat-container">
                    <div className="section-title">💬 Consulta a la Reunión</div>
                    <div className="chat-messages">
                      {chatMessages.length === 0 ? (
                        <div style={{ color: "var(--text-dim)", fontSize: "0.85rem", textAlign: "center", margin: "auto" }}>
                          Haz preguntas sobre lo conversado (ej. "¿Quién propuso el cambio de base de datos?", "¿Qué día entregará Ana el reporte?").
                        </div>
                      ) : (
                        chatMessages.map((msg, i) => (
                          <React.Fragment key={i}>
                            <div className="chat-bubble user">{msg.question}</div>
                            <div className="chat-bubble assistant">{msg.answer}</div>
                          </React.Fragment>
                        ))
                      )}
                    </div>

                    <form onSubmit={handleSendChat} className="chat-input-row">
                      <input
                        type="text"
                        placeholder="Haz una pregunta sobre esta reunión..."
                        value={chatQuestion}
                        onChange={(e) => setChatQuestion(e.target.value)}
                        disabled={chatLoading}
                      />
                      <button className="btn-primary" type="submit" disabled={chatLoading || !chatQuestion.trim()}>
                        {chatLoading ? "..." : "Preguntar"}
                      </button>
                    </form>
                  </div>
                )}
              </>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
