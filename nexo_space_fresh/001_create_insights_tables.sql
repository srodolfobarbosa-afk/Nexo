-- Migrations: cria tabelas para insights
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS insights_pending (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz DEFAULT now(),
  origem text,
  ordem text,
  resultado jsonb,
  insight_raw text,
  embedding vector(1536),
  model_name text,
  model_meta jsonb,
  status text DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS insights_verified (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  added_at timestamptz DEFAULT now(),
  insight text,
  embedding vector(1536),
  provenance jsonb,
  trust_score numeric,
  tags text[],
  auditoria jsonb
);

CREATE INDEX IF NOT EXISTS idx_insights_verified_embedding ON insights_verified USING ivfflat (embedding) WITH (lists = 100);