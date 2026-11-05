# Glosario de BL_Loops

> Vocabulario mínimo para recorrer todos los laboratorios. Cada término tiene una definición en
> lenguaje sencillo, un ejemplo concreto y el laboratorio donde puedes **verlo funcionar**.
> Si un documento usa una palabra que no entiendes, búscala aquí antes de seguir.

Cómo leerlo:

- **Qué es:** la idea en una o dos frases, sin jerga adicional.
- **Ejemplo:** algo que puedes reconocer en pantalla o en un archivo.
- **Lo ves en:** el laboratorio donde el concepto deja de ser teoría.

## Índice rápido

| Tema | Términos |
|---|---|
| [Modelos y contexto](#1-modelos-y-contexto) | LLM, token, contexto, prompt, instrucción de sistema, temperatura, Ollama, etiqueta de modelo, inferencia local, alucinación |
| [Agentes](#2-agentes) | agente, herramienta, memoria de sesión, condición de parada, presupuesto, aprobación humana, mínimo privilegio, skill, contrato, huella |
| [Coordinar varios pasos](#3-coordinar-varios-pasos) | línea base, orquestación, handoff, gate determinista, maker/checker, fan-out/fan-in, concurrencia, speedup, loop, mejor candidato, timeout, fallback visible |
| [Recuperar conocimiento (RAG)](#4-recuperar-conocimiento-rag) | RAG, corpus, fragmento, índice, FTS5/BM25, embedding, similitud coseno, top-k, recall@k, búsqueda híbrida/RRF, grafo, triple, multi-hop, arista extraída/inferida, cita, abstención, inyección indirecta, map-reduce |
| [Evidencia y observabilidad](#5-evidencia-y-observabilidad) | fixture, caso de evaluación, traza, evento, JSONL, sanitización, SSE, snapshot, prueba determinista, doble de prueba, spike, SHA, cohorte, preflight, egress, sandbox |
| [Entorno de trabajo](#6-entorno-de-trabajo) | `uv`, `.venv`, `uv.lock`, `.env`, loopback, puerto, FastAPI, Pydantic, React Flow |
| [Video generado por código](#7-video-generado-por-código) | composición y línea de tiempo, render determinista, storyboard, plano, animatic, filtergraph, escapado, ffprobe |

---

## 1. Modelos y contexto

### LLM

**Qué es:** un *modelo de lenguaje grande*. Recibe texto y predice, token a token, el texto que
probablemente sigue. No “consulta una base de datos”: genera.
**Ejemplo:** `qwen3.5:4b` y `gemma4:e4b` son LLM locales.
**Lo ves en:** [02-single-agent](../../../02-single-agent/README.md).

### Token

**Qué es:** el trozo de texto con el que trabaja el modelo; suele ser una palabra corta o parte de
una palabra. Coste, velocidad y límite de contexto se miden en tokens.
**Ejemplo:** el campo `prompt_tokens` de una traza indica cuántos tokens leyó el modelo.
**Lo ves en:** el comando `/memoria` de [02-single-agent](../../../02-single-agent/README.md).

### Contexto

**Qué es:** todo lo que el modelo recibe en una llamada: instrucción de sistema, historial, datos
recuperados y la pregunta actual. Lo que no está en el contexto no existe para el modelo.
**Ejemplo:** el chat del 02 reenvía el historial completo en cada turno; por eso “recuerda”.
**Lo ves en:** [02-single-agent](../../../02-single-agent/README.md) y en los laboratorios RAG.

### Prompt

**Qué es:** el texto que escribimos para pedirle algo al modelo. Un buen prompt separa rol, tarea,
contexto, formato de salida y restricciones.
**Ejemplo:** `PromptSpec` convierte una idea vaga en un prompt con criterios verificables.
**Lo ves en:** [01-prompt-agent-factory](../../../01-prompt-agent-factory/README.md).

### Instrucción de sistema

**Qué es:** el primer mensaje del contexto (`role: system`). Fija reglas que deben valer durante
toda la conversación, como “cita tus fuentes” o “responde en el idioma del usuario”.
**Ejemplo:** `SYSTEM_PROMPT` del 06 obliga a citar `[S1]`, `[S2]`.
**Lo ves en:** [06-naive-rag](../../../06-naive-rag/README.md).

### Temperatura

**Qué es:** un control de aleatoriedad. Baja (0–0.3) produce respuestas más repetibles; alta
produce más variedad y más riesgo de inventar.
**Ejemplo:** el 25 usa `temperature=0.2` para extraer acuerdos en JSON estable; los estudios 22 y
23 usan 0.3 para el guion.
**Lo ves en:** [25-meeting-summarizer](../../../25-meeting-summarizer/README.md).

### Ollama

**Qué es:** el servidor local que carga los pesos del modelo y expone una API HTTP en
`http://127.0.0.1:11434`. Todos los laboratorios hablan únicamente con él.
**Ejemplo:** `ollama list` muestra los modelos instalados; `ollama ps` los que están en memoria.
**Lo ves en:** todos los laboratorios que generan texto.

### Etiqueta de modelo

**Qué es:** el nombre exacto con el que Ollama identifica un modelo: `familia:variante`.
**Ejemplo:** `qwen3.5:4b` (básico), `qwen3.5:9b` (estándar). Las etiquetas que terminan en
`:cloud` se rechazan porque no son inferencia local.
**Lo ves en:** el banner de [02-single-agent](../../../02-single-agent/README.md).

### Inferencia local

**Qué es:** generar texto con un modelo que corre en tu propia máquina. Ningún prompt viaja a un
proveedor externo y no existe un “plan B” en la nube.
**Ejemplo:** si Ollama está apagado, la corrida falla con un diagnóstico; no cambia de proveedor.
**Lo ves en:** el fallo didáctico “Ollama detenido” de los laboratorios 02 a 05.

### Alucinación

**Qué es:** una afirmación generada con seguridad pero sin respaldo en el contexto ni en la
realidad. Los contratos, las citas y los gates existen para detectarlas.
**Ejemplo:** una minuta que asigna un responsable que nadie nombró en la reunión.
**Lo ves en:** [25-meeting-summarizer](../../../25-meeting-summarizer/README.md) y en las citas de
los laboratorios RAG.

## 2. Agentes

### Agente

**Qué es:** un programa que observa una entrada, prepara contexto, pide una decisión a un modelo y
actúa dentro de límites. La diferencia con “un prompt” es el bucle de control alrededor del modelo.
**Ejemplo:** el agente de ventas del 09 decide qué buscar, busca una vez y responde.
**Lo ves en:** [02-single-agent](../../../02-single-agent/README.md) (mínimo) y
[09-agentic-rag](../../../09-agentic-rag/README.md) (con herramienta).

### Herramienta (tool) y tool calling

**Qué es:** una función que el modelo puede *pedir* usar (por ejemplo, buscar). El modelo propone la
llamada; el runtime decide si la ejecuta. *Tool calling* es ese protocolo de petición.
**Ejemplo:** `search_sales_library` del 09 se ejecuta como máximo una vez por turno.
**Lo ves en:** [09-agentic-rag](../../../09-agentic-rag/README.md).

### Memoria de sesión

**Qué es:** el historial que se conserva mientras el programa está abierto. En BL_Loops vive en
RAM: al cerrar, desaparece.
**Ejemplo:** `/olvidar` en el 02 vacía el historial y demuestra que la memoria es solo una lista.
**Lo ves en:** [02-single-agent](../../../02-single-agent/README.md).

### Condición de parada

**Qué es:** la regla explícita que dice cuándo un agente o un loop termina: éxito, falta de
información, permiso insuficiente o presupuesto agotado.
**Ejemplo:** `stop_conditions` en un `AgentSpec`; `stop_reason` en el 05.
**Lo ves en:** [01-prompt-agent-factory](../../../01-prompt-agent-factory/README.md) y
[05-agent-loops](../../../05-agent-loops/README.md).

### Presupuesto

**Qué es:** el máximo de recursos que una corrida puede gastar: iteraciones, errores, tiempo o
tokens. El primero que se agota detiene la ejecución.
**Ejemplo:** el 05 permite cinco iteraciones, dos errores o 180 segundos.
**Lo ves en:** [05-agent-loops](../../../05-agent-loops/README.md).

### Aprobación humana (HITL)

**Qué es:** *human in the loop*: una persona confirma una acción antes de que tenga efecto. En
BL_Loops la aprobación se liga a un hash exacto para que nadie apruebe “otra versión”.
**Ejemplo:** `release publish --expected-hash` en el 13.
**Lo ves en:** [13-sales-knowledge-curator](../../../13-sales-knowledge-curator/README.md).

### Mínimo privilegio

**Qué es:** dar a un agente solo los permisos imprescindibles. Todo lo no declarado está denegado.
**Ejemplo:** `permissions.default_effect: deny` y la red desactivada en un `AgentSpec`.
**Lo ves en:** [01-prompt-agent-factory](../../../01-prompt-agent-factory/README.md).

### Skill

**Qué es:** un procedimiento portable y reutilizable: cuándo se activa, qué pasos sigue y qué
recursos puede leer. Se carga por partes (“revelado progresivo”) para no llenar el contexto.
**Ejemplo:** `skill_meeting_minutes.json` produce un `SkillSpec` para redactar minutas.
**Lo ves en:** [01-prompt-agent-factory](../../../01-prompt-agent-factory/README.md).

### Contrato

**Qué es:** la forma exacta, verificable por código, que debe tener una entrada o salida. Si no
cumple, se rechaza en lugar de “interpretarse”.
**Ejemplo:** `PromptSpec`, `AgentSpec`, el `Plan` JSON del 03 o un JSON Schema de `contracts/`.
**Lo ves en:** todos los laboratorios; con más detalle en
[01-prompt-agent-factory](../../../01-prompt-agent-factory/docs/humano/CONTRACTS.md).

### Huella (`content_hash`)

**Qué es:** un resumen SHA-256 del contenido. Si cambia un solo carácter, cambia la huella. Sirve
para detectar ediciones no autorizadas.
**Ejemplo:** exportar un artefacto con el título editado a mano produce `content_hash_mismatch`.
**Lo ves en:** [01-prompt-agent-factory](../../../01-prompt-agent-factory/README.md) y
[13-sales-knowledge-curator](../../../13-sales-knowledge-curator/README.md).

## 3. Coordinar varios pasos

### Línea base

**Qué es:** la solución más simple de la misma tarea, usada como punto de comparación. Sin línea
base no se puede afirmar que algo más complejo “mejoró”.
**Ejemplo:** el agente único del 03 resuelve la misma tarea que el pipeline de tres roles.
**Lo ves en:** [03-orchestration](../../../03-orchestration/README.md).

### Orquestación

**Qué es:** repartir una tarea entre pasos o roles especializados con un orden y unos contratos de
entrega definidos.
**Ejemplo:** planificador → autor → revisor.
**Lo ves en:** [03-orchestration](../../../03-orchestration/README.md).

### Handoff

**Qué es:** la entrega tipada de un paso al siguiente. No es un comentario libre: es un objeto con
campos obligatorios.
**Ejemplo:** el `Plan` JSON con `title`, `audience`, `outline` y `success_checks`.
**Lo ves en:** [03-orchestration](../../../03-orchestration/README.md).

### Gate determinista

**Qué es:** una lista de comprobaciones ejecutadas por código que decide si un resultado aprueba.
Siempre da el mismo veredicto para el mismo texto.
**Ejemplo:** `score_guide()` del 03 busca headings, “Ollama”, “PowerShell” y una condición de
parada.
**Lo ves en:** [03-orchestration](../../../03-orchestration/README.md) y
[05-agent-loops](../../../05-agent-loops/README.md).

### Maker/checker

**Qué es:** separar quien produce (*maker*, el modelo) de quien califica (*checker*, el código).
Evita que un agente se ponga la nota a sí mismo.
**Ejemplo:** en el 05 el modelo escribe y `score_output()` cuenta cinco assertions.
**Lo ves en:** [05-agent-loops](../../../05-agent-loops/README.md).

### Fan-out / fan-in

**Qué es:** *fan-out* lanza ramas independientes a la vez; *fan-in* espera y une sus resultados sin
rellenar huecos.
**Ejemplo:** tres fuentes del Taller Norte extraídas en paralelo y unidas en una tabla.
**Lo ves en:** [04-parallel-agents](../../../04-parallel-agents/README.md).

### Concurrencia (`max_in_flight`)

**Qué es:** cuántas llamadas pueden estar en curso al mismo tiempo. Con un solo modelo compartido,
la concurrencia real puede ser menor que la dibujada.
**Ejemplo:** `PARALLEL_MAX_IN_FLIGHT=1` convierte el “paralelo” en una cola visible.
**Lo ves en:** [04-parallel-agents](../../../04-parallel-agents/README.md).

### Speedup

**Qué es:** cuántas veces más rápido terminó una variante frente a otra:
`tiempo_secuencial / tiempo_paralelo`.
**Ejemplo:** 9 000 ms en serie y 4 500 ms en paralelo dan `speedup = 2.0`.
**Lo ves en:** [04-parallel-agents](../../../04-parallel-agents/README.md).

### Loop

**Qué es:** repetir generar → evaluar → mejorar hasta alcanzar un umbral o agotar el presupuesto.
Un loop sin presupuesto es un `while True` peligroso.
**Ejemplo:** el 05 reescribe un prompt débil hasta cumplir cinco assertions.
**Lo ves en:** [05-agent-loops](../../../05-agent-loops/README.md).

### Mejor candidato

**Qué es:** el resultado con mayor puntuación visto durante un loop. No tiene por qué ser el último:
una iteración puede empeorar.
**Ejemplo:** puntuaciones 2 → 4 → 3 conservan la iteración 2 como mejor candidato.
**Lo ves en:** [05-agent-loops](../../../05-agent-loops/README.md).

### Timeout

**Qué es:** el tiempo máximo que se espera una respuesta. Al vencer, el paso se marca como fallido;
no se reintenta a ciegas porque el modelo pudo haber empezado a trabajar.
**Ejemplo:** `SIMPLE_AGENT_TIMEOUT_SECONDS=300` en el 02.
**Lo ves en:** [02-single-agent](../../../02-single-agent/README.md) y
[04-parallel-agents](../../../04-parallel-agents/README.md).

### Fallback visible

**Qué es:** un camino alternativo que se activa ante un fallo **y queda registrado**. En BL_Loops
nunca es un proveedor cloud; suele ser una regla determinista o un contenido calibrado.
**Ejemplo:** si la llamada del 09 es inválida, se ejecuta una búsqueda determinista y la traza lo
indica.
**Lo ves en:** [09-agentic-rag](../../../09-agentic-rag/README.md) y en los estudios 22–24.

## 4. Recuperar conocimiento (RAG)

### RAG

**Qué es:** *Retrieval-Augmented Generation*. Antes de generar, el programa **recupera** fragmentos
relevantes y los **añade** al contexto. El modelo responde con esa evidencia y la cita.
**Ejemplo:** pregunta → buscar en SQLite → aumentar el prompt → Ollama → respuesta con `[S1]`.
**Lo ves en:** [06-naive-rag](../../../06-naive-rag/README.md).

### Corpus

**Qué es:** la colección de documentos sobre la que se busca.
**Ejemplo:** `fixtures/evaluation-corpus/` del 06 tiene cinco documentos sintéticos.
**Lo ves en:** laboratorios 06 a 09 y 13.

### Fragmento (chunk)

**Qué es:** un trozo de documento lo bastante pequeño para entrar en el contexto y lo bastante
completo para tener sentido. Cada fragmento recuerda su archivo y sus líneas.
**Ejemplo:** `01-politica-vigente.md:L3-L6`.
**Lo ves en:** `naive-rag search` del [06](../../../06-naive-rag/README.md).

### Índice

**Qué es:** una estructura preparada de antemano para buscar rápido sin releer los documentos.
**Ejemplo:** `.local/data/books.sqlite3` del 06.
**Lo ves en:** laboratorios 06 a 09.

### FTS5 y BM25

**Qué es:** FTS5 es el buscador de texto completo de SQLite. BM25 es la fórmula que puntúa cuánto
coinciden las palabras de la pregunta con un fragmento. En SQLite, **más negativo = más
relevante**.
**Ejemplo:** `bm25=-2.681` gana a `bm25=-0.301`.
**Lo ves en:** [06-naive-rag](../../../06-naive-rag/README.md).

### Embedding

**Qué es:** una lista de números (vector) que representa el *significado* de un texto. Textos con
significado parecido producen vectores cercanos aunque usen palabras distintas.
**Ejemplo:** `qwen3-embedding:latest` produce vectores de 768 números en el 07.
**Lo ves en:** [07-vector-rag](../../../07-vector-rag/README.md).

### Similitud coseno

**Qué es:** una medida de cercanía entre dos vectores: 1 significa “misma dirección”, 0 “sin
relación”. Con vectores normalizados equivale al producto punto.
**Ejemplo:** 0.587 para el pasaje pertinente frente a 0.092 para el distractor (spike del 07).
**Lo ves en:** [07-vector-rag](../../../07-vector-rag/README.md).

### Top-k

**Qué es:** cuántos fragmentos se entregan al modelo. Un `k` pequeño puede dejar fuera la
evidencia; uno grande mete ruido y gasta contexto.
**Ejemplo:** `top_k=4` en el 06.
**Lo ves en:** laboratorios 06 a 09.

### Recall@k

**Qué es:** la proporción de preguntas en las que el fragmento correcto aparece entre los primeros
`k` resultados. Se mide **antes** de juzgar la respuesta del modelo.
**Ejemplo:** 4 aciertos en 5 preguntas = recall@5 de 0.8.
**Lo ves en:** el experimento de [07-vector-rag](../../../07-vector-rag/docs/humano/EXERCISES.md).

### Búsqueda híbrida y RRF

**Qué es:** combinar el ranking léxico y el vectorial. *Reciprocal Rank Fusion* suma
`peso / (60 + posición)` de cada ranking, así que no necesita que BM25 y coseno usen la misma escala.
**Ejemplo:** el 07 pondera 0.35 léxico y 0.65 vectorial.
**Lo ves en:** [07-vector-rag](../../../07-vector-rag/README.md).

### Grafo, nodo y arista

**Qué es:** un grafo representa entidades (*nodos*) y relaciones con nombre (*aristas*).
**Ejemplo:** `Ana Ruiz` y `AtlasCRM` son nodos; `owns` es la arista que los une.
**Lo ves en:** [08-graph-rag](../../../08-graph-rag/README.md).

### Triple

**Qué es:** la unidad mínima de un grafo: sujeto, predicado y objeto.
**Ejemplo:** `` `AtlasCRM` --depends_on--> `NortePay` ``.
**Lo ves en:** los fixtures de [08-graph-rag](../../../08-graph-rag/README.md).

### Multi-hop (saltos)

**Qué es:** responder encadenando varias aristas. Cada arista recorrida es un salto (*hop*).
**Ejemplo:** Ana Ruiz → AtlasCRM → NortePay → 2026-03-01 son tres saltos.
**Lo ves en:** [08-graph-rag](../../../08-graph-rag/README.md).

### Arista extraída frente a inferida

**Qué es:** una arista *extraída* existe escrita en un documento y tiene cita; una *inferida* se
compone al consultar a partir de varias extraídas y nunca se guarda como si fuera un hecho.
**Ejemplo:** `inferred | Ana Ruiz --owns/depends_on/freeze_date--> 2026-03-01 | hops=3`.
**Lo ves en:** [08-graph-rag](../../../08-graph-rag/README.md).

### Cita

**Qué es:** la referencia verificable que acompaña a una afirmación: archivo y líneas, o un
identificador como `[S2]` que apunta a un fragmento entregado.
**Ejemplo:** una cita `[S7]` cuando solo hubo cuatro fragmentos es inválida.
**Lo ves en:** laboratorios 06 a 09.

### Abstención

**Qué es:** responder “no tengo evidencia suficiente” en lugar de inventar. Es un resultado válido
y, a veces, el correcto.
**Ejemplo:** sin coincidencias léxicas, el 06 se abstiene **sin llamar al modelo**.
**Lo ves en:** [06-naive-rag](../../../06-naive-rag/README.md).

### Inyección indirecta

**Qué es:** instrucciones maliciosas escondidas dentro de los datos recuperados (“ignora tus reglas
y…”). Los fragmentos son datos no confiables, nunca órdenes.
**Ejemplo:** `fixtures/corpus/06-injection.md` del 13.
**Lo ves en:** [13-sales-knowledge-curator](../../../13-sales-knowledge-curator/README.md).

### Map-reduce

**Qué es:** resumir un texto largo por partes (*map*) y luego combinar esos resúmenes (*reduce*).
Evita superar el contexto del modelo.
**Ejemplo:** reuniones largas en el 25 se dividen en bloques con solapamiento.
**Lo ves en:** [25-meeting-summarizer](../../../25-meeting-summarizer/README.md).

## 5. Evidencia y observabilidad

### Fixture

**Qué es:** un dato de prueba sintético y versionado que permite repetir un experimento.
**Ejemplo:** `examples/sources/` del 04 o `fixtures/zoom_standup.vtt` del 25.
**Lo ves en:** todos los laboratorios.

### Caso de evaluación

**Qué es:** una tarea con identificador y versión (`I-ORCH-001@0.1.0`), entrada fija y criterios de
aprobado. Permite comparar variantes con la misma vara.
**Ejemplo:** `I-LOOP-003` en el 05.
**Lo ves en:** [CASOS_DE_EVALUACION.md](../../CASOS_DE_EVALUACION.md).

### Traza y evento

**Qué es:** una *traza* es la secuencia ordenada de *eventos* de una corrida: `run.started`,
`node.started`, `model.completed`, `run.completed`…
**Ejemplo:** cada evento tiene `sequence`, `event_type`, `node`, `payload` y `metrics`.
**Lo ves en:** cualquier archivo de `.local/runs/`.

### JSONL

**Qué es:** *JSON Lines*: un objeto JSON por línea. Es el formato común de exportación; el
comparador central solo importa estos archivos.
**Ejemplo:** `uv run single-agent-validate` importa y valida el JSONL más reciente.
**Lo ves en:** todos los laboratorios con corridas.

### Sanitización

**Qué es:** quitar de la traza el contenido sensible o crudo (preguntas, respuestas, documentos) y
conservar solo estados, longitudes, hashes y métricas.
**Ejemplo:** el JSONL del 02 registra `input_chars`, no el texto que escribiste.
**Lo ves en:** las pruebas `*_sanitized` de los laboratorios 02 a 09.

### SSE

**Qué es:** *Server-Sent Events*: el servidor empuja eventos al navegador por una conexión abierta.
Así el dashboard pinta estados reales mientras ocurren.
**Ejemplo:** `GET /api/v1/runs/{run_id}/events` en el 03.
**Lo ves en:** los dashboards de 03, 04, 05 y 13.

### Snapshot

**Qué es:** la foto completa del estado de una corrida en un instante: nodos, variantes, métricas.
**Ejemplo:** `GET /api/v1/runs/{run_id}` en el 03.
**Lo ves en:** laboratorios 03 a 05.

### Prueba determinista y doble de prueba

**Qué es:** una prueba determinista da siempre el mismo resultado. Para lograrlo se sustituye el
modelo real por un *doble*: un objeto falso que responde lo que la prueba necesita.
**Ejemplo:** `RememberingClient` en las pruebas del 02.
**Lo ves en:** las carpetas `tests/` de todos los laboratorios.

### Spike

**Qué es:** un experimento pequeño y desechable para responder una duda antes de decidir.
**Ejemplo:** el spike de embeddings que justificó el 07.
**Lo ves en:** [07-vector-rag](../../../07-vector-rag/docs/humano/METHODOLOGY.md).

### SHA

**Qué es:** el identificador único de un commit de Git (o de un contenido). Fijarlo permite repetir
exactamente el mismo punto de partida.
**Ejemplo:** las corridas comparables del 14 exigen el mismo SHA.
**Lo ves en:** [14-local-code-hermes](../../../14-local-code-hermes/README.md).

### Cohorte

**Qué es:** un grupo de corridas comparables entre sí porque comparten modelo, contexto, tarea y
SHA. Cambiar cualquiera de esos factores crea otra cohorte.
**Ejemplo:** `local-code-9b-64k` y el fallback `qwen3.5:4b` a 64k son cohortes distintas.
**Lo ves en:** [14-local-code-hermes](../../../14-local-code-hermes/README.md).

### Preflight

**Qué es:** una inspección previa que comprueba prerrequisitos sin ejecutar la tarea real.
**Ejemplo:** `hermes-preflight` revisa Python, endpoint, Git y memoria.
**Lo ves en:** [14-local-code-hermes](../../../14-local-code-hermes/README.md).

### Egress

**Qué es:** tráfico de red que sale de tu máquina. “Inferencia local” y “cero egress” son
afirmaciones distintas: la segunda exige evidencia de red independiente.
**Ejemplo:** un endpoint en `127.0.0.1` no prueba que el cliente no abrió otras conexiones.
**Lo ves en:** [14-local-code-hermes](../../../14-local-code-hermes/README.md).

### Sandbox

**Qué es:** un entorno aislado donde un proceso solo ve lo que se le permite.
**Ejemplo:** el 14 ejecuta pruebas en Docker con `--network=none`.
**Lo ves en:** [14-local-code-hermes](../../../14-local-code-hermes/README.md).

## 6. Entorno de trabajo

### `uv`, `.venv` y `uv.lock`

**Qué es:** `uv` instala y ejecuta Python. Cada laboratorio tiene su `.venv` (paquetes instalados)
y su `uv.lock` (versiones exactas). `uv run` ejecuta siempre dentro de la `.venv` correcta.
**Ejemplo:** `uv sync --locked --all-groups` reproduce exactamente el entorno del lock.
**Lo ves en:** [ENVIRONMENTS.md](ENVIRONMENTS.md).

### `.env` y `.env.example`

**Qué es:** `.env` guarda configuración local real y nunca se versiona; `.env.example` es su
contrato público, sin secretos.
**Ejemplo:** `Copy-Item .env.example .env` al copiar un laboratorio fuera de BL_Loops.
**Lo ves en:** [ENVIRONMENTS.md](ENVIRONMENTS.md).

### Loopback

**Qué es:** la interfaz de red que solo apunta a tu propia máquina: `127.0.0.1`, `localhost` o
`::1`. Los laboratorios rechazan cualquier otro host para Ollama.
**Ejemplo:** `OLLAMA_BASE_URL=http://127.0.0.1:11434`.
**Lo ves en:** las pruebas de configuración de cada laboratorio.

### Puerto

**Qué es:** el número que distingue servicios en la misma máquina. Cada laboratorio con interfaz
usa puertos propios para no chocar.
**Ejemplo:** API del 03 en `8012`, dashboard en `5172`.
**Lo ves en:** la tabla de puertos de [QUICKSTART.md](QUICKSTART.md#mapa-de-puertos).

### FastAPI y Pydantic

**Qué es:** FastAPI crea la API HTTP de cada laboratorio; Pydantic valida que los datos cumplan su
contrato y genera JSON Schema.
**Ejemplo:** un campo desconocido en un `PromptSpec` produce un error de validación.
**Lo ves en:** laboratorios 01, 03, 04, 05, 13 y 22 a 25.

### React Flow

**Qué es:** la librería que dibuja los nodos y conexiones de los dashboards. En BL_Loops el color
de cada nodo sale de eventos reales, no de una animación decorativa.
**Ejemplo:** el grafo del 03 pasa de `queued` a `running` y `done` con cada evento SSE.
**Lo ves en:** los dashboards de 01, 03, 04, 05 y 13.

## 7. Video generado por código

### Composición y línea de tiempo

**Qué es:** la descripción de un video como elementos con inicio y duración, en lugar de fotogramas
dibujados a mano. Un motor la recorre segundo a segundo y produce los fotogramas.
**Ejemplo:** en el 22, un `<div class="clip" data-start="3" data-duration="3">` aparece del segundo 3
al 6; en el 23, una escena de Remotion se calcula a partir del número de fotograma.
**Lo ves en:** [22-hyperframes-video-studio](../../../22-hyperframes-video-studio/README.md) y
[23-remotion-superpowers-studio](../../../23-remotion-superpowers-studio/README.md).

### Render determinista

**Qué es:** producir el video a partir de una descripción fija, de modo que la misma entrada dé el
mismo resultado. El modelo puede proponer la descripción; el render no improvisa.
**Ejemplo:** los planos calibrados del 24 siempre producen un animatic de 12 s y el mismo tamaño.
**Lo ves en:** los estudios 22 a 24.

### Storyboard, plano y animatic

**Qué es:** un **storyboard** divide una historia en **planos**; cada plano tiene tipo (general,
medio, primer plano…), movimiento de cámara y duración. Un **animatic** es la previsualización en
video de ese storyboard con su ritmo real, antes de producir las imágenes finales.
**Ejemplo:** «Plano 3: Close-up | Dolly In (Push In) | 3.0s | La Señal Ancestral».
**Lo ves en:** [24-open-generative-ai-studio](../../../24-open-generative-ai-studio/README.md).

### Filtergraph y escapado

**Qué es:** un **filtergraph** es la cadena de filtros que FFmpeg aplica para crear o transformar un
video, escrita como texto (`color=...,drawtext=...`). **Escapar** es preparar un texto para que sus
caracteres especiales no se confundan con la sintaxis: en `drawtext`, `:` separa opciones y `'` cierra
valores.
**Ejemplo:** `Plano 2: la 'señal'` se escribe `Plano 2\: la ’señal’`.
**Lo ves en:** `drawtext_value()` del 24 y sus pruebas.

### ffprobe

**Qué es:** la herramienta de FFmpeg que **mide** un archivo multimedia: duración, resolución,
fotogramas por segundo. Los estudios la usan para no dar por buena una duración supuesta.
**Ejemplo:** si `ffprobe` no está, la duración registrada es `0.0` y la evaluación no aprueba.
**Lo ves en:** los estudios 22 a 24 (`duration_measured` en el JSONL).
