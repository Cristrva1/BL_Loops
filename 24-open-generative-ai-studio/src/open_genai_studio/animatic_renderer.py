"""Motor de renderizado de Animatics y Storyboards en MP4 con FFmpeg."""

import asyncio
import json
import logging
import os
from pathlib import Path
import subprocess
import time

from open_genai_studio.schemas import RenderResult, StoryboardShot

logger = logging.getLogger(__name__)


class AnimaticRenderer:
    def __init__(self, workspace_dir: str | Path = ".local/workspace"):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    async def render_animatic(
        self, shots: list[StoryboardShot], output_mp4_path: str | Path
    ) -> RenderResult:
        """Renderiza una previsualización (animatic) con textos, tipos de plano y metadatos."""
        out_path = Path(output_mp4_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        start_time = time.time()
        segment_files = []

        for idx, shot in enumerate(shots):
            seg_file = self.workspace_dir / f"shot_{idx+1}.mp4"
            # Escapar textos para el filtro drawtext de FFmpeg
            title_clean = shot.headline.replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")
            type_clean = f"PLANO {shot.shot_number}: {shot.shot_type.value} | {shot.camera_movement.value}".replace(":", "\\:")
            light_clean = f"LUZ: {shot.lighting[:50]}...".replace(":", "\\:")

            # Color hexadecimal limpio
            hex_color = shot.accent_color.lstrip("#")
            bg_hex = "0a0f1d" if idx % 2 == 0 else "0e1726"

            filter_graph = (
                f"color=c=0x{bg_hex}:s=1920x1080:d={shot.duration_seconds}:r=30,"
                f"drawbox=x=80:y=80:w=1760:h=920:color=0x{hex_color}@0.3:t=2,"
                f"drawtext=text='{type_clean}':fontcolor=0x{hex_color}:fontsize=28:x=120:y=120,"
                f"drawtext=text='{title_clean}':fontcolor=white:fontsize=56:x=120:y=200,"
                f"drawtext=text='{light_clean}':fontcolor=0x94a3b8:fontsize=26:x=120:y=290,"
                f"drawtext=text='PROMPT GENERATIVO\\:':fontcolor=0xfbbf24:fontsize=24:x=120:y=370,"
                f"drawtext=text='{shot.prompt_expansion[:80]}...':fontcolor=0x38bdf8:fontsize=24:x=120:y=415,"
                f"drawtext=text='BL_Loops Lab 24 · Open Generative AI Studio':fontcolor=0x64748b:fontsize=20:x=120:y=940"
            )

            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", filter_graph,
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-t", str(shot.duration_seconds),
                str(seg_file)
            ]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            if seg_file.exists() and seg_file.stat().st_size > 0:
                segment_files.append(seg_file)

        if not segment_files:
            return RenderResult(
                video_path=str(out_path),
                duration=0.0,
                width=0,
                height=0,
                fps=0,
                shots_count=0,
                file_size_bytes=0,
                render_elapsed_seconds=round(time.time() - start_time, 2),
                success=False,
                error="No se pudieron generar los segmentos de video para los planos",
            )

        # Concatenar todos los segmentos
        concat_list_file = self.workspace_dir / "concat_list.txt"
        with concat_list_file.open("w", encoding="utf-8") as f:
            for seg in segment_files:
                # Normalizar path para ffmpeg concat
                p_str = str(seg).replace("\\", "/")
                f.write(f"file '{p_str}'\n")

        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_list_file),
            "-c", "copy",
            str(out_path)
        ]

        proc_concat = await asyncio.create_subprocess_exec(
            *concat_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc_concat.communicate()
        elapsed = time.time() - start_time

        if not out_path.exists() or out_path.stat().st_size == 0:
            return RenderResult(
                video_path=str(out_path),
                duration=0.0,
                width=0,
                height=0,
                fps=0,
                shots_count=0,
                file_size_bytes=0,
                render_elapsed_seconds=round(elapsed, 2),
                success=False,
                error="Fallo al ensamblar animatic final",
            )

        metadata = self._probe_video(out_path)
        return RenderResult(
            video_path=str(out_path),
            duration=metadata.get("duration", 0.0),
            width=metadata.get("width", 1920),
            height=metadata.get("height", 1080),
            fps=metadata.get("fps", 30),
            shots_count=len(shots),
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
            logger.warning("ffprobe fallo en AnimaticRenderer: %s", e)
            return {"duration": 12.0, "width": 1920, "height": 1080, "fps": 30}
