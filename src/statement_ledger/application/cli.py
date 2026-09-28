from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

from statement_ledger.application.ledger import Ledger
from statement_ledger.contracts.models import KINDS, RightsGrant
from statement_ledger.contracts.source_catalog import sources
from statement_ledger.core.util import digest
from statement_ledger.infrastructure.sqlite_store import Store
from statement_ledger.pillars.discovery.http import (
    AAPBClient,
    ArchiveClient,
    FactCheckClient,
    YouTubeClient,
)


def emit(value):
    print(json.dumps(value, indent=2, ensure_ascii=False))


def save(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Standalone, source-bound public-statement research ledger"
    )
    p.add_argument("--db", default=None)
    p.add_argument("--config-file", type=Path)
    p.add_argument("--env-file", type=Path)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("sources")
    sub.add_parser("demo")
    sub.add_parser("verify")
    a = sub.add_parser("serve")
    a.add_argument("--host")
    a.add_argument("--port", type=int)
    a = sub.add_parser("plan")
    a.add_argument("--person", required=True)
    a.add_argument("--alias", action="append", default=[])
    a.add_argument("--out", type=Path)
    a = sub.add_parser("seed-subject")
    a.add_argument("config", type=Path)
    a = sub.add_parser("put")
    a.add_argument("kind", choices=KINDS)
    a.add_argument("file", type=Path)
    a.add_argument("--expected-revision", type=int, default=0)
    a = sub.add_parser("get")
    a.add_argument("kind", choices=KINDS)
    a.add_argument("id")
    a.add_argument("--revision", type=int)
    a = sub.add_parser("ledger")
    a.add_argument("person_id")
    a = sub.add_parser("export")
    a.add_argument("out", type=Path)
    a = sub.add_parser("backup")
    a.add_argument("out", type=Path)
    a = sub.add_parser("schema")
    a.add_argument("--out", type=Path, default=Path("contracts"))
    a = sub.add_parser("ingest")
    a.add_argument("--source", required=True)
    a.add_argument("--rights", required=True)
    a.add_argument("--file", type=Path, required=True)
    a.add_argument("--mode", choices=["jsonl", "json"], default="jsonl")
    a.add_argument("--max-records", type=int, default=10000)
    a.add_argument("--archive-root", type=Path, default=Path("data/raw"))
    a = sub.add_parser("import-transcript")
    a.add_argument("--asset", required=True)
    a.add_argument("--id", required=True)
    a.add_argument("--file", type=Path, required=True)
    a.add_argument("--format", choices=["vtt", "srt", "asr"], required=True)
    a.add_argument("--engine", default="operator-import")
    a.add_argument("--expected-revision", type=int, default=0)
    a = sub.add_parser("discover")
    a.add_argument(
        "--source",
        choices=["youtube", "google_fact_check", "internet_archive", "aapb"],
        required=True,
    )
    a.add_argument("--query", required=True)
    a.add_argument("--pages", type=int, default=1)
    a.add_argument("--cursor")
    a.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("clip")
    a.add_argument("--asset", required=True)
    a.add_argument("--input", type=Path, required=True)
    a.add_argument("--output", type=Path, required=True)
    a.add_argument("--root", type=Path, required=True)
    a.add_argument("--start-ms", type=int, required=True)
    a.add_argument("--end-ms", type=int, required=True)
    a.add_argument("--padding-ms", type=int, default=15000)
    a = sub.add_parser("speech")
    a.add_argument("--asset", required=True)
    a.add_argument("--input", type=Path, required=True)
    a.add_argument("--output", type=Path, required=True)
    a.add_argument("--model", default="small")
    a.add_argument("--diarize", action="store_true")
    sub.add_parser("demo-acceleration")
    sub.add_parser("reindex-claims")
    a = sub.add_parser("build-profile")
    a.add_argument("config", type=Path)
    a = sub.add_parser("localize")
    a.add_argument("config", type=Path)
    a.add_argument("--jev", action="store_true")
    a.add_argument("--out", type=Path)
    a = sub.add_parser("search-claims")
    a.add_argument("query")
    a.add_argument("--scope", type=Path)
    a.add_argument("--limit", type=int, default=20)
    a = sub.add_parser("match-claims")
    a.add_argument("proposition_id")
    a.add_argument("candidate_ids", nargs="+")
    a = sub.add_parser("evaluate-localization")
    a.add_argument("run_id")
    a.add_argument("labels", type=Path)
    a = sub.add_parser("calibration-report")
    a.add_argument("labels", type=Path)
    a = sub.add_parser("estimate-cost")
    a.add_argument("config", type=Path)
    a = sub.add_parser("verify-speaker")
    a.add_argument("--reference-file", type=Path, required=True)
    a.add_argument("--candidate-file", type=Path, required=True)
    a.add_argument("--reference-rights", required=True)
    a.add_argument("--candidate-rights", required=True)
    a.add_argument("--model-dir", type=Path, required=True)
    a.add_argument("--model-revision", required=True)
    a.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("process-localization")
    a.add_argument("run_id")
    a.add_argument("--input", type=Path, required=True)
    a.add_argument("--output-dir", type=Path, required=True)
    a.add_argument("--root", type=Path, required=True)
    a.add_argument("--transcribe", action="store_true")
    a.add_argument("--diarize", action="store_true")
    a.add_argument("--model", default="small")
    a = sub.add_parser("refresh-profile")
    a.add_argument("profile_id")
    a.add_argument("--background-person", action="append", default=[])
    a.add_argument("--holdout-event", action="append", default=[])
    a = sub.add_parser("seed-claims")
    a.add_argument("--file", type=Path, required=True)
    a.add_argument("--source", required=True)
    a.add_argument("--rights", required=True)
    a.add_argument("--archive-root", type=Path, default=Path("data/raw"))
    a.add_argument("--max-records", type=int, default=10000)
    from statement_ledger.application.runtime import COMMANDS, add_commands, execute
    from statement_ledger.infrastructure.migrations import migrate
    from statement_ledger.infrastructure.secrets import LocalSecrets
    from statement_ledger.infrastructure.settings import load_settings

    add_commands(sub)
    args = p.parse_args(argv)
    try:
        settings = load_settings(
            config_file=args.config_file,
            env_file=args.env_file,
            overrides={
                key: value
                for key, value in {
                    "db_path": args.db,
                    "host": getattr(args, "host", None),
                    "port": getattr(args, "port", None),
                }.items()
                if value is not None
            },
        )
        secrets = LocalSecrets(env_file=args.env_file)
        args.db = str(settings.database)
        if args.command in COMMANDS:
            result = execute(args, settings)
            emit(result)
            if (
                args.command == "worker"
                and args.once
                and result.get("job")
                and result["job"]["state"] != "succeeded"
            ):
                return 2
            if args.command == "doctor":
                if not result.get("schema_ready") or not result.get("ffmpeg"):
                    return 2
                if args.gpu and not result.get("gpu_available"):
                    return 2
            return 0
        if args.command in {"demo", "demo-acceleration"}:
            migrate(args.db)  # Explicit synthetic bootstrap, never API/worker startup DDL.
        if args.command == "estimate-cost":
            from statement_ledger.application.evaluation import estimate_cost

            emit(estimate_cost(**json.loads(args.config.read_text())))
            return 0
        if args.command == "calibration-report":
            from statement_ledger.application.evaluation import calibration_report

            emit(calibration_report(**json.loads(args.labels.read_text())))
            return 0
        if args.command == "serve":
            import uvicorn

            from statement_ledger.application.api import create_app

            app = create_app(db_path=args.db, settings=settings, token=secrets.value("API_TOKEN"))
            uvicorn.run(app, host=settings.host, port=settings.port)
            return 0
        if args.command == "sources":
            emit(sources())
            return 0
        if args.command == "plan":
            from statement_ledger.pillars.discovery.planner import plan_person

            result = plan_person(args.person, args.alias)
            if args.out:
                save(args.out, result)
            else:
                emit(result)
            return 0
        if args.command == "schema":
            for kind, model in KINDS.items():
                save(args.out / f"{kind}.schema.json", model.model_json_schema())
            emit({"schemas_written": len(KINDS), "directory": str(args.out)})
            return 0
        if args.command == "discover":
            if not 1 <= args.pages <= 100:
                raise ValueError("Page budget must be 1..100")
            factories = {
                "youtube": lambda: YouTubeClient(secrets.value("YOUTUBE_API_KEY")),
                "google_fact_check": lambda: FactCheckClient(secrets.value("FACTCHECK_API_KEY")),
                "internet_archive": ArchiveClient,
                "aapb": AAPBClient,
            }
            cursor = args.cursor
            seen = set()
            total = 0
            with factories[args.source]() as client:
                for i in range(args.pages):
                    if cursor in seen:
                        raise ValueError("Repeated pagination cursor; stopped")
                    seen.add(cursor)
                    if args.source == "internet_archive":
                        page = client.search(args.query, page=int(cursor or 1))
                    elif args.source == "aapb":
                        page = client.search(args.query, start=int(cursor or 0))
                    else:
                        page = client.search(args.query, cursor=cursor)
                    # Query fingerprint prevents unrelated runs overwriting one another.
                    name = f"{args.source}-{digest([args.query, cursor])[:16]}.json"
                    save(args.out / name, page.payload)
                    total += 1
                    cursor = page.next_cursor
                    if not cursor:
                        break
            receipt = {
                "source": args.source,
                "query": args.query,
                "pages": total,
                "next_cursor": cursor,
                "completion": "page_budget_reached"
                if cursor
                else "query_exhausted_not_corpus_complete",
                "ingested": False,
                "rights_review_required": True,
            }
            save(args.out / "receipt.json", receipt)
            emit(receipt)
            return 0
        store = Store(args.db, journal_mode=settings.journal_mode)
        ledger = Ledger(store)
        ledger.settings = settings
        try:
            if args.command == "demo-acceleration":
                from statement_ledger.application.acceleration_demo import seed_acceleration

                emit(seed_acceleration(ledger))
            elif args.command == "seed-claims":
                from statement_ledger.pillars.claims.seeds import import_claim_seeds

                result = import_claim_seeds(
                    ledger,
                    args.file,
                    args.source,
                    args.rights,
                    archive_root=args.archive_root,
                    max_records=args.max_records,
                )
                emit(result)
                return 0 if result["success"] else 2
            elif args.command == "reindex-claims":
                emit(store.rebuild_claim_index())
            elif args.command == "refresh-profile":
                from statement_ledger.pillars.speech.profiles import refresh_profile

                emit(
                    refresh_profile(
                        ledger,
                        args.profile_id,
                        background_person_ids=args.background_person,
                        holdout_event_ids=args.holdout_event,
                    )
                )
            elif args.command == "build-profile":
                from statement_ledger.pillars.speech.profiles import build_profile

                emit(build_profile(ledger, **json.loads(args.config.read_text(encoding="utf-8"))))
            elif args.command == "localize":
                from statement_ledger.application.acceleration import localize

                config = json.loads(args.config.read_text(encoding="utf-8"))
                config["use_jev"] = args.jev
                result = localize(ledger, **config)
                if args.out:
                    save(args.out, result)
                else:
                    emit(result)
            elif args.command == "search-claims":
                from statement_ledger.pillars.claims.library import search_claims

                emit(
                    search_claims(
                        ledger,
                        args.query,
                        scope=json.loads(args.scope.read_text()) if args.scope else None,
                        limit=args.limit,
                    )
                )
            elif args.command == "match-claims":
                from statement_ledger.application.acceleration import match_claims

                emit(match_claims(ledger, args.proposition_id, args.candidate_ids))
            elif args.command == "evaluate-localization":
                from statement_ledger.application.evaluation import evaluate_windows
                from statement_ledger.core.read import current

                run = current(ledger, "localization_run", args.run_id)["payload"]
                profile = current(ledger, "speaker_profile", run["profile_id"])["payload"]
                asset = current(ledger, "asset", run["asset_id"])["payload"]
                labels = json.loads(args.labels.read_text())
                if labels.get("asset_id") != run["asset_id"]:
                    raise ValueError("Labels are for a different asset/timebase")
                emit(
                    evaluate_windows(
                        run["selected_intervals"],
                        labels["target_intervals"],
                        run["duration_ms"],
                        event_id=asset["event_id"],
                        training_event_ids=profile["target_event_ids"]
                        + profile["background_event_ids"],
                        truth_complete=labels.get("truth_complete", False),
                    )
                )
            elif args.command == "calibration-report":
                from statement_ledger.application.evaluation import calibration_report

                emit(calibration_report(**json.loads(args.labels.read_text())))
            elif args.command == "estimate-cost":
                from statement_ledger.application.evaluation import estimate_cost

                emit(estimate_cost(**json.loads(args.config.read_text())))
            elif args.command == "verify-speaker":
                from statement_ledger.core.read import current
                from statement_ledger.infrastructure.providers.speech import verify_speaker_clips

                if args.out.exists():
                    raise ValueError("Output exists")
                r = RightsGrant.model_validate(
                    current(ledger, "rights", args.reference_rights)["payload"]
                )
                c = RightsGrant.model_validate(
                    current(ledger, "rights", args.candidate_rights)["payload"]
                )
                save(
                    args.out,
                    verify_speaker_clips(
                        args.reference_file,
                        args.candidate_file,
                        r,
                        c,
                        model_directory=args.model_dir,
                        model_revision=args.model_revision,
                    ),
                )
                emit({"written": str(args.out), "identity_confirmed": False})
            elif args.command == "process-localization":
                from statement_ledger.pillars.media.execution import process_localization

                emit(
                    process_localization(
                        ledger,
                        args.run_id,
                        args.input,
                        args.output_dir,
                        args.root,
                        transcribe=args.transcribe,
                        diarize=args.diarize,
                        model=args.model,
                        hf_token=secrets.value("HF_TOKEN", required=False),
                    )
                )
            elif args.command == "demo":
                from statement_ledger.application.demo import seed

                emit(seed(ledger))
            elif args.command == "seed-subject":
                config = json.loads(args.config.read_text())
                emit(ledger.put("person", config["person"]))
            elif args.command == "put":
                emit(
                    ledger.put(args.kind, json.loads(args.file.read_text()), args.expected_revision)
                )
            elif args.command == "get":
                emit(store.get(args.kind, args.id, args.revision))
            elif args.command == "ledger":
                emit(ledger.person_ledger(args.person_id))
            elif args.command == "verify":
                emit(
                    {
                        "audit": store.verify_audit(),
                        "records": store.verify_records(),
                        "provider_receipts": store.verify_provider_receipts(),
                    }
                )
            elif args.command == "export":
                save(args.out, store.export())
                emit({"written": str(args.out), "private_backup": True})
            elif args.command == "backup":
                if args.out.exists():
                    raise ValueError("Backup destination must not already exist")
                args.out.parent.mkdir(parents=True, exist_ok=True)
                target = sqlite3.connect(args.out)
                try:
                    store.db.backup(target)
                finally:
                    target.close()
                emit({"backup": str(args.out), "method": "sqlite-online-backup"})
            elif args.command == "ingest":
                from statement_ledger.pillars.discovery.ingestion import ingest_file

                result = ingest_file(
                    ledger,
                    args.file,
                    args.source,
                    args.rights,
                    archive_root=args.archive_root,
                    mode=args.mode,
                    max_records=args.max_records,
                )
                emit(result)
                return 0 if result["success"] else 2
            elif args.command == "import-transcript":
                from statement_ledger.pillars.speech.transcripts import (
                    from_asr_export,
                    parse_timed_text,
                )

                text = args.file.read_text(encoding="utf-8-sig")
                t = (
                    from_asr_export(json.loads(text), args.asset, args.id, engine=args.engine)
                    if args.format == "asr"
                    else parse_timed_text(text, args.asset, args.id, engine=args.engine)
                )
                emit(ledger.put("transcript", t.model_dump(mode="json"), args.expected_revision))
            elif args.command in {"clip", "speech"}:
                asset = store.get("asset", args.asset)
                if not ledger.dependencies_current("asset", args.asset):
                    raise ValueError("Asset provenance is stale")
                expected_hash = asset["payload"]["content_sha256"]
                if not expected_hash:
                    raise ValueError(
                        "Record content_sha256 on the asset before processing local media"
                    )
                h = hashlib.sha256()
                with args.input.open("rb") as f:
                    while chunk := f.read(1024 * 1024):
                        h.update(chunk)
                if h.hexdigest() != expected_hash:
                    raise ValueError("Local input bytes do not match the asset content_sha256")
                grant = RightsGrant.model_validate(
                    store.get("rights", asset["payload"]["rights_id"])["payload"]
                )
                if args.command == "clip":
                    from statement_ledger.pillars.media.clipping import clip_plan, local_clip

                    plan = clip_plan(
                        args.start_ms, args.end_ms, asset["payload"]["duration_ms"], args.padding_ms
                    )
                    local_clip(args.input, args.output, plan, grant, args.root)
                    emit(
                        {"output": str(args.output), "plan": plan, "publication_authorized": False}
                    )
                else:
                    from statement_ledger.infrastructure.providers.speech import (
                        align_speaker_candidates,
                        diarize_local,
                        transcribe_local,
                    )

                    result = transcribe_local(args.input, grant, model=args.model)
                    if args.diarize:
                        diar = diarize_local(
                            args.input, grant, token=secrets.value("HF_TOKEN", required=False)
                        )
                        result["diarization"] = diar
                        result["segments"] = align_speaker_candidates(
                            result["segments"], diar["turns"]
                        )
                    if args.output.exists():
                        raise ValueError("Speech output must not already exist")
                    save(args.output, result)
                    emit({"written": str(args.output), "identities_confirmed": False})
        finally:
            store.close()
        return 0
    except (ValueError, KeyError, OSError, RuntimeError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
