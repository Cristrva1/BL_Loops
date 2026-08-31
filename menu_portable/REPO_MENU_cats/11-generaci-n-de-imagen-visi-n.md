# 11. Generación de Imagen & Visión — detalle de repos

> Abre este archivo SOLO si tienes finalistas en esta categoría.
> Cada entrada: desc, stack, instalación, choose/avoid, combina/compite.

## `comfyui`
role=runtime · exec=hybrid · setup=heavy · mcp=False · prov=— · tags=comfy,docker,frontend,javascript,python,react,typescript

**Qué es:** The most powerful and modular AI engine for content creation..
**Stack:** python, typescript, javascript, react, docker, comfy
**Repo:** https://github.com/Comfy-Org/ComfyUI.git

**Instalación** [~]: `git clone https://github.com/Comfy-Org/ComfyUI.git && cd ComfyUI && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres control total y pipelines reproducibles
**Evita si:** buscas simplicidad inmediata ([Fooocus](#-fooocus)).
**Combina con:** `comfyui-ipadapter-plus`, `real-esrgan`, `pipeline de reels`

## `comfyui-ipadapter-plus`
role=library · exec=local · setup=heavy · mcp=False · prov=— · tags=comfy,frontend,javascript,postgres,python,typescript

**Qué es:** The IPAdapter are very powerful models for image-to-image conditioning. The subject or even just the style of the reference image(s) can be easily transferred to a generation. Think of it as a 1-image lora.
**Stack:** python, typescript, javascript, postgres, comfy
**Repo:** https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

**Instalación** [~]: `pip install comfyui_ipadapter_plus   (o: uv add comfyui_ipadapter_plus)`
_Nombre PyPI puede diferir de 'ComfyUI_IPAdapter_plus'; verifica en pypi.org._

**Elige si:** trabajas en ComfyUI y necesitas consistencia visual por referencia
**Evita si:** no usas ComfyUI o te basta con prompts de estilo.
**Combina con:** `litellm`, `cosmos`, `comfyui`

## `controlnet`
role=library · exec=local · setup=heavy · mcp=False · prov=— · tags=python,typescript

**Qué es:** ControlNet 1.1 is released. Those new models will be merged to this repo after we make sure that everything is good.
**Stack:** python, typescript
**Repo:** https://github.com/lllyasviel/ControlNet.git

**Instalación** [~]: `pip install controlnet   (o: uv add controlnet)`
_Nombre PyPI puede diferir de 'ControlNet'; verifica en pypi.org._

**Elige si:** necesitas control estructural fino de la composición
**Evita si:** ya trabajas en SD WebUI ([sd-webui-controlnet](#-sd-webui-controlnet)) o ComfyUI (tienen integración propia) y no necesitas el repo original.
**Combina con:** `diffusers`, `comfyui`

## `cosmos`
role=runtime · exec=local · setup=heavy · mcp=False · prov=— · tags=docker,postgres,python,typescript

**Qué es:** Colección NVIDIA Cosmos para modelos de mundo y video. Setup pesado: GPU y checkpoints. No es un editor de imagen ligero.
**Stack:** python, typescript, docker, postgres
**Repo:** https://github.com/NVIDIA/cosmos.git

**Instalación** [~]: `git clone https://github.com/NVIDIA/cosmos.git && cd cosmos && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** trabajas IA física/robótica y necesitas datos sintéticos
**Evita si:** haces tareas de texto/UI o no tienes GPU para servirlo.
**Combina con:** `diffusers`

## `deep-live-cam`
role=app · exec=hybrid · setup=medium · mcp=False · prov=— · tags=multimedia,postgres,python,typescript,vision

**Qué es:** Real-time face swap and video deepfake with a single click and only a single image.
**Stack:** python, typescript, postgres
**Repo:** https://github.com/hacksider/Deep-Live-Cam.git

