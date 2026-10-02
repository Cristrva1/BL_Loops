# Laboratorio 23: Remotion Superpowers Studio (IA Local)

Laboratorio didáctico para evaluar **Remotion** (`remotion-dev/remotion`) y el patrón de producción de **Remotion Superpowers** (`DojoCodingLabs/remotion-superpowers`) integrados con IA Local (**Ollama**).

El laboratorio utiliza un modelo local (`qwen3.5:9b`) para planificar escenas audiovisuales, calcular los intervalos de fotogramas, coreografiar transiciones y renderizar a MP4 mediante componentes React y `@remotion/cli`.

## Inicio Rápido

```powershell
# 1. Instalar dependencias Python
cd 23-remotion-superpowers-studio
uv sync

# 2. Instalar dependencias Node / Remotion
npm install

# 3. Ejecutar la demostración
uv run remotion-studio-demo

# 4. Iniciar el servidor API y panel visual
uv run python -m remotion_studio.main
```

Consulta la guía completa en [docs/humano/README.md](docs/humano/README.md).
