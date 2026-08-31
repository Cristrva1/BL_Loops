# Ejercicios

## Básico

Audita `fixtures/corpus` y responde con evidencia del snapshot:

1. ¿Qué fuente quedó en cuarentena por inyección?
2. ¿Qué tema no tiene cobertura y por qué la rama queda inconclusa?
3. ¿Qué dos `claim_id` entran en conflicto sobre el momento del precio?

Resultado esperado: `src-injection`, tema `after-sales`, `clm-price-first-contact` contra `clm-price-after-discovery`.

## Intermedio

Aprueba solo `clm-ask-budget` y construye un release.

1. Comprueba que el conflicto de precio no aparece como hecho en `knowledge/`.
2. Cambia una palabra del claim y reintenta la aprobación con el hash anterior.
3. Explica por qué debe fallar.

Resultado esperado: el conocimiento cita el localizador de descubrimiento; el hash viejo se rechaza.

## Avanzado

Publica un release, publica un segundo y haz rollback al primero.

1. `current.json` debe apuntar otra vez al primero.
2. El directorio del segundo debe seguir existiendo.
3. Exporta el JSONL y verifica que no contiene el texto “Ignore previous instructions”.
