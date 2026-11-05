"""Director de IA Local para Remotion Superpowers."""

import json
import logging

import httpx

from remotion_studio.schemas import RemotionBrief, RemotionScene

logger = logging.getLogger(__name__)

DEFAULT_REMOTION_SCENES = [
    RemotionScene(
        id="scene-1-react-video",
        title="Remotion: Video en React",
        start_frame=0,
        duration_in_frames=90,
        headline="Remotion: Video Programático en React",
        subheadline="Aprovecha componentes, hooks de React, estilos CSS y el ecosistema web para crear video real.",
        bg_gradient="linear-gradient(135deg, #090d16 0%, #1e1b4b 100%)",
        accent_color="#6366f1",
        badge="React + Video",
        code="<Composition id='MainVideo' component={Main} />",
    ),
    RemotionScene(
        id="scene-2-timing",
        title="Control por Fotogramas",
        start_frame=90,
        duration_in_frames=90,
        headline="Sincronía Milimétrica por Fotogramas",
        subheadline="Usa useCurrentFrame(), interpolate() y spring() para animaciones fluidas sin caídas de cuadros.",
        bg_gradient="linear-gradient(135deg, #090d16 0%, #064e3b 100%)",
        accent_color="#10b981",
        badge="Frame Accuracy",
        code="const frame = useCurrentFrame();",
    ),
    RemotionScene(
        id="scene-3-superpowers",
        title="Patrón Superpowers",
        start_frame=180,
        duration_in_frames=90,
        headline="Remotion Superpowers: IA Agéntica",
        subheadline="Metodología donde un agente diseña guión, secuencias, ritmo auditivo y transiciones.",
        bg_gradient="linear-gradient(135deg, #090d16 0%, #701a75 100%)",
        accent_color="#d946ef",
        badge="Superpowers Pattern",
        code="npx remotion render src/index.ts MainVideo",
    ),
    RemotionScene(
        id="scene-4-local-render",
        title="Renderizado Local",
        start_frame=270,
        duration_in_frames=90,
        headline="Render Headless 100% Local",
        subheadline="Compilación a MP4 de alta velocidad con Chrome Headless y FFmpeg en tu propia GPU.",
        bg_gradient="linear-gradient(135deg, #090d16 0%, #7c2d12 100%)",
        accent_color="#f97316",
        badge="Local Production",
        code="BL_Loops Lab 23 · Remotion Superpowers",
    ),
]


class RemotionOllamaDirector:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "qwen3.5:9b"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        # Procedencia de las últimas escenas: "ollama" o "fallback"; el orquestador la publica.
        self.last_source = "none"
        self.last_fallback_reason: str | None = None

    async def generate_scenes(self, brief: RemotionBrief) -> list[RemotionScene]:
        """Genera escenas de video calculando los fotogramas exactos con Ollama."""
        fps = brief.fps
        total_frames = int(round(brief.target_duration * fps))
        scenes_count = 4
        frames_per_scene = total_frames // scenes_count

        prompt = f"""Actúa como Director Audiovisual y Desarrollador Especialista en Remotion y Remotion Superpowers.
El usuario necesita un video didáctico de {brief.target_duration} segundos a {fps} FPS (total: {total_frames} fotogramas) sobre:
"{brief.topic}"

Estructura el video en 4 escenas exactas de {frames_per_scene} fotogramas cada una.
1. Remotion: concepto de crear video con código React y componentes.
2. Control por fotogramas: useCurrentFrame, spring(), interpolate().
3. Patrón Remotion Superpowers: producción agéntica, audio-first, transiciones.
4. Renderizado local headless a MP4 con Chrome y FFmpeg.

RESPONDE ÚNICAMENTE CON UN ARREGLO JSON VÁLIDO. NO agregues texto antes ni después.
Formato de cada elemento:
{{
  "id": "scene-1",
  "title": "Título corto",
  "start_frame": 0,
  "duration_in_frames": {frames_per_scene},
  "headline": "Titular impactante",
  "subheadline": "Explicación breve",
  "bg_gradient": "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)",
  "accent_color": "#6366f1",
  "badge": "Categoría",
  "code": "Código React o comando"
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
                    if "```json" in raw_text:
                        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in raw_text:
                        raw_text = raw_text.split("```")[1].split("```")[0].strip()

                    parsed = json.loads(raw_text)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        scenes = []
                        current_frame = 0
                        calc_frames = total_frames // len(parsed)
                        for idx, item in enumerate(parsed):
                            scenes.append(
                                RemotionScene(
                                    id=item.get("id", f"scene-{idx+1}"),
                                    title=item.get("title", f"Escena {idx+1}"),
                                    start_frame=current_frame,
                                    duration_in_frames=calc_frames,
                                    headline=item.get("headline", "Remotion Video"),
                                    subheadline=item.get("subheadline", "Video programático en React."),
                                    bg_gradient=item.get("bg_gradient", "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)"),
                                    accent_color=item.get("accent_color", "#6366f1"),
                                    badge=item.get("badge", "Remotion"),
                                    code=item.get("code", "useCurrentFrame()"),
                                )
                            )
                            current_frame += calc_frames
                        self.last_source = "ollama"
                        self.last_fallback_reason = None
                        return scenes
        except Exception as exc:  # noqa: BLE001 - cualquier fallo del modelo activa el respaldo visible
            self.last_fallback_reason = f"{type(exc).__name__} al consultar Ollama"
            logger.warning("Ollama no entregó escenas (%s); se usan escenas calibradas.", exc)

        # Fallback calibrado
        calibrated = []
        cur_frame = 0
        for s in DEFAULT_REMOTION_SCENES:
            calibrated.append(
                RemotionScene(
                    id=s.id,
                    title=s.title,
                    start_frame=cur_frame,
                    duration_in_frames=frames_per_scene,
                    headline=s.headline,
                    subheadline=s.subheadline,
                    bg_gradient=s.bg_gradient,
                    accent_color=s.accent_color,
                    badge=s.badge,
                    code=s.code,
                )
            )
            cur_frame += frames_per_scene
        return calibrated
