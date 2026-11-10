# Ejercicios: 23-remotion-superpowers-studio

Haz los ejercicios en orden. Los dos primeros solo necesitan Python; el avanzado necesita `npm ci`.
Las soluciones están plegadas: ábrelas después de intentarlo.

## Básico: de segundos a fotogramas

**Objetivo:** predecir, antes de ejecutar nada, cómo reparte el estudio un video de 10 s.

1. Calcula a mano: fotogramas totales, fotogramas por escena y fotograma en el que empieza la
   escena 3.
2. Comprueba tu respuesta con el script del [ejemplo 3](EXAMPLES.md#ejemplo-3-de-segundos-a-fotogramas).

<details>
<summary>Solución</summary>

10 s × 30 fps = 300 fotogramas; 300 / 4 = 75 por escena. La escena 3 empieza en el fotograma
2 × 75 = 150 y termina en el 224. El script devuelve `escenas [75, 75, 75, 75] | suma 300 = 10.00 s`.

En Remotion Studio (`npm run dev`) puedes saltar al fotograma 150 y ver cómo entra la tercera escena.
</details>

## Intermedio: que no se pierda ningún fotograma

**Objetivo:** con 7 s (210 fotogramas), la división entera da 4 escenas de 52 y pierde 2 fotogramas.
Reparte el resto para que la suma sea exactamente la pedida.

1. Escribe en `ollama_director.py` una función `frame_plan(total_frames, scenes_count)` que devuelva
   la lista de fotogramas por escena.
2. Úsala en las dos ramas del director: la respuesta del modelo y el respaldo calibrado.
3. Añade una prueba con `RemotionBrief(target_duration=7.0)`.

<details>
<summary>Solución</summary>

```python
def frame_plan(total_frames: int, scenes_count: int) -> list[int]:
    """Reparte los fotogramas: el resto de la división se suma a la última escena."""

    base = total_frames // scenes_count
    plan = [base] * scenes_count
    plan[-1] += total_frames - base * scenes_count
    return plan
```

En la rama del modelo, sustituye `calc_frames = total_frames // len(parsed)` por
`plan = frame_plan(total_frames, len(parsed))` y usa `plan[idx]` como duración y para avanzar
`current_frame`. En la rama calibrada, lo mismo con `frame_plan(total_frames, len(DEFAULT_REMOTION_SCENES))`.

Prueba:

```python
async def test_no_frame_is_lost_when_the_division_is_not_exact() -> None:
    from remotion_studio.ollama_director import RemotionOllamaDirector, frame_plan

    assert frame_plan(210, 4) == [52, 52, 52, 54]
    director = RemotionOllamaDirector(base_url="http://127.0.0.1:9")

    scenes = await director.generate_scenes(RemotionBrief(target_duration=7.0))

    assert sum(scene.duration_in_frames for scene in scenes) == 210
    assert scenes[-1].start_frame == 156
```

Con la solución aplicada en una copia del laboratorio, el script del ejemplo 3 pasa a mostrar
`7.0 s -> pedidos 210 fotogramas | escenas [52, 52, 52, 54] | suma 210 = 7.00 s` y la prueba nueva
pasa. ¿Por qué no repartir el resto entre varias escenas? También vale; lo importante es que la suma
sea exacta y que la decisión esté probada.
</details>

## Avanzado: efecto máquina de escribir

**Objetivo:** que el subtítulo de cada escena aparezca letra a letra, una cada 2 fotogramas, en
`src/video_composition/SceneSequence.tsx`.

**Comprueba:** `npm run typecheck` y dos fotogramas sueltos de la primera escena:

```powershell
npx remotion still src/video_composition/index.ts MainVideo .local/still_40.png --frame=40
npx remotion still src/video_composition/index.ts MainVideo .local/still_80.png --frame=80
```

<details>
<summary>Solución</summary>

Justo después de `useVideoConfig()`:

```tsx
// Máquina de escribir: una letra nueva cada 2 fotogramas.
const visibleChars = Math.floor(frame / 2);
```

Y en el párrafo del subtítulo:

```tsx
{scene.subheadline.slice(0, visibleChars)}
```

Resultado comprobado renderizando ambos fotogramas: en el 40 se ve «Aprovecha componente»
(20 caracteres) y en el 80, «Aprovecha componentes, hooks de React, e» (40 caracteres). En el 80
la tarjeta ya empieza a desvanecerse, porque la salida ocupa los últimos 15 fotogramas de cada
escena de 90.

`frame` es el fotograma **local** de la escena: el efecto vuelve a empezar en cada `<Sequence>` sin
escribir ninguna lógica de tiempo global.
</details>

## Reto abierto: transiciones entre escenas

El paquete `@remotion/transitions` ya está instalado (`package.json`), pero la composición no lo usa.
Sustituye las `<Sequence>` de `MainComposition.tsx` por un `<TransitionSeries>` con `fade()` entre
escenas y responde:

- ¿Cambia la duración total? (Pista: en Remotion, una transición solapa dos escenas.)
- ¿Qué tendrías que ajustar en el cálculo de fotogramas de Python para que el video siga durando lo
  pedido?

Este reto no tiene solución única; compara tu resultado con `ffprobe` y con la evaluación del JSONL.
