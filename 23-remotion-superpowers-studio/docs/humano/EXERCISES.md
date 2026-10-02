# Ejercicios Didácticos: 23-remotion-superpowers-studio

## Ejercicio Básico: Ajuste de la Curva de Resorte (Spring Physics)
- **Objetivo**: En `src/video_composition/SceneSequence.tsx`, modificar la configuración del resorte (`damping`, `mass`, `stiffness`) para crear una entrada más elástica (tipo "bouncy").
- **Verificación**: Abrir `npm run dev` en el navegador y comprobar visualmente el rebote de la tarjeta al entrar.

## Ejercicio Intermedio: Transición con `@remotion/transitions`
- **Objetivo**: Incorporar el componente `<TransitionSeries>` del paquete `@remotion/transitions` entre las escenas en `MainComposition.tsx` (por ejemplo, `fade()` o `slide()`).
- **Verificación**: Renderizar el video con `uv run remotion-studio-demo` y constatar la transición suave de fundido cruzado entre planos.

## Ejercicio Avanzado: Efecto de Tipografía Cinética (Typewriter)
- **Objetivo**: Implementar un efecto de máquina de escribir para el titular de cada escena usando `subheadline.slice(0, Math.floor(frame / 2))` en función del fotograma actual.
- **Verificación**: Observar que las letras aparecen secuencialmente conforme avanza la reproducción.
