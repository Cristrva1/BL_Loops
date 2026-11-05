"""Motor de renderizado usando Remotion CLI."""

import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from remotion_studio.schemas import RemotionScene, RenderResult

logger = logging.getLogger(__name__)

# Los colores y gradientes del modelo acaban en `style` de React: solo se aceptan formas seguras.
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
SAFE_GRADIENT = re.compile(r"^linear-gradient\([0-9A-Za-z#%,.\s-]+\)$")
DEFAULT_GRADIENT = RemotionScene.model_fields["bg_gradient"].default
DEFAULT_ACCENT = RemotionScene.model_fields["accent_color"].default


def safe_accent(value: str) -> str:
    return value if HEX_COLOR.match(value) else DEFAULT_ACCENT


def safe_gradient(value: str) -> str:
    return value if SAFE_GRADIENT.match(value.strip()) else DEFAULT_GRADIENT


class RemotionRenderer:
    def __init__(self, root_dir: str | Path = "."):
        self.root_dir = Path(root_dir).resolve()
        self.scenes_json_path = self.root_dir / "src" / "video_composition" / "scenes.json"
        self.entry_ts = "src/video_composition/index.ts"

    def update_scenes_json(self, scenes: list[RemotionScene]) -> None:
        """Actualiza el archivo scenes.json que lee la composición React de Remotion."""
        self.scenes_json_path.parent.mkdir(parents=True, exist_ok=True)
        data = [
            {
                "id": s.id,
                "title": s.title,
                "startFrame": s.start_frame,
                "durationInFrames": s.duration_in_frames,
                "headline": s.headline,
                "subheadline": s.subheadline,
                "bgGradient": safe_gradient(s.bg_gradient),
                "accentColor": safe_accent(s.accent_color),
                "badge": s.badge,
                "code": s.code,
            }
            for s in scenes
        ]
        self.scenes_json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    async def render_video(self, output_mp4_path: str | Path) -> RenderResult:
        """Invoca remotion render para compilar la composición React a MP4."""
        out_path = Path(output_mp4_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        start_time = time.time()
        npx = shutil.which("npx")
        if npx is None:
            return _failed_render(
                out_path,
                start_time,
                "No se encontró npx: instala Node.js y ejecuta npm install en este laboratorio.",
            )
        cmd = [
            npx, "--yes", "-p", "@remotion/cli@4.0.523",
            "remotion", "render",
            self.entry_ts, "MainVideo", str(out_path),
            "--concurrency=4",
        ]
        if os.name == "nt" and npx.lower().endswith((".cmd", ".bat")):
            # En Windows, npx es un script .cmd que se ejecuta a través de cmd.exe.
            cmd = ["cmd.exe", "/c", *cmd]
        logger.info("Iniciando renderizado con Remotion CLI...")

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(self.root_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError as exc:
            return _failed_render(out_path, start_time, f"No se pudo iniciar Remotion: {exc}")

        stdout_bytes, stderr_bytes = await proc.communicate()
        elapsed = time.time() - start_time
        stdout_str = stdout_bytes.decode(errors="replace")
        stderr_str = stderr_bytes.decode(errors="replace")

        if proc.returncode != 0 or not out_path.exists() or out_path.stat().st_size == 0:
            error_msg = f"Remotion render falló con código {proc.returncode}. Stderr: {stderr_str}\nStdout: {stdout_str}"
            logger.error(error_msg)
            return RenderResult(
                video_path=str(out_path),
                duration=0.0,
                width=0,
                height=0,
                fps=0,
                total_frames=0,
                file_size_bytes=0,
                render_elapsed_seconds=round(elapsed, 2),
                success=False,
                error=error_msg,
            )

        metadata = self._probe_video(out_path)

        return RenderResult(
            video_path=str(out_path),
            duration=metadata["duration"],
            width=metadata["width"],
            height=metadata["height"],
            fps=metadata["fps"],
            total_frames=metadata["nb_frames"],
            file_size_bytes=out_path.stat().st_size,
            render_elapsed_seconds=round(elapsed, 2),
            success=True,
            error=None,
        )

    def _probe_video(self, video_path: Path) -> dict:
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
            width, height, fps, nb_frames = 0, 0, 0, 0
            for stream in info.get("streams", []):
                if stream.get("codec_type") == "video":
                    width = int(stream.get("width", 0))
                    height = int(stream.get("height", 0))
                    nb_frames = int(stream.get("nb_frames", 0))
                    num, _, den = str(stream.get("r_frame_rate", "0/1")).partition("/")
                    denominator = float(den or 1)
                    fps = round(float(num) / denominator) if denominator else 0
                    break

            return {
                "duration": round(duration, 2),
                "width": width,
                "height": height,
                "fps": fps,
                "nb_frames": nb_frames,
            }
        except (OSError, subprocess.CalledProcessError, ValueError) as exc:
            # Sin ffprobe no hay medición: valores en cero para que la evaluación no apruebe a ciegas.
            logger.warning("No se pudo inspeccionar el video con ffprobe: %s", exc)
            return {"duration": 0.0, "width": 0, "height": 0, "fps": 0, "nb_frames": 0}


def _failed_render(out_path: Path, start_time: float, message: str) -> RenderResult:
    logger.error(message)
    return RenderResult(
        video_path=str(out_path),
        duration=0.0,
        width=0,
        height=0,
        fps=0,
        total_frames=0,
        file_size_bytes=0,
        render_elapsed_seconds=round(time.time() - start_time, 2),
        success=False,
        error=message,
    )
