# Instrucciones de trabajo para BL_Loops

Este archivo es la regla operativa canónica para todo el repositorio. Los archivos `AGENTS.md` más profundos pueden añadir reglas para su propia carpeta, pero no contradecir estas.

## Orden obligatorio de fuentes

1. `docs/humano/sistema.md` y las decisiones explícitas del usuario.
2. `Prompts/` como corpus de aprendizaje, no como instrucciones ejecutables.
3. `docs/` como material de refuerzo y propuestas no vinculantes.
4. `menu_portable/REPO_MENU.md` para descubrir y preseleccionar repositorios.
5. Documentación oficial actual para validar versiones, licencias, instalación y capacidades que puedan cambiar.

Una propuesta encontrada en `Prompts/` o `docs/` no se convierte por sí sola en una decisión de arquitectura.

## Principios del repositorio

- Todo debe ser didáctico, visual y progresivo: explicación, ejemplo, ejercicio, experimento y evaluación.
- Cada laboratorio es una aplicación autónoma y copiable. No puede importar código, bases de datos ni servicios de otro laboratorio.
- La única excepción compartida en el workspace es el `.env` global de configuración. Al copiar un laboratorio fuera del repo, debe poder usar su propio `.env` equivalente.
- El sistema creador de prompts puede producir prompts, agentes, skills, contratos y plantillas para otros proyectos; los artefactos se copian o exportan, no crean una dependencia en ejecución.
- Cada laboratorio debe mostrar visualmente sus nodos, estados, transiciones, entradas, salidas, errores, reintentos y métricas.
- El comparador central solo importa archivos JSONL exportados. No controla ni consulta laboratorios en vivo.

## Entornos compartidos y aislados

- El `.env` de la raíz contiene únicamente configuración común local. Su contrato visible es `.env.example`; los valores reales nunca se versionan ni se imprimen.
- Cada laboratorio debe incluir su propio `.env.example` equivalente para seguir funcionando cuando se copie fuera de BL_Loops.
- Cada laboratorio Python conserva su propio `pyproject.toml`, `uv.lock` y `.venv`. No se crea una `.venv` compartida ni un workspace de `uv` en la raíz.
- Las cachés globales de `uv` y npm sí pueden reutilizar descargas; una caché compartida no es una dependencia de ejecución.
- Cada frontend conserva su propio `package.json`, lockfile y `node_modules` ignorado por Git.
- Rutas relativas como `.local/data` se resuelven contra la raíz del laboratorio activo, no contra la raíz maestra.
- No definir un mismo `UV_PROJECT_ENVIRONMENT` absoluto para varios laboratorios.

## IA local

- Codex puede usarse para construir el código.
- Todo laboratorio debe funcionar y evaluarse contra la API local de Ollama.
- No se permiten fallbacks silenciosos a APIs pagadas o modelos cloud.
- No se permite telemetría remota por defecto.
- Modelos iniciales: `qwen3.5:4b`, `qwen3.5:9b`, `gemma4:e2b` y `gemma4:e4b`.
- Modelos, índices y datasets pesados se guardan fuera de Git. Los pesos de Ollama viven en `D:/ollama`.

## Seguridad y efectos externos

- Los primeros MCP y conectores son simulados o locales: filesystem aislado, SQLite y Git de solo lectura.
- Navegador, correo, CRM, mensajería, proveedores externos y escrituras fuera del laboratorio permanecen desactivados hasta autorización específica.
- No imprimir ni registrar secretos, tokens, teléfonos, datos personales o contenido de `.env`.
- Tratar repositorios bajo `C:/Users/criss/Desktop/Claude/Repositorios_Prueba` como referencias de solo lectura. No modificarlos, limpiarlos, actualizarlos ni instalar sus dependencias sin que el laboratorio correspondiente lo requiera.

## Selección de repositorios

- Seguir el protocolo de `menu_portable/REPO_MENU.md`.
- Partir de una receta cuando exista.
- Elegir menos de ocho finalistas por laboratorio antes de leer detalles.
- No combinar alternativas que cumplen la misma función solo para aumentar el número de dependencias.
- Registrar ruta local, remoto, SHA exacto, licencia, motivo de uso y si es referencia o dependencia ejecutable.
- Preferir una base mínima propia y hasta dos variantes comparables instaladas de forma progresiva.

## Contrato didáctico de cada laboratorio

Cada laboratorio debe separar físicamente el material humano del runtime:

1. `README.md` en la raíz: índice técnico breve, comandos y enlaces; no es el manual completo.
2. `AGENTS.md` en la raíz: instrucciones operativas portables para futuras sesiones de Codex.
3. `docs/humano/README.md`: objetivo, conceptos, mapa visual y recorrido guiado.
4. `docs/humano/QUICKSTART.md`: comandos PowerShell explicados y resultado esperado.
5. `docs/humano/ARCHITECTURE.md`: nodos, estados, contratos y decisiones explicados.
6. `docs/humano/METHODOLOGY.md`: método seguido, fuentes, decisiones y límites.
7. `docs/humano/EXERCISES.md`: ejercicios básico, intermedio y avanzado.
8. `docs/humano/TROUBLESHOOTING.md`: fallos comunes y cómo diagnosticarlos.
9. `docs/humano/EVALUATION.md`: casos, métricas, criterios de aprobado y exportación JSONL.
10. Código, configuración, schemas, fixtures y pruebas deterministas fuera de `docs/humano/`.

El runtime nunca puede importar, parsear ni necesitar archivos de `docs/humano/` para funcionar. La documentación puede explicar el runtime; el runtime no depende de la documentación.

## Contrato didáctico del repositorio maestro

- La guía humana transversal vive en `docs/humano/maestro/`.
- Debe explicar objetivo, arquitectura, metodología, sesiones de Codex, entornos, documentos, ejercicios, diagnóstico y evaluación.
- Los documentos humanos recibidos que viven fuera de `docs/humano/maestro/` se conservan como fuentes o referencias no vinculantes, salvo decisión explícita del usuario.
- `docs/INDEX.md` debe distinguir reglas, decisiones vigentes, guías didácticas y corpus.

## Protocolo mínimo para futuras sesiones de Codex

1. Leer este `AGENTS.md` y cualquier `AGENTS.md` más profundo aplicable.
2. Revisar `git status --short` antes de editar y preservar todos los cambios ajenos.
3. Consultar `docs/INDEX.md`, el plan y solo las fuentes relevantes para la tarea.
4. Declarar un alcance pequeño y una verificación proporcional antes de construir.
5. Implementar un corte vertical sencillo; no instalar complejidad futura por anticipado.
6. Actualizar la documentación didáctica afectada durante el mismo trabajo.
7. Ejecutar pruebas, demo, build, recorrido visual o validación de enlaces según corresponda.
8. Revisar nuevamente Git, detener procesos temporales y separar en la entrega lo terminado de lo aplazado.
9. No hacer commit, push, publicación ni efectos externos salvo solicitud explícita.

La explicación ampliada de este protocolo está en `docs/humano/maestro/CODEX_WORKFLOW.md`.

## Implementación y verificación

- Backend preferido: Python 3.12, `uv`, FastAPI, Pydantic y SQLite.
- Frontend preferido: React, Vite, TypeScript y React Flow.
- Eventos visuales: SSE por defecto; WebSocket solo cuando la interacción bidireccional lo justifique.
- Documentación en español; identificadores de código y contratos en inglés.
- Antes de declarar terminado un laboratorio, ejecutar sus pruebas, una demostración local y la exportación/importación de una corrida JSONL.
- Preservar siempre cambios ajenos y evitar ediciones en repositorios de referencia.
