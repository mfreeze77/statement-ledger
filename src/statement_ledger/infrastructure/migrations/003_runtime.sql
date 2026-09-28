CREATE TABLE IF NOT EXISTS work_jobs (
 id TEXT PRIMARY KEY, dedupe_key TEXT UNIQUE NOT NULL, payload TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('pending','running','succeeded','failed','cancelled','blocked')),
 attempts INTEGER NOT NULL DEFAULT 0, max_attempts INTEGER NOT NULL,
 available REAL NOT NULL, lease_until REAL, lease_token TEXT, capability TEXT NOT NULL,
 cancel_requested INTEGER NOT NULL DEFAULT 0, result TEXT, error_code TEXT, created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS work_ready ON work_jobs(state,capability,available);
CREATE TABLE IF NOT EXISTS work_attempts (
 id TEXT PRIMARY KEY, job_id TEXT NOT NULL REFERENCES work_jobs(id),
 ordinal INTEGER NOT NULL, started_at REAL NOT NULL, finished_at REAL,
 status TEXT NOT NULL, duration_ms REAL, error_code TEXT,
 UNIQUE(job_id,ordinal)
);
CREATE TABLE IF NOT EXISTS artifact_refs (
 key TEXT PRIMARY KEY, sha256 TEXT NOT NULL, size INTEGER NOT NULL,
 created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS job_artifacts (
 job_id TEXT NOT NULL REFERENCES work_jobs(id), key TEXT NOT NULL REFERENCES artifact_refs(key),
 PRIMARY KEY(job_id,key)
);
CREATE TABLE IF NOT EXISTS provider_operations (
 id TEXT PRIMARY KEY, request_hash TEXT NOT NULL, provider TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('started','completed','unknown','cancelled')),
 estimated_micro_usd INTEGER NOT NULL, actual_micro_usd INTEGER,
 usage TEXT, started_at REAL NOT NULL, finished_at REAL,
 cost_status TEXT NOT NULL CHECK(cost_status IN ('estimated','actual','unknown'))
);
