"""Storyboard Studio: pide a Ollama un desglose de planos y valida el contrato antes de usarlo.

Si Ollama no responde o devuelve algo que no cumple el contrato, se usan planos calibrados y el
motivo queda en `last_fallback_reason` para que el orquestador lo publique: nunca es silencioso.
"""

import logging
from enum import Enum

import httpx

from open_genai_studio.model_output import load_json, short_reason
from open_genai_studio.schemas import (
    CameraMovement,
    ShotType,
    StoryboardProject,
    StoryboardShot,
)

logger = logging.getLogger(__name__)

TARGET_SHOTS = 4

DEFAULT_SHOTS = [
    StoryboardShot(
        shot_number=1,
        shot_type=ShotType.EXTREME_WIDE,
        camera_movement=CameraMovement.SLOW_PAN_RIGHT,
        duration_seconds=3.0,
        headline="El Vasto Glaciar de Europa",
        description="Vista panorámica de una cordillera de hielo azul bajo una atmósfera cargada de tormentas magnéticas.",
        prompt_expansion="Ultra-wide cinematic establishing shot of an alien frozen canyon, colossal towering ice spikes, electric teal fissures glowing from beneath, volumetric fog rolling across glaciers, anamorphic lens flare, 8k resolution, photorealistic, Kodak Vision3 500T 35mm film grain, slow contemplative pacing.",
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


def _options(enum_cls: type[Enum]) -> str:
    return ", ".join(f"'{member.value}'" for member in enum_cls)


def build_prompt(narrative_concept: str, duration_seconds: float) -> str:
    """Instrucción para el modelo; las opciones válidas salen de los enums del contrato."""

    return f"""Actúa como director de fotografía de un estudio de previsualización.
Necesito un storyboard de {TARGET_SHOTS} planos para esta sinopsis:
"{narrative_concept}"

Cada plano dura {duration_seconds} segundos. Para cada plano indica:
1. shot_number (1 a {TARGET_SHOTS})
2. shot_type (uno de: {_options(ShotType)})
3. camera_movement (uno de: {_options(CameraMovement)})
4. headline (título breve del plano, en español)
5. description (acción visible, en español)
6. prompt_expansion (prompt cinematográfico detallado en inglés para generadores de imagen o video)
7. lighting (estilo de iluminación)
8. accent_color (código hex como '#38bdf8')

RESPONDE ÚNICAMENTE CON UN ARREGLO JSON VÁLIDO DE {TARGET_SHOTS} OBJETOS. SIN TEXTO ADICIONAL.
"""


def _enum_member(enum_cls: type[Enum], raw: object, field: str) -> Enum:
    lookup = {str(member.value).casefold(): member for member in enum_cls}
    member = lookup.get(str(raw).strip().casefold())
    if member is None:
        raise ValueError(f"{field} desconocido: {str(raw)[:40]!r}")
    return member


def parse_shots(
    raw_text: str, duration_seconds: float, expected: int = TARGET_SHOTS
) -> list[StoryboardShot]:
    """Convierte la respuesta del modelo en planos o lanza ValueError explicando qué falló.

    Se acepta una lista JSON o un objeto con la lista en `shots`/`storyboard`. Los tipos de plano y
    movimientos se comparan sin distinguir mayúsculas. La duración la fija el estudio, no el modelo,
    para que la suma de planos coincida con la duración pedida.
    """

    parsed = load_json(raw_text)
    if isinstance(parsed, dict):
        parsed = parsed.get("shots") or parsed.get("storyboard")
    if not isinstance(parsed, list):
        raise ValueError("la respuesta no contiene una lista de planos")
    if len(parsed) != expected:
        raise ValueError(f"se esperaban {expected} planos y llegaron {len(parsed)}")

    shots: list[StoryboardShot] = []
    for number, item in enumerate(parsed, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"el plano {number} no es un objeto JSON")
        shots.append(
            StoryboardShot(
                shot_number=number,
                shot_type=_enum_member(
                    ShotType, item.get("shot_type", ShotType.WIDE.value), "shot_type"
                ),
                camera_movement=_enum_member(
                    CameraMovement,
                    item.get("camera_movement", CameraMovement.DOLLY_IN.value),
                    "camera_movement",
                ),
                duration_seconds=duration_seconds,
                headline=str(item.get("headline") or f"Plano {number}"),
                description=str(item.get("description") or ""),
                prompt_expansion=str(item.get("prompt_expansion") or ""),
                lighting=str(item.get("lighting") or "Volumetric lighting"),
                accent_color=str(item.get("accent_color") or "#6366f1"),
            )
        )
    return shots


def calibrated_shots(duration_seconds: float) -> list[StoryboardShot]:
    """Copia de los planos de respaldo con la duración del proyecto actual."""

    return [
        shot.model_copy(update={"duration_seconds": duration_seconds}) for shot in DEFAULT_SHOTS
    ]


class OpenGenAIStoryboardEngine:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "qwen3.5:9b"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        # Procedencia de los últimos planos: "ollama" o "fallback"; el orquestador la publica.
        self.last_source = "none"
        self.last_fallback_reason: str | None = None

    def _fallback(self, reason: str, duration_seconds: float) -> list[StoryboardShot]:
        self.last_source = "fallback"
        self.last_fallback_reason = reason
        logger.warning("Storyboard calibrado en uso: %s", reason)
        return calibrated_shots(duration_seconds)

    async def generate_storyboard(self, project: StoryboardProject) -> list[StoryboardShot]:
        """Genera el desglose de planos con Ollama o, si falla, devuelve el respaldo visible."""

        duration = round(project.total_duration_target / TARGET_SHOTS, 2)
        try:
            async with httpx.AsyncClient(timeout=120.0, trust_env=False) as client:
                res = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": project.model or self.model,
                        "prompt": build_prompt(project.narrative_concept, duration),
                        "stream": False,
                        "options": {"temperature": 0.4},
                    },
                )
        except httpx.HTTPError as exc:
            return self._fallback(f"{type(exc).__name__} al consultar Ollama", duration)
        if res.status_code != 200:
            return self._fallback(f"Ollama respondió HTTP {res.status_code}", duration)
        try:
            shots = parse_shots(res.json().get("response", ""), duration)
        except (ValueError, AttributeError) as exc:
            return self._fallback(f"respuesta no válida: {short_reason(exc)}", duration)
        self.last_source = "ollama"
        self.last_fallback_reason = None
        return shots
