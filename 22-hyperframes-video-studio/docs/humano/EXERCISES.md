# Ejercicios: 22-hyperframes-video-studio

Haz los ejercicios en orden. Ninguno necesita Ollama ni renderizar: todos se comprueban con Python y
`uv run pytest`. Las soluciones están plegadas; ábrelas después de intentarlo.

## Básico 1: la línea de tiempo la decide el estudio

**Objetivo:** comprobar cómo se reparte una duración de 10 s entre las cinco escenas.

Escribe un script que pida escenas a un director sin Ollama (usa un puerto vacío, como
`http://127.0.0.1:9`), genere la composición y ejecute el lint.

<details>
<summary>Solución</summary>

```python
import asyncio

from hyperframes_studio.ollama_client import OllamaVideoDirector
from hyperframes_studio.schemas import VideoBrief
from hyperframes_studio.templates import generate_hyperframes_html, lint_composition

brief = VideoBrief(target_duration=10.0)
director = OllamaVideoDirector(base_url="http://127.0.0.1:9")  # sin Ollama: fallback
scenes = asyncio.run(director.generate_scenes(brief))
print([(s.start_time, s.duration) for s in scenes], director.last_source)
print("lint:", lint_composition(generate_hyperframes_html(brief, scenes), scenes) or "sin problemas")
```

Salida obtenida:

```text
[(0.0, 2.0), (2.0, 2.0), (4.0, 2.0), (6.0, 2.0), (8.0, 2.0)] fallback
lint: sin problemas
```

Con Ollama activo el contenido cambia, pero los tiempos son los mismos: el estudio los recalcula
aunque el modelo proponga otros (lo comprueba
`test_director_keeps_the_timeline_even_if_the_model_proposes_other_times`).
</details>

## Básico 2: el texto del modelo no se ejecuta

**Objetivo:** demostrar que un titular con etiquetas HTML aparece como texto.

Sustituye el titular de la primera escena por `<b>Hola</b> & adiós`, genera la composición y busca
cómo quedó escrito.

<details>
<summary>Solución</summary>

Continúa el script del ejercicio anterior (usa sus `brief` y `scenes`):

```python
prueba = scenes[0].model_copy(update={"headline": "<b>Hola</b> & adiós"})
html = generate_hyperframes_html(brief, [prueba, *scenes[1:]])
print("&lt;b&gt;Hola&lt;/b&gt; &amp; adiós" in html, "<b>Hola</b>" in html)
```

Salida obtenida: `True False`. El navegador mostrará los caracteres `<b>`; no pondrá el texto en
negrita. Lo mismo protege frente a un `<script>` o un `<div class="clip">` inventados por el modelo.
</details>

## Intermedio: el lint también comprueba la duración total

**Objetivo:** que `lint_composition()` acepte `expected_total` y avise si la suma de escenas no
coincide con la duración pedida; el orquestador debe pasarle `brief.target_duration`.

**Comprueba:** añade una prueba que espere el mensaje
`la composición dura 15.0 s y se pidieron 20.0 s` y ejecuta `uv run pytest`. Alguna prueba
existente fallará: averigua por qué antes de corregirla.

<details>
<summary>Solución</summary>

En `templates.py`, un parámetro nuevo y una comprobación al final:

```python
def lint_composition(
    html_text: str,
    scenes: list[SceneSpec],
    tolerance: float = 0.05,
    expected_total: float | None = None,
) -> list[str]:
    ...
        expected_start = start + duration
    if expected_total is not None and abs(expected_start - expected_total) > tolerance:
        problems.append(
            f"la composición dura {round(expected_start, 2)} s y se pidieron {expected_total} s"
        )
    return problems
```

En `orchestrator.py`:

```python
problems = lint_composition(html_code, scenes, expected_total=brief.target_duration)
```

Prueba:

```python
def test_lint_detects_a_total_duration_mismatch() -> None:
    html = generate_hyperframes_html(VideoBrief(), DEFAULT_SCENES)

    assert lint_composition(html, DEFAULT_SCENES, expected_total=20.0) == [
        "la composición dura 15.0 s y se pidieron 20.0 s"
    ]
```

Si algún doble de prueba sustituye `lint_composition` con una función que no acepta argumentos con
nombre, fallará con `unexpected keyword argument 'expected_total'`: el doble debe aceptar
`**_kwargs`. Las pruebas del laboratorio ya lo hacen. Con la solución aplicada en una copia del
laboratorio se obtuvo `30 passed`.
</details>

## Avanzado: el director exige exactamente cinco escenas

**Objetivo:** si el modelo devuelve un número de escenas distinto de 5, el director debe usar el
respaldo y explicarlo: `respuesta no válida: se esperaban 5 escenas y llegaron N`. Es la misma
idea de contrato que aplica [el laboratorio 24](../../../24-open-generative-ai-studio/docs/humano/EXAMPLES.md#ejemplo-4-el-contrato-del-storyboard-en-acción).

**Comprueba:** escribe una prueba que simule a Ollama con `httpx.MockTransport` devolviendo una sola
escena.

<details>
<summary>Solución</summary>

En `ollama_client.py`, justo después de `parsed = json.loads(raw_text)`:

```python
if isinstance(parsed, list) and len(parsed) != 5:
    self.last_fallback_reason = (
        f"respuesta no válida: se esperaban 5 escenas y llegaron {len(parsed)}"
    )
elif isinstance(parsed, list):
    ...  # el bloque que ya construía las escenas
```

Prueba:

```python
async def test_director_requires_exactly_five_scenes(monkeypatch: pytest.MonkeyPatch) -> None:
    real_client = httpx.AsyncClient
    answer = json.dumps([{"headline": "solo una"}])

    def factory(**kwargs):
        handler = lambda _request: httpx.Response(200, json={"response": answer})  # noqa: E731
        return real_client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", factory)
    director = OllamaVideoDirector()

    scenes = await director.generate_scenes(VideoBrief())

    assert len(scenes) == 5
    assert director.last_source == "fallback"
    assert director.last_fallback_reason == "respuesta no válida: se esperaban 5 escenas y llegaron 1"
```

Las escenas devueltas son las calibradas y el motivo viaja al evento SSE y al JSONL. Con esta
solución y la del ejercicio intermedio, la copia del laboratorio dio `30 passed`.
</details>

## Reto abierto: compara con el lint oficial

Con Node.js instalado, ejecuta el lint de HyperFrames sobre la última composición:

```powershell
Set-Location .\.local\workspace
$env:HYPERFRAMES_NO_TELEMETRY = "1"
npx --yes hyperframes@0.8.34 lint --json
```

Anota qué reglas comprueba que el lint local no cubre y decide cuál merece la pena llevar a
`lint_composition()`. La salida depende de la versión de HyperFrames, por eso este reto no tiene una
solución única.
