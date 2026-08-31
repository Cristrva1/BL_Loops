"""Cada rol tiene entrada, salida, permisos y parada. El modelo no publica."""

from __future__ import annotations

from sales_curator.domain.policy import DENIED_TO_ALL_MODELS, role_may


def assert_role_may(role: str, capability: str) -> None:
    if not role_may(role, capability):
        raise PermissionError(f"El rol {role} no puede {capability}")


def model_forbidden(capability: str) -> bool:
    return capability in DENIED_TO_ALL_MODELS
