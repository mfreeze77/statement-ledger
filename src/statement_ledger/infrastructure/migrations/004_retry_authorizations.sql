-- Explicit owner permission for ONE additional reservation, never automatic replay.
CREATE TABLE provider_retry_authorizations (
 id TEXT PRIMARY KEY,
 request_hash TEXT NOT NULL,
 provider TEXT NOT NULL,
 basis_sha256 TEXT NOT NULL,
 actor TEXT NOT NULL,
 reason TEXT NOT NULL,
 authorized_at REAL NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('issued','consumed','revoked')),
 consumed_by TEXT REFERENCES provider_operations(id),
 finished_at REAL
);
CREATE UNIQUE INDEX provider_one_pending_authorization
 ON provider_retry_authorizations(provider,request_hash) WHERE state='issued';
