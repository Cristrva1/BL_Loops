"""Prompt Studio: convierte una idea breve en un prompt cinematográfico estructurado.

El resultado siempre tiene las mismas cuatro claves. Si Ollama falla o responde fuera de contrato,
se devuelve una plantilla calibrada y `last_source` vale "fallback" con su motivo.
"""

import logging

import httpx

from open_genai_studio.model_output import load_json, short_reason
from open_genai_studio.schemas import PromptExpansionRequest

logger = logging.getLogger(__name__)

RESULT_KEYS = ("positive_prompt", "negative_prompt", "camera_settings", "mood_palette")


def build_prompt(request: PromptExpansionRequest) -> str:
    return f"""Actúa como ingeniero de prompts cinematográficos.
Expande la siguiente idea inicial:
"{request.raw_idea}"
Con estilo: "{request.style}".

Debes generar un objeto JSON con estas claves:
1. "positive_prompt": prompt en inglés con iluminación (volumetric, rim light), lente
   (anamorphic, 35mm), atmósfera, texturas y dirección cinematográfica.
2. "negative_prompt": términos a evitar (baja resolución, distorsión, texto deformado, borroso).
3. "camera_settings": ajustes técnicos recomendados (por ejemplo: 35mm lens, f/2.0, 1/50).
4. "mood_palette": lista de colores dominantes (por ejemplo: ["#0ea5e9", "#f59e0b"]).

RESPONDE ÚNICAMENTE EN FORMATO JSON. SIN TEXTO ADICIONAL.
"""


def _as_text(value: object) -> str:
    if isinstance(value, dict):
        return ", ".join(f"{key}: {item}" for key, item in value.items())
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value or "").strip()


def parse_expansion(raw_text: str) -> dict:
    """Normaliza la respuesta del modelo a las cuatro claves del contrato o lanza ValueError."""

    data = load_json(raw_text)
    if not isinstance(data, dict):
        raise ValueError("la respuesta no es un objeto JSON")
    positive = _as_text(data.get("positive_prompt"))
    if not positive:
        raise ValueError("falta positive_prompt")
    palette = data.get("mood_palette") or []
    if isinstance(palette, str):
        palette = [color.strip() for color in palette.split(",")]
    if not isinstance(palette, list):
        raise ValueError("mood_palette debe ser una lista")
    return {
        "positive_prompt": positive,
        "negative_prompt": _as_text(data.get("negative_prompt")),
        "camera_settings": _as_text(data.get("camera_settings")),
        "mood_palette": [str(color).strip() for color in palette if str(color).strip()][:8],
    }


def calibrated_expansion(request: PromptExpansionRequest) -> dict:
    """Plantilla determinista: misma entrada, misma salida, sin intervención del modelo."""

    return {
        "positive_prompt": (
            f"Cinematic {request.style} shot of {request.raw_idea}, anamorphic lens flare, "
            "volumetric fog, Kodak Vision3 500T 35mm film grain, high detail."
        ),
        "negative_prompt": (
            "blurry, oversaturated, low quality, artifacts, distorted geometry, extra limbs, "
            "watermark."
        ),
        "camera_settings": "Large-format digital camera, anamorphic 50mm lens, T2.0",
        "mood_palette": ["#0ea5e9", "#f59e0b", "#0f172a"],
    }


class PromptStudioExpander:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "qwen3.5:9b"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.last_source = "none"
        self.last_fallback_reason: str | None = None

    def _fallback(self, reason: str, request: PromptExpansionRequest) -> dict:
        self.last_source = "fallback"
        self.last_fallback_reason = reason
        logger.warning("Plantilla de prompt calibrada en uso: %s", reason)
        return calibrated_expansion(request)

    async def expand_prompt(self, request: PromptExpansionRequest) -> dict:
        """Expande una idea simple en prompt positivo, negativo, cámara y paleta."""

        try:
            async with httpx.AsyncClient(timeout=120.0, trust_env=False) as client:
                res = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": request.model or self.model,
                        "prompt": build_prompt(request),
                        "stream": False,
                        "options": {"temperature": 0.5},
                    },
                )
        except httpx.HTTPError as exc:
            return self._fallback(f"{type(exc).__name__} al consultar Ollama", request)
        if res.status_code != 200:
            return self._fallback(f"Ollama respondió HTTP {res.status_code}", request)
        try:
            expanded = parse_expansion(res.json().get("response", ""))
        except (ValueError, AttributeError) as exc:
            return self._fallback(f"respuesta no válida: {short_reason(exc)}", request)
        self.last_source = "ollama"
        self.last_fallback_reason = None
        return expanded
