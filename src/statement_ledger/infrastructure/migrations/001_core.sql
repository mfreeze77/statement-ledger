PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS revisions (
 kind TEXT NOT NULL, id TEXT NOT NULL, revision INTEGER NOT NULL,
 payload TEXT NOT NULL, hash TEXT NOT NULL, dependencies TEXT NOT NULL,
 created_at TEXT NOT NULL, actor TEXT NOT NULL,
 PRIMARY KEY(kind,id,revision));
CREATE TABLE IF NOT EXISTS heads (
 kind TEXT NOT NULL, id TEXT NOT NULL, revision INTEGER NOT NULL,
 stale INTEGER NOT NULL DEFAULT 0, stale_reason TEXT,
 PRIMARY KEY(kind,id), FOREIGN KEY(kind,id,revision) REFERENCES revisions(kind,id,revision));
CREATE TABLE IF NOT EXISTS dependencies (
 child_kind TEXT NOT NULL, child_id TEXT NOT NULL,
 parent_kind TEXT NOT NULL, parent_id TEXT NOT NULL, parent_revision INTEGER NOT NULL,
 PRIMARY KEY(child_kind,child_id,parent_kind,parent_id));
CREATE INDEX IF NOT EXISTS dependencies_parent ON dependencies(parent_kind,parent_id);
CREATE TABLE IF NOT EXISTS audit (
 sequence INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
 previous_hash TEXT NOT NULL, hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS outbox (
 sequence INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
 state TEXT NOT NULL DEFAULT 'pending');
