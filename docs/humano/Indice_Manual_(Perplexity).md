# Índice profesional del manual de Prompt, Context, RAG y Agent Engineering (edición 2026)

## 1. Introducción al manual
Presenta el propósito del documento, el perfil de lector ideal y la diferencia entre una guía de prompts aislados y un manual de ingeniería de sistemas con LLMs. También define por qué en 2026 el trabajo serio ya combina prompting, contexto, recuperación, herramientas, evaluación y arquitectura de agentes.[cite:5][cite:7]

## 2. Qué cambió en 2026
Explica el cambio de paradigma desde “prompt engineering” como técnica dominante hacia una visión más amplia donde el desempeño depende del contexto completo, el loop de ejecución, la memoria, los documentos recuperados y la verificación. Esta sección sirve para alinear expectativas y evitar que el lector siga usando recetas de 2023–2024 como si fueran suficientes.[cite:7][cite:15]

## 3. Fundamentos de los modelos de lenguaje
Introduce cómo predicen tokens, por qué responden de forma probabilística y qué implicaciones tiene eso para la precisión, consistencia y alucinación. Da la base para entender por qué pequeños cambios en instrucciones o contexto pueden alterar mucho el resultado.[cite:5][cite:10]

## 4. Anatomía de una instrucción efectiva
Descompone un prompt en rol, objetivo, contexto, restricciones, ejemplos, formato de salida y criterio de calidad. El objetivo es enseñar a diseñar instrucciones reproducibles y no depender de improvisación.[cite:5][cite:15]

## 5. Zero-shot prompting
Explica cómo pedir una tarea sin ejemplos previos, cuándo funciona bien y cuándo se queda corto. Es útil para prototipado rápido, tareas simples y casos donde el modelo ya conoce bien el patrón.[cite:5][cite:10]

## 6. Few-shot prompting
Cubre el uso de pocos ejemplos para enseñar el patrón deseado, especialmente en clasificación, extracción, normalización y tareas con formato estricto. También muestra cómo elegir ejemplos diversos para reducir sesgos y mejorar robustez.[cite:5][cite:10]

## 7. Many-shot prompting
Describe el uso de decenas o cientos de ejemplos dentro de ventanas de contexto largas, una práctica que ganó relevancia con modelos de gran contexto. Esta sección debe explicar beneficios, costos y el punto en que más ejemplos ya no aportan mejoras claras.[cite:5][file:1]

## 8. Role prompting y persona assignment
Explica cómo definir un rol funcional para activar lenguaje, prioridades y criterios de una disciplina concreta. También aclara que el rol sirve más cuando está conectado con tarea, contexto y estándar de salida, no como adorno genérico.[cite:5][file:1]

## 9. Prompting con formato estructurado
Aborda cómo forzar respuestas en JSON, tablas, esquemas o salidas tipadas para integraciones con software. En 2026 esto es central porque la utilidad empresarial depende mucho de la capacidad de producir salidas confiables y parseables.[cite:15][file:1]

## 10. Prompting para extracción y clasificación
Reúne patrones prácticos para extraer entidades, sentimientos, atributos, fechas, riesgos o campos específicos desde texto libre. Conviene incluir ejemplos empresariales porque es uno de los casos de uso más rentables y repetibles.[cite:5][cite:18]

## 11. Prompting para redacción y transformación de texto
Cubre tareas como resumir, traducir, reescribir, adaptar tono, simplificar, expandir o convertir formatos. Debe enseñar cómo controlar longitud, fidelidad, estilo y cobertura sin perder precisión.[cite:5][cite:15]

## 12. Prompting de razonamiento
Introduce la familia de técnicas donde el modelo realiza pasos intermedios antes de responder. Es importante explicar tanto su valor en tareas complejas como sus límites, porque no toda tarea mejora al forzar razonamiento explícito.[cite:5][file:1]

## 13. Chain-of-Thought y variantes
Desarrolla Chain-of-Thought, Zero-shot CoT, Auto-CoT y patrones afines. También debe incorporar evidencia crítica reciente sobre fallas de generalización para que el lector no trate esta técnica como una solución universal.[cite:5][file:1]

## 14. Self-consistency
Explica cómo muestrear varias trayectorias de razonamiento y decidir por mayoría o consistencia entre respuestas. Es útil cuando existe una respuesta verificable y el costo extra se justifica por la mejora en precisión.[cite:5][file:1]

## 15. Tree-of-Thought y Graph-of-Thought
Presenta técnicas de exploración deliberada de caminos de razonamiento para problemas con planificación, búsqueda o dependencia no lineal. Debe dejar claro que son valiosas en tareas específicas, pero no siempre son la opción más eficiente.[cite:5][file:1]

## 16. Program-of-Thought y uso de código
Explica cuándo conviene hacer que el modelo genere código o pasos computables para delegar cálculo a un intérprete. Es una técnica poderosa para tareas numéricas, simbólicas y financieras donde el error aritmético importa.[file:1][cite:5]

## 17. Self-refine, reflexión y revisión iterativa
Describe bucles donde el modelo genera, critica y corrige su propia salida. Esta sección es clave para explicar cómo mejorar calidad en redacción, código y análisis sin depender de una sola generación inicial.[file:1][cite:5]

