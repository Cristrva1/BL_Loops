# Architecture Guardian (CTO)

> **Status**: `stub` | Anillo: Core | Última revisión: 2026-05-07

---

## 1. Propósito

Velar por que todos los módulos nuevos y cambios respeten los contratos del sistema. Bloquea cambios que rompen la interfaz estable de otros módulos.

---

## 2. Anillo y rol

- **Anillo**: 1 — Núcleo
- **Rol análogo**: CTO / Architecture Guardian
- **Patrón**: Contract Validator + Change Gate

---

## 3. Reporta a / Dirige a

- **Reporta a**: Meta-Orchestrator
- **Dirige a**: validación de todos los módulos al registrarse o actualizar su contrato

---

## 4. Puerto (interfaz) — pendiente de especificar

```python
class ArchitectureGuardianPort:
    async def validate_module_contract(self, module_spec: ModuleSpec) -> ValidationResult:
        """
        Valida que el nuevo módulo respete los contratos existentes.
        """

    async def approve_schema_change(self, schema_change: SchemaChange) -> ApprovalResult:
        """
        Aprueba o bloquea cambios en JSON Schemas de eventos o puertos.
        """
```

---

## 5. Estado que posee

- **PostgreSQL** (`module_registry`): catálogo de módulos registrados con sus versiones de contrato.
- **PostgreSQL** (`schema_changes`): historial de cambios de esquema aprobados/rechazados.

---

## 6. SLOs (preliminares)

- Validación de contrato: < 500ms
- Disponibilidad: 99.5% (no es ruta crítica)

---

> **TODO**: Completar secciones 5–11 en iteración siguiente. Prioridad: después de fases 1–3.
