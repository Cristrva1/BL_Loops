"""Generador de composiciones HTML para HyperFrames."""

from hyperframes_studio.schemas import SceneSpec, VideoBrief


def generate_hyperframes_html(brief: VideoBrief, scenes: list[SceneSpec]) -> str:
    """Construye un documento HTML válido según las especificaciones de HyperFrames."""
    total_duration = sum(s.duration for s in scenes)
    width = brief.width
    height = brief.height

    scenes_html = []
    gsap_tweens = []

    for idx, scene in enumerate(scenes):
        snippet_html = ""
        if scene.code_snippet:
            snippet_html = f"""
            <div class="code-box">
              <span class="code-dot red"></span>
              <span class="code-dot yellow"></span>
              <span class="code-dot green"></span>
              <pre><code>{scene.code_snippet}</code></pre>
            </div>
            """

        scene_markup = f"""
        <div id="{scene.id}" class="clip scene-card"
             data-start="{scene.start_time}"
             data-duration="{scene.duration}"
             data-track-index="1"
             style="background: {scene.bg_gradient};">
          <div class="scene-content">
            <div class="scene-header">
              <span class="badge" style="background: {scene.accent_color}22; color: {scene.accent_color}; border-color: {scene.accent_color}66;">
                {scene.badge_text}
              </span>
              <span class="step-indicator">Paso {idx + 1} de {len(scenes)}</span>
            </div>
            <h1 class="headline" style="--accent: {scene.accent_color};">{scene.headline}</h1>
            <p class="body-text">{scene.body}</p>
            {snippet_html}
          </div>
        </div>
        """
        scenes_html.append(scene_markup)

        # GSAP animations for each scene
        t_start = scene.start_time
        gsap_tweens.append(
            f"""
        // Animación para {scene.id}
        tl.from("#{scene.id} .scene-content", {{
          opacity: 0,
          y: 40,
          scale: 0.96,
          duration: 0.6,
          ease: "power2.out"
        }}, {t_start});
        tl.to("#{scene.id} .scene-content", {{
          opacity: 0,
          y: -30,
          duration: 0.4,
          ease: "power2.in"
        }}, {t_start + scene.duration - 0.4});
        """
        )

    all_scenes_str = "\n".join(scenes_html)
    all_tweens_str = "\n".join(gsap_tweens)

    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width={width}, height={height}" />
  <title>Tutorial HyperFrames</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    html, body {{
      width: {width}px;
      height: {height}px;
      overflow: hidden;
      background: #020617;
      color: #f8fafc;
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }}
    #root {{
      position: relative;
      width: 100%;
      height: 100%;
      overflow: hidden;
    }}
    .scene-card {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 80px 140px;
    }}
    .scene-content {{
      width: 100%;
      max-width: 1400px;
      display: flex;
      flex-direction: column;
      gap: 28px;
    }}
    .scene-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .badge {{
      display: inline-block;
      padding: 8px 18px;
      border-radius: 9999px;
      font-size: 20px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      border: 1px solid;
    }}
    .step-indicator {{
      font-size: 20px;
      color: #94a3b8;
      font-weight: 500;
    }}
    .headline {{
      font-size: 68px;
      line-height: 1.15;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #ffffff;
      text-shadow: 0 4px 24px rgba(0,0,0,0.5);
    }}
    .body-text {{
      font-size: 32px;
      line-height: 1.45;
      color: #cbd5e1;
      max-width: 1100px;
    }}
    .code-box {{
      margin-top: 10px;
      background: #0b1120;
      border: 1px solid #1e293b;
      border-radius: 16px;
      padding: 24px 32px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.4);
      position: relative;
    }}
    .code-dot {{
      display: inline-block;
      width: 14px;
      height: 14px;
      border-radius: 50%;
      margin-right: 8px;
    }}
    .code-dot.red {{ background: #ef4444; }}
    .code-dot.yellow {{ background: #f59e0b; }}
    .code-dot.green {{ background: #10b981; }}
    pre {{
      margin-top: 14px;
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 30px;
      color: #38bdf8;
      overflow: hidden;
    }}
    /* Watermark / Brand Footer */
    .brand-footer {{
      position: absolute;
      bottom: 40px;
      left: 140px;
      right: 140px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 18px;
      color: #64748b;
      border-top: 1px solid rgba(255,255,255,0.1);
      padding-top: 20px;
    }}
    .brand-logo {{
      font-weight: 700;
      letter-spacing: 0.05em;
      color: #e2e8f0;
    }}
    /* Progress bar */
    .timeline-bar {{
      position: absolute;
      bottom: 0;
      left: 0;
      height: 6px;
      background: linear-gradient(90deg, #6366f1, #d946ef, #10b981);
      width: 100%;
      transform-origin: left center;
      transform: scaleX(0);
    }}
  </style>
</head>
<body>
  <div id="root"
       data-composition-id="main"
       data-start="0"
       data-duration="{total_duration}"
       data-width="{width}"
       data-height="{height}">
    
    {all_scenes_str}

    <div class="brand-footer clip" data-start="0" data-duration="{total_duration}" data-track-index="2">
      <span class="brand-logo">⚡ BL_Loops · HyperFrames Video Studio</span>
      <span>Renderizado Determinista Local · Chrome Headless + FFmpeg</span>
    </div>

    <div id="progress-indicator" class="timeline-bar clip" data-start="0" data-duration="{total_duration}" data-track-index="3"></div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});

    // Barra de progreso global
    tl.to("#progress-indicator", {{
      scaleX: 1,
      duration: {total_duration},
      ease: "none"
    }}, 0);

    {all_tweens_str}

    window.__timelines["main"] = tl;
  </script>
</body>
</html>
"""
