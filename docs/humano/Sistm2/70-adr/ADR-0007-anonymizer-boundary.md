# ADR-0007 — El Anonymizer como frontera obligatoria antes de la memoria semántica global

> **Status**: `accepted` | Fecha: 2026-05-07 | Autores: equipo de diseño

---

## Contexto

El sistema aprende de las interacciones de todos los usuarios (memoria semántica global). Sin embargo, los datos de los usuarios son privados y no deben cruzar la frontera individual sin anonimización. Se necesita un mecanismo formal y obligatorio que garantice que ningún dato con PII llegue a la memoria semántica.

---

## Decisión

**Establecemos el Anonymizer como frontera arquitectónica obligatoria** entre la memoria episódica (per-usuario, con PII) y la memoria semántica global (anonimizada). Esta frontera es:

- **Código**: una función/servicio que verifica activamente la ausencia de PII antes de permitir el paso.
- **Arquitectónica**: ningún módulo puede escribir en `semantic_memory` sin pasar por el Anonymizer.
- **Verificable**: el campo `anonymized = TRUE` en la tabla `semantic_memory` solo lo pone el Anonymizer, no los módulos llamantes.

**El Anonymizer vive en el User Profiler**, no en el Pattern Miner. Es responsabilidad del origen garantizar la anonimización, no del destino.

---

## Lo que el Anonymizer verifica

1. Sin `tenant_id` en los datos que pasan.
2. Sin nombres propios de personas (heurística + modelo NER liviano).
3. Sin emails, teléfonos, direcciones.
4. Sin identificadores únicos que permitan re-identificación.
5. Que el contenido es una señal de comportamiento (patrón), no un texto completo de petición/respuesta.

---

## Consecuencias positivas

- **Privacidad by design**: PII nunca llega a la memoria global por construcción, no por disciplina.
- **GDPR simplificado**: si un usuario solicita borrado, se elimina su perfil y su memoria episódica. La memoria semántica no necesita modificarse (no contiene datos individuales).
- **Confianza en el aprendizaje**: los patrones que aprende el sistema son de comportamiento agregado, no de individuos.
- **Auditable**: el campo `anonymized` en la tabla es evidencia de que el proceso se ejecutó.

---

## Consecuencias negativas

- **Pérdida de señal**: la anonimización puede reducir la riqueza de la señal que llega al Pattern Miner.
- **Latencia adicional**: el proceso de verificación de PII agrega latencia al flujo de escritura semántica.
- **Falsos positivos en detección de PII**: el modelo NER puede marcar como PII datos que no lo son, reduciendo el volumen de señales.

---

## Alternativas consideradas

| Alternativa | Razón de rechazo |
|---|---|
| Anonimizar en el Pattern Miner | Desplaza la responsabilidad al destino; el origen puede olvidar la obligación |
| Confianza en los módulos (sin frontera formal) | No auditable; un bug en cualquier módulo puede filtrar PII |
| Datos de entrenamiento separados (sin memoria global) | Elimina la capacidad de aprendizaje continuo de la arquitectura |
| Federated learning | Complejidad técnica muy alta; fuera de scope en fases iniciales |

---

## Revisión

Esta decisión **no se revisará** en cuanto a la obligatoriedad del Anonymizer. Lo que sí puede revisarse es la implementación del detector de PII (mejorar el modelo NER, añadir reglas adicionales) a medida que se tienen más datos sobre falsos positivos y negativos.