**Instalación** [~]: `git clone https://github.com/hacksider/Deep-Live-Cam.git && cd Deep-Live-Cam && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** necesitas swap en vivo legítimo con consentimiento
**Evita si:** no puedes garantizar uso ético/consentimiento o no tienes GPU.
**Combina con:** `face-recognition`

## `diffusers`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=postgres,python,typescript

**Qué es:** Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at.
**Stack:** python, typescript, postgres
**Repo:** https://github.com/huggingface/diffusers.git

**Instalación** [~]: `pip install diffusers   (o: uv add diffusers)`
_Nombre PyPI puede diferir de 'diffusers'; verifica en pypi.org._

**Elige si:** programas generación y quieres control total por código
**Evita si:** quieres una UI lista ([Fooocus](#-fooocus)) o grafos nodales ([ComfyUI](#-comfyui)).
**Combina con:** `controlnet`, `cosmos`

## `face-recognition`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=docker,postgres,python,typescript

**Qué es:** Recognize and manipulate faces from Python or from the command line with the world's simplest face recognition library.
**Stack:** python, typescript, docker, postgres
**Repo:** https://github.com/ageitgey/face_recognition.git

**Instalación** [~]: `pip install face_recognition   (o: uv add face_recognition)`
_Nombre PyPI puede diferir de 'face_recognition'; verifica en pypi.org._

**Elige si:** necesitas reconocimiento facial básico y rápido de implementar
**Evita si:** buscas restauración/animación ([GFPGAN](#-gfpgan)/[LivePortrait](#-liveportrait)) o precisión de producción (mejor DeepFace/InsightFace).
**Combina con:** `deep-live-cam`

## `fooocus`
role=skill · exec=local · setup=heavy · mcp=False · prov=— · tags=comfy,docker,javascript,python,typescript

**Qué es:** Fooocus is an image generating software (based on Gradio ).
**Stack:** python, typescript, javascript, docker, comfy
**Repo:** https://github.com/lllyasviel/Fooocus.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/Fooocus/). Si necesitas el código: git clone https://github.com/lllyasviel/Fooocus.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres resultados ya, sin curva
**Evita si:** necesitas control fino del pipeline ([ComfyUI](#-comfyui)).
**Combina con:** `real-esrgan`

## `gfpgan`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=javascript,postgres,python,typescript

**Qué es:** 1. :boom: Updated online demo: . Here is the backup. 1. :boom: Updated online demo: 1. .
**Stack:** python, typescript, javascript, postgres
**Repo:** https://github.com/TencentARC/GFPGAN.git

**Instalación** [~]: `pip install gfpgan   (o: uv add gfpgan)`
_Nombre PyPI puede diferir de 'GFPGAN'; verifica en pypi.org._

**Elige si:** restauras rostros borrosos o fundidos
**Evita si:** necesitas upscaling general de la imagen ([Real-ESRGAN](#-real-esrgan)).
**Combina con:** `real-esrgan`

## `invokeai`
role=runtime · exec=local · setup=medium · mcp=False · prov=— · tags=docker,javascript,python,react,typescript

**Qué es:** Invoke - Professional Creative AI Tools for Visual Media.
**Stack:** python, typescript, javascript, react, docker
**Repo:** https://github.com/invoke-ai/InvokeAI.git

**Instalación** [~]: `git clone https://github.com/invoke-ai/InvokeAI.git && cd InvokeAI && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** trabajas creatividad profesional y quieres una app estable con canvas
**Evita si:** solo haces una prueba puntual ([Fooocus](#-fooocus)) o prefieres grafos nodales ([ComfyUI](#-comfyui)).
**Combina con:** `diffusers`, `controlnet`

## `litellm`
role=platform · exec=hybrid · setup=medium · mcp=False · prov=— · tags=docker,javascript,postgres,python,typescript

**Qué es:** LiteLLM is an open source AI Gateway that gives you a single, unified interface to call 100+ LLM providers — OpenAI, Anthropic, Gemini, Bedrock, Azure, and more — using the OpenAI format.
**Stack:** python, typescript, javascript, docker, postgres
**Repo:** https://github.com/BerriAI/litellm.git

**Instalación** [~]: `git clone https://github.com/BerriAI/litellm.git && cd litellm && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** trabajas con múltiples modelos o quieres fallback/control de costos
**Evita si:** usas un único proveedor fijo y no necesitas abstracción.
**Combina con:** `langchain`, `langfuse`, `llm-council`

## `liveportrait`
role=library · exec=local · setup=heavy · mcp=False · prov=— · tags=comfy,javascript,postgres,python,typescript

**Qué es:** `2025/06/01`: 🌍 Over the past year, LivePortrait has 🚀 become an efficient portrait-animation (humans, cats and dogs) solution adopted by major video platforms—Kuaishou, Douyin, Jianying, WeChat Channels—as well as numerous startups and creators. 🎉 `2025/01/01`: 🐶 We updated a new version of the Animals model with more data, see here. `2024/10/18`: ❗ We have upda.
**Stack:** python, typescript, javascript, postgres, comfy
**Repo:** https://github.com/KlingAIResearch/LivePortrait.git

**Instalación** [~]: `pip install liveportrait   (o: uv add liveportrait)`
_Nombre PyPI puede diferir de 'LivePortrait'; verifica en pypi.org._

**Elige si:** animas retratos a partir de una foto
**Evita si:** necesitas swap en vivo ([Deep-Live-Cam](#-deep-live-cam)) o no tienes GPU.
**Combina con:** `moviepy`

## `luxtts`
role=directory · exec=local · setup=heavy · mcp=False · prov=— · tags=comfy,javascript,multimedia,python,typescript

**Qué es:** LuxTTS is an lightweight zipvoice based text-to-speech model designed for high quality voice cloning and realistic generation at speeds exceeding 150x realtime.
**Stack:** python, typescript, javascript, comfy
**Repo:** https://github.com/ysharma3501/LuxTTS.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/LuxTTS/). Si necesitas el código: git clone https://github.com/ysharma3501/LuxTTS.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** —
**Evita si:** el caso no requiere generación multimedia o ya usas alternativas dedicadas
**Combina con:** `litellm`, `cosmos`, `comfyui`

## `nemo`
role=runtime · exec=local · setup=medium · mcp=False · prov=— · tags=docker,python,typescript

**Qué es:** Checkout our HuggingFace🤗 collection for the latest open weight checkpoints and demos!.
**Stack:** python, typescript, docker
**Repo:** https://github.com/NVIDIA-NeMo/NeMo.git

**Instalación** [~]: `git clone https://github.com/NVIDIA-NeMo/NeMo.git && cd NeMo && docker compose up -d`
_Requiere Docker; el compose puede variar — revisa docker-compose.yml._

**Elige si:** quieres **nvidia nemo speech**
**Evita si:** el caso no requiere generación multimedia o ya usas alternativas dedicadas
**Combina con:** `litellm`, `cosmos`, `comfyui`

## `sd-webui-controlnet`
role=library · exec=local · setup=medium · mcp=False · prov=— · tags=frontend,postgres,python,typescript,vision

**Qué es:** The WebUI extension for ControlNet and other injection-based SD controls.
**Stack:** python, typescript, postgres
**Repo:** https://github.com/Mikubill/sd-webui-controlnet.git

**Instalación** [~]: `pip install sd-webui-controlnet   (o: uv add sd-webui-controlnet)`
_Nombre PyPI puede diferir de 'sd-webui-controlnet'; verifica en pypi.org._

**Elige si:** ya usas SD WebUI y quieres ControlNet sin cambiar de entorno
**Evita si:** trabajas en ComfyUI (usa sus propios nodos) o por código ([diffusers](#-diffusers)).
**Combina con:** `stable-diffusion-webui`, `controlnet`

## `stable-diffusion-webui`
role=skill · exec=local · setup=medium · mcp=False · prov=— · tags=frontend,javascript,postgres,python,typescript,vision

**Qué es:** A web interface for Stable Diffusion, implemented using Gradio library.
**Stack:** python, typescript, javascript, postgres
**Repo:** https://github.com/AUTOMATIC1111/stable-diffusion-webui.git

**Instalación** [+]: `Copiar la skill a la carpeta de skills de tu agente (p.ej. .claude/skills/stable-diffusion-webui/). Si necesitas el código: git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git`
_Material de referencia/playbook; no es una dependencia runtime._

**Elige si:** quieres extensiones y comunidad amplia
**Evita si:** prefieres un flujo moderno y limpio ([InvokeAI](#-invokeai)).
**Combina con:** `sd-webui-controlnet`

## `tts`
role=library · exec=local · setup=heavy · mcp=False · prov=— · tags=docker,python,typescript

**Qué es:** 📣 ⓍTTSv2 is here with 16 languages and better performance across the board. 📣 ⓍTTS fine-tuning code is out. Check the example recipes. 📣 ⓍTTS can now stream with <200ms latency. 📣 ⓍTTS, our production TTS model that can speak 13 languages, is released Blog Post, Demo, Docs.
**Stack:** python, typescript, docker
**Repo:** https://github.com/coqui-ai/TTS.git

**Instalación** [~]: `pip install tts   (o: uv add tts)`
_Nombre PyPI puede diferir de 'TTS'; verifica en pypi.org._

**Elige si:** quieres flexibilidad y varios modelos en una librería
**Evita si:** necesitas tiempo real puro ([supertonic](#-supertonic)) o soporte comercial (Coqui está inactivo).
**Combina con:** `whisperx`, `moviepy`

## `unlimited-ocr`
role=library · exec=hybrid · setup=heavy · mcp=False · prov=— · tags=vision,ocr,docs

**Qué es:** Unlimited OCR apunta a extracción de texto y estructura en documentos largos. Setup de visión; no es un editor PDF.
**Stack:** python, typescript, docker, postgres
**Repo:** https://github.com/baidu/Unlimited-OCR.git

**Instalación** [~]: `pip install unlimited-ocr   (o: uv add unlimited-ocr)`
_Nombre PyPI puede diferir de 'Unlimited-OCR'; verifica en pypi.org._

**Elige si:** quieres unlimited ocr works
**Evita si:** el caso no requiere generación multimedia o ya usas alternativas dedicadas
**Combina con:** `litellm`, `cosmos`, `comfyui`
