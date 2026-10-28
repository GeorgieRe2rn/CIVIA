CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sources (
    id VARCHAR(100) PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    retrieved_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS territories (
    id VARCHAR(5) PRIMARY KEY,
    name VARCHAR(160) NOT NULL,
    level VARCHAR(32) NOT NULL,
    state_id VARCHAR(2) NOT NULL,
    code_system VARCHAR(64) NOT NULL,
    geometry geometry(Geometry, 4326),
    CONSTRAINT territories_ine_id CHECK (id ~ '^14[0-9]{3}$'),
    CONSTRAINT territories_state CHECK (state_id = '14')
);

CREATE TABLE IF NOT EXISTS elections (
    election_id VARCHAR(40) PRIMARY KEY,
    year INTEGER NOT NULL,
    election_date DATE NOT NULL,
    election_type VARCHAR(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS participation (
    territory_id VARCHAR(5) NOT NULL REFERENCES territories(id),
    election_id VARCHAR(40) NOT NULL REFERENCES elections(election_id),
    nominal_count INTEGER NOT NULL CHECK (nominal_count >= 0),
    voted_count INTEGER NOT NULL CHECK (voted_count >= 0),
    not_voted_count INTEGER NOT NULL CHECK (not_voted_count >= 0),
    unknown_count INTEGER NOT NULL CHECK (unknown_count >= 0),
    known_count INTEGER NOT NULL CHECK (known_count >= 0),
    participation_pct DOUBLE PRECISION NOT NULL CHECK (participation_pct BETWEEN 0 AND 100),
    abstention_pct DOUBLE PRECISION NOT NULL CHECK (abstention_pct BETWEEN 0 AND 100),
    unknown_pct DOUBLE PRECISION NOT NULL CHECK (unknown_pct BETWEEN 0 AND 100),
    participation_lower_pct DOUBLE PRECISION NOT NULL CHECK (participation_lower_pct BETWEEN 0 AND 100),
    participation_upper_pct DOUBLE PRECISION NOT NULL CHECK (participation_upper_pct BETWEEN 0 AND 100),
    source_id VARCHAR(100) NOT NULL REFERENCES sources(id),
    data_status VARCHAR(16) NOT NULL,
    denominator VARCHAR(16) NOT NULL,
    PRIMARY KEY (territory_id, election_id),
    CONSTRAINT participation_counts CHECK (nominal_count = voted_count + not_voted_count + unknown_count)
);

CREATE TABLE IF NOT EXISTS model_versions (
    model_version VARCHAR(160) PRIMARY KEY,
    source_version VARCHAR(160) NOT NULL,
    strategy VARCHAR(32) NOT NULL,
    evaluation_mode VARCHAR(64) NOT NULL,
    mae_pp DOUBLE PRECISION NOT NULL CHECK (mae_pp >= 0),
    baseline_mae_pp DOUBLE PRECISION NOT NULL CHECK (baseline_mae_pp >= 0),
    n_test INTEGER NOT NULL CHECK (n_test > 0),
    interval_json JSONB,
    warnings_json JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS predictions (
    territory_id VARCHAR(5) NOT NULL REFERENCES territories(id),
    election_id VARCHAR(40) NOT NULL REFERENCES elections(election_id),
    model_version VARCHAR(160) NOT NULL REFERENCES model_versions(model_version),
    abstention_pct DOUBLE PRECISION NOT NULL CHECK (abstention_pct BETWEEN 0 AND 100),
    participation_pct DOUBLE PRECISION NOT NULL CHECK (participation_pct BETWEEN 0 AND 100),
    mae_pp DOUBLE PRECISION NOT NULL CHECK (mae_pp >= 0),
    baseline_mae_pp DOUBLE PRECISION NOT NULL CHECK (baseline_mae_pp >= 0),
    n_test INTEGER NOT NULL CHECK (n_test > 0),
    interval_json JSONB,
    warnings_json JSONB NOT NULL,
    strategy VARCHAR(32) NOT NULL,
    evaluation_mode VARCHAR(64) NOT NULL,
    PRIMARY KEY (territory_id, election_id)
);

CREATE INDEX IF NOT EXISTS ix_participation_election ON participation(election_id);
CREATE INDEX IF NOT EXISTS ix_predictions_election ON predictions(election_id);
