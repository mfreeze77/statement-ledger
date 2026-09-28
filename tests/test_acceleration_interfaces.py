import hashlib
import json
import shutil
import sqlite3
import wave

import pytest
from fastapi.testclient import TestClient

from statement_ledger.acceleration_demo import seed_acceleration
from statement_ledger.api import create_app
from statement_ledger.cli import main
from statement_ledger.localization import plan_localization
from statement_ledger.media_work import process_localization
from statement_ledger.models import RightsGrant
from statement_ledger.speech import verify_speaker_clips
from statement_ledger.store import Store
from statement_ledger.util import digest

TOKEN = "acceleration-test-token-only-" + "a" * 32


@pytest.fixture
def accelerated(ledger):
    ledger.fixture = seed_acceleration(ledger)
    return ledger


@pytest.fixture
def client(accelerated):
    with TestClient(create_app(accelerated.store.path, TOKEN)) as c:
        yield c


def auth():
    return {"Authorization": "Bearer " + TOKEN}


def test_new_api_routes_require_auth(client):
    for url in [
        "/api/profiles/build",
        "/api/localization/plan",
        "/api/localization/combine",
        "/api/claims/search",
        "/api/claims/match",
    ]:
        assert client.post(url, json={}).status_code == 401


def test_api_claim_search(client):
    result = client.post(
        "/api/claims/search", headers=auth(), json={"text": "Synthetic Lab samples"}
    )
    assert result.status_code == 200 and result.json()["items"]


def test_api_localization_is_default_shadow(client):
    r = client.post(
        "/api/localization/plan",
        headers=auth(),
        json={"profile_id": "profile-demo", "transcript_id": "style-heldout-transcript"},
    )
    assert r.status_code == 200
    assert r.json()["run"]["payload"]["selected_audio_ms"] == 600000


def test_api_profile_build(client, accelerated):
    p = accelerated.fixture["profile_input"]
    p = {**p, "profile_id": "api-profile"}
    r = client.post("/api/profiles/build", headers=auth(), json=p)
    assert r.status_code == 200 and r.json()["payload"]["features"]


def test_api_status_has_no_key(client, monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "never-return-me")
    r = client.get("/api/acceleration/status", headers=auth())
    assert r.status_code == 200 and "never-return-me" not in r.text


def test_api_jev_disabled(client, monkeypatch):
    monkeypatch.delenv("SL_ENABLE_JEV", raising=False)
    r = client.post(
        "/api/localization/plan",
        headers=auth(),
        json={
            "profile_id": "profile-demo",
            "transcript_id": "style-heldout-transcript",
            "use_jev": True,
        },
    )
    assert r.status_code == 422


