"""Cliente para interactuar con IA Local (Ollama) para planificar videos."""

import json
import logging

import httpx

from hyperframes_studio.schemas import SceneSpec, VideoBrief

logger = logging.getLogger(__name__)

DEFAULT_SCENES = [
    SceneSpec(
        id="scene-1-intro",
        title="Introducción a HyperFrames",
        start_time=0.0,
        duration=3.0,
        headline="HyperFrames: Write HTML. Render Video.",
        body="El framework open-source que convierte HTML, CSS y animaciones en videos MP4 deterministas.",
        bg_gradient="linear-gradient(135deg, #090d16 0%, #1e1b4b 100%)",
        accent_color="#6366f1",
        badge_text="Framework Audiovisual",
        code_snippet="npx hyperframes init my-video",
    ),
    SceneSpec(
        id="scene-2-architecture",
        title="Arquitectura Declarativa",
        start_time=3.0,
        duration=3.0,
        headline="HTML + CSS + GSAP Seekable Timelines",
        body="Define clips con data-start y data-duration. Chrome Headless renderiza cuadro por cuadro a 30/60 FPS.",
        bg_gradient="linear-gradient(135deg, #090d16 0%, #064e3b 100%)",
        accent_color="#10b981",
        badge_text="Seekable Timelines",
        code_snippet='<div class="clip" data-start="0" data-duration="3">',
    ),
    SceneSpec(
        id="scene-3-cli",
        title="Cómo Usarlo",
        start_time=6.0,
        duration=3.0,
        headline="Flujo de Trabajo del Desarrollador",
        body="Scaffolding instantáneo, previsualización en vivo en el navegador y compilación a MP4 con FFmpeg.",
        bg_gradient="linear-gradient(135deg, #090d16 0%, #701a75 100%)",
        accent_color="#d946ef",
        badge_text="Dev Loop",
        code_snippet="npx hyperframes render -o video.mp4",
    ),
    SceneSpec(
        id="scene-4-capabilities",
        title="¿Qué Puede Hacer?",
        start_time=9.0,
        duration=3.0,
        headline="Capacidades de Producción",
        body="Lanzamientos de producto, explainers, motion graphics, audio normalizado LUFS y overlays WebM transparentes.",
        bg_gradient="linear-gradient(135deg, #090d16 0%, #7c2d12 100%)",
        accent_color="#f97316",
        badge_text="Capacidades",
        code_snippet="Render determinista · 100% Local · Cero costes cloud",
    ),
    SceneSpec(
        id="scene-5-outro",
        title="Construye para Agentes",
        start_time=12.0,
        duration=3.0,
        headline="Diseñado para Agentes de Código",
        body="20 skills nativas para Claude Code, Cursor, Codex y agentes locales para dirigir y renderizar automáticamente.",
        bg_gradient="linear-gradient(135deg, #090d16 0%, #1e1b4b 100%)",
        accent_color="#818cf8",
        badge_text="Ecosistema de Agentes",
        code_snippet="BL_Loops Lab 22 · HeyGen HyperFrames",
    ),
]


class OllamaVideoDirector:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "qwen3.5:9b"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        # Procedencia de las últimas escenas: "ollama" o "fallback". El orquestador la publica
        # como evento y métrica para que el respaldo nunca sea silencioso.
        self.last_source = "none"
        self.last_fallback_reason: str | None = None

    async def generate_scenes(self, brief: VideoBrief) -> list[SceneSpec]:
        """Genera el desglose de escenas cinematográficas usando el modelo local Ollama."""
        prompt = f"""Actúa como Director Audiovisual y Desarrollador Experto en HyperFrames.
El usuario necesita un video didáctico de {brief.target_duration} segundos sobre el siguiente tema:
"{brief.topic}"

El video debe estructurarse en 5 escenas exactas de {brief.target_duration / 5.0} segundos cada una.
Cada escena debe explicar un aspecto clave:
1. Qué es HyperFrames (Write HTML. Render Video. Built for Agents).
2. La arquitectura (HTML declarativo, data-start, data-duration, GSAP timelines seekable).
3. Cómo se usa (init, preview en vivo, render a MP4 con Chrome Headless y FFmpeg).
4. Lo que puede hacer (explainers, motion graphics, normalización LUFS, transiciones, WebM).
5. Conclusión orientada a agentes de código.

RESPONDE ÚNICAMENTE CON UN ARREGLO JSON VÁLIDO. NO agregues texto antes ni después.
Formato de cada elemento:
{{
  "id": "scene-1",
  "title": "Título corto",
  "start_time": 0.0,
  "duration": {brief.target_duration / 5.0},
  "headline": "Titular impactante en pantalla",
  "body": "Explicación breve y didáctica",
  "bg_gradient": "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)",
  "accent_color": "#6366f1",
  "badge_text": "Categoría",
  "code_snippet": "Comando o código de ejemplo"
}}
"""
        self.last_source = "fallback"
        self.last_fallback_reason = "la respuesta no contenía escenas válidas"
        try:
            async with httpx.AsyncClient(timeout=120.0, trust_env=False) as client:
                res = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": brief.model or self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.3},
                    },
                )
                if res.status_code != 200:
                    self.last_fallback_reason = f"Ollama respondió HTTP {res.status_code}"
                else:
                    raw_text = res.json().get("response", "").strip()
                    # Clean markdown codeblocks if present
                    if "```json" in raw_text:
                        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in raw_text:
                        raw_text = raw_text.split("```")[1].split("```")[0].strip()

                    parsed = json.loads(raw_text)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        scenes = []
                        current_start = 0.0
                        duration_per_scene = brief.target_duration / len(parsed)
                        for idx, item in enumerate(parsed):
                            scenes.append(
                                SceneSpec(
                                    id=item.get("id", f"scene-{idx+1}"),
                                    title=item.get("title", f"Escena {idx+1}"),
                                    # La línea de tiempo la fija el estudio: escenas contiguas
                                    # que suman exactamente la duración pedida.
                                    start_time=round(current_start, 2),
                                    duration=round(duration_per_scene, 2),
                                    headline=item.get("headline", "HyperFrames"),
                                    body=item.get("body", "Framework de video HTML."),
                                    bg_gradient=item.get("bg_gradient", "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)"),
                                    accent_color=item.get("accent_color", "#6366f1"),
                                    badge_text=item.get("badge_text", "HyperFrames"),
                                    code_snippet=item.get("code_snippet", "npx hyperframes render"),
                                )
                            )
                            current_start += duration_per_scene
                        self.last_source = "ollama"
                        self.last_fallback_reason = None
                        return scenes
        except Exception as exc:  # noqa: BLE001 - cualquier fallo del modelo activa el respaldo visible
            self.last_fallback_reason = f"{type(exc).__name__} al consultar Ollama"
            logger.warning("Ollama no entregó escenas (%s); se usan escenas calibradas.", exc)

        # Fallback determinista respetando la duración solicitada
        duration_per_scene = brief.target_duration / len(DEFAULT_SCENES)
        calibrated_scenes = []
        for i, s in enumerate(DEFAULT_SCENES):
            calibrated_scenes.append(
                SceneSpec(
                    id=s.id,
                    title=s.title,
                    start_time=round(i * duration_per_scene, 2),
                    duration=round(duration_per_scene, 2),
                    headline=s.headline,
                    body=s.body,
                    bg_gradient=s.bg_gradient,
                    accent_color=s.accent_color,
                    badge_text=s.badge_text,
                    code_snippet=s.code_snippet,
                )
            )
        return calibrated_scenes
