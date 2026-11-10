# Ejemplos resueltos · Graph RAG

> Los ejemplos 1 a 6 se ejecutan **sin Ollama** y su salida es exactamente reproducible. El
> ejemplo 7 depende del modelo: se muestra la forma esperada. Ejecuta todo desde `08-graph-rag`,
> después de indexar:
>
> ```powershell
> uv run graph-rag index --source .\fixtures\evaluation-corpus
> ```

| # | Ejemplo | Concepto |
|---|---|---|
| 1 | Indexar | Nodos, aristas y fragmentos |
| 2 | Una ruta de tres saltos | Extraídas con cita, una inferida sin guardar |
| 3 | El contraste léxico | El eslabón que falta en el ranking |
| 4 | Saltos inversos | Recorrer una flecha al revés |
| 5 | El límite de saltos | Un presupuesto que corta la respuesta |
| 6 | Sin semillas | Cuando el grafo no tiene por dónde empezar |
| 7 | Generar con citas | Lo que recibe el modelo |

---

## Ejemplo 1 · Indexar

```powershell
uv run graph-rag index --source .\fixtures\evaluation-corpus
```

```text
Indice listo: 5/5 docs, 14 nodos, 11 aristas extraidas, 9 fragmentos.
SQLite: .local/data/graph.sqlite3
Corpus SHA-256: ec7ddc87b42c4a58d080f57f8d218f3ee5ba2d6b088869edfba16f4a57c0b5f9
```

**Qué observar:** solo las líneas con la forma `` `Sujeto` --predicado--> `Objeto` `` se convierten en
aristas (11 en total). El resto del texto se trocea en 9 fragmentos para la comparación léxica.
`04-calendario.md` no tiene ninguna arista: es prosa que menciona fechas para despistar a la búsqueda
por palabras.

## Ejemplo 2 · Una ruta de tres saltos

```powershell
uv run graph-rag search --mode graph "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
```

```text
1.
Ana Ruiz --owns--> AtlasCRM --depends_on--> NortePay --freeze_date--> 2026-03-01
graph LR
  Ana_Ruiz -->|owns| AtlasCRM
  AtlasCRM -->|depends_on| NortePay
  NortePay -->|freeze_date| 2026_03_01
extracted | Ana Ruiz --owns--> AtlasCRM | 01-personas.md:L16-L16
extracted | AtlasCRM --depends_on--> NortePay | 02-proyectos.md:L14-L14
extracted | NortePay --freeze_date--> 2026-03-01 | 03-proveedores.md:L13-L13
inferred | Ana Ruiz --owns/depends_on/freeze_date--> 2026-03-01 | hops=3

2.
Ana Ruiz --owns--> AtlasCRM --depends_on--> NortePay
...
3.
Ana Ruiz --owns--> AtlasCRM
...
```

**Qué observar:**

- La pregunta contiene la **semilla** «Ana Ruiz», una etiqueta de nodo. Desde ahí, BFS (búsqueda en
  anchura) recorre aristas hasta tres saltos.
- Cada salto `extracted` cita **archivo y línea**: tres documentos distintos sostienen la respuesta.
- La línea `inferred` resume la cadena de extremo a extremo. Es una conclusión del recorrido, no un
  hecho escrito, y por eso **nunca se guarda** en SQLite.
- Las rutas se ordenan de más larga a más corta. El bloque `graph LR` es Mermaid: pégalo en un
  visor Mermaid para ver el dibujo.

## Ejemplo 3 · El contraste léxico

```powershell
uv run graph-rag search --mode lexical "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
```

```text
Comparacion lexica:
1. 03-proveedores.md:L3-L9 score=-2.246
2. 01-personas.md:L3-L12 score=-2.035
3. 01-personas.md:L16-L18 score=-1.548
4. 05-distractores.md:L3-L4 score=-0.891
5. 04-calendario.md:L3-L7 score=-0.821
```

**Por qué falla:** la búsqueda por palabras trae personas («Ana Ruiz»), proveedores
(«congelación», «fecha») y hasta el calendario y los distractores, pero **no** `02-proyectos.md`,
que no contiene ninguna palabra de la pregunta. Sin ese documento no hay forma de saber que AtlasCRM
depende de NortePay: un modelo que solo vea estos cinco fragmentos podría adivinar una fecha
cualquiera del calendario.

## Ejemplo 4 · Saltos inversos

```powershell
uv run graph-rag search --mode graph "¿Quién es responsable de AtlasCRM?"
```

```text
1.
AtlasCRM --depends_on--> NortePay --freeze_date--> 2026-03-01
...
3.
AtlasCRM <--owns-- Ana Ruiz
graph LR
  Ana_Ruiz -->|owns| AtlasCRM
extracted | Ana Ruiz --owns--> AtlasCRM | 01-personas.md:L16-L16
```

**Qué observar:**

