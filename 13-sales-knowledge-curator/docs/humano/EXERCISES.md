# Ejercicios

## Básico · gobernanza editorial

1. Ejecuta la demo y comprueba que termina en `staging`, no en `published`.
2. Localiza `candidate-diff.json` y enumera claims incluidos y excluidos.
3. Intenta publicar con un hash alterado y explica el rechazo.
4. Publica con el hash exacto, valida el release y exporta el JSONL.

Resultado esperado: la disputa de precio, la inyección y la afirmación comercial sin método quedan
fuera; `current.json` solo cambia después de la aprobación posterior.

## Intermedio · documento autorizado

Usa un PDF o DOCX sintético creado por ti y un contrato de derechos que no permita redistribución
ni NotebookLM.

1. Impórtalo desde `.local/inbox`.
2. Compara el SHA-256 original del manifiesto con el archivo.
3. Revisa la advertencia de fidelidad y el localizador por líneas.
4. Intenta importar un archivo fuera del inbox y otro con proyección vacía.

Resultado esperado: el original no cambia; los dos casos inseguros fallan; el contenido privado no
adquiere permiso de redistribución por haber sido convertido.

Compara después `audit --extractor deterministic` con `audit --extractor ollama`. Fuerza una cuota
de chunks insuficiente y confirma que el sistema falla antes de solicitar inferencia y conserva un
JSONL `run.failed`.

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
