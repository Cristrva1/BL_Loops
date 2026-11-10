# Ejercicios: 24-open-generative-ai-studio

Haz los ejercicios en orden. Cada uno indica cómo comprobar tu resultado; la solución está plegada
para que la abras solo después de intentarlo. Ninguno necesita Ollama.

Antes de empezar, guarda el estado del laboratorio para poder volver atrás:

```powershell
git status --short .
```

## Básico 1: cambia la duración y comprueba la medición

**Objetivo:** confirmar que la duración la decide el estudio y que la mide `ffprobe`.

1. Abre el panel (`uv run python -m open_genai_studio.main`) y pon «Duración total» en `20`.
2. Pulsa «Generar storyboard y animatic» y espera al nodo Evaluación.

**Comprueba:** ¿cuánto dura cada plano en la pestaña Storyboard? ¿Qué muestra «Duración (ffprobe)»?

<details>
<summary>Solución</summary>

Cada plano dura `5 s` (20 / 4) y la duración medida es `20 s`. La evaluación aprueba con desvío
`0 s`. Se comprobó ejecutando el orquestador con `total_duration_target=20`: planos
`[5.0, 5.0, 5.0, 5.0]`, duración medida `20.0`.

El panel no deja escribir menos de 4. Si llamas a la API con `"total_duration_target": 3`, responde
`422`: con 4 planos cada uno duraría 0,75 s y el contrato exige al menos 1 s por plano (`ge=1.0`); por
eso el proyecto exige `total_duration_target >= 4`.
</details>

## Básico 2: provoca un rechazo por contrato

**Objetivo:** ver qué respuestas del modelo se aceptan y cuáles activan el fallback.

Escribe un script `contrato.py` que llame a `parse_shots()` con estas tres respuestas simuladas y
muestre el resultado o el motivo del rechazo:

1. Una lista JSON de 3 planos.
2. Un objeto `{"shots": [...]}` con 4 planos válidos.
3. Una lista de 4 planos donde uno tiene `"shot_type": "Over the shoulder"`.

<details>
<summary>Solución</summary>

```python
import json

from open_genai_studio.storyboard_engine import parse_shots

plano = {"shot_type": "Wide Shot", "camera_movement": "Static", "headline": "Plano"}
casos = {
    "tres planos": json.dumps([plano] * 3),
    "objeto con shots": json.dumps({"shots": [plano] * 4}),
    "tipo desconocido": json.dumps([plano] * 3 + [{**plano, "shot_type": "Over the shoulder"}]),
}
for nombre, respuesta in casos.items():
    try:
        planos = parse_shots(respuesta, duration_seconds=3.0)
        print(f"{nombre}: aceptada con {len(planos)} planos")
    except ValueError as exc:
        print(f"{nombre}: rechazada -> {exc}")
```

Salida esperada (es determinista):

```text
tres planos: rechazada -> se esperaban 4 planos y llegaron 3
objeto con shots: aceptada con 4 planos
tipo desconocido: rechazada -> shot_type desconocido: 'Over the shoulder'
```

En una corrida real, cada rechazo se convierte en
`Fallback visible: respuesta no válida: <motivo>` en los eventos SSE.
</details>

## Intermedio 1: añade un tipo de plano nuevo

**Objetivo:** que «Over the Shoulder» sea un tipo de plano válido, sin tocar el prompt a mano.

1. Añade el valor al enum correspondiente de `schemas.py`.
2. Añade una prueba en `tests/test_contracts_and_safety.py` que demuestre que `parse_shots()` acepta
   `"over the shoulder"` en minúsculas.

**Comprueba:** `uv run pytest` pasa y el ejercicio «Básico 2» ya no rechaza el tercer caso.

<details>
<summary>Solución</summary>

En `schemas.py`:

```python
class ShotType(StrEnum):
    ...
    DRONE_AERIAL = "Drone Aerial"
    OVER_THE_SHOULDER = "Over the Shoulder"
```

Prueba:

```python
def test_over_the_shoulder_is_a_valid_shot_type() -> None:
    planos = [dict(MODEL_SHOTS[1], shot_type="over the shoulder")] * 4

    shots = parse_shots(json.dumps(planos), duration_seconds=3.0)

    assert shots[0].shot_type is ShotType.OVER_THE_SHOULDER
```

