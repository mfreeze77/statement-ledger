CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
        CREATE VIRTUAL TABLE IF NOT EXISTS claim_search USING fts5(proposition_id UNINDEXED,text,scope,tokenize='unicode61');
        CREATE TABLE IF NOT EXISTS provider_receipts(
          id TEXT PRIMARY KEY, request_hash TEXT NOT NULL, attempt INTEGER NOT NULL,
          http_status INTEGER, body BLOB NOT NULL, body_sha256 TEXT NOT NULL,
          truncated INTEGER NOT NULL, captured_at TEXT NOT NULL, request_metadata TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS payload_proposition ON revisions(kind,json_extract(payload,'$.proposition_id'));
        CREATE INDEX IF NOT EXISTS correction_target ON revisions(kind,json_extract(payload,'$.target_kind'),json_extract(payload,'$.target_id'));
        CREATE INDEX IF NOT EXISTS decision_cache_key ON revisions(json_extract(payload,'$.request_hash'))
          WHERE kind='decision_run';
