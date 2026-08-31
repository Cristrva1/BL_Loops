# RAG vectorial e híbrido, paso a paso

## Por qué existe

El RAG léxico es suficiente para búsquedas con palabras exactas y para este volumen. Falló, sin
embargo, cinco preguntas parafraseadas de ventas. Un spike local separó claramente un pasaje
semánticamente relevante de un distractor. También reveló que varias fichas contienen secciones de
Wikipedia ajenas al libro.

Por eso este laboratorio resuelve dos problemas distintos:

1. **Recall semántico:** encontrar ideas aunque cambien las palabras.
2. **Higiene:** no indexar secciones contaminadas ni fichas que solo contienen metadatos.

```mermaid
flowchart LR
    M[Markdown] --> Q[Filtro de secciones]
    Q --> C[Fragmentos citables]
    C --> F[(FTS5)]
    C --> E[Ollama embed]
    E --> V[(Vectores SQLite)]
    P[Pregunta] --> LF[Ranking léxico]
    P --> VF[Ranking coseno]
    F --> LF
    V --> VF
    LF --> R[Fusión RRF]
    VF --> R
    R --> G[Ollama chat + citas]
```

Sigue [QUICKSTART.md](QUICKSTART.md), después compara modos con
[EVALUATION.md](EVALUATION.md).
