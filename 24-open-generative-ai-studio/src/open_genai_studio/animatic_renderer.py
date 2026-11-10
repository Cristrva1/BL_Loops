"""Motor de renderizado de animatics: storyboard -> segmentos MP4 con FFmpeg -> video final.

Cada plano se dibuja con el filtro `drawtext` de FFmpeg sobre un fondo de color. El texto puede
venir del modelo, así que se prepara antes de entrar en el filtergraph: una comilla o un `:` sin
escapar romperían el comando completo.
"""

import asyncio
import json
import logging
import re
import shutil
import subprocess
import time
from pathlib import Path

from open_genai_studio.schemas import RenderResult, StoryboardShot

logger = logging.getLogger(__name__)

HEX_COLOR = re.compile(r"^#?([0-9a-fA-F]{6})$")
DEFAULT_ACCENT = "6366f1"
WIDTH, HEIGHT, FPS = 1920, 1080, 30

# En Windows, drawtext sin `fontfile` suele fallar («Cannot find a valid font»). Se usa la primera
# fuente que exista; ANIMATIC_FONT_FILE en el `.env` permite elegir otra.
FONT_CANDIDATES = (
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
)


def drawtext_value(text: str, limit: int | None = None) -> str:
    """Prepara un texto para `drawtext=text='...'` dentro de un filtergraph de FFmpeg.

    - Se compactan espacios y saltos de línea.
    - La comilla simple cerraría el valor: se sustituye por la tipográfica (’).
    - La barra invertida se sustituye para no crear escapes accidentales.
    - `:` separa las opciones de drawtext: se escapa como `\\:`.
    - `%` queda literal porque cada drawtext usa `expansion=none`.
    """

    cleaned = " ".join(text.split())
    if limit is not None and len(cleaned) > limit:
        cleaned = cleaned[: limit - 1].rstrip() + "…"
    cleaned = cleaned.replace("\\", "/").replace("'", "’")
    return cleaned.replace(":", "\\:")


def find_font_file(candidates: tuple[str, ...] = FONT_CANDIDATES) -> Path | None:
    """Primera fuente disponible del sistema, o None para que FFmpeg use fontconfig."""

    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return path
    return None


def fontfile_option(font_file: str | Path | None) -> str:
    """Opción `:fontfile='...'` lista para drawtext; el `:` de `C:/` se escapa como `\\:`."""

    if font_file is None:
        return ""
    value = Path(font_file).as_posix()
    if "'" in value:
        return ""  # una comilla cerraría el valor: mejor dejar que FFmpeg elija la fuente
    escaped = value.replace(":", "\\:")
    return f":fontfile='{escaped}'"


def safe_hex_color(value: str) -> str:
    """Devuelve un color `rrggbb` válido; un valor inventado por el modelo cae al color base."""

    match = HEX_COLOR.match(value.strip())
    return match.group(1).lower() if match else DEFAULT_ACCENT


def build_filter_graph(
    shot: StoryboardShot, index: int, font_file: str | Path | None = None
) -> str:
    """Filtergraph de un plano: fondo, marco con el color de acento y seis líneas de texto."""

    accent = safe_hex_color(shot.accent_color)
    font = fontfile_option(font_file)
    background = "0a0f1d" if index % 2 == 0 else "0e1726"
    label = f"PLANO {shot.shot_number}: {shot.shot_type.value} | {shot.camera_movement.value}"
    lines = [
        (drawtext_value(label), f"0x{accent}", 28, 120),
        (drawtext_value(shot.headline, 70), "white", 56, 200),
        (drawtext_value(f"LUZ: {shot.lighting}", 90), "0x94a3b8", 26, 290),
        (drawtext_value("PROMPT GENERATIVO:"), "0xfbbf24", 24, 370),
        (drawtext_value(shot.prompt_expansion, 110), "0x38bdf8", 24, 415),
        (drawtext_value("BL_Loops Lab 24 · Open Generative AI Studio"), "0x64748b", 20, 940),
    ]
    parts = [
        f"color=c=0x{background}:s={WIDTH}x{HEIGHT}:d={shot.duration_seconds}:r={FPS}",
        f"drawbox=x=80:y=80:w=1760:h=920:color=0x{accent}@0.3:t=2",
    ]
    parts.extend(
        f"drawtext=text='{text}':expansion=none{font}:fontcolor={color}:fontsize={size}:x=120:y={y}"
        for text, color, size, y in lines
    )
    return ",".join(parts)


class AnimaticRenderer:
    def __init__(
        self,
        workspace_dir: str | Path = ".local/workspace",
        font_file: str | Path | None = None,
    ):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.font_file = Path(font_file) if font_file else find_font_file()

    async def render_animatic(
        self, shots: list[StoryboardShot], output_mp4_path: str | Path
    ) -> RenderResult:
        """Renderiza un animatic con el tipo de plano, la luz y el prompt de cada toma."""

        out_path = Path(output_mp4_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        start_time = time.time()

        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg is None:
            return _failed(
                out_path, start_time, "No se encontró FFmpeg: instálalo para renderizar."
            )
        if not shots:
            return _failed(out_path, start_time, "El storyboard no tiene planos que renderizar.")

        segment_files: list[Path] = []
        for index, shot in enumerate(shots):
            segment = self.workspace_dir / f"shot_{index + 1}.mp4"
            cmd = [
                ffmpeg,
                "-y",
                "-f",
                "lavfi",
                "-i",
                build_filter_graph(shot, index, self.font_file),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-t",
                str(shot.duration_seconds),
                str(segment),
            ]
            ok, detail = await _run(cmd)
            if not ok or not segment.is_file() or segment.stat().st_size == 0:
                return _failed(
                    out_path, start_time, f"FFmpeg no pudo generar el plano {index + 1}: {detail}"
                )
            segment_files.append(segment)

        concat_list = self.workspace_dir / "concat_list.txt"
        concat_list.write_text(
            "".join(f"file '{seg.as_posix()}'\n" for seg in segment_files), encoding="utf-8"
        )
        concat_cmd = [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_list),
            "-c",
            "copy",
            str(out_path),
        ]
        ok, detail = await _run(concat_cmd)
        elapsed = time.time() - start_time
        if not ok or not out_path.is_file() or out_path.stat().st_size == 0:
            return _failed(out_path, start_time, f"Fallo al ensamblar el animatic final: {detail}")

        metadata = self._probe_video(out_path)
        return RenderResult(
            video_path=str(out_path),
            duration=metadata["duration"],
            width=metadata["width"],
            height=metadata["height"],
            fps=metadata["fps"],
            shots_count=len(shots),
            file_size_bytes=out_path.stat().st_size,
            render_elapsed_seconds=round(elapsed, 2),
            success=True,
            error=None,
        )

    def _probe_video(self, video_path: Path) -> dict:
        """Mide el video real con ffprobe. Sin medición, devuelve ceros: nunca inventa valores."""

        try:
            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                str(video_path),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(res.stdout)
            duration = float(info.get("format", {}).get("duration", 0.0))
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
            logger.warning("No se pudo inspeccionar el animatic con ffprobe: %s", exc)
            return {"duration": 0.0, "width": 0, "height": 0, "fps": 0}


async def _run(cmd: list[str]) -> tuple[bool, str]:
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
    except OSError as exc:
        return False, str(exc)
    _stdout, stderr = await proc.communicate()
    tail = stderr.decode(errors="replace").strip().splitlines()[-1:] or [""]
    return proc.returncode == 0, tail[0]


def _failed(out_path: Path, start_time: float, message: str) -> RenderResult:
    logger.error(message)
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
        error=message,
    )
