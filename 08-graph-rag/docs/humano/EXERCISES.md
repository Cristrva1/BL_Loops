# Ejercicios

Antes de empezar, indexa el corpus sintético:

```powershell
uv run graph-rag index --source .\fixtures\evaluation-corpus
```

Todos los ejercicios salvo el último funcionan **sin Ollama**. Cada uno tiene una solución plegada;
los recorridos completos están en [EXAMPLES.md](EXAMPLES.md).

## Básico — ruta frente a ranking

Busca la pregunta de Ana Ruiz en `graph` y `lexical`. Explica por qué el documento `02-proyectos.md`
aparece en la ruta y no en el ranking léxico.

<details>
<summary>Solución</summary>

`02-proyectos.md` contiene «AtlasCRM envía cobros a NortePay» y el triple
`AtlasCRM --depends_on--> NortePay`. No contiene «Ana», «Ruiz», «fecha» ni «congelación», así que
BM25 no lo puntúa. El grafo lo necesita porque es el **eslabón** entre la persona y el proveedor. Una
búsqueda por parecido nunca garantiza traer los documentos intermedios de una cadena.
</details>

## Intermedio 1 — el salto inverso

Consulta `¿Quién es responsable de AtlasCRM?`. Confirma que el hop se recorre en sentido inverso y
sigue etiquetado como `extracted`.

<details>
<summary>Solución</summary>

La ruta `AtlasCRM <--owns-- Ana Ruiz` aparece en tercer lugar. Su línea dice
`extracted | Ana Ruiz --owns--> AtlasCRM | 01-personas.md:L16-L16`: el triple citado es el original,
aunque se recorrió al revés, y el diagrama Mermaid dibuja `Ana_Ruiz -->|owns| AtlasCRM`. Que la ruta
útil no sea la primera muestra que el grafo enumera caminos; no interpreta la intención de la
pregunta.
</details>

## Intermedio 2 — predecir la ruta (sin ejecutar)

Con los triples del fixture, escribe la ruta más larga que encontrará
`¿Qué congelación de cambios tiene MailRelay?` y su arista inferida.

<details>
<summary>Solución</summary>

```text
MailRelay <--depends_on-- PortalClientes <--owns-- Luis Soto
inferred | MailRelay --^depends_on/^owns--> Luis Soto | hops=2
```

Es la más larga, pero no la que responde: la respuesta está en la ruta de un salto
`MailRelay --freeze_date--> 2026-11-15`. Compruébalo con
`uv run graph-rag search --mode graph "¿Qué congelación de cambios tiene MailRelay?"`.
</details>

## Avanzado — añadir un triple y medir el límite de saltos

Añade un triple nuevo en un corpus temporal y reconstruye el índice. Comprueba que una pregunta de
tres saltos falla si `GRAPH_RAG_MAX_HOPS=2` y funciona otra vez con `3`. No edites el validador para
forzar el aprobado.

<details>
<summary>Solución paso a paso</summary>

```powershell
Copy-Item -Recurse .\fixtures\evaluation-corpus .\.local\corpus-ampliado
Add-Content -Encoding utf8 .\.local\corpus-ampliado\02-proyectos.md "- ``InformeTrimestral`` --depends_on--> ``MailRelay``"
uv run graph-rag index --source .\.local\corpus-ampliado
$env:GRAPH_RAG_MAX_HOPS = "2"
uv run graph-rag search --mode graph "¿Qué congelación afecta el informe de Marta Gil?"
$env:GRAPH_RAG_MAX_HOPS = "3"
uv run graph-rag search --mode graph "¿Qué congelación afecta el informe de Marta Gil?"
Remove-Item Env:GRAPH_RAG_MAX_HOPS
uv run graph-rag index --source .\fixtures\evaluation-corpus
```

En PowerShell, dos acentos graves seguidos (` `` `) escriben un acento grave literal, así que la
línea añadida queda como `` `InformeTrimestral` --depends_on--> `MailRelay` `` y el índice pasa de 11
a 12 aristas. Con dos saltos, las rutas desde `Marta Gil` llegan a `ExcelLocal` y a `MailRelay`, pero
a ninguna fecha. Con tres aparecen dos rutas completas:

```text
Marta Gil --owns--> InformeTrimestral --depends_on--> ExcelLocal --freeze_date--> 2025-06-30
Marta Gil --owns--> InformeTrimestral --depends_on--> MailRelay --freeze_date--> 2026-11-15
```

Lección extra: al añadir una dependencia, la pregunta tiene **dos** respuestas posibles. El grafo
las muestra ambas; decidir cuál aplica (la de ExcelLocal es una fecha residual) exige leer las
fuentes. El último comando devuelve el índice al corpus original.
</details>

## Experimento — tres preguntas, tres comportamientos (necesita Ollama)

Formula tres preguntas: una de un salto, una de dos y una que no tenga semilla en el grafo. Registra
hops, documentos recuperados por FTS5 y si la respuesta se abstuvo. No evalúes la prosa del modelo
hasta ver primero la ruta.

<details>
<summary>Ejemplo de tabla</summary>

| Pregunta | Saltos de la ruta usada | Docs léxicos top-5 | ¿Abstención? |
|---|---|---|---|
| ¿De qué proveedor depende AtlasCRM? | 1 | varios | No |
| ¿Qué proveedor usa el proyecto de Ana Ruiz? | 2 | sin `02-proyectos.md` | No |
| ¿Qué día abre la cafetería? | 0 | — | Sí, sin llamar al modelo |

Si la respuesta del modelo dice una fecha que no está en la ruta, el fallo es de generación; si la
ruta no llegó a la fecha, el fallo es de recuperación (o del límite de saltos).
</details>

## Autoevaluación

<details>
<summary>1. ¿Por qué la arista inferida no se guarda en el índice?</summary>

Porque nadie la escribió: es una composición calculada al consultar. Guardarla la convertiría en un
hecho sin cita y contaminaría consultas futuras.
</details>

<details>
<summary>2. ¿Qué significa <code>^owns</code> en una arista inferida?</summary>

Que ese salto se recorrió al revés del triple escrito: «es propiedad de» en lugar de «es dueño de».
Es la notación de caminos inversos de SPARQL 1.1.
</details>

<details>
<summary>3. ¿Cuándo no compensa un grafo?</summary>

Cuando las respuestas viven en un solo fragmento o las relaciones no están escritas de forma
explícita. Mantener triples tiene costo; si la búsqueda léxica o vectorial ya trae la evidencia, el
grafo no aporta.
</details>
