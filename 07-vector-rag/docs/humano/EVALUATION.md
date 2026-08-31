# Evaluación

**Caso:** `I-RAG-VECTOR-005@0.1.0`

El fixture contiene escucha diagnóstica, venta sin presión, un método obsoleto, una sección
contaminada y venta remota.

```powershell
uv run vector-rag index --source .\fixtures\evaluation-corpus
uv run vector-rag search --mode lexical "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag search --mode vector "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag search --mode hybrid "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag ask "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag-validate
```

Criterios:

- Vector e híbrido recuperan `01-escucha.md` en top-5 para la paráfrasis.
- La sección sobre quarterback nunca se indexa.
- El método obsoleto no se presenta como vigente.
- La respuesta cita IDs existentes y las líneas contienen evidencia.
- El índice registra modelo, dimensiones y perfil exactos.
- La corrida no guarda texto crudo ni usa red cloud.

Métricas: ranking léxico/vectorial, coseno, fuentes recuperadas, caracteres de contexto, latencia,
tokens de prompt y salida. La comparación útil es recall@k y fidelidad, no solo velocidad.
