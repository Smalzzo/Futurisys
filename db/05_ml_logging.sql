-- 05_ml_logging.sql
-- Schéma et tables de traçabilité pour le service ML (PostgreSQL 16+)

CREATE SCHEMA IF NOT EXISTS ml_logs;

DROP TABLE IF EXISTS ml_logs.model_metadata CASCADE;

-- =========================
-- Table: prediction_log
-- =========================
DROP TABLE IF EXISTS ml_logs.prediction_log CASCADE;
CREATE TABLE IF NOT EXISTS ml_logs.prediction_log (
    id              BIGSERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    endpoint        TEXT        NOT NULL,               
    requested_by    TEXT,                               
    employee_id     BIGINT,                             
    latency_ms      INTEGER,                            
    status          TEXT        NOT NULL DEFAULT 'OK',  
    payload         JSONB       NOT NULL,               
    output          JSONB       NOT NULL                
);

-- Index: requêtes fréquentes
CREATE INDEX IF NOT EXISTS ix_prediction_created_at       ON ml_logs.prediction_log (created_at);
CREATE INDEX IF NOT EXISTS ix_prediction_employee         ON ml_logs.prediction_log (employee_id);
CREATE INDEX IF NOT EXISTS gin_prediction_payload         ON ml_logs.prediction_log USING gin (payload jsonb_path_ops);
CREATE INDEX IF NOT EXISTS gin_prediction_output          ON ml_logs.prediction_log USING gin (output  jsonb_path_ops);

-- =========================
-- Table: error_log
-- =========================
DROP TABLE IF EXISTS ml_logs.error_log CASCADE;
CREATE TABLE IF NOT EXISTS ml_logs.error_log (
    id              BIGSERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    endpoint        TEXT,                               
    http_status     INTEGER,                            
    error_class     TEXT,                               
    error_message   TEXT,                               
    context         JSONB       NOT NULL DEFAULT '{}'::jsonb  
);

CREATE INDEX IF NOT EXISTS ix_error_created_at            ON ml_logs.error_log (created_at);
CREATE INDEX IF NOT EXISTS gin_error_context              ON ml_logs.error_log USING gin (context jsonb_path_ops);

