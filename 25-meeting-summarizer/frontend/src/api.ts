import type {
  ChatMessage,
  FixtureSample,
  MeetingListItem,
  MeetingMetadata,
  MeetingSummaryReport,
  PipelineEvent,
} from "./types";

const API_BASE = "";

export async function fetchHealth(): Promise<{ status: string; ollama_available: boolean; default_model: string }> {
  const resp = await fetch(`${API_BASE}/api/v1/health`);
  if (!resp.ok) throw new Error("Error comprobando el estado del servidor");
  return resp.json();
}

export async function fetchModels(): Promise<{ models: string[]; current_default: string }> {
  const resp = await fetch(`${API_BASE}/api/v1/models`);
  if (!resp.ok) throw new Error("Error obteniendo modelos de Ollama");
  return resp.json();
}

export async function fetchFixtures(): Promise<FixtureSample[]> {
  const resp = await fetch(`${API_BASE}/api/v1/fixtures`);
  if (!resp.ok) return [];
  const data = await resp.json();
  return data.fixtures || [];
}

export async function parsePreview(
  text: string,
  title?: string
): Promise<{ metadata: MeetingMetadata; total_turns: number }> {
  const resp = await fetch(`${API_BASE}/api/v1/parse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: jsonStringify({ transcript_text: text, title }),
  });
  if (!resp.ok) throw new Error("Error analizando transcripción");
  return resp.json();
}

export async function summarizeStreamSSE(
  params: {
    transcript_text: string;
    title?: string;
    model?: string;
    mode?: string;
    save_to_db?: boolean;
  },
  onEvent: (event: PipelineEvent) => void,
  onError: (err: Error) => void,
  onComplete: () => void
): Promise<() => void> {
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/summarize/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }

      if (!response.body) {
        throw new Error("No se recibió flujo de datos SSE del servidor.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const block of lines) {
          const trimmed = block.trim();
          if (trimmed.startsWith("data:")) {
            const rawJson = trimmed.slice(5).trim();
            if (rawJson) {
              try {
                const parsed: PipelineEvent = JSON.parse(rawJson);
                onEvent(parsed);
              } catch (e) {
                console.warn("Error parseando evento SSE:", e);
              }
            }
          }
        }
      }

      onComplete();
    } catch (error: any) {
      if (error.name !== "AbortError") {
        onError(error);
      }
    }
  })();

  return () => controller.abort();
}

export async function fetchMeetings(): Promise<MeetingListItem[]> {
  const resp = await fetch(`${API_BASE}/api/v1/meetings`);
  if (!resp.ok) return [];
  return resp.json();
}

export async function fetchMeetingDetail(
  meetingId: string
): Promise<{ meeting: any; report: MeetingSummaryReport | null; chat_history: ChatMessage[] }> {
  const resp = await fetch(`${API_BASE}/api/v1/meetings/${meetingId}`);
  if (!resp.ok) throw new Error("Reunión no encontrada");
  return resp.json();
}

export async function askMeetingQuestion(
  meetingId: string,
  question: string,
  model?: string
): Promise<{ answer: string; citations: string[] }> {
  const resp = await fetch(`${API_BASE}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ meeting_id: meetingId, question, model }),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: "Error en la consulta" }));
    throw new Error(err.detail || "Error en la consulta");
  }
  return resp.json();
}

function jsonStringify(obj: any): string {
  return JSON.stringify(obj);
}
