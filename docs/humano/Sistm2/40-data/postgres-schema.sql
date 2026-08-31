-- =============================================================
-- Schema de referencia — Orquestación Auto-Mejorante
-- PostgreSQL 16 | Estado: draft | Última revisión: 2026-05-07
-- =============================================================
-- Extensiones requeridas
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_partman";

-- =============================================================
-- 1. EVENT STORE (fuente de verdad, append-only)
-- =============================================================
CREATE TABLE IF NOT EXISTS event_store (
    event_id        UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type      VARCHAR(120)    NOT NULL,
    event_version   VARCHAR(10)     NOT NULL DEFAULT 'v1',
    occurred_at     TIMESTAMPTZ     NOT NULL DEFAULT now(),
    producer        VARCHAR(80)     NOT NULL,
    correlation_id  UUID            NOT NULL,
    causation_id    UUID            NOT NULL,
    tenant_id       VARCHAR(80)     NOT NULL,
    payload         JSONB           NOT NULL,
    metadata        JSONB           NOT NULL DEFAULT '{}'
) PARTITION BY RANGE (occurred_at);

-- Índices del event store
CREATE INDEX idx_event_store_correlation    ON event_store (correlation_id);
CREATE INDEX idx_event_store_tenant         ON event_store (tenant_id, occurred_at DESC);
CREATE INDEX idx_event_store_type           ON event_store (event_type, occurred_at DESC);
CREATE INDEX idx_event_store_producer       ON event_store (producer, occurred_at DESC);

-- Partición inicial (pg_partman gestiona el resto)
CREATE TABLE event_store_2026_05 PARTITION OF event_store
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

