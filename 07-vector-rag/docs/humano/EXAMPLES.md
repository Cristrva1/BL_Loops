# Ejemplos resueltos · RAG vectorial híbrido

> Los ejemplos 1 a 4 se ejecutan **sin Ollama** y su salida es exactamente reproducible: usan el
> filtro real del laboratorio, vectores de juguete y las constantes reales de la fusión. Los
> ejemplos 5 y 6 necesitan embeddings de Ollama: se muestra la forma esperada. Ejecuta todo desde
> `07-vector-rag`.

| # | Ejemplo | Concepto |
|---|---|---|
| 1 | El filtro de calidad | Higiene antes de buscar |
| 2 | Coseno con vectores de juguete | Cercanía de significado |
| 3 | Fusión RRF paso a paso | Combinar rankings sin igualar escalas |
| 4 | Recall@k a mano | Medir la recuperación antes de juzgar la respuesta |
| 5 | Tres modos, una paráfrasis | Dónde gana cada recuperador |
| 6 | El perfil durable | Por qué no se mezclan vectores |

---

## Ejemplo 1 · El filtro de calidad

```powershell
@'
from pathlib import Path
from vector_rag.quality import prepare_markdown

for ruta in sorted(Path("fixtures/evaluation-corpus").glob("*.md")):
    doc = prepare_markdown(ruta, ruta.read_text(encoding="utf-8"))
    print(f"{ruta.name}: estado={doc.source_status} secciones_excluidas={doc.excluded_sections} bloques={len(doc.blocks)}")
    for bloque in doc.blocks:
        print(f"    L{bloque.start_line}-L{bloque.end_line} [{bloque.heading}] {bloque.text[:70]}")
'@ | uv run python -
```

```text
01-escucha.md: estado=received secciones_excluidas=0 bloques=1
    L3-L3 [Diagnóstico consultivo] La escucha diagnóstica explora el contexto del comprador antes de ofre
02-presion.md: estado=received secciones_excluidas=0 bloques=1
    L3-L3 [Venta sin presión] Una relación sostenible prioriza aportar valor y permite que la person
03-obsoleto.md: estado=received secciones_excluidas=0 bloques=2
    L3-L3 [Guion histórico] **Estado:** obsoleto
    L5-L5 [Guion histórico] El guion antiguo recomienda presentar el producto antes de escuchar.
04-ruido.md: estado=received secciones_excluidas=2 bloques=0
05-digital.md: estado=received secciones_excluidas=0 bloques=1
    L3-L3 [Conversación remota] En una reunión virtual conviene confirmar atención, agenda y siguiente
```

**Qué observar:** `04-ruido.md` solo tiene secciones `Contexto (Wikipedia)` y `Temas (Open Library)`,
que la política excluye. Se queda sin bloques y **no se indexa**: por eso el índice dirá `4/5 docs`.
El filtro no decide qué es verdad: `03-obsoleto.md` se indexa con su marca «obsoleto» para que el
modelo la vea. Ningún recuperador, por bueno que sea, corrige un dato contaminado; solo lo encuentra
mejor.

## Ejemplo 2 · Coseno con vectores de juguete

Un embedding real tiene 768 números. Para entender la idea basta con 3 «dimensiones de significado»
inventadas: *escuchar*, *vender rápido* y *astronomía*.

```powershell
@'
import math

def coseno(a, b):
    punto = sum(x * y for x, y in zip(a, b))
    return punto / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))

pregunta = [0.9, 0.1, 0.0]   # "entender al comprador antes de ofrecer"
escucha = [0.8, 0.3, 0.0]    # 01-escucha.md
presion = [0.2, 0.9, 0.0]    # un texto de cierre agresivo
satelite = [0.0, 0.1, 0.95]  # un distractor astronomico
for nombre, vector in [("escucha", escucha), ("presion", presion), ("satelite", satelite)]:
    print(f"coseno(pregunta, {nombre}) = {coseno(pregunta, vector):.3f}")
'@ | uv run python -
```

```text
coseno(pregunta, escucha) = 0.969
coseno(pregunta, presion) = 0.323
coseno(pregunta, satelite) = 0.012
```

**Qué aprender:** el coseno mide el **ángulo** entre dos vectores: cerca de 1 si apuntan hacia el
mismo «significado», cerca de 0 si no tienen relación. No importan las palabras exactas, importa la
dirección. El laboratorio normaliza los vectores a longitud 1, así que el coseno se calcula como un
simple producto punto. En el spike real con `qwen3-embedding:latest` el pasaje pertinente obtuvo
0.587 y el distractor 0.092: los números reales son más modestos, pero la separación es la misma.

## Ejemplo 3 · Fusión RRF paso a paso

BM25 y coseno usan escalas distintas, así que no se pueden sumar. *Reciprocal Rank Fusion* usa solo
las **posiciones**: cada ranking aporta `peso / (60 + posición)`.

