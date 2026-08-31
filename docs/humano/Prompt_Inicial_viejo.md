Quiero construir una metodología de trabajo, con el fin de construir sistemas, proyectos, repositorios, apps web, etc… con apps de modelos llm de ia de codigo (codex, claude code, grok, ollama ia local), hardware cpu: amd ryzen 7 5800x 3d, ram: 32 gb de ram 3200mhz, disco duro: ssd nvme samsung 990 pro 2tb, gpu: Nvidia RTX 5060ti 16gb vram, windows 11 pro.

La metodología debe de tener el mejor equilibrio entre una metodología de grado empresarial, para crear sistemas robustos y seguros vs la metodología más eficiente para construir con modelos llm de código.

Declara estos modelos como disponibles, tengo suscripción 5x de Anthropic Claude Code con Sonnet 5 (High, xHigh, Max), Opus 5 (High, xHigh, Max, Ultracode), Fable (High, xHigh, Max, Ultracode) y suscripción 5x de OpenAI Codex con ChatGpt Sol (High, xHigh, Max, Ultra), Terra (High, xHigh, Max, Ultra), Luna (High, xHigh, Max, Ultra) y suscripción de Supergrok de xAI con GrokBuild Grok 4.6 (High, xHigh). Ordena según consumo de tokens, benchmark, nivel de aciertos programando, analizando arquitectura, depurando, refactorizando, orquestando agentes, planeando, nivel y capacidad, nivel de coding, nivel de contexto, reasoning, thinking, code review, etc.... 

También se puede hacer uso de ia local con ollama o cualquier servicio.

Declara todas las métricas sobre consumo de tokens, costos, capacidades nivel de inteligencia y demás información sobre cada uno de los modelos y sus niveles de esfuerzo, etc… toda la información que tenga el documento, todo como verdad, no hace falta conducir investigación propia. (Aclaración: Anthropic nivel de esfuerzo ultracode, OpenAi nivel de esfuerzo Ultra).