## 18. Anti-patrones de prompting
Recoge errores comunes: instrucciones vagas, objetivos contradictorios, falta de formato, abuso de CoT, exceso de restricciones negativas y ejemplos mal elegidos. Su valor es práctico porque evita horas de prueba y error innecesarias.[file:1][cite:15]

## 19. System prompts
Introduce los mensajes de sistema como capa de comportamiento persistente para reglas, tono, políticas y prioridades. En producción, esta capa suele ser más importante que el prompt visible del usuario.[file:1][cite:15]

## 20. Context engineering
Define la disciplina de diseñar todo el entorno informacional del modelo: prompt, historial, documentos, memoria, herramientas, metadatos y orden de presentación. En 2026, esta capa se vuelve central porque la calidad depende más del contexto total que de una instrucción brillante aislada.[cite:7][cite:18]

## 21. Gestión del presupuesto de contexto
Explica cómo decidir qué información entra en la ventana, qué se resume, qué se elimina y qué se reinyecta más tarde. Esta sección conecta costo, latencia y calidad de respuesta.[cite:7][cite:18]

## 22. Orden, prioridad y pérdida en contexto largo
Analiza fenómenos como “lost in the middle”, saturación y degradación cuando el contexto crece demasiado. Debe enseñar estrategias de ordenamiento, repetición mínima y colocación de la consulta para maximizar atención útil.[file:1][cite:15]

## 23. Memoria de corto y largo plazo
Explica cómo almacenar y recuperar información de sesiones previas o pasos anteriores sin contaminar el contexto con ruido. También debe distinguir entre memoria conversacional, memoria de trabajo y memoria persistente.[cite:7][cite:18]

## 24. Herramientas y tool use
Describe cómo un LLM usa buscadores, bases de datos, APIs, calculadoras, navegadores o ejecutores de código. Esta sección es esencial para reducir alucinaciones y mover tareas fuera del puro texto predictivo.[file:1][cite:15]

## 25. ReAct
Presenta el patrón de razonamiento y acción intercalados para resolver problemas con observaciones externas. Conviene incluir tanto sus ventajas como la evidencia de fragilidad cuando el modelo razona mal o toma acciones inválidas.[file:1][cite:5]

## 26. RAG: fundamentos
Define Retrieval-Augmented Generation como el proceso de recuperar conocimiento externo antes de responder. Esta técnica sigue siendo fundamental para grounding factual, soporte documental y trabajo empresarial con bases propias.[file:1][cite:31]

## 27. RAG para producción
Cubre chunking, embeddings, indexing, reranking, filtros, citación, cobertura y control de relevancia. Debe mostrar que tener RAG no basta; el rendimiento depende de la calidad del pipeline y del diseño de recuperación.[cite:31][cite:18]

## 28. Agentic retrieval
Explica la diferencia entre recuperar fragmentos de forma estática y permitir que el agente recupere, reformule, valide y vuelva a consultar en varios pasos. Es una evolución importante para tareas complejas con preguntas ambiguas o multietapa.[cite:36][cite:7]

## 29. Configuración de agentes
Describe cómo definir objetivos, herramientas, permisos, memoria, instrucciones base, paradas y criterios de éxito de un agente. Es el puente entre un chatbot bien guiado y un sistema que realmente ejecuta trabajo.[cite:36][cite:18]

## 30. Loops de agentes
Introduce el ciclo observar, planear, actuar, verificar, registrar y continuar. En 2026, diseñar este loop correctamente es una de las diferencias más grandes entre demos atractivas y sistemas útiles.[cite:7][cite:36]

## 31. Harness engineering
Define la capa de orquestación que gobierna al agente: ejecución, herramientas, manejo de estados, errores, retries, sandbox, observabilidad y control de seguridad. Esta sección debe presentar el harness como arquitectura operativa, no como simple wrapper del modelo.[cite:42][cite:7]

## 32. MCP y protocolos de herramientas
Explica cómo estandarizar el acceso del modelo a herramientas y fuentes externas mediante interfaces consistentes. El objetivo es que el lector entienda interoperabilidad, seguridad y mantenibilidad en ecosistemas de agentes.[cite:42][cite:15]

## 33. Planificación y descomposición de tareas
Aborda cómo dividir objetivos complejos en subobjetivos verificables. Es especialmente importante en agentes, workflows empresariales y tareas largas de investigación o automatización.[cite:5][cite:42]

## 34. Flujos multiagente
Presenta arquitecturas donde varios agentes colaboran con roles distintos, por ejemplo investigar, planear, ejecutar y auditar. También debe tratar riesgos de complejidad, costo y coordinación defectuosa.[cite:7][cite:42]

## 35. Optimización automática de prompts
Explica cómo usar algoritmos, meta-prompts y búsqueda guiada por métricas para mejorar instrucciones sin depender solo de intuición humana. Esta sección conecta investigación reciente con prácticas de optimización aplicables.[cite:13][file:1]

