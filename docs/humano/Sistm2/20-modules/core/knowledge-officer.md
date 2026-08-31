# Knowledge Officer (CKO)

> **Status**: `stub` | Anillo: Core | Última revisión: 2026-05-07

---

## 1. Propósito

Dueño de la memoria global del sistema. Decide qué patrones se promueven a doctrina permanente, qué se archiva y qué se descarta. Gestiona la retención de datos.

---

## 2. Anillo y rol

- **Anillo**: 1 — Núcleo
- **Rol análogo**: CKO / Chief Knowledge Officer
- **Patrón**: Knowledge Curator + Retention Policy Engine

---

## 3. Reporta a / Dirige a

- **Reporta a**: Meta-Orchestrator
- **Dirige a**: Guild de Memoria (políticas de retención), Doctrine Publisher (aprobación de doctrinas)
- **Coordina con**: User Profiler (gestión de perfil a nivel de retención)

---

## 4. Puerto (interfaz) — pendiente de especificar

```python
class KnowledgeOfficerPort:
    async def approve_doctrine(self, event: DoctrineProposed) -> ApprovalDecision:
        """
        Aprueba o rechaza una doctrina antes de que el Doctrine Publisher la despliegue.
        """

    async def apply_retention_policy(self, tenant_id: str) -> None:
        """
        Aplica política de retención a datos episódicos y semánticos.
        """

    async def handle_deletion_request(self, tenant_id: str) -> None:
        """
        Gestiona solicitudes de borrado de datos (GDPR).
        """
```

---

## 5. Estado que posee

- **PostgreSQL** (`knowledge_policies`): políticas de retención y descarte activas.
- **PostgreSQL** (`doctrine_approvals`): historial de aprobaciones/rechazos.

---

> **TODO**: Completar secciones 5–11. Prioridad: fase 7 (Pattern Miner offline).