- La semilla es «AtlasCRM», pero el triple escrito es `Ana Ruiz --owns--> AtlasCRM`. El recorrido lo
  sigue **al revés** (`<--owns--`): así se responde «¿quién es dueño de…?».
- El diagrama Mermaid y la línea `extracted` conservan el sentido original de la flecha.
- La ruta útil aparece en tercer lugar: el grafo no entiende la pregunta, solo enumera caminos desde
  la semilla. Elegir la ruta pertinente es trabajo del modelo (o tuyo).

Con dos saltos inversos, la arista inferida marca cada inversión con `^`, la notación de caminos
inversos de SPARQL. Por ejemplo, con «¿Qué congelación de cambios tiene MailRelay?»:

```text
MailRelay <--depends_on-- PortalClientes <--owns-- Luis Soto
inferred | MailRelay --^depends_on/^owns--> Luis Soto | hops=2
```

Se lee: «MailRelay es la dependencia de PortalClientes, cuyo dueño es Luis Soto».

## Ejemplo 5 · El límite de saltos

```powershell
$env:GRAPH_RAG_MAX_HOPS = "2"
uv run graph-rag search --mode graph "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
Remove-Item Env:GRAPH_RAG_MAX_HOPS
```

```text
1.
Ana Ruiz --owns--> AtlasCRM --depends_on--> NortePay
graph LR
  Ana_Ruiz -->|owns| AtlasCRM
  AtlasCRM -->|depends_on| NortePay
extracted | Ana Ruiz --owns--> AtlasCRM | 01-personas.md:L16-L16
extracted | AtlasCRM --depends_on--> NortePay | 02-proyectos.md:L14-L14
inferred | Ana Ruiz --owns/depends_on--> NortePay | hops=2
```

**Qué aprender:** con dos saltos el recorrido se detiene en NortePay y **la fecha nunca aparece**. El
límite de saltos es un presupuesto: evita explorar todo el grafo, pero si es menor que la distancia
real, la respuesta queda fuera de alcance. Un buen sistema lo declara en vez de rellenar el hueco.

## Ejemplo 6 · Sin semillas

```powershell
uv run graph-rag search --mode graph "¿Qué día abre la cafetería?"
```

```text
Sin rutas. Semillas: (ninguna)
```

Y con `ask`, también sin Ollama porque nunca llega a llamarlo:

```powershell
uv run graph-rag ask "¿Qué día abre la cafetería?"
```

```text
RAG graph | chat=qwen3.5:4b | hops<=3
[1/3 recorrer] graph -> 0 rutas, 0 aristas extraidas, 0 inferida
[2/3 aumentar] skipped
[3/3 generar] skipped

Respuesta > No encontre una ruta en el grafo con las entidades de la pregunta.
Traza JSONL: .local/runs/<fecha>-run-<id>.jsonl
```

**Qué aprender:** ninguna palabra de la pregunta coincide con una etiqueta de nodo, así que el grafo
no tiene por dónde empezar. No es un error: es la abstención del grafo, igual que la del laboratorio
06 cuando FTS5 no encuentra palabras.

## Ejemplo 7 · Generar con citas (necesita Ollama)

```powershell
uv run graph-rag ask "¿Qué fecha de congelación afecta el proyecto de Ana Ruiz?"
uv run graph-rag-validate
```

La parte de recuperación es determinista y se obtuvo con Ollama apagado (la corrida termina con
`Operacion fallida: No se pudo conectar con Ollama local.` justo antes de generar):

```text
RAG graph | chat=qwen3.5:4b | hops<=3
[1/3 recorrer] graph -> 3 rutas, 3 aristas extraidas, 1 inferida
[2/3 aumentar] 3 fuentes citables

Ruta:
Ana Ruiz --owns--> AtlasCRM --depends_on--> NortePay --freeze_date--> 2026-03-01
...
inferred | Ana Ruiz --owns/depends_on/freeze_date--> 2026-03-01 | hops=3
```

Con Ollama encendido continúa con esta forma:

```text
[3/3 generar] done | <ms> ms

Respuesta > <texto del modelo; debería decir 2026-03-01 con citas [S1]…[S3]>

Fuentes:
- [S1] 01-personas.md:L16-L16 | extracted | owns
- [S2] 02-proyectos.md:L14-L14 | extracted | depends_on
- [S3] 03-proveedores.md:L13-L13 | extracted | freeze_date
...
Traza JSONL: .local/runs/<fecha>-run-<id>.jsonl
```

**Qué observar:** el modelo recibe la ruta, sus tres aristas extraídas con cita y la arista inferida
marcada como tal. La traza JSONL guarda hops, nodos visitados y aristas recorridas, pero **no** la
pregunta, los nombres de la ruta ni la respuesta.

---

Siguiente paso: [EXERCISES.md](EXERCISES.md).