def test_cli_demo_and_search(tmp_path, capsys):
    db = str(tmp_path / "demo.sqlite3")
    assert main(["--db", db, "demo-acceleration"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["synthetic"] and result["evaluation"]["target_time_recall"] == 1
    assert main(["--db", db, "search-claims", "Synthetic Lab"]) == 0
    assert json.loads(capsys.readouterr().out)["items"]


def test_cli_profile_and_localization(accelerated, tmp_path, capsys):
    p = tmp_path / "profile.json"
    p.write_text(json.dumps({**accelerated.fixture["profile_input"], "profile_id": "cli-profile"}))
    assert main(["--db", accelerated.store.path, "build-profile", str(p)]) == 0
    capsys.readouterr()
    q = tmp_path / "localize.json"
    q.write_text(
        json.dumps(
            {
                "profile_id": "cli-profile",
                "transcript_id": "style-heldout-transcript",
                "config": {"mode": "assist"},
            }
        )
    )
    assert main(["--db", accelerated.store.path, "localize", str(q)]) == 0
    assert json.loads(capsys.readouterr().out)["run"]["payload"]["selected_audio_ms"] < 600000


def test_cli_evaluation_asset_mismatch(accelerated, tmp_path, capsys):
    p = tmp_path / "labels.json"
    p.write_text(json.dumps({"asset_id": "wrong", "target_intervals": []}))
    assert (
        main(
            [
                "--db",
                accelerated.store.path,
                "evaluate-localization",
                accelerated.fixture["assist"]["run"]["id"],
                str(p),
            ]
        )
        == 2
    )


def test_cli_estimate_cost(tmp_path, capsys):
    p = tmp_path / "cost.json"
    p.write_text(
        json.dumps({"duration_ms": 60000, "selected_audio_ms": 30000, "audio_cost_per_minute": 0.1})
    )
    assert main(["--db", str(tmp_path / "cost.sqlite3"), "estimate-cost", str(p)]) == 0
    assert json.loads(capsys.readouterr().out)["estimated_savings"] == 0.05


def test_existing_schema_additive_migration(tmp_path):
    # Build the exact original store schema, insert original canonical fields only.
    from statement_ledger.store import SCHEMA

    path = tmp_path / "old.sqlite3"
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    p = {
        "id": "old-prop",
        "text": "An old preserved claim",
        "kind": "empirical",
        "scope": {
            "entity": None,
            "metric": None,
            "geography": None,
            "period": None,
            "unit": None,
            "baseline": None,
            "comparator": None,
            "quantity": None,
            "definition": None,
        },
    }
    deps = []
    h = digest({"payload": p, "dependencies": deps})
    db.execute(
        "INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?)",
        (
            "proposition",
            "old-prop",
            1,
            json.dumps(p),
            h,
            "[]",
            "2026-01-01T00:00:00+00:00",
            "fixture",
        ),
    )
    db.execute("INSERT INTO heads VALUES(?,?,?,0,NULL)", ("proposition", "old-prop", 1))
    db.commit()
    db.close()
    store = Store(path, initialize=True)
    try:
        assert store.get("proposition", "old-prop")["payload"] == p
        assert store.get("proposition", "old-prop")["hash"] == h
        assert store.db.execute("SELECT count(*) FROM claim_search").fetchone()[0] == 1
        assert store.verify_records()["valid"]
    finally:
        store.close()


def test_optional_acoustic_verification_advisory_only(tmp_path):
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    a.write_bytes(b"a")
    b.write_bytes(b"b")
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    grant = RightsGrant(
        id="g",
        source_id="manual_import",
        basis="synthetic",
        allowed=["process_audio", "process_biometrics"],
        reviewed_by="test",
    )

    class Model:
        def verify_files(self, *args):
            return 0.92, True

    r = verify_speaker_clips(
        a,
        b,
        grant,
        grant,
        model_directory=model_dir,
        model_revision="fixture",
        model_factory=lambda **k: Model(),
    )
    assert (
        r["cosine_similarity"] == 0.92 and not r["identity_confirmed"] and r["probability"] is None
    )


def test_acoustic_biometrics_permission_required(tmp_path):
    grant = RightsGrant(
        id="g",
        source_id="manual_import",
        basis="synthetic",
        allowed=["process_audio"],
        reviewed_by="test",
    )
    with pytest.raises(ValueError, match="process_biometrics"):
        verify_speaker_clips(
            tmp_path / "a",
            tmp_path / "b",
            grant,
            grant,
            model_directory=tmp_path,
            model_revision="fixture",
        )


def make_short_run(ledger, tmp_path):
    source = tmp_path / "source.wav"
    with wave.open(str(source), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b"\x00\x00" * 16000 * 2)
    ledger.put(
        "asset",
        {
            "id": "media-work-asset",
            "event_id": "style-heldout-event",
            "observation_id": "obs-style-heldout-event",
            "rights_id": "demo-rights",
            "url": "https://example.org/synthetic-audio",
            "duration_ms": 2000,
            "content_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        },
    )
    ledger.put(
        "transcript",
        {
            "id": "media-work-transcript",
            "asset_id": "media-work-asset",
            "engine": "synthetic",
            "segments": [
                {
                    "start_ms": 0,
                    "end_ms": 2000,
                    "speaker_label": "unassigned",
                    "text": "Look at the underlying record, that is the distinction.",
                }
            ],
        },
    )
    r = plan_localization(ledger, "profile-demo", "media-work-transcript")
    return source, r["id"]


@pytest.mark.skipif(
    not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="FFmpeg required"
)
def test_localization_clips_real_synthetic_audio(accelerated, tmp_path):
    source, rid = make_short_run(accelerated, tmp_path)
    manifest = process_localization(accelerated, rid, source, tmp_path / "work", tmp_path)
    assert manifest["status"] == "completed" and len(manifest["items"]) == 1
    assert manifest["items"][0]["probed_duration_ms"] == pytest.approx(2000, abs=100)
    assert not manifest["identities_confirmed"]


def test_media_work_hash_mismatch(accelerated, tmp_path):
    source, rid = make_short_run(accelerated, tmp_path)
    source.write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash"):
        process_localization(accelerated, rid, source, tmp_path / "work", tmp_path)


def test_media_work_keeps_source_timebase_and_local_labels(accelerated, tmp_path):
    source, rid = make_short_run(accelerated, tmp_path)

    def clipper(src, dst, *args):
        dst.write_bytes(b"clip")

    def transcriber(*a, **k):
        return {"segments": [{"start": 0, "end": 1, "text": "Words", "speaker": "unassigned"}]}

    def diarizer(*a, **k):
        return {"turns": [{"start_ms": 0, "end_ms": 1000, "speaker_label": "speaker_0"}]}

    r = process_localization(
        accelerated,
        rid,
        source,
        tmp_path / "work",
        tmp_path,
        transcribe=True,
        diarize=True,
        clipper=clipper,
        transcriber=transcriber,
        diarizer=diarizer,
    )
    seg = r["items"][0]["processing"]["segments"][0]
    assert seg["speaker"] == "window-0000:speaker_0" and seg["source_start_ms"] == 0


def test_media_work_failure_leaves_receipt(accelerated, tmp_path):
    source, rid = make_short_run(accelerated, tmp_path)

    def broken(*a, **k):
        raise RuntimeError("synthetic failure")

    with pytest.raises(RuntimeError):
        process_localization(accelerated, rid, source, tmp_path / "work", tmp_path, clipper=broken)
    assert json.loads((tmp_path / "work/manifest.json").read_text())["status"] == "failed"