-- =============================================================
-- 2. PROYECCIÓN: REQUESTS
-- =============================================================
CREATE TABLE IF NOT EXISTS requests_view (
    correlation_id      UUID            PRIMARY KEY,
    tenant_id           VARCHAR(80)     NOT NULL,
    status              VARCHAR(30)     NOT NULL
                            CHECK (status IN ('received','classified','planning',
                                              'executing','synthesizing','qa',
                                              'delivered','failed','fallback')),
    classification      VARCHAR(30),
    guilds_invoked      TEXT[],
    plan_created_at     TIMESTAMPTZ,
    delivered_at        TIMESTAMPTZ,
    total_tokens        INTEGER,
    total_latency_ms    INTEGER,
    qa_passed           BOOLEAN,
    fallback_used       BOOLEAN         DEFAULT FALSE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_requests_tenant    ON requests_view (tenant_id, created_at DESC);
CREATE INDEX idx_requests_status    ON requests_view (status);

-- =============================================================
-- 3. PROYECCIÓN: TASKS
-- =============================================================
CREATE TABLE IF NOT EXISTS tasks_view (
    task_id             UUID            PRIMARY KEY,
    correlation_id      UUID            NOT NULL REFERENCES requests_view(correlation_id),
    tenant_id           VARCHAR(80)     NOT NULL,
    guild               VARCHAR(40)     NOT NULL,
    status              VARCHAR(20)     NOT NULL
                            CHECK (status IN ('dispatched','in_progress','completed','failed','retrying')),
    instructions        TEXT,
    result_content      TEXT,
    tokens_used         INTEGER,
    latency_ms          INTEGER,
    llm_model           VARCHAR(80),
    retry_count         INTEGER         DEFAULT 0,
    dispatched_at       TIMESTAMPTZ     NOT NULL,
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_tasks_correlation  ON tasks_view (correlation_id);
CREATE INDEX idx_tasks_guild        ON tasks_view (guild, dispatched_at DESC);

-- =============================================================
-- 4. PERFILES DE USUARIO
-- =============================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    tenant_id           VARCHAR(80)     PRIMARY KEY,
    version             INTEGER         NOT NULL DEFAULT 1,
    explicit_data       JSONB           NOT NULL DEFAULT '{}',
    inferred_data       JSONB           NOT NULL DEFAULT '{}',
    history_summary     JSONB           NOT NULL DEFAULT '{}',
    active_doctrines    UUID[]          NOT NULL DEFAULT '{}',
    -- Columnas indexables de explicit_data
    language            VARCHAR(10)     GENERATED ALWAYS AS (explicit_data->>'language') STORED,
    profession          VARCHAR(120)    GENERATED ALWAYS AS (explicit_data->>'profession') STORED,
    preferred_format    VARCHAR(30)     GENERATED ALWAYS AS (explicit_data->>'preferred_response_format') STORED,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_profiles_language  ON user_profiles (language);
CREATE INDEX idx_profiles_profession ON user_profiles (profession);

-- Historial de versiones de perfil (para rollback y auditoría)
CREATE TABLE IF NOT EXISTS profile_history (
    id                  BIGSERIAL       PRIMARY KEY,
    tenant_id           VARCHAR(80)     NOT NULL,
    version             INTEGER         NOT NULL,
    snapshot            JSONB           NOT NULL,
    changed_by          VARCHAR(80),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_profile_history_tenant ON profile_history (tenant_id, version DESC);

-- =============================================================
-- 5. MEMORIA EPISÓDICA
-- =============================================================
CREATE TABLE IF NOT EXISTS episodic_memory (
    id                  BIGSERIAL       PRIMARY KEY,
    tenant_id           VARCHAR(80)     NOT NULL,
    correlation_id      UUID,
    interaction_type    VARCHAR(40),
    summary             TEXT            NOT NULL,
    key_topics          TEXT[],
    sentiment           NUMERIC(3,2),   -- -1.0 a 1.0
    satisfaction_signal NUMERIC(3,2),   -- 0.0 a 1.0
    occurred_at         TIMESTAMPTZ     NOT NULL DEFAULT now()
) PARTITION BY RANGE (occurred_at);

CREATE INDEX idx_episodic_tenant    ON episodic_memory (tenant_id, occurred_at DESC);
CREATE INDEX idx_episodic_topics    ON episodic_memory USING GIN (key_topics);

-- Partición inicial
CREATE TABLE episodic_memory_2026_05 PARTITION OF episodic_memory
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

-- =============================================================
-- 6. MEMORIA SEMÁNTICA GLOBAL (solo datos anonimizados)
-- =============================================================
CREATE TABLE IF NOT EXISTS semantic_memory (
    id                  BIGSERIAL       PRIMARY KEY,
    embedding           VECTOR(1536)    NOT NULL,   -- dimensión según modelo de embeddings
    content_hash        VARCHAR(64)     NOT NULL UNIQUE,  -- para deduplicación
    metadata            JSONB           NOT NULL DEFAULT '{}',
    -- metadata NUNCA debe contener tenant_id ni PII
    -- Solo: topics, domain, quality_score, cluster_id, source_module
    anonymized          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_semantic_embedding ON semantic_memory USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_semantic_metadata  ON semantic_memory USING GIN (metadata);

-- =============================================================
-- 7. DOCTRINAS
-- =============================================================
CREATE TABLE IF NOT EXISTS doctrines (
    doctrine_id         UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    version             INTEGER         NOT NULL DEFAULT 1,
    status              VARCHAR(20)     NOT NULL DEFAULT 'proposed'
                            CHECK (status IN ('proposed','approved','active','retired','rolled_back')),
    scope               TEXT[]          NOT NULL,   -- módulos afectados
    changes             JSONB           NOT NULL,   -- prompt_updates, policy_updates, router_updates
    experiment_id       UUID,
    lift_quality_pct    NUMERIC(5,2),
    lift_efficiency_pct NUMERIC(5,2),
    lift_satisfaction_pct NUMERIC(5,2),
    statistical_confidence NUMERIC(4,3),
    proposed_at         TIMESTAMPTZ     NOT NULL DEFAULT now(),
    activated_at        TIMESTAMPTZ,
    retired_at          TIMESTAMPTZ,
    proposed_by         VARCHAR(80)     NOT NULL DEFAULT 'pattern-miner',
    approved_by         VARCHAR(80)
);

CREATE INDEX idx_doctrines_status   ON doctrines (status);
CREATE INDEX idx_doctrines_scope    ON doctrines USING GIN (scope);

-- =============================================================
-- 8. EXPERIMENTOS A/B
-- =============================================================
CREATE TABLE IF NOT EXISTS experiments (
    experiment_id       UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    doctrine_id         UUID            NOT NULL REFERENCES doctrines(doctrine_id),
    status              VARCHAR(20)     NOT NULL DEFAULT 'designed'
                            CHECK (status IN ('designed','running','concluded','archived')),
    treatment_cohort_pct NUMERIC(4,1)  NOT NULL DEFAULT 5.0,
    min_duration_days   INTEGER         NOT NULL DEFAULT 7,
    significance_target NUMERIC(4,3)   NOT NULL DEFAULT 0.05,
    baseline_kpis       JSONB           NOT NULL DEFAULT '{}',
    treatment_kpis      JSONB           NOT NULL DEFAULT '{}',
    winner              VARCHAR(20)     CHECK (winner IN ('treatment','control','inconclusive')),
    started_at          TIMESTAMPTZ,
    concluded_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

-- =============================================================
-- 9. PATRONES DETECTADOS
-- =============================================================
CREATE TABLE IF NOT EXISTS patterns (
    pattern_id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    status              VARCHAR(20)     NOT NULL DEFAULT 'detected'
                            CHECK (status IN ('detected','validated','promoted','discarded')),
    description         TEXT            NOT NULL,
    affected_modules    TEXT[],
    signal_strength     NUMERIC(4,3),
    sample_size         INTEGER,
    cluster_ids         TEXT[],
    raw_data            JSONB           NOT NULL DEFAULT '{}',
    detected_at         TIMESTAMPTZ     NOT NULL DEFAULT now(),
    promoted_to_doctrine UUID           REFERENCES doctrines(doctrine_id)
);

-- =============================================================
-- 10. COMPLIANCE & GUARDRAILS
-- =============================================================
CREATE TABLE IF NOT EXISTS compliance_rules (
    rule_id             UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name           VARCHAR(120)    NOT NULL UNIQUE,
    rule_type           VARCHAR(40)     NOT NULL,
    condition           JSONB           NOT NULL,
    action              VARCHAR(20)     NOT NULL CHECK (action IN ('block','modify','flag')),
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS guardrail_events (
    id                  BIGSERIAL       PRIMARY KEY,
    rule_id             UUID            REFERENCES compliance_rules(rule_id),
    correlation_id      UUID,
    tenant_id           VARCHAR(80),
    action_taken        VARCHAR(20)     NOT NULL,
    context             JSONB           NOT NULL DEFAULT '{}',
    occurred_at         TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_guardrail_correlation ON guardrail_events (correlation_id);
CREATE INDEX idx_guardrail_tenant      ON guardrail_events (tenant_id, occurred_at DESC);

-- =============================================================
-- 11. KPI ROLLUPS (para dashboard de telemetría)
-- =============================================================
CREATE TABLE IF NOT EXISTS kpi_rollups (
    id                  BIGSERIAL       PRIMARY KEY,
    window_type         VARCHAR(10)     NOT NULL CHECK (window_type IN ('hourly','daily','weekly')),
    window_start        TIMESTAMPTZ     NOT NULL,
    kpi_name            VARCHAR(80)     NOT NULL,
    value               NUMERIC(12,4)   NOT NULL,
    unit                VARCHAR(20),
    metadata            JSONB           NOT NULL DEFAULT '{}',
    computed_at         TIMESTAMPTZ     NOT NULL DEFAULT now(),
    UNIQUE (window_type, window_start, kpi_name)
);

CREATE INDEX idx_kpi_rollups_name   ON kpi_rollups (kpi_name, window_start DESC);

-- =============================================================
-- 12. AUDIT FINDINGS
-- =============================================================
CREATE TABLE IF NOT EXISTS audit_findings (
    finding_id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    finding_type        VARCHAR(60)     NOT NULL,
    severity            VARCHAR(10)     NOT NULL CHECK (severity IN ('info','warning','critical')),
    status              VARCHAR(20)     NOT NULL DEFAULT 'open'
                            CHECK (status IN ('open','investigating','resolved','dismissed')),
    description         TEXT            NOT NULL,
    affected_module     VARCHAR(80),
    evidence            JSONB           NOT NULL DEFAULT '{}',
    opened_by           VARCHAR(80)     NOT NULL DEFAULT 'auditor',
    opened_at           TIMESTAMPTZ     NOT NULL DEFAULT now(),
    resolved_at         TIMESTAMPTZ
);

CREATE INDEX idx_audit_findings_status   ON audit_findings (status, severity);
CREATE INDEX idx_audit_findings_module   ON audit_findings (affected_module);
