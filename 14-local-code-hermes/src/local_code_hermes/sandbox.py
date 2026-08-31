"""Aislamiento local minimo para ejecutar los checks del fixture."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from local_code_hermes.command import OUTPUT_LIMIT, CommandResult

DEFAULT_IMAGE = "nikolaik/python-nodejs:python3.11-nodejs20"


class DockerSandbox:
    """Ejecuta comandos en un contenedor efimero sin red.

    El unico bind mount es el workspace del caso. La imagen debe existir
    localmente; esta clase nunca hace ``pull`` ni modifica el daemon.
    """

    def __init__(
        self,
        workspace: Path,
        *,
        image: str = DEFAULT_IMAGE,
        timeout_seconds: float = 60.0,
    ) -> None:
        resolved = workspace.resolve()
        if not resolved.is_dir():
            raise ValueError("El workspace del sandbox no existe.")
        if not image or any(char.isspace() for char in image) or image.startswith("-"):
            raise ValueError("La imagen Docker no es valida.")
        if timeout_seconds <= 0:
            raise ValueError("El timeout del sandbox debe ser positivo.")
        self.workspace = resolved
        self.image = image
        self.timeout_seconds = timeout_seconds

    def _docker_args(self, args: Sequence[str]) -> tuple[str, ...]:
        command = tuple(args)
        if not command or any(not isinstance(arg, str) or not arg for arg in command):
            raise ValueError("El sandbox necesita un comando no vacio.")
        return (
            "docker",
            "run",
            "--rm",
            "--network=none",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
            "--pids-limit=256",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=256m",
            "--mount",
            f"type=bind,source={self.workspace},target=/workspace",
            "--workdir",
            "/workspace",
            "--env",
            "PYTHONDONTWRITEBYTECODE=1",
            self.image,
            *command,
        )

    def run(
        self,
        args: Sequence[str],
        *,
        timeout_seconds: float | None = None,
    ) -> CommandResult:
        timeout = self.timeout_seconds if timeout_seconds is None else timeout_seconds
        if timeout <= 0:
            raise ValueError("El timeout del sandbox debe ser positivo.")
        docker_args = self._docker_args(args)
        try:
            completed = subprocess.run(
                docker_args,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
                shell=False,
                stdin=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            return CommandResult(returncode=127, error_kind="not_found")
        except subprocess.TimeoutExpired:
            return CommandResult(returncode=124, error_kind="timeout")
        return CommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout[:OUTPUT_LIMIT],
            stderr=completed.stderr[:OUTPUT_LIMIT],
            error_kind=None if completed.returncode == 0 else "nonzero",
        )

    def execute_check(self, args: tuple[str, ...], timeout_seconds: float) -> int:
        """Adapt the host interpreter token to the Python executable in the image."""

        command = list(args)
        if command and (
            command[0] == sys.executable
            or command[0].casefold().endswith(("/python.exe", "\\python.exe"))
        ):
            command[0] = "python"
        return self.run(command, timeout_seconds=timeout_seconds).returncode

    def image_identity(self) -> str | None:
        """Returns the local image ID without pulling or exposing daemon output."""

        try:
            completed = subprocess.run(
                ("docker", "image", "inspect", "--format={{.Id}}", self.image),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
                check=False,
                shell=False,
                stdin=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
        value = completed.stdout.strip()
        if completed.returncode != 0 or not value.startswith("sha256:"):
            return None
        return value if len(value) == len("sha256:") + 64 else None