```powershell
@'
from vector_rag.index import LEXICAL_RRF_WEIGHT, VECTOR_RRF_WEIGHT

print(f"pesos RRF: lexico={LEXICAL_RRF_WEIGHT} vectorial={VECTOR_RRF_WEIGHT} k=60")
def rrf(posicion_lexica, posicion_vectorial):
    total = 0.0
    if posicion_lexica:
        total += LEXICAL_RRF_WEIGHT / (60 + posicion_lexica)
    if posicion_vectorial:
        total += VECTOR_RRF_WEIGHT / (60 + posicion_vectorial)
    return total

for nombre, lex, vec in [("A: 1.o lexico, 3.o vectorial", 1, 3), ("B: solo 1.o vectorial", None, 1),
                         ("C: solo 1.o lexico", 1, None), ("D: 2.o en ambos", 2, 2)]:
    print(f"{nombre:<28} RRF = {rrf(lex, vec):.5f}")
'@ | uv run python -
```

```text
pesos RRF: lexico=0.35 vectorial=0.65 k=60
A: 1.o lexico, 3.o vectorial RRF = 0.01606
B: solo 1.o vectorial        RRF = 0.01066
C: solo 1.o lexico           RRF = 0.00574
D: 2.o en ambos              RRF = 0.01613
```

**Qué aprender:**

- **D gana a A**: ser segundo en ambos rankings vale más que ser primero en uno y tercero en otro.
  La fusión premia el acuerdo entre recuperadores.
- **B gana a C**: el ranking vectorial pesa casi el doble (0.65 frente a 0.35), porque el corpus de
  ventas tiene muchas preguntas parafraseadas.
- La constante 60 suaviza la diferencia entre posiciones cercanas: pasar de 1.º a 2.º cambia poco.

## Ejemplo 4 · Recall@k a mano

Formulaste cinco preguntas y anotaste si el fragmento correcto aparecía entre los 5 primeros:

| Pregunta | Léxico | Vectorial | Híbrido |
|---|---|---|---|
| Literal 1 | sí | sí | sí |
| Literal 2 | sí | no | sí |
| Paráfrasis 1 | no | sí | sí |
| Paráfrasis 2 | no | sí | sí |
| Paráfrasis 3 | no | no | no |
| **recall@5** | **2/5 = 0.4** | **3/5 = 0.6** | **4/5 = 0.8** |

**Qué aprender:** recall@k mide la **recuperación**, no la redacción. Si el fragmento correcto no
llegó al contexto, ni el mejor modelo puede responder fielmente. Mide esto primero; juzga la
respuesta después. (Tabla ilustrativa: el ejercicio de [EXERCISES.md](EXERCISES.md) te pide construir
la tuya con preguntas reales.)

## Ejemplo 5 · Tres modos, una paráfrasis (necesita Ollama)

```powershell
uv run vector-rag index --source .\fixtures\evaluation-corpus
uv run vector-rag search --mode lexical "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag search --mode vector  "¿Cómo comprender sus prioridades sin lanzarme a vender?"
uv run vector-rag search --mode hybrid  "¿Cómo comprender sus prioridades sin lanzarme a vender?"
```

La línea del índice es determinista (solo depende del filtro y del troceado):

```text
Indice listo: 4/5 docs, 4 vectores, 2 secciones excluidas, 0 fuentes no revisadas.
```

Cada resultado de `search` tiene esta forma:

```text
1. 01-escucha.md:L3-L3 status=received lexical=<posición o -> vector=<coseno>
```

**Qué observar:** en modo `lexical` esta paráfrasis **no devuelve ningún resultado**: no comparte
palabras útiles con el corpus (se comprobó con el índice real). En `vector` e `hybrid` sí aparecen
fragmentos; `lexical=-` en una línea significa que FTS5 no encontró ese fragmento. Si `01-escucha.md`
aparece en `vector` e `hybrid`, acabas de ver exactamente el problema que justificó este laboratorio.
El caso de evaluación exige que ambos modos lo recuperen en el top-5.

## Ejemplo 6 · El perfil durable (necesita Ollama)

```powershell
uv run vector-rag stats
$env:VECTOR_RAG_EMBEDDING_DIMENSIONS = "1024"
uv run vector-rag search --mode vector "necesidad real"
Remove-Item Env:VECTOR_RAG_EMBEDDING_DIMENSIONS
```

Salida esperada (el mensaje de error es exacto; se comprobó contra el índice real del laboratorio):

```text
Indice: 4 docs, 4 vectores de 768d, 2 secciones excluidas.
Operacion fallida: El indice no coincide con el perfil de embeddings configurado.
```

**Qué aprender:** un índice queda atado al modelo, la dimensión y la instrucción de consulta con que
se construyó. Comparar un vector de 1024 números con otros de 768 no tiene sentido, así que el
laboratorio **falla cerrado** en lugar de devolver resultados basura. Para cambiar el perfil se
reconstruye el índice completo.

---

Siguiente paso: [EXERCISES.md](EXERCISES.md).
