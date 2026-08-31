Tu hardware (RTX 5060 Ti 16GB VRAM, Ryzen 7 5800X3D y 32GB RAM) permite alojar modelos de hasta 27B en cuantizaciones Q3/Q4 o modelos de 12B–14B en Q8, dejando entre 14.5 GB y 15 GB de VRAM real utilizable tras el consumo base de Windows 11\.

| Modelo | Cuantización / Formato | Uso VRAM | Contexto útil | Razonamiento | Coding | Tareas / Agentes | URL para descarga (Hugging Face) |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Qwen3 14B** | Q4\_K\_M (GGUF) | \~9.5 – 10.7 GB | 32K – 128K | Alto (MMLU 81.1) | Alto | Muy Alto (Todoterreno diario) | [Qwen/Qwen3-14B-GGUF](https://huggingface.co/Qwen/Qwen3-14B-GGUF) |
| **Qwen3.8 27B** | AD-IQ3\_S / Q3\_K\_M | \~13.8 GB  | 8K – 16K  | Muy Alto (Modo Thinking)  | Extremo (SWE-bench Pro 61.7) | Muy Alto (Multimodal base)  | [Qwen/Qwen3.8-27B-GGUF](https://www.google.com/search?q=https://huggingface.co/Qwen/Qwen3.8-27B-GGUF) |
| **Gemma 4 12B** | Q4\_K\_M / Q8\_0 | \~7.5 GB (Q4) / \~13 GB (Q8) | 16K – 32K | Alto | Medio-Alto | Excelente (Soporte y redacción) | [google/gemma-4-12b-it-GGUF](https://www.google.com/search?q=https://huggingface.co/google/gemma-4-12b-it-GGUF) |
| **Devstral Small 2 24B** | Q4\_K\_M (GGUF) | \~15.0 GB | 256K nativo | Alto | Muy Alto (SWE-bench 68.0%) | Especialista en loops de código | [mistralai/Devstral-Small-2-24B-GGUF](https://www.google.com/search?q=https://huggingface.co/mistralai/Devstral-Small-2-24B-GGUF) |
| **DeepSeek-R1-Distill 14B** | Q8\_0 (GGUF) | \~9.0 GB | 32K – 64K | Extremo (Lógica pura y STEM) | Alto (Debugging paso a paso) | Medio (Enfocado en CoT) | [deepseek-ai/DeepSeek-R1-Distill-Qwen-14B-GGUF](https://www.google.com/search?q=https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B-GGUF) |
| **Phi-4 Reasoning 14B** | Q4\_K\_M (GGUF) | \~9.2 GB | 16K – 32K | Muy Alto (Supera a modelos 70B) | Alto | Medio-Alto | [microsoft/phi-4-gguf](https://huggingface.co/microsoft/phi-4-gguf) |
| **GPT-OSS 20B** | MXFP4 / Q4\_K\_M | \~13.7 GB | 60K | Excelente (Test lógicos) | Alto | Muy Alto (42 tok/s en inferencia) | [tensorops/gpt-oss-20b-GGUF](https://www.google.com/search?q=https://huggingface.co/tensorops/gpt-oss-20b-GGUF) |
| **Qwen3.5 4B** | Q8\_0 / Q4\_K\_M | \~3.4 GB | 32K | Medio-Alto | Medio | Extremo (97.5% en Tool Calling) | [Qwen/Qwen3.5-4B-GGUF](https://www.google.com/search?q=https://huggingface.co/Qwen/Qwen3.5-4B-GGUF) |
| **Mistral-Nemo-12B Abliterated** | Q8\_0 / Q4\_K\_M | \~7.5 – 13.0 GB | 128K | Alto | Medio | Sin censura / Rol / Creativo | [failspy/Mistral-Nemo-12B-Instruct-Abliterated-GGUF](https://www.google.com/search?q=https://huggingface.co/failspy/Mistral-Nemo-12B-Instruct-Abliterated-GGUF) |
| **BGE-M3 (Embeddings)** | FP16 / ONNX | \~1.5 GB (o CPU) | 8,192 | N/A | N/A | Estándar de oro RAG híbrido | [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) |

**Runtimes y Motores de Ejecución Alternativos a Ollama**

* **llama.cpp server (**llama-server.exe**)**: Ofrece el menor consumo de memoria base y control de bajo nivel para API compatible con OpenAI. Permite procesar múltiples solicitudes concurrentes del mismo modelo sin duplicar el peso en VRAM usando slots paralelos (\-np).  
*   
* **vLLM / Aphrodite Engine (vía WSL2)**: Diseñados para producción y alta concurrencia mediante *PagedAttention*. Maximizan el throughput cuando varios usuarios consultan la API al mismo tiempo.  
*   
* **TabbyAPI (ExLlamaV2)**: Motor optimizado para GPUs Nvidia con formato .exl2. Supera a GGUF en velocidad de inferencia pura cuando se ajusta la cuantización al tamaño exacto de la VRAM.  
*   
* **LM Studio CLI / Headless Server**: Permite servir endpoints locales exponiendo modelos cuantizados sin necesidad de mantener la interfaz gráfica abierta en Windows.  
* 

**Arquitectura y Ejecución en Paralelo (Asistente y Atención al Cliente)**

Para correr flujos en loop y múltiples modelos a la vez con 16GB de VRAM, existen dos modalidades:

* **1\. Ejecución concurrente del mismo modelo (Multi-Slot)**: Cargas un único modelo en memoria (por ejemplo, Gemma 4 12B Q4\_K\_M a \~7.5GB) y habilitas procesamiento simultáneo de peticiones compartiendo los mismos pesos en VRAM.  
* 

  * *llama.cpp*: Ejecuta llama-server.exe \-m gemma-4-12b-q4.gguf \--port 8000 \-c 16384 \-np 4 \--ngl 99. El parámetro \-np 4 permite responder 4 chats en paralelo dividiendo el contexto.  
  *   
  * *Ollama*: Configura las variables de entorno de Windows OLLAMA\_NUM\_PARALLEL=4 y OLLAMA\_MAX\_QUEUE=512.  
  *   
* **2\. Ejecución multi-modelo simultánea (Pipeline Router \+ Agente)**:  
* 

  * **VRAM split (\~11 GB ocupados en total)**:  
  * 

    * Instancia 1 (Puerto 8001): **Qwen3.5 4B Q8** (\~3.4GB VRAM) actúa como *Router*, clasificador de intención y ejecutor de herramientas/function-calling.  
    *   
    * Instancia 2 (Puerto 8000): **Gemma 4 12B Q4** (\~7.5GB VRAM) genera la respuesta final conversacional y empática al cliente.  
    *   
    * Embeddings: **nomic-embed-text** o **BGE-M3** ejecutados sobre CPU/RAM de 32GB para dejar la VRAM libre a los modelos de lenguaje.  
    *   
  * *Despliegue*:  
  * 

  * DOS

:: Instancia 1: Router y Function Calling  
llama-server.exe \-m Qwen3.5\-4B-Q8\_0.gguf \--port 8001 \-c 8192 \--ngl 99

:: Instancia 2: Asistente Conversacional  
llama-server.exe \-m gemma-4\-12b-it-Q4\_K\_M.gguf \--port 8000 \-c 16384 \--ngl 99

*   
  *   
* **3\. Loop de automatización agéntico**:  
* Conecta tu backend (Python con librerías como FastAPI, LiteLLM o LangGraph) enviando la entrada del usuario al puerto 8001 (Router). Si la solicitud requiere base de conocimientos, se recuperan fragmentos vectoriales en CPU con BGE-M3, y el prompt enriquecido se envía al puerto 8000 (Gemma 4\) para la síntesis final.

