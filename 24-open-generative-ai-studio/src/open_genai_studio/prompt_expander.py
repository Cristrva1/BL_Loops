"""Módulo de Expansión Cinematográfica de Prompts (Prompt Studio)."""

import json
import logging
import httpx
from open_genai_studio.schemas import PromptExpansionRequest

logger = logging.getLogger(__name__)


class PromptStudioExpander:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "qwen3.5:9b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def expand_prompt(self, request: PromptExpansionRequest) -> dict:
        """Expande una idea simple en un set de prompt cinematográfico positivo y negativo."""
        prompt = f"""Actúa como Ingeniero de Prompts Cinematográficos de Open Generative AI.
Expande la siguiente idea inicial:
"{request.raw_idea}"
Con estilo: "{request.style}".

Debes generar:
1. "positive_prompt": Prompt en inglés rico en detalles de iluminación (volumetric, rim light), lente (anamorphic, 35mm), atmósfera, texturas, calidad 8k y dirección cinematográfica.
2. "negative_prompt": Términos negativos para evitar baja resolución, distorsión, texto deformado, borroso.
3. "camera_settings": Detalles técnicos recomendados (ej: 35mm lens, f/2.0, shutter 1/50).
4. "mood_palette": Lista de colores dominantes (ej: ['deep cyan', 'amber', 'obsidian']).

RESPONDE ÚNICAMENTE EN FORMATO JSON. SIN TEXTO ADICIONAL.
"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                res = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": request.model or self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.5},
                    },
                )
                if res.status_code == 200:
                    raw_text = res.json().get("response", "").strip()
                    if "```json" in raw_text:
                        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in raw_text:
                        raw_text = raw_text.split("```")[1].split("```")[0].strip()
                    return json.loads(raw_text)
        except Exception as e:
            logger.warning("Fallo en PromptStudioExpander: %s", e)

        return {
            "positive_prompt": f"Cinematic {request.style} shot of {request.raw_idea}, anamorphic lens flare, volumetric fog, Kodak Vision3 500T 35mm film grain, masterpiece, 8k.",
            "negative_prompt": "blurry, oversaturated, low quality, artifacts, distorted geometry, extra limbs, watermark.",
            "camera_settings": "Arri Alexa LF, Panavision Ultra Vista Anamorphic 50mm, T2.0",
            "mood_palette": ["#0ea5e9", "#f59e0b", "#0f172a"]
        }
