# Metodología: 23-remotion-superpowers-studio

## Pregunta de partida

¿Qué gana un agente si, en lugar de «hacer un video», rellena datos que un programa de video ya
sabe dibujar? Este laboratorio lo prueba con Remotion: el modelo propone texto y colores, Python
calcula fotogramas y React dibuja cada fotograma a partir de su número.

## Fuentes y su papel

| Fuente | Dónde | Papel | Registro |
|---|---|---|---|
| Remotion 4.0.523 | `https://github.com/remotion-dev/remotion`, paquetes `remotion`, `@remotion/cli`, `@remotion/transitions` | Dependencia ejecutable (`package-lock.json`) | Licencia propia de Remotion: gratuita para personas, empresas con hasta 3 empleados, organizaciones sin ánimo de lucro y evaluación; licencia de empresa para el resto. Texto en `node_modules/remotion/LICENSE.md` |
| Remotion Superpowers | `https://github.com/DojoCodingLabs/remotion-superpowers` | Referencia conceptual del patrón «el agente edita datos, el motor renderiza» | No se instala ni se copia código; licencia no verificada en este laboratorio |
| React 19 y TypeScript 5 | `package-lock.json` | Composición y comprobación de tipos | Licencias MIT y Apache-2.0 |
| FFmpeg / ffprobe | Instalación local | Medición | — |
| Ollama | `http://127.0.0.1:11434` | Contenido de las escenas | Modelos iniciales del repositorio |

## Decisiones y por qué

1. **Fotogramas enteros como unidad.** Remotion trabaja con fotogramas `0, 1, 2…`; el estudio
   traduce segundos a fotogramas una sola vez, en Python, y React nunca mide el tiempo real.
2. **El modelo rellena datos, no escribe código.** `scenes.json` tiene un esquema fijo; React escapa
   el texto y los estilos pasan por una lista blanca.
3. **Contrato honesto del brief.** `Root.tsx` fija 1920×1080 a 30 fps; el brief solo admite esos
   valores, para que el cálculo de Python y el render no puedan discrepar.
4. **Fallback visible.** Sin Ollama, escenas calibradas marcadas como `fallback` en terminal, eventos,
   panel y JSONL.
5. **Sin telemetría.** Remotion solo registra uso cuando se configura una `licenseKey` (se comprobó en
   el código de `@remotion/renderer` 4.0.523); el laboratorio no la configura.
6. **Medir, no suponer.** Duración, fps y fotogramas se leen con `ffprobe`; sin medición, ceros.

## Cómo se verificó

- 21 pruebas deterministas (`uv run pytest`): configuración, contrato del brief (modelo cloud, fps,
  duración), fallback visible, cálculo de fotogramas, estilos validados en `scenes.json`, 409/422 y
  medición sin pista de video.
- `npm run typecheck` sin errores (requería `resolveJsonModule`, añadido en `tsconfig.json`).
- Demo completa con render real de Remotion: 12,0 s, 1920×1080, 30 fps, 360 fotogramas.
- Fotogramas sueltos con `npx remotion still` para comprobar el ejercicio avanzado.

## Límites conocidos

- La división entera de fotogramas puede perder hasta 3 fotogramas (ejercicio intermedio).
- Dos renders iguales no producen archivos idénticos byte a byte (2646,45 KB frente a 2644,73 KB en
  la verificación), aunque coinciden contenido y duración.
- `@remotion/transitions` está instalado pero no se usa.
- La calidad del guion depende del modelo; no hay un juez automático de contenido.
