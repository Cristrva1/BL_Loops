# Ejercicios del repositorio maestro

Los ejercicios enseñan a orientarse, diseñar y verificar sin depender de una IA cloud ni modificar repositorios de referencia.

## Nivel básico — Clasificar archivos

### Objetivo

Distinguir documentación humana, decisión, runtime y estado generado.

### Actividad

Clasifica estas rutas:

```text
AGENTS.md
docs/PLAN_MAESTRO_DIDACTICO.md
docs/humano/sistema.md
01-prompt-agent-factory/backend/src/
01-prompt-agent-factory/docs/humano/ARCHITECTURE.md
01-prompt-agent-factory/.local/exports/
```

### Resultado esperado

| Ruta | Clasificación |
|---|---|
| `AGENTS.md` | Regla operativa |
| Plan maestro | Decisión transversal |
| `sistema.md` | Fuente humana primaria |
| `backend/src` | Runtime |
| Arquitectura del laboratorio | Enseñanza humana |
| `.local/exports` | Estado generado, ignorado por Git |

### Aprobado

Puedes explicar por qué el runtime nunca debe importar ninguno de los dos documentos humanos.

## Nivel intermedio — Diseñar un laboratorio mínimo

### Objetivo

Convertir una pregunta educativa en una estructura pequeña.

### Actividad

Elige la pregunta:

> ¿Cuándo debe un agente detenerse sin llamar otra vez al modelo?

Escribe, sin implementar todavía:

1. Una entrada sintética.
2. Tres estados visibles.
3. Una condición de parada.
4. Un error intencional.
5. Una métrica.
6. Los archivos mínimos necesarios.
7. Los documentos humanos que actualizarías.

### Restricción

No puedes añadir una base de datos, un framework multiagente ni SSE salvo que justifiques qué observación concreta permiten.

### Aprobado

Tu propuesta cabe en un corte vertical y separa claramente runtime y aprendizaje.

## Nivel avanzado — Auditar independencia

### Objetivo

Demostrar que un laboratorio es copiable.

### Actividad

En una copia temporal fuera de BL_Loops:

1. Copia un único laboratorio.
2. Crea su `.env` desde `.env.example`.
3. Ejecuta `uv sync --all-groups`.
4. Ejecuta pruebas y demostración.
5. Comprueba que no busca rutas de otro laboratorio.
6. Registra qué artefactos genera dentro de su `.local`.

No realices esta prueba sobre una carpeta con cambios no preservados.

### Aprobado

La copia funciona sin importar código, bases o servicios de BL_Loops, excepto Ollama local y la configuración que acabas de copiar.

## Experimento — `.venv` aislada frente a entorno compartido

### Hipótesis

Una `.venv` por laboratorio conserva reproducibilidad; una común introduce cambios cruzados.

### Diseño seguro

No contamines proyectos reales. Crea dos proyectos sintéticos temporales con dependencias incompatibles, sincroniza cada uno en su `.venv` y compara:

- `sys.prefix`.
- Versiones instaladas.
- Lockfiles.
- Resultado después de actualizar solo uno.

### Reflexión

Responde:

1. ¿Qué ahorro ofrece la caché de `uv` aunque existan dos entornos?
2. ¿Qué evidencia perderías si ambos proyectos usaran una ruta absoluta común?
3. ¿Por qué un entorno compartido contradice la autonomía de BL_Loops?

## Autoevaluación

Marca cada afirmación solo si puedes demostrarla:

- [ ] Sé qué documento tiene autoridad sobre una propuesta del corpus.
- [ ] Sé dónde debe vivir un tutorial y dónde un schema ejecutable.
- [ ] Sé preparar un laboratorio sin crear una `.venv` raíz.
- [ ] Sé explicar qué comparte el `.env` y qué no comparte.
- [ ] Sé definir una verificación antes de implementar.