## 36. DSPy y programación declarativa de LLMs
Desarrolla el enfoque de programar módulos, firmas y optimizadores en lugar de escribir prompts manuales aislados. En 2026, esto representa uno de los cambios más fuertes hacia pipelines medibles y reproducibles.[cite:9][cite:36]

## 37. Evaluación de prompts y sistemas
Explica cómo medir exactitud, consistencia, factualidad, cobertura, cumplimiento de formato, costo y latencia. Sin evaluación, no existe mejora real; solo preferencia subjetiva.[file:1][cite:18]

## 38. Benchmarks y métricas
Introduce benchmarks como MMLU, GSM8K, HumanEval, HotPotQA y otros relevantes, además de métricas como EM, F1, pass@k y format compliance. Esta sección debe enseñar a interpretar benchmarks sin sobreextender conclusiones a todos los casos de negocio.[file:1][cite:31]

## 39. LLM-as-a-judge
Describe el uso de modelos para evaluar salidas, comparar variantes y automatizar parte del control de calidad. También debe cubrir sus sesgos, fragilidad y necesidad de calibración humana.[file:1][cite:18]

## 40. Testing, regresión y experimentación
Cubre A/B testing, suites de prueba, validación continua y detección de regresiones después de cambiar prompts, contexto o herramientas. Es la base de un proceso serio de mejora continua.[file:1][cite:18]

## 41. Observabilidad y trazas
Explica cómo registrar entradas, contextos recuperados, decisiones del agente, herramientas llamadas, errores y resultados. Sin trazabilidad, diagnosticar fallos en sistemas con LLM se vuelve casi imposible.[cite:18][cite:36]

## 42. Costos, latencia y eficiencia
Analiza el impacto del tamaño del contexto, número de llamadas, reranking, reflexión y tool use sobre el costo total del sistema. Es una sección indispensable para decisiones reales de negocio.[cite:18][cite:15]

## 43. Seguridad, jailbreaks y aislamiento
Presenta riesgos como prompt injection, exfiltración de datos, uso inseguro de herramientas y escalamiento indebido de acciones. También debe cubrir sandboxing, permisos mínimos y separación de responsabilidades.[cite:42][cite:15]

## 44. Casos de uso empresariales
Aterriza el manual en escenarios como ventas, atención al cliente, soporte interno, análisis documental, marketing, legal, operaciones y programación. La función de esta sección es traducir teoría en ventajas de negocio concretas.[cite:18][cite:31]

## 45. Plantillas y patrones reutilizables
Compila prompts, system prompts, esqueletos de tareas, plantillas de extracción, análisis, auditoría, RAG y agentes. Debe funcionar como biblioteca práctica para uso diario.[file:1][cite:15]

## 46. Herramientas actuales del ecosistema
Presenta plataformas, frameworks y utilidades relevantes para 2026, incluyendo documentación viva, experimentación, observabilidad, optimización y despliegue. El enfoque debe estar en herramientas activas y con utilidad real en producción.[cite:15][cite:18][cite:9]

## 47. Repositorios recomendados
Lista repositorios valiosos para aprender, probar y construir, priorizando los bien mantenidos y con adopción visible. Conviene incluir guías, frameworks de programación declarativa, repos de prompting y ejemplos de agentes.[file:1][cite:9][cite:17]

## 48. Comunidades, fuentes y actualización continua
Explica dónde seguir aprendiendo: papers, documentación oficial, benchmarks, comunidades técnicas, repositorios activos y canales de discusión con señal alta. El objetivo es que el manual no envejezca como documento estático.[file:1][cite:5][cite:15]

## 49. Metodología para mantener el manual vivo
Define cómo revisar nuevas técnicas, validar si merecen entrar al manual, descartar modas y actualizar plantillas según evidencia. Esta sección convierte el manual en un sistema de aprendizaje continuo y no en una foto congelada del mercado.[cite:13][cite:7]

## 50. Apéndices
Incluye glosario, comparativas rápidas, tablas de decisión, checklists, matrices de cuándo usar cada técnica y bibliografía operativa mínima. Su función es facilitar consulta rápida para trabajo diario.[file:1][cite:5]

## Organización sugerida del libro
Para que el manual quede claro y profesional, esta sería una macroestructura recomendada:

1. Fundamentos del modelo y del prompting.
2. Técnicas de prompting y razonamiento.
3. Salidas estructuradas, herramientas y RAG.
4. Context engineering, memoria y gestión de contexto.
5. Agentes, loops, harness y protocolos.
6. Optimización, evaluación y observabilidad.
7. Producción, seguridad y negocio.
8. Plantillas, repositorios y sistema de actualización.

## Enfoque editorial recomendado
Cada capítulo puede seguir una estructura fija para volver el manual más útil en negocio y más fácil de mantener:

- Definición corta del concepto.
- Cuándo usarlo.
- Cuándo no usarlo.
- Beneficios esperados.
- Riesgos o limitaciones.
- Ejemplo práctico.
- Métricas de evaluación.
- Herramientas o repositorios relacionados.

Este formato ayuda a que el manual no sea solo teórico, sino operativo y accionable para implementación real.[cite:18][cite:15]
