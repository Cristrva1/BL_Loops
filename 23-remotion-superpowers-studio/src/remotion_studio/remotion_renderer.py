"""Motor de renderizado usando Remotion CLI."""

import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path

from remotion_studio.schemas import RemotionScene, RenderResult

logger = logging.getLogger(__name__)


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
                "bgGradient": s.bg_gradient,
                "accentColor": s.accent_color,
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
        logger.info("Iniciando renderizado con Remotion CLI...")

        # Usamos cmd.exe /c npx remotion render
        proc = await asyncio.create_subprocess_exec(
            "cmd.exe", "/c",
            "npx", "--yes", "-p", "@remotion/cli@4.0.523",
            "remotion", "render",
            self.entry_ts, "MainVideo", str(out_path),
            "--concurrency=4",
            cwd=str(self.root_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

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
            duration=metadata.get("duration", 0.0),
            width=metadata.get("width", 1920),
            height=metadata.get("height", 1080),
            fps=metadata.get("fps", 30),
            total_frames=metadata.get("nb_frames", 360),
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

            width, height, fps, nb_frames = 1920, 1080, 30, 360
            for stream in info.get("streams", []):
                if stream.get("codec_type") == "video":
                    width = int(stream.get("width", 1920))
                    height = int(stream.get("height", 1080))
                    nb_frames = int(stream.get("nb_frames", 360))
                    r_frame_rate = stream.get("r_frame_rate", "30/1")
                    if "/" in r_frame_rate:
                        num, den = r_frame_rate.split("/")
                        fps = round(float(num) / float(den))
                    break

            return {
                "duration": round(duration, 2),
                "width": width,
                "height": height,
                "fps": fps,
                "nb_frames": nb_frames,
            }
        except Exception as e:
            logger.warning("ffprobe fallo en Remotion: %s", e)
            return {"duration": 12.0, "width": 1920, "height": 1080, "fps": 30, "nb_frames": 360}
