"""Bucle acotado del agente: decidir, buscar una vez y responder con evidencia."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Protocol, TextIO

from sales_agent.config import Settings
from sales_agent.embeddings import EMBEDDING_PROFILE, EmbeddingClient
from sales_agent.index import Embedder, HybridSalesIndex, SearchResult
from sales_agent.ollama_client import ChatResult, OllamaChatClient, ToolCall
from sales_agent.prompting import (
    SALES_LIBRARY_TOOL,
    SYSTEM_PROMPT,
    TOOL_NAME,
    source_label,
    tool_result,
    valid_citations,
)
from sales_agent.run_log import RunLogger


class AgentProtocolError(RuntimeError):
    """El modelo intento continuar fuera del ciclo acotado del agente."""


class ChatClient(Protocol):
    def chat(
        self,
        messages: list[dict[str, object]],
        tools: list[dict[str, object]] | None = None,
    ) -> ChatResult: ...


class SalesIndex(Protocol):
    def search(
        self,
        question: str,
        *,
        top_k: int,
        mode: str,
        embedder: Embedder,
    ) -> tuple[SearchResult, ...]: ...


@dataclass(frozen=True, slots=True)
class AgentAnswer:
    answer: str
    sources: tuple[SearchResult, ...]
    tool_query: str
    route: str
    citation_valid: bool
    run_path: Path


def _history_messages(
    history: Sequence[dict[str, str]], history_turns: int
) -> list[dict[str, object]]:
    if history_turns == 0:
        return []
    allowed: list[dict[str, object]] = []
    for message in history:
        role = message.get("role")
        content = message.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            allowed.append({"role": role, "content": content.strip()})
    return allowed[-history_turns * 2 :]


def _select_tool_call(result: ChatResult, question: str) -> tuple[ToolCall, str]:
    if len(result.tool_calls) == 1:
        call = result.tool_calls[0]
        query = call.arguments.get("query")
        if call.name == TOOL_NAME and isinstance(query, str):
            normalized = " ".join(query.split())
            if 2 <= len(normalized) <= 600:
                return ToolCall(call.call_id, TOOL_NAME, {"query": normalized}), "model_tool_call"
    return (
        ToolCall("runtime-fallback", TOOL_NAME, {"query": question}),
        "runtime_fallback",
    )


def _assistant_tool_message(call: ToolCall) -> dict[str, object]:
    return {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "id": call.call_id,
                "type": "function",
                "function": {"name": call.name, "arguments": call.arguments},
            }
        ],
    }


def run_turn(
    settings: Settings,
    question: str,
    *,
    history: Sequence[dict[str, str]],
    index: SalesIndex | None = None,
    embedder: Embedder | None = None,
    client: ChatClient | None = None,
    output: TextIO = sys.stdout,
) -> AgentAnswer:
    query = " ".join(question.split())
    if not query:
        raise ValueError("La pregunta no puede estar vacia.")
    if len(query) > 4000:
        raise ValueError("La pregunta supera el limite de 4000 caracteres.")

    actual_embedder = embedder or EmbeddingClient(
        settings.base_url,
        settings.embedding_model,
        settings.embedding_dimensions,
        settings.timeout_seconds,
    )
    actual_index = index or HybridSalesIndex(
        settings.index_path,
        settings.embedding_model,
        settings.embedding_dimensions,
        EMBEDDING_PROFILE,
    )
    actual_client = client or OllamaChatClient(
        settings.base_url,
        settings.chat_model,
        settings.timeout_seconds,
    )
    logger = RunLogger(
        settings.runs_dir,
        chat_model=settings.chat_model,
        embedding_model=settings.embedding_model,
        dimensions=settings.embedding_dimensions,
        index_ref=settings.index_path.relative_to(settings.root).as_posix(),
    )
    logger.emit(
        "run.started",
        payload={
            "input_chars": len(query),
            "history_messages": min(len(history), settings.history_turns * 2),
            "tool_limit": 1,
            "raw_input_stored": False,
        },
    )
    sources: tuple[SearchResult, ...] = ()
    tool_calls_executed = 0
    print(
        f"Agente de ventas | chat={settings.chat_model} | "
        f"embedding={settings.embedding_model}/{settings.embedding_dimensions}",
        file=output,
    )

    try:
        planner_messages: list[dict[str, object]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *_history_messages(history, settings.history_turns),
            {"role": "user", "content": query},
        ]
        logger.emit("model.requested", node_id="decide", state="waiting")
        decision_started = perf_counter()
        decision = actual_client.chat(planner_messages, tools=[SALES_LIBRARY_TOOL])
        decision_ms = round((perf_counter() - decision_started) * 1000, 3)
        call, route = _select_tool_call(decision, query)
        tool_query = str(call.arguments["query"])
        logger.emit(
            "model.completed",
            node_id="decide",
            state="done",
            payload={
                "route": route,
                "requested_tool_calls": len(decision.tool_calls),
                "tool_query_chars": len(tool_query),
            },
            metrics={
                "wall_duration_ms": decision_ms,
                "ollama_duration_ms": decision.total_duration_ms,
                "prompt_tokens": decision.prompt_tokens,
                "output_tokens": decision.output_tokens,
            },
        )
        print(f"[1/4 decidir] {route}", file=output)

        logger.emit("tool.started", node_id=TOOL_NAME, state="running")
        tool_started = perf_counter()
        tool_calls_executed = 1
        sources = actual_index.search(
            tool_query,
            top_k=settings.top_k,
            mode="hybrid",
            embedder=actual_embedder,
        )
        tool_ms = round((perf_counter() - tool_started) * 1000, 3)
        logger.emit(
            "tool.completed",
            node_id=TOOL_NAME,
            state="done",
            payload={"matches": len(sources), "mode": "hybrid"},
            metrics={"wall_duration_ms": tool_ms},
        )
        print(f"[2/4 herramienta] {TOOL_NAME} -> {len(sources)} fuentes", file=output)

        if not sources:
            answer = (
                "No encontre evidencia suficiente en la biblioteca filtrada para responder "
                "con rigor. Conviene enriquecer o corregir el corpus antes de usar esta "
                "respuesta para una decision de ventas."
            )
            print("[3/4 evidencia] insuficiente", file=output)
            print("[4/4 responder] sin generacion\n", file=output)
            print(f"Respuesta > {answer}", file=output)
            logger.finish("completed", "no_matches", sources=0, tool_calls=tool_calls_executed)
            return AgentAnswer(answer, (), tool_query, route, True, logger.path)

        evidence = tool_result(sources)
        logger.emit(
            "node.completed",
            node_id="ground",
            state="done",
            payload={
                "sources": len(sources),
                "context_chars": sum(len(source.content) for source in sources),
                "untrusted_evidence": True,
            },
        )
        print(f"[3/4 evidencia] {len(sources)} fragmentos no confiables delimitados", file=output)
        final_messages = [
            *planner_messages,
            _assistant_tool_message(call),
            {"role": "tool", "tool_name": TOOL_NAME, "content": evidence},
        ]
        logger.emit("model.requested", node_id="answer", state="waiting")
        answer_started = perf_counter()
        generated = actual_client.chat(final_messages, tools=None)
        answer_ms = round((perf_counter() - answer_started) * 1000, 3)
        if generated.tool_calls or not generated.content:
            raise AgentProtocolError(
                "La respuesta final intento abrir otro ciclo o no produjo contenido."
            )
        citation_ok = valid_citations(generated.content, len(sources))
        logger.emit(
            "model.completed",
            node_id="answer",
            state="done",
            payload={
                "answer_chars": len(generated.content),
                "citation_valid": citation_ok,
            },
            metrics={
                "wall_duration_ms": answer_ms,
                "ollama_duration_ms": generated.total_duration_ms,
                "prompt_tokens": generated.prompt_tokens,
                "output_tokens": generated.output_tokens,
            },
        )
        print(f"[4/4 responder] done | {answer_ms:.1f} ms\n", file=output)
        print(f"Respuesta > {generated.content}\n\nFuentes:", file=output)
        for number, source in enumerate(sources, 1):
            vector = "-" if source.vector_score is None else f"{source.vector_score:.3f}"
            print(
                f"- {source_label(number, source)} | estado={source.source_status} | "
                f"lexical={source.lexical_rank or '-'} | vector={vector}",
                file=output,
            )
        if not citation_ok:
            print("ADVERTENCIA: la respuesta no uso citas validas.", file=output)
        logger.finish("completed", "answered", sources=len(sources), tool_calls=tool_calls_executed)
        print(f"Traza JSONL: {logger.path.relative_to(settings.root)}", file=output)
        return AgentAnswer(
            generated.content,
            sources,
            tool_query,
            route,
            citation_ok,
            logger.path,
        )
    except (Exception, KeyboardInterrupt) as exc:
        if not logger.finished:
            logger.emit(
                "error.raised",
                node_id="agent",
                state="failed",
                payload={"error_type": type(exc).__name__},
            )
            logger.finish(
                "failed",
                "agent_error",
                sources=len(sources),
                tool_calls=tool_calls_executed,
            )
        raise


class Conversation:
    """Sesion multi-turno en RAM; cada turno conserva su propia traza sanitizada."""

    def __init__(
        self,
        settings: Settings,
        *,
        index: SalesIndex | None = None,
        embedder: Embedder | None = None,
        client: ChatClient | None = None,
        output: TextIO = sys.stdout,
    ) -> None:
        self.settings = settings
        self.index = index or HybridSalesIndex(
            settings.index_path,
            settings.embedding_model,
            settings.embedding_dimensions,
            EMBEDDING_PROFILE,
        )
        self.embedder = embedder or EmbeddingClient(
            settings.base_url,
            settings.embedding_model,
            settings.embedding_dimensions,
            settings.timeout_seconds,
        )
        self.client = client or OllamaChatClient(
            settings.base_url,
            settings.chat_model,
            settings.timeout_seconds,
        )
        self.output = output
        self._history: list[dict[str, str]] = []

    @property
    def history(self) -> tuple[dict[str, str], ...]:
        return tuple(self._history)

    def clear(self) -> None:
        """Descarta de forma explicita toda la memoria volatil de la sesion."""
        self._history.clear()

    def ask(self, question: str) -> AgentAnswer:
        result = run_turn(
            self.settings,
            question,
            history=self._history,
            index=self.index,
            embedder=self.embedder,
            client=self.client,
            output=self.output,
        )
        if self.settings.history_turns:
            self._history.extend(
                (
                    {"role": "user", "content": " ".join(question.split())},
                    {"role": "assistant", "content": result.answer},
                )
            )
            self._history = self._history[-self.settings.history_turns * 2 :]
        return result
