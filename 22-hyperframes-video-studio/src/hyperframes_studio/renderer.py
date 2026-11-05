"""Motor de renderizado usando HyperFrames CLI y Chromium Headless."""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import time
from pathlib import Path

from hyperframes_studio.schemas import RenderResult

logger = logging.getLogger(__name__)

# HyperFrames envía telemetría anónima (PostHog) salvo que se desactive. BL_Loops no permite
# telemetría por defecto: el CLI respeta estas dos variables con los valores 1/true/yes/on.
TELEMETRY_OPT_OUT = {"HYPERFRAMES_NO_TELEMETRY": "1", "DO_NOT_TRACK": "1"}


def render_environment() -> dict[str, str]:
    """Entorno del subproceso de render: el del sistema más la exclusión de telemetría."""

    return {**os.environ, **TELEMETRY_OPT_OUT}


class HyperFramesRenderer:
    def __init__(self, workspace_dir: str | Path = ".local/workspace"):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def prepare_workspace(self, html_content: str) -> Path:
        """Prepara los archivos necesarios para HyperFrames."""
        index_html_path = self.workspace_dir / "index.html"
        index_html_path.write_text(html_content, encoding="utf-8")

        # hyperframes.json configuration
        hf_config = {
            "version": "1.0",
            "name": "hyperframes-studio-render",
            "compositions": {
                "main": {
                    "entry": "index.html",
                    "fps": 30,
                    "width": 1920,
                    "height": 1080
                }
            }
        }
        (self.workspace_dir / "hyperframes.json").write_text(json.dumps(hf_config, indent=2), encoding="utf-8")

        # Minimal package.json for npx resolution
        pkg_json = {
            "name": "hf-render-job",
            "private": True,
            "type": "module"
        }
        (self.workspace_dir / "package.json").write_text(json.dumps(pkg_json, indent=2), encoding="utf-8")

        return index_html_path

    async def render_video(self, output_mp4_path: str | Path) -> RenderResult:
        """Invoca npx hyperframes render para compilar el HTML a MP4."""
        out_path = Path(output_mp4_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        start_time = time.time()
        npx = shutil.which("npx")
        if npx is None:
            return _failed_render(
                out_path,
                start_time,
                "No se encontró npx: instala Node.js para renderizar con HyperFrames.",
            )
        cmd = [npx, "--yes", "hyperframes@0.8.34", "render", "-o", str(out_path)]
        if os.name == "nt" and npx.lower().endswith((".cmd", ".bat")):
            # En Windows, npx es un script .cmd que se ejecuta a través de cmd.exe.
            cmd = ["cmd.exe", "/c", *cmd]
        logger.info("Iniciando renderizado con HyperFrames: %s", " ".join(cmd))

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(self.workspace_dir),
                env=render_environment(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError as exc:
            return _failed_render(out_path, start_time, f"No se pudo iniciar HyperFrames: {exc}")

        _stdout_bytes, stderr_bytes = await proc.communicate()
        elapsed = time.time() - start_time
        stderr_str = stderr_bytes.decode(errors="replace")

        if proc.returncode != 0 or not out_path.exists() or out_path.stat().st_size == 0:
            error_msg = f"HyperFrames falló con código {proc.returncode}. Stderr: {stderr_str}"
            logger.error(error_msg)
            return RenderResult(
                video_path=str(out_path),
                duration=0.0,
                width=0,
                height=0,
                fps=0,
                file_size_bytes=0,
                render_elapsed_seconds=round(elapsed, 2),
                success=False,
                error=error_msg,
            )

        # Extraer metadatos con ffprobe
        metadata = self._probe_video(out_path)

        return RenderResult(
            video_path=str(out_path),
            duration=metadata["duration"],
            width=metadata["width"],
            height=metadata["height"],
            fps=metadata["fps"],
            file_size_bytes=out_path.stat().st_size,
            render_elapsed_seconds=round(elapsed, 2),
            success=True,
            error=None,
        )

    def _probe_video(self, video_path: Path) -> dict:
        """Lee resolución, fps y duración con ffprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(video_path)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(res.stdout)
            format_info = info.get("format", {})
            duration = float(format_info.get("duration", 0.0))

            # Sin pista de video no hay medición: ceros, nunca una resolución supuesta.
            width, height, fps = 0, 0, 0
            for stream in info.get("streams", []):
                if stream.get("codec_type") == "video":
                    width = int(stream.get("width", 0))
                    height = int(stream.get("height", 0))
                    num, _, den = str(stream.get("r_frame_rate", "0/1")).partition("/")
                    denominator = float(den or 1)
                    fps = round(float(num) / denominator) if denominator else 0
                    break

            return {"duration": round(duration, 2), "width": width, "height": height, "fps": fps}
        except (OSError, subprocess.CalledProcessError, ValueError) as exc:
            # Sin ffprobe no hay medición: duración 0 para que la evaluación no apruebe a ciegas.
            logger.warning("No se pudo inspeccionar el video con ffprobe: %s", exc)
            return {"duration": 0.0, "width": 0, "height": 0, "fps": 0}


def _failed_render(out_path: Path, start_time: float, message: str) -> RenderResult:
    logger.error(message)
    return RenderResult(
        video_path=str(out_path),
        duration=0.0,
        width=0,
        height=0,
        fps=0,
        file_size_bytes=0,
        render_elapsed_seconds=round(time.time() - start_time, 2),
        success=False,
        error=message,
    )
