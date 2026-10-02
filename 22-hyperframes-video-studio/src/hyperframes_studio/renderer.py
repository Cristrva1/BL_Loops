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

        cmd = [
            "npx", "--yes", "hyperframes@0.8.34",
            "render",
            "-o", str(out_path)
        ]

        start_time = time.time()
        logger.info("Iniciando renderizado con HyperFrames: %s", " ".join(cmd))

        # En Windows usamos shell=True o powershell/cmd para resolver npx
        proc = await asyncio.create_subprocess_exec(
            "cmd.exe", "/c", "npx", "--yes", "hyperframes@0.8.34", "render", "-o", str(out_path),
            cwd=str(self.workspace_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout_bytes, stderr_bytes = await proc.communicate()
        elapsed = time.time() - start_time
        stdout_str = stdout_bytes.decode(errors="replace")
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
            duration=metadata.get("duration", 0.0),
            width=metadata.get("width", 1920),
            height=metadata.get("height", 1080),
            fps=metadata.get("fps", 30),
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

            width, height, fps = 1920, 1080, 30
            for stream in info.get("streams", []):
                if stream.get("codec_type") == "video":
                    width = int(stream.get("width", 1920))
                    height = int(stream.get("height", 1080))
                    r_frame_rate = stream.get("r_frame_rate", "30/1")
                    if "/" in r_frame_rate:
                        num, den = r_frame_rate.split("/")
                        fps = round(float(num) / float(den))
                    break

            return {"duration": round(duration, 2), "width": width, "height": height, "fps": fps}
        except Exception as e:
            logger.warning("No se pudo inspeccionar ffprobe: %s. Usando valores estándar.", e)
            return {"duration": 15.0, "width": 1920, "height": 1080, "fps": 30}
