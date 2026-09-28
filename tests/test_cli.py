import json
from statement_ledger.cli import main
from statement_ledger.store import Store

def test_demo_cli(tmp_path,capsys):
    assert main(["--db",str(tmp_path/"test.db"),"demo"])==0
    result=json.loads(capsys.readouterr().out)
    assert result["counts"]["distinct_aligned_assertion_occurrences"]==2

def test_discovery_does_not_run_without_key(tmp_path,monkeypatch):
    monkeypatch.delenv("YOUTUBE_API_KEY",raising=False)
    assert main(["discover","--source","youtube","--query","Example","--out",str(tmp_path/"out")])==2

def test_schemas_export(tmp_path,capsys):
    assert main(["schema","--out",str(tmp_path/"schemas")])==0
    assert len(list((tmp_path/"schemas").glob("*.json")))==20

def test_sqlite_backup_restore(tmp_path,capsys):
    db=tmp_path/"original.db";backup=tmp_path/"backup.db"
    assert main(["--db",str(db),"demo"])==0
    assert main(["--db",str(db),"backup",str(backup)])==0
    s=Store(backup)
    try:assert s.verify_audit()["valid"] and s.verify_records()["valid"]
    finally:s.close()

def test_full_standalone_plan(tmp_path,capsys):
    assert main(["plan","--person","Scott Jennings","--out",str(tmp_path/"plan.json")])==0
    p=json.loads((tmp_path/"plan.json").read_text())
    assert len(p["work"])>=47 and p["automatic_execution"] is False

def test_plan_queries_evidence_sources_by_claim_not_name(tmp_path,capsys):
    assert main(["plan","--person","Example Person","--out",str(tmp_path/"plan.json")])==0
    work={w["source_id"]:w for w in json.loads((tmp_path/"plan.json").read_text())["work"]}
    for sid in ("tv_news_archive","subject_social_accounts","subject_written_work","podcasts_radio"):
        assert work[sid]["queries"]==["Example Person"] and work[sid]["state"]=="access_or_adapter_required"
    evidence=[w for w in work.values() if w["source_role"]=="primary_evidence"]
    assert {"congress_gov","govinfo","bls","census","fred","openfec","courtlistener","official_publications"}<={w["source_id"] for w in evidence}
    assert all(w["queries"]==[] and w["state"]=="claim_driven" for w in evidence)
