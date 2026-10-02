"""Demostración interactiva de consola con fixtures sintéticos."""

from __future__ import annotations

import asyncio

from .config import Settings
from .contracts import SummarizeRequest
from .ollama_client import OllamaClient
from .storage import Storage
from .summarizer import MeetingSummarizerEngine

SAMPLE_TRANSCRIPT = """
00:00:05 Carlos Mendoza: Buenos días equipo. Hoy tenemos que cerrar los acuerdos para el lanzamiento de la versión 2.0 y asignar los pendientes críticos.
00:00:18 Ana Sofía: Hola Carlos. Por el lado de frontend, ya integramos los nuevos componentes de visualización. Solo nos falta probar el rendimiento con conjuntos de datos grandes.
00:00:32 Jorge Ramírez: Desde el backend, la migración a SQLite local y el endpoint SSE ya quedaron listos. Hice pruebas de carga con 500 solicitudes por minuto y el tiempo de respuesta se mantiene bajo 15ms.
00:00:50 Carlos Mendoza: Excelente trabajo de ambos. Respecto a la base de datos, ¿decidimos mantener SQLite local para todos los laboratorios o vamos a considerar Postgres para alguno?
00:01:05 Jorge Ramírez: Acordamos en la sesión anterior que cada laboratorio debe ser 100% autónomo y portable, por lo que SQLite embebido es la mejor decisión técnica. No requiere contenedores externos ni configuración compleja.
00:01:25 Carlos Mendoza: Totalmente de acuerdo, ratificamos SQLite como el estándar definitivo. Ahora revisemos los compromisos: Ana, ¿cuándo puedes tener terminadas las pruebas de estrés del frontend?
00:01:40 Ana Sofía: Me comprometo a tener el informe completo y las optimizaciones de renderizado listas este jueves antes de las 5:00 PM.
00:01:52 Carlos Mendoza: Perfecto. Jorge, tú te encargas de redactar la documentación de arquitectura en docs/humano/ y preparar los casos de prueba con pytest para el viernes por la mañana.
00:02:08 Jorge Ramírez: Enterado Carlos, lo tendré el viernes a las 11:00 AM sin falta.
00:02:15 Carlos Mendoza: Excelente. Por mi parte, yo prepararé la presentación ejecutiva para los directores el próximo lunes. ¿Hay algún bloqueo o duda pendiente?
00:02:28 Ana Sofía: Solo confirmar si los modelos locales de Ollama correrán en la máquina de pruebas o si cada desarrollador usará su GPU.
00:02:40 Carlos Mendoza: Cada desarrollador usará su Ollama local con qwen3.5:9b. Si no hay más dudas, cerramos la llamada. ¡Gracias a todos!
"""


async def run_demo() -> None:
    print("=" * 70)
    print("BL_Loops · Laboratorio 25: Resúmenes de Videollamadas (Demo Local)")
    print("=" * 70)

    settings = Settings()
    ollama = OllamaClient(
        base_url=settings.ollama_base_url,
        default_model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
        num_ctx=settings.ollama_num_ctx,
    )

    print(f"1. Verificando conexión con Ollama en {settings.ollama_base_url}...")
    if not ollama.is_available():
        print("AVISO: Ollama no respondió en 127.0.0.1:11434.")
        print("Asegúrate de iniciar Ollama antes de ejecutar la inferencia.")
        return

    print("   Ollama detectado y disponible.")
    models = ollama.list_models()
    print(f"   Modelos instalados: {', '.join(models[:4])} (total: {len(models)})")
    target_model = settings.ollama_model if settings.ollama_model in models else (models[0] if models else "qwen3.5:9b")
    print(f"   Modelo seleccionado: {target_model}")

    storage = Storage(settings.get_db_path())
    engine = MeetingSummarizerEngine(ollama, storage)

    req = SummarizeRequest(
        transcript_text=SAMPLE_TRANSCRIPT,
        title="Sincronización de Lanzamiento v2.0",
        model=target_model,
        mode="completo",
    )

    print(f"\n2. Procesando transcripción ({len(SAMPLE_TRANSCRIPT.split())} palabras)...")
    last_report = None

    async for event in engine.summarize_stream(req):
        pct = event.progress
        print(f"   [{pct:3d}%] {event.message}")
        if event.stage == "completed" and event.payload:
            last_report = event.payload.get("report")

    if last_report:
        print("\n" + "=" * 70)
        print("RESULTADO DE LA MINUTA ESTRUCTURADA:")
        print("=" * 70)
        print(f"\n📌 RESUMEN EJECUTIVO:\n{last_report['executive_summary']}")

        print("\n🎯 DECISIONES ACORDADAS:")
        for d in last_report.get("decisions", []):
            print(f"  • {d['decision']} (Motivo: {d.get('rationale') or 'Consenso de equipo'})")

        print("\n✅ COMPROMISOS / TAREAS ASIGNADAS:")
        for a in last_report.get("action_items", []):
            deadline = a.get("deadline") or "Por definir"
            print(f"  • [{a['priority'].upper()}] {a['assignee']}: {a['task']} → Plazo: {deadline}")

        print("\n✉️ MINUTA LISTA PARA ENVIAR (SLACK / EMAIL):")
        print("-" * 50)
        print(last_report.get("email_followup", ""))
        print("-" * 50)
        print(f"\nReunión guardada exitosamente en SQLite: {settings.get_db_path()}")


def main() -> None:
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
