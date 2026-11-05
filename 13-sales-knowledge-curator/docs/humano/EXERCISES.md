# Ejercicios

Cada ejercicio tiene una solución o pista plegada. El básico funciona sin red ni Ollama y su
recorrido completo, con salidas reales, está en [EXAMPLES.md](EXAMPLES.md).

## Básico · gobernanza editorial

1. Ejecuta la demo y comprueba que termina en `staging`, no en `published`.
2. Localiza `candidate-diff.json` y enumera claims incluidos y excluidos.
3. Intenta publicar con un hash alterado y explica el rechazo.
4. Publica con el hash exacto, valida el release y exporta el JSONL.

Resultado esperado: la disputa de precio, la inyección y la afirmación comercial sin método quedan
fuera; `current.json` solo cambia después de la aprobación posterior.

<details>
<summary>Solución</summary>

1. La demo imprime `state=staging` y un `candidate_hash`.
2. `candidate_diff` (también en `.local/data/releases/<release>/candidate-diff.json` tras publicar)
   incluye `clm-ask-budget`, `clm-discovery-duration` y `clm-sunday-close`, y excluye las otras seis.
3. Con un hash inventado: `error: El hash aprobado no coincide con el candidato actual`. La aprobación
   es de una versión exacta, no de «el release» en abstracto.
4. `release publish` con el hash correcto → `state=published`; `validate` → `"valid": true`;
   `export-run` → `"terminal_event": "run.completed"`.

La tabla del [ejemplo 3](EXAMPLES.md#ejemplo-3--nueve-afirmaciones-seis-estados) explica por qué
cada afirmación tiene su estado.
</details>

## Básico 2 · detectar una manipulación

1. Publica y valida un release como en el ejercicio anterior.
2. Añade una línea cualquiera a `.local/data/releases/<release_id>/knowledge/closing.md`.
3. Vuelve a ejecutar `uv run sales-curator validate --release <release_id>`.

<details>
<summary>Solución</summary>

`validate` responde `"valid": false` con `"hash alterado: knowledge/closing.md"`. Cada archivo del
release tiene su huella en el manifiesto; cambiar un byte rompe la verificación. Para corregirlo no
se edita el manifiesto: se repite el proceso editorial y se publica un release nuevo.
</details>

## Intermedio · documento autorizado

Usa un PDF o DOCX sintético creado por ti y un contrato de derechos que no permita redistribución
ni NotebookLM.

1. Impórtalo desde `.local/inbox`.
2. Compara el SHA-256 original del manifiesto con el archivo.
3. Revisa la advertencia de fidelidad y el localizador por líneas.
4. Intenta importar un archivo fuera del inbox y otro con proyección vacía.

Resultado esperado: el original no cambia; los dos casos inseguros fallan; el contenido privado no
adquiere permiso de redistribución por haber sido convertido.

<details>
<summary>Pista</summary>

Los comandos exactos de importación y el formato del contrato de derechos están en
[QUICKSTART.md](QUICKSTART.md) y en `examples/document-rights.example.json`. La idea a demostrar es
que **convertir** un documento a Markdown no cambia sus derechos: si el contrato dice
`redistribution_allowed: false`, el paquete NotebookLM debe excluirlo.
</details>

Compara después `audit --extractor deterministic` con `audit --extractor ollama`. Fuerza una cuota
de chunks insuficiente y confirma que el sistema falla antes de solicitar inferencia y conserva un
JSONL `run.failed`.

## Avanzado · loop de biblioteca

1. Inventaría `fixtures/library` y comprueba que `Libros.md` no entra.
2. Lanza `library research` con presupuesto y jurisdicción explícitos.
3. Verifica que *Influence* queda en `dossier_ready` sin PDF y *Pride and Prejudice* puede
   adquirir copia solo si el catálogo simulado o real marca descarga legal.
4. Exporta con `--authorize-export` a una carpeta temporal y confirma que no hay `.pdf`.
5. Intenta exportar sin `--authorize-export` y registra el rechazo.

Resultado esperado: el loop enriquece fichas y no persigue PDFs comerciales.

<details>
<summary>Por qué Influence no obtiene PDF</summary>

Es una obra comercial vigente: los catálogos pueden ofrecer ficha, vista previa o préstamo, pero no
`full_download` con derechos elegibles. *Pride and Prejudice* es de dominio público, así que un
catálogo puede marcar descarga legal. La diferencia no la decide el título ni la popularidad, sino la
evidencia de derechos de cada oferta.
</details>

## Avanzado · investigación multifuente

Con jurisdicción y allowlist explícitas:

1. Investiga el mismo título en Open Library y Google Books.
2. Clasifica cada oferta como catálogo, lectura, preview, préstamo o descarga completa.
3. Desactiva uno de los tres gates de red y confirma que no hay solicitud.
4. Reduce el presupuesto para que una rama falle y verifica que el reporte conserva la advertencia.
5. Exporta los paquetes NotebookLM y RAG; demuestra que no contienen texto de un libro restringido.

Resultado esperado: una coincidencia bibliográfica no se presenta como copia legal y un fallo de
proveedor no borra los resultados trazables del otro.

## Experimento de navegador

En un host que permita automatización, intenta una ruta permitida y otra denegada por
`robots.txt`. Después simula o prueba un redirect fuera de allowlist.

Resultado esperado: solo la primera captura produce Markdown/manifiesto; las otras se detienen
antes de persistir evidencia utilizable.
