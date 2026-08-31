# 12. Audio, Voz & Video — detalle de repos

> Abre este archivo SOLO si tienes finalistas en esta categoría.
> Cada entrada: desc, stack, instalación, choose/avoid, combina/compite.

## `faster-whisper`
role=runtime · exec=cloud · setup=heavy · mcp=False · prov=— · tags=docker,fastapi,multimedia,python,typescript,whisper

**Qué es:** faster-whisper is a reimplementation of OpenAI's Whisper model using CTranslate2, which is a fast inference engine for Transformer models.
**Stack:** python, typescript, docker, fastapi, whisper
**Repo:** https://github.com/SYSTRAN/faster-whisper.git

**Instalación** [+]: `Crear cuenta / API key en el proveedor (no self-host).`
_Servicio gestionado; no se clona._

**Elige si:** el rendimiento, la memoria o el coste de GPU importan
**Evita si:** necesitas alineación/diarización ([whisperX](#-whisperx)) o te basta el CLI oficial.
**Combina con:** `fluxer`, `whisper`, `whisperx`

## `ffmpeg`
role=directory · exec=local · setup=medium · mcp=False · prov=— · tags=typescript

**Qué es:** FFmpeg is a collection of libraries and tools to process multimedia content such as audio, video, subtitles and related metadata.
**Stack:** typescript
**Repo:** https://github.com/FFmpeg/FFmpeg.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/FFmpeg/). Si necesitas el código: git clone https://github.com/FFmpeg/FFmpeg.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres ffmpeg readme
**Evita si:** el caso no requiere generación multimedia o ya usas alternativas dedicadas
**Combina con:** `fluxer`, `whisper`, `faster-whisper`

## `fluxer`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=javascript,javascript-typescript,typescript

**Qué es:** As of this writing (15 June 2026), we are working to finalise the API and self-hosting documentation over the next few days.
**Stack:** javascript/typescript, typescript, javascript
**Repo:** https://github.com/fluxerapp/fluxer.git

**Instalación** [~]: `git clone https://github.com/fluxerapp/fluxer.git && cd fluxer && (pnpm install || npm install)`
_Proyecto Node; usa pnpm si hay pnpm-lock.yaml._

**Elige si:** quieres probar algo nuevo y seguir su evolución
**Evita si:** necesitas estabilidad de producción (API aún en finalización).
**Combina con:** `open-generative-ai`

## `lossless-cut`
role=app · exec=local · setup=medium · mcp=False · prov=— · tags=javascript,javascript-typescript,multimedia,postgres,python,typescript

**Qué es:** The swiss army knife of lossless video/audio editing.
**Stack:** javascript/typescript, python, typescript, javascript, postgres
**Repo:** https://github.com/mifi/lossless-cut.git

**Instalación** [~]: `git clone https://github.com/mifi/lossless-cut.git && cd lossless-cut && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** cortas material rápido y sin recomprimir
**Evita si:** necesitas edición compositiva, efectos o reencode ([moviepy](#-moviepy)).
**Combina con:** `moviepy`, `pipeline de reels`

## `moviepy`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=docker,postgres,python,typescript

**Qué es:** MoviePy recently upgraded to v2.0, introducing major breaking changes. You can consult the last v1 docs here but beware that v1 is no longer maintained. For more info on how to update your code from v1 to v2, see this guide.
**Stack:** python, typescript, docker, postgres
**Repo:** https://github.com/Zulko/moviepy.git

**Instalación** [~]: `pip install moviepy   (o: uv add moviepy)`
_Nombre PyPI puede diferir de 'moviepy'; verifica en pypi.org._

**Elige si:** ensamblas video por código en Python
**Evita si:** prefieres React/programático web ([remotion](#-remotion)) o una UI ([OpenCut](#-opencut)).
**Combina con:** `whisperx`, `tts`, `pipeline de reels`

## `omnivoice-studio`
role=app · exec=hybrid · setup=heavy · mcp=False · prov=— · tags=docker,fastapi,javascript,multimedia,python,react,typescript,whisper

**Qué es:** OmniVoice Studio concentra clonación y síntesis de voz en un studio local. Está en beta; espera roturas entre versiones.
**Stack:** python, typescript, javascript, react, docker, fastapi, whisper
**Repo:** https://github.com/debpalash/OmniVoice-Studio.git

**Instalación** [~]: `git clone https://github.com/debpalash/OmniVoice-Studio.git && cd OmniVoice-Studio && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres suite de voz completa local (dictado + clonación + dubbing)
**Evita si:** solo necesitas TTS simple por CLI/librería ([TTS](#-tts)) o estabilidad de producción.
**Combina con:** `whisperx`

## `remotion`
role=library · exec=hybrid · setup=medium · mcp=False · prov=— · tags=javascript,javascript-typescript,multimedia,react,typescript

**Qué es:** Remotion renderiza video desde componentes React. Úsalo para piezas generadas por código (intros, datos, motion graphics), no como NLE clásico.
**Stack:** javascript/typescript, typescript, javascript, react
**Repo:** https://github.com/remotion-dev/remotion.git

**Instalación** [~]: `npm install remotion   (o: pnpm add remotion)`
_Nombre npm puede diferir de 'remotion'; verifica en npmjs.com._

**Elige si:** generas video a escala con React y quieres variantes parametrizadas
**Evita si:** trabajas en Python ([moviepy](#-moviepy)) o buscas un editor visual.
**Combina con:** `open-generative-ai`, `pipeline de reels`

## `remotion-superpowers`
role=platform · exec=cloud · setup=heavy · mcp=False · prov=— · tags=javascript,multimedia,python,react,typescript,whisper

**Qué es:** A free, open-source Claude Code plugin that turns Remotion into a full video production studio — by Dojo Coding.
**Stack:** python, typescript, javascript, react, whisper
**Repo:** https://github.com/DojoCodingLabs/remotion-superpowers.git

**Instalación** [+]: `Crear cuenta / API key en el proveedor (no self-host).`
_Servicio gestionado; no se clona._

**Elige si:** quieres 🎬 remotion superpowers v2.1
**Evita si:** el caso no requiere generación multimedia o ya usas alternativas dedicadas
**Combina con:** `fluxer`, `whisper`, `faster-whisper`

## `supertonic`
role=library · exec=hybrid · setup=heavy · mcp=False · prov=— · tags=javascript,multimedia,python,typescript

**Qué es:** Supertonic is a lightning-fast, on-device multilingual text-to-speech system designed for local inference with minimal overhead. Powered by ONNX Runtime, it runs entirely on your device—no cloud, no API calls, no privacy concerns.
**Stack:** python, typescript, javascript
**Repo:** https://github.com/supertone-inc/supertonic.git

**Instalación** [~]: `pip install supertonic   (o: uv add supertonic)`
_Nombre PyPI puede diferir de 'supertonic'; verifica en pypi.org._

**Elige si:** quieres voz local en tiempo real y sin nube
**Evita si:** priorizas clonación de máxima fidelidad ([VoxCPM](#-voxcpm)) o flexibilidad multi-modelo ([TTS](#-tts)).
**Combina con:** `whisperx`, `moviepy`

## `vibevoice`
role=directory · exec=hybrid · setup=medium · mcp=False · prov=— · tags=multimedia,postgres,python,typescript

**Qué es:** 🎙️ VibeVoice: Open-Source Frontier Voice AI.
**Stack:** python, typescript, postgres
**Repo:** https://github.com/microsoft/VibeVoice.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/VibeVoice/). Si necesitas el código: git clone https://github.com/microsoft/VibeVoice.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres 🎙️ vibevoice: open-source frontier voice ai
**Evita si:** el caso no requiere generación multimedia o ya usas alternativas dedicadas
**Combina con:** `fluxer`, `whisper`, `faster-whisper`

## `video-use`
role=skill · exec=hybrid · setup=medium · mcp=False · prov=— · tags=multimedia,python,typescript

**Qué es:** Introducing video-use — edit videos with Claude Code. 100% open source.
**Stack:** python, typescript
**Repo:** https://github.com/browser-use/video-use.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/video-use/). Si necesitas el código: git clone https://github.com/browser-use/video-use.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** —
**Evita si:** el caso no requiere generación multimedia o ya usas alternativas dedicadas
**Combina con:** `fluxer`, `whisper`, `faster-whisper`

## `videofy-minimal`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=docker,fastapi,javascript,multimedia,python,react,typescript

**Qué es:** Videofy Minimal is a local tool for turning news articles into short videos for digital signage screens.
**Stack:** python, typescript, javascript, react, docker, fastapi
**Repo:** https://github.com/schibsted/videofy_minimal.git

**Instalación** [~]: `git clone https://github.com/schibsted/videofy_minimal.git && cd videofy_minimal && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres reels simples ya, sin montar un pipeline entero
**Evita si:** necesitas variantes programáticas a escala ([remotion](#-remotion)) o control fino por código ([moviepy](#-moviepy)).
**Combina con:** `whisper`, `supertonic`

## `voxcpm`
role=library · exec=hybrid · setup=heavy · mcp=False · prov=— · tags=comfy,docker,fastapi,javascript,postgres,python,typescript

**Qué es:** 👋 Join our community for discussion and support!.
**Stack:** python, typescript, javascript, docker, postgres, fastapi, comfy
**Repo:** https://github.com/OpenBMB/VoxCPM.git

**Instalación** [~]: `pip install voxcpm   (o: uv add voxcpm)`
_Nombre PyPI puede diferir de 'VoxCPM'; verifica en pypi.org._

**Elige si:** quieres voz muy natural o clonada y tienes GPU
**Evita si:** priorizas latencia mínima ([supertonic](#-supertonic)) o no tienes GPU.
**Combina con:** `tts`

## `wan2gp`
role=platform · exec=local · setup=heavy · mcp=False · prov=— · tags=comfy,docker,multimedia,postgres,python,react,typescript,vision

**Qué es:** WanGP is a one-stop super app for the best open source generative models across video, image, audio, and text-to-speech.
**Stack:** python, typescript, react, docker, postgres, comfy
**Repo:** https://github.com/deepbeepmeep/Wan2GP.git

**Instalación** [~]: `git clone https://github.com/deepbeepmeep/Wan2GP.git && cd Wan2GP && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres wangp by deepbeepmeep : the best open source generative models accessible to the gpu poor
**Evita si:** el caso no requiere generación multimedia o ya usas alternativas dedicadas
**Combina con:** `fluxer`, `whisper`, `faster-whisper`

## `whisper`
role=library · exec=cloud · setup=heavy · mcp=False · prov=— · tags=multimedia,postgres,python,typescript,whisper

**Qué es:** Whisper is a general-purpose speech recognition model. It is trained on a large dataset of diverse audio and is also a multitasking model that can perform multilingual speech recognition, speech translation, and language identification.
**Stack:** python, typescript, postgres, whisper
**Repo:** https://github.com/openai/whisper.git

**Instalación** [~]: `pip install whisper   (o: uv add whisper)`
_Nombre PyPI puede diferir de 'whisper'; verifica en pypi.org._

**Elige si:** quieres la referencia robusta y no te obsesiona la latencia
**Evita si:** necesitas más velocidad ([faster-whisper](#-faster-whisper)) o timings por palabra ([whisperX](#-whisperx)).
**Combina con:** `whisperx`, `pipeline de reels`

## `whisperx`
role=library · exec=hybrid · setup=heavy · mcp=False · prov=— · tags=multimedia,python,typescript,whisper

**Qué es:** If you’re looking for a transcription API for meetings, consider checking out Recall.ai's Meeting Transcription API, an API that works with Zoom, Google Meet, Microsoft Teams, and more. Recall.ai diarizes by pulling the speaker data and separate audio streams from the meeting platforms, which means 100% accurate speaker diarization with actual speaker names.
**Stack:** python, typescript, whisper
**Repo:** https://github.com/m-bain/whisperX.git

**Instalación** [~]: `pip install whisperx   (o: uv add whisperx)`
_Nombre PyPI puede diferir de 'whisperX'; verifica en pypi.org._

**Elige si:** necesitas subtítulos precisos o diarización
**Evita si:** te basta texto plano ([whisper](#-whisper)) o no quieres gestionar tokens de HF.
**Combina con:** `whisper`, `moviepy`, `pipeline de reels`