No hace falta cambiar `build_prompt()`: la lista de opciones que ve el modelo se genera desde el
enum. Así el prompt y el contrato no pueden desincronizarse. Se comprobó en una copia del
laboratorio: `38 passed`, y el tercer caso de «Básico 2» pasa a `aceptada con 4 planos`.
</details>

## Intermedio 2: muestra la descripción en el animatic

**Objetivo:** añadir una séptima línea de texto con `shot.description` entre la luz (y=290) y la
etiqueta del prompt (y=370).

**Comprueba:** `uv run pytest`. Una prueba fallará: descubre cuál y por qué antes de corregirla.

<details>
<summary>Solución</summary>

En `build_filter_graph()`, añade una tupla a `lines`, después de la línea de luz:

```python
(drawtext_value(shot.description, 110), "0xe2e8f0", 24, 330),
```

Falla `test_filter_graph_keeps_model_text_inside_quoted_values`, que espera exactamente 6 `drawtext`,
6 `expansion=none` y 24 comillas. Actualiza los tres valores a 7, 7 y 28: la prueba no estaba mal,
documentaba el contrato anterior. Con el cambio, el render real de los 4 planos calibrados se
comprobó con FFmpeg: éxito, `12.0 s`, 4 planos.

La descripción también viene del modelo: por eso pasa por `drawtext_value()` como el resto.
</details>

## Avanzado: anima el movimiento de cámara

**Objetivo:** que el titular se desplace en horizontal cuando el plano es `Slow Pan Right`,
`Slow Pan Left` o `Tracking Shot`, y quede quieto en los demás.

Pista: en `drawtext`, `x` acepta una expresión con `t`, el tiempo en segundos del fotograma.

**Comprueba:** mide la posición del titular en varios fotogramas (no basta con mirar el video ni con
comparar hashes de imágenes: la compresión cambia los píxeles aunque el contenido sea idéntico).

<details>
<summary>Solución</summary>

Un diccionario de expresiones por movimiento y una quinta componente `x` en cada línea:

```python
MOVEMENT_X = {
    CameraMovement.SLOW_PAN_RIGHT: "120+t*40",
    CameraMovement.SLOW_PAN_LEFT: "240-t*40",
    CameraMovement.TRACKING_SHOT: "120+t*25",
}

headline_x = MOVEMENT_X.get(shot.camera_movement, "120")
lines = [
    (drawtext_value(label), f"0x{accent}", 28, "120", 120),
    (drawtext_value(shot.headline, 70), "white", 56, headline_x, 200),
    ...
]
parts.extend(
    f"drawtext=text='{text}':expansion=none{font}:fontcolor={color}:fontsize={size}"
    f":x='{x}':y={y}"
    for text, color, size, x, y in lines
)
```

La expresión va entre comillas (`x='120+t*40'`): si algún día usas funciones con comas, como
`min(a,b)`, la coma no se confundirá con el separador de filtros.

Para medir, este script busca la primera columna clara en la banda del titular (y de 200 a 260):

```python
import subprocess
from pathlib import Path


def borde_izquierdo(segmento: Path, ts: str) -> int:
    w, h = 1800, 60
    raw = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-ss", ts, "-i", str(segmento), "-frames:v", "1",
         "-vf", f"crop={w}:{h}:0:200,format=gray", "-f", "rawvideo", "-"],
        capture_output=True, check=True,
    ).stdout
    columnas = [x for y in range(h) for x in range(w) if raw[y * w + x] > 200]
    return min(columnas) if columnas else -1


ws = Path(".local/workspace")
for nombre in ("shot_1.mp4", "shot_4.mp4"):
    print(nombre, [borde_izquierdo(ws / nombre, ts) for ts in ("0.0", "1.0", "2.5")])
```

Resultado medido tras renderizar los planos calibrados de 3 s:

```text
shot_1.mp4 [126, 166, 226]
shot_4.mp4 [126, 126, 126]
```

El plano 1 (`Slow Pan Right`) avanza 40 px por segundo; el plano 4 (`Crane Down`) no se mueve en
horizontal. Reto extra: anima `Crane Down` con una expresión en `y`.
</details>
