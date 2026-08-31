"""Ejecucion inyectable de comandos de diagnostico, siempre sin shell."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

OUTPUT_LIMIT = 65_536


@dataclass(frozen=True, slots=True)
class CommandRequest:
    args: tuple[str, ...]
    cwd: Path | None = None
    env_overrides: Mapping[str, str] = field(default_factory=dict)
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        if not self.args or any(not isinstance(arg, str) or not arg for arg in self.args):
            raise ValueError("El comando necesita argumentos de texto no vacios.")
        if self.timeout_seconds <= 0:
            raise ValueError("El timeout debe ser positivo.")


@dataclass(frozen=True, slots=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""
    error_kind: str | None = None


class CommandRunner(Protocol):
    def run(self, request: CommandRequest) -> CommandResult:
        """Ejecuta una solicitud sin interpretar texto como shell."""


class SubprocessCommandRunner:
    """Runner real para el preflight manual futuro; los tests usan un doble."""

    def run(self, request: CommandRequest) -> CommandResult:
        environment = os.environ.copy()
        environment.update(request.env_overrides)
        try:
            completed = subprocess.run(
                request.args,
                cwd=request.cwd,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=request.timeout_seconds,
                check=False,
                shell=False,
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


def request(args: Sequence[str], **kwargs: object) -> CommandRequest:
    """Construye una solicitud a partir de una secuencia sin aceptar un shell string."""

    return CommandRequest(args=tuple(args), **kwargs)
