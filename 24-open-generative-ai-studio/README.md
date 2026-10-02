# Laboratorio 24: Open Generative AI Studio (IA Local)

Laboratorio didáctico para evaluar la arquitectura modular de **Open Generative AI** (`Anil-matcha/Open-Generative-AI`) impulsada por **IA Local (Ollama)**.

Proporciona un workbench integral que incluye:
1. **Prompt Studio**: Expansión estructurada de ideas simples a prompts de alta densidad cinematográfica (iluminación volumétrica, lentes anamórficos, tipo de plano, movimiento de cámara).
2. **Storyboard Studio**: Desglose secuencial de guiones en planos cinematográficos coherentes.
3. **Animatic Engine**: Renderizado de animatics en video MP4 a 1080p con efectos Ken Burns y tipografía mediante FFmpeg.

## Inicio Rápido

```powershell
# 1. Sincronizar dependencias
cd 24-open-generative-ai-studio
uv sync

# 2. Ejecutar la demostración
uv run open-genai-demo

# 3. Iniciar el servidor API y panel visual
uv run python -m open_genai_studio.main
```

Consulta la guía completa en [docs/humano/README.md](docs/humano/README.md).
