# Instrucciones de trabajo de 23-remotion-superpowers-studio

Estas reglas se aplican a todo el laboratorio. Dentro de BL_Loops se suman al `AGENTS.md` de la raíz;
al copiar la carpeta, conservan sus límites esenciales.

## Objetivo y estado

- Enseña video programático con React: el modelo propone contenido, el estudio calcula fotogramas y
  Remotion renderiza de forma determinista.
- Implementado: director Ollama con escenas calibradas, cálculo de fotogramas, `scenes.json` con
  estilos validados, render con `npx -p @remotion/cli@4.0.523 remotion render`, medición con
  `ffprobe`, API FastAPI con SSE y panel, demo `remotion-studio-demo`, JSONL y pruebas.
- No presentar como existentes: audio, voz, subtítulos, transiciones de `@remotion/transitions` (el
  paquete está instalado, pero la composición no lo usa) ni integración con el plugin
  remotion-superpowers.

## Separación y seguridad

- `src/`, `frontend/` y `tests/` son operativos; `docs/humano/` es enseñanza y nunca una dependencia
  del runtime.
- Solo se admite Ollama por HTTP en loopback y modelos sin etiqueta cloud, también en el campo
  `model` del brief. El brief solo admite 1920×1080 a 30 fps porque `Root.tsx` fija esos valores.
- React escapa el texto de las escenas; colores y gradientes del modelo pasan por una lista blanca
  antes de escribirse en `scenes.json` (`remotion_renderer.py`).
- Remotion solo registra uso si se configura una `licenseKey`; no añadir una.
- Sin medición no hay métricas: si `ffprobe` falla o no hay pista de video, se registran ceros.
- No añadir fallback cloud ni recursos remotos al panel.

## Entorno

- Python: `pyproject.toml`, `uv.lock` y `.venv` de este laboratorio (Python 3.12).
- Node.js 22+: `package.json` y `package-lock.json` propios; instalar con `npm ci`. `node_modules/`
  está ignorado por Git.
- Configuración por **fusión de claves**: `.env` de la raíz, después el del laboratorio y por último
  las variables del proceso. Contrato en `.env.example`.
- Puerto propio: `127.0.0.1:8023`. CORS solo admite ese origen.
- `src/video_composition/scenes.json` está versionado y cada corrida lo reescribe. No confirmar en
  Git un `scenes.json` generado por una corrida con Ollama salvo que se pida.

## Forma de trabajar

1. Revisar `git status --short` y preservar todo cambio previo.
2. Leer `README.md`, `docs/humano/EXAMPLES.md` y el documento humano relacionado con la tarea.
3. Escribir o ajustar primero la prueba determinista. Las pruebas no usan red ni lanzan Remotion.
4. Si cambias la composición React, ejecuta `npm run typecheck` y renderiza un fotograma con
   `npx remotion still src/video_composition/index.ts MainVideo .local/still.png --frame=100`.
5. Actualizar documentación y pruebas en el mismo cambio.
6. No hacer commit, push, publicación ni descargas de modelos sin solicitud explícita.

## Verificación

```powershell
uv sync
npm ci
uv run pytest
uv run ruff check .
npm run typecheck
uv run remotion-studio-demo
git status --short src/video_composition/scenes.json
```

Sin Ollama, la demo usa las escenas calibradas y `scenes.json` no debe cambiar.