Mi objetivo es aprovechar la capacidad multi agente de cada app y modelo según su capacidad, proveedor y nivel de esfuerzo, todo esto con la capacidad de generar skills que puedan usar el cli para invocar a otro agente de otro proveedor (ej: utilizando grok se usa una skill para usar vía CLI Codex o Claude, lo mismo con Claude o Codex, los 3 tienen skill para llamar por cli a los otros 2 (6 skills), en el caso de Claude Code hay un plugin de codex oficial y un plugin de grok no oficial funcional.

Tengo pensado usar algún modelo de anthropic o OpenAI con el nivel de esfuerzo necesario para implementar todo este plan y otro para empezar la implementación para que construya  todos los documentos que se tiene que actualizar, crear, configurar, eliminar, limpiar y/o afinar, arreglar todo (usando agentes claro). Creación de prompts, agentes, skills, roadmap, etc…

Además de usar Anthropic o OpenAi como roquestador para inicio de sesiones.

Necesitamos mezclar procesos entre orquestación y workers, donde todos participen (el orquestador no tiene que ser solo orquestador, también puede hacer work) para utilizar al máximo, pero evitar ventanas de contexto largas o trabajos por largos periodos de tiempo o algo mas que haga alucinar al agente o hacer que el agente escriba outputs incompletos.

Una metodología final muy optimizada usando los modelos correctos en su tarea correcta con el nivel de esfuerzo correcto, una orquestación de agentes ordenada, entre agentes propios de la app de orquestación y el cli y los agentes que liebre el cli. Trabajando en paralelo, algunos adelantando trabajo, otros revisando trabajo ya hecho, y otro realizando trabajo o pruebas. 

Hay que estandarizar usando agents y skills versátiles para que cualquiera de los 3 proveedores los pueda usar en cualquier sesión y modelo, intervención humana para la toma de decisiones difíciles, decisiones que afecten algún sistema o mensaje con contacto humano (asesores, clientes, directores), cambios de arquitectura y otros temas que propongas, de ahi en mas el flujo debe ser friendly user (para usuario con conocimiento bajo/básico) y dejar a los agentes hacer todo (actualmente se usa una /skill “/abrir-sesion”, “cerrar-sesion” para los inicios de trabajo y al finalizar el trabajo, para asegurar el correcto encarrilamiento del branch, head, flujo de trabajo, trabajo terminado, handoff, etc…) pero el humano solo invoca al principio la skill, resuelve cualquier duda, todo el agente ya sabe que hacer y procede a trabajar automáticamente, termina y el humano escribe cerrar sesión (incluso hasta cerrar sesion se podría quitar.

Por favor evita cuellos de botella y exceso de pruebas y niveles de autorización, sin tanta copia física, worktrees, release. cutover difíciles, pruebas CI. Aunque nada de esto está prohibido, si es necesario se crea copia física, release, cutover, fallback, worktree, branch, etc…

El objetivo es evitar falsos positivos, grandes ramas de trabajos, o trabajos con herencia de errores conduciendo a ninguna parte, necesitamos avanzar rápido sin tanto control empresarial, tener varios trabajos en paralelo, multi agentes y multi cli. Quiero usar todo lo que esté al alcance y sacar el máximo provecho de mis suscripciones,  evitar alucinaciones, optimizar los modelos para que hagan el mejor trabajo posible con el esfuerzo adecuado. Poder usar muchos agentes para trabajar en paralelo (agentes propios de la app y agentes en CLI), revisión, pruebas, etc… y avanzar en grande en mi proyecto.

Algunos modelos pueden avanzar en fases futuras construyendo o adelantando trabajo avanzando fases completas, sistemas, módulos, herramientas, o cualquier sistema para posteriormente en un futuro solo hacer la conexión y pruebas, o también, se puede hacer que todos los modelos y agentes trabajen en la misma fase para acabar rápido, 

Es indispensable definir qué puede haber agentes que solo planean o solo supervisen o compartan tareas, otros como asistente actualizando archivos, otros revisando trabajos, haciendo pruebas, test, etc… Hay muchos trabajos y tenemos mucha capacidad y muchos modelos. Pero es necesario conocer los límites de los modelos y de los clientes, conexiones, agentes, plugins, mcp, skills, y cada componente en la metodología. Además de conocer y definir los limites de cada modelo.

Analiza las skills que creo codex para Para ajustarse y afinarse a la metodología y el uso de los modelo y esfuerzo según el proveedor (Anthropic, Opena AI, xAi) y tarea o workflow:  
“””

1. Conexión de Claude con Grok, Invocación vía CLI de Grok en Claude Code.  
2. Conexión de Grok con Claude Code, Invocación vía CLI de Claude en Grok Build  
3. Conexión de Codex con Grok, Invocación vía de CLI de Grok en Codex.  
4. Conexión de Grok con Claude Code, Invocación vía de CLI de Grok en Codex.  
5. Conexión de Claude con Codex, Invocación vía de CLI de Grok en Codex.  
6. Conexión de Codex con Claude, Invocación vía de CLI de Grok en Codex.

“””

Revisa bien todo, hay muchas cosas que considerar y desenredar para que fluya el trabajo.

Es fundamental que todos los outputs emitidos por los agentes para agentes sean optimizados, tambien todos los ouptus de los agentes hacia el humano con excepción de cuando se tenga que tomar una decisión humano ahi si hay que explicar bien todo. Entender el ahorro de tokens en outputs innecesarios explicando cosas, solo vale la pena cuando el humano tiene que tomar una decisión ahí se tiene que tomar en cuenta que el humano tiene un nivel bajo/básico de conocimiento sobre programación y elementos de la metodología. En cada inicio de sesión recomienda el modelo y nivel de esfuerzo para el trabajo (tiene que ser del mismo proveedor donde se abrió la sesión).

Para cada inicio de sesión, para cada tarea, para todo,  es necesario definir modelo de ia y nivel de esfuerzo recomendado.

