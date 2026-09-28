import pytest
from fastapi.testclient import TestClient

from statement_ledger.api import create_app
from statement_ledger.demo import PERSON_ID, seed
from statement_ledger.service import Ledger
from statement_ledger.store import Store

TOKEN = "a" * 40


@pytest.fixture
def client(tmp_path):
    db = tmp_path / "api.sqlite3"
    s = Store(db, initialize=True)
    seed(Ledger(s))
    s.close()
    with TestClient(create_app(str(db), TOKEN)) as c:
        yield c


def auth():
    return {"Authorization": f"Bearer {TOKEN}"}


def test_api_token_required_at_start(monkeypatch):
    monkeypatch.delenv("SL_API_TOKEN", raising=False)
    with pytest.raises(RuntimeError):
        create_app("test", "")


def test_health_and_shell_only_public(client):
    assert client.get("/healthz").status_code == 200
    assert client.get("/").status_code == 200
    assert client.get("/api/counts").status_code == 401
    assert client.get("/api/openapi.json").status_code == 401


def test_no_browser_stored_token(client):
    script = client.get("/static/app.js").text
    assert "localStorage" not in script and "sessionStorage" not in script
    assert "innerHTML" not in script


def test_sources(client):
    assert len(client.get("/api/sources", headers=auth()).json()["sources"]) >= 47


def test_ledger(client):
    r = client.get(f"/api/people/{PERSON_ID}/ledger", headers=auth())
    assert r.status_code == 200
    assert r.json()["counts"]["distinct_aligned_assertion_occurrences"] == 2


def test_write_auth_and_conflict(client):
    path = "/api/records/person"
    data = {"record": {"id": "test", "display_name": "Test"}}
    assert client.post(path, json=data).status_code == 401
    assert client.post(path, json=data, headers=auth()).status_code == 200
    assert client.post(path, json=data, headers=auth()).status_code == 409


def test_bad_record_422(client):
    assert (
        client.post(
            "/api/records/person",
            headers=auth(),
            json={"record": {"display_name": "x", "illegal_extra": 1}},
        ).status_code
        == 422
    )


def test_historical_read(client):
    r = client.get(f"/api/records/person/{PERSON_ID}?revision=1", headers=auth())
    assert r.json()["historical_revision"] is True


def test_discovery_plan_has_no_execution(client):
    r = client.post("/api/discovery/plan", headers=auth(), json={"name": "Example"})
    assert r.status_code == 200 and r.json()["automatic_execution"] is False


def test_clip_plan(client):
    r = client.post(
        "/api/clips/plan",
        headers=auth(),
        json={"start_ms": 1000, "end_ms": 2000, "duration_ms": 5000},
    )
    assert r.json()["context_start_ms"] == 0 and r.json()["context_end_ms"] == 5000


def test_invalid_clip_plan(client):
    assert (
        client.post(
            "/api/clips/plan",
            headers=auth(),
            json={"start_ms": 2000, "end_ms": 1000, "duration_ms": 5000},
        ).status_code
        == 422
    )


def test_headers(client):
    r = client.get("/")
    assert r.headers["Cache-Control"] == "no-store"
    assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]


def test_bounded_request(client):
    assert (
        client.post(
            "/api/records/person", headers=auth(), content=b"x" * (4 * 1024 * 1024 + 1)
        ).status_code
        == 413
    )


def test_no_static_path_traversal(client):
    assert client.get("/static/secret.env").status_code == 404


def test_openapi_available_authenticated(client):
    assert (
        client.get("/api/openapi.json", headers=auth()).json()["info"]["title"]
        == "Statement Ledger"
    )
