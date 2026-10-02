"""Motor de Storyboard y expansión de planos con IA Local."""

import json
import logging
import httpx
from open_genai_studio.schemas import (
    CameraMovement,
    ShotType,
    StoryboardProject,
    StoryboardShot,
)

logger = logging.getLogger(__name__)

DEFAULT_SHOTS = [
    StoryboardShot(
        shot_number=1,
        shot_type=ShotType.EXTREME_WIDE,
        camera_movement=CameraMovement.SLOW_PAN_RIGHT,
        duration_seconds=3.0,
        headline="El Vasto Glaciar de Europa",
        description="Vista panorámica de una cordillera de hielo azul bajo una atmósfera cargada de tormentas magnéticas.",
        prompt_expansion="Ultra-wide cinematic establishing shot of an alien frozen canyon, colossal towering ice spikes, electric teal fissures glowing from beneath, volumetric fog rolling across glaciers, anamorphic lens flare, 8k resolution, photorealistic, Kodak Vision3 500T 35mm film grain, directed by Denis Villeneuve.",
        lighting="Cold twilight ambient, electric cyan bioluminescent subsurface glow",
        accent_color="#38bdf8",
    ),
    StoryboardShot(
        shot_number=2,
        shot_type=ShotType.MEDIUM,
        camera_movement=CameraMovement.TRACKING_SHOT,
        duration_seconds=3.0,
        headline="El Avance del Explorador",
        description="Un explorador espacial con traje táctico de aislamiento avanza con un escáner cuántico parpadeante.",
        prompt_expansion="Medium tracking shot following a solitary futuristic explorer in an armored pressurized environmental suit, helmet visor reflecting pulsating holographic waveforms, textured weathered fabric, heavy snow flurries drifting, cinematic shallow depth of field, f/1.8 lens bokeh.",
        lighting="High-contrast warm amber helmet floodlight cutting through dense freezing mist",
        accent_color="#f59e0b",
    ),
    StoryboardShot(
        shot_number=3,
        shot_type=ShotType.CLOSE_UP,
        camera_movement=CameraMovement.DOLLY_IN,
        duration_seconds=3.0,
        headline="La Señal Ancestral",
        description="Primer plano del dispositivo detector marcando una señal anómala emergiendo del permafrost.",
        prompt_expansion="Intense macro close-up of a handheld tactical sensor terminal, detailed rugged titanium frame, glass screen displaying complex geometric resonance rings in deep violet and gold, subtle chromatic aberration, reflections of ice crystals, ultra high definition.",
        lighting="Internal glow from neon interface diodes casting specular highlights on frosted metal",
        accent_color="#a855f7",
    ),
    StoryboardShot(
        shot_number=4,
        shot_type=ShotType.WIDE,
        camera_movement=CameraMovement.CRANE_DOWN,
        duration_seconds=3.0,
        headline="El Despertar del Monolito",
        description="El hielo se fractura revelando una estructura piramidal ancestral que emite ondas de choque silenciosas.",
        prompt_expansion="Epic wide shot of a colossal obsidian alien monolith emerging through cracked shattered glaciers, geometric micro-hieroglyphs glowing molten amber, dynamic particle dispersion of shattered ice shards, cinematic low angle, IMAX 70mm composition, hyperdetailed masterpiece.",
        lighting="Dramatic blinding dawn silhouette with golden volcanic fissures illuminating the monolith",
        accent_color="#10b981",
    ),
]


class OpenGenAIStoryboardEngine:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "qwen3.5:9b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate_storyboard(self, project: StoryboardProject) -> list[StoryboardShot]:
        """Genera el desglose cinematográfico de planos usando Ollama."""
        target_shots = 4
        dur_per_shot = project.total_duration_target / target_shots

        prompt = f"""Actúa como Director Cinematográfico de Open Generative AI.
El usuario necesita un storyboard de 4 planos para la siguiente sinopsis:
"{project.narrative_concept}"

Duración de cada plano: {dur_per_shot} segundos.
Para cada plano debes especificar:
1. shot_number (1 a 4)
2. shot_type (uno de: 'Extreme Wide Shot', 'Wide Shot', 'Medium Shot', 'Close-up', 'Drone Aerial')
3. camera_movement (uno de: 'Static', 'Slow Pan Right', 'Dolly In (Push In)', 'Tracking Shot', 'Crane Down')
4. duration_seconds ({dur_per_shot})
5. headline (título breve del plano)
6. description (acción visible)
7. prompt_expansion (prompt cinematográfico en inglés muy detallado para modelos de video/imagen)
8. lighting (estilo de iluminación)
9. accent_color (código hex como '#38bdf8')

RESPONDE ÚNICAMENTE CON UN ARREGLO JSON VÁLIDO. SIN TEXTO ADICIONAL.
"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                res = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": project.model or self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.4},
                    },
                )
                if res.status_code == 200:
                    raw_text = res.json().get("response", "").strip()
                    if "```json" in raw_text:
                        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in raw_text:
                        raw_text = raw_text.split("```")[1].split("```")[0].strip()

                    parsed = json.loads(raw_text)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        shots = []
                        for idx, item in enumerate(parsed):
                            shots.append(
                                StoryboardShot(
                                    shot_number=idx + 1,
                                    shot_type=ShotType(item.get("shot_type", "Wide Shot")),
                                    camera_movement=CameraMovement(item.get("camera_movement", "Dolly In (Push In)")),
                                    duration_seconds=dur_per_shot,
                                    headline=item.get("headline", f"Plano {idx+1}"),
                                    description=item.get("description", "Acción cinematográfica."),
                                    prompt_expansion=item.get("prompt_expansion", "Cinematic 8k shot"),
                                    lighting=item.get("lighting", "Volumetric lighting"),
                                    accent_color=item.get("accent_color", "#6366f1"),
                                )
                            )
                        return shots
        except Exception as e:
            logger.warning("Fallo en Ollama Storyboard: %s. Usando planos calibrados.", e)

        # Retornar planos calibrados
        calibrated = []
        for s in DEFAULT_SHOTS:
            calibrated.append(
                StoryboardShot(
                    shot_number=s.shot_number,
                    shot_type=s.shot_type,
                    camera_movement=s.camera_movement,
                    duration_seconds=dur_per_shot,
                    headline=s.headline,
                    description=s.description,
                    prompt_expansion=s.prompt_expansion,
                    lighting=s.lighting,
                    accent_color=s.accent_color,
                )
            )
        return calibrated
