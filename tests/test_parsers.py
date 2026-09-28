import bz2
import gzip
import json
from pathlib import Path

import pytest

from statement_ledger.connectors.parsers import ParseError, iter_rows, parse
from statement_ledger.connectors.registry import sources
from statement_ledger.ingest import ingest_file

QUOTATION = {
    "quoteID": "2020-01-01-000001",
    "quotation": "Synthetic words.",
    "speaker": "Dana Example",
    "date": "2020-01-01",
    "qids": ["QEXAMPLE"],
    "probas": [["Dana Example", 0.7], ["None", 0.3]],
    "urls": ["https://example.org/a"],
    "numOccurrences": 99,
}


def test_quotebank_lead_not_verified_statement():
    o = parse("quotebank", QUOTATION, "rights")[0]
    assert o.kind == "quotation_lead" and o.reported_speaker == "Dana Example"
    assert o.raw_payload["numOccurrences"] == 99
    assert o.published_at is None  # Earliest article occurrence is not publication/event time.


def test_stable_observation_id():
    assert parse("quotebank", QUOTATION, "r")[0].id == parse("quotebank", QUOTATION, "r")[0].id


def test_gdelt_preserves_quote_context():
    row = {
        "date": "20200101000100",
        "url": "https://example.org/a",
        "title": "t",
        "lang": "English",
        "quotes": [
            {"pre": "Dana said ", "quote": "hello", "post": " to the host"},
            {"quote": "bye"},
        ],
    }
    out = parse("gdelt_gqg", row, "r")
    assert len(out) == 2 and out[0].raw_payload["quotation"]["pre"] == "Dana said "
    assert out[0].reported_speaker is None and out[0].published_at is None


def test_youtube_metadata_not_speaker_confirmation():
    data = {
        "items": [
            {
                "id": {"videoId": "abc123", "kind": "youtube#video"},
                "snippet": {
                    "title": "Test",
                    "description": "Dana discussed",
                    "publishedAt": "2026-01-01T00:00:00Z",
                },
            },
            {"id": {"channelId": "chan", "kind": "youtube#channel"}, "snippet": {"title": "No"}},
        ]
    }
    out = parse("youtube", data, "r")
    assert len(out) == 1 and out[0].reported_speaker is None


def test_youtube_playlist_uses_video_id_not_playlist_item_id():
    out = parse(
        "youtube",
        {
            "items": [
                {
                    "id": "playlist-item-id",
                    "snippet": {"resourceId": {"videoId": "actual-video"}, "title": "t"},
                }
            ]
        },
        "r",
    )
    assert out[0].native_id == "actual-video"


def test_google_reviews_not_collapsed_by_url():
    data = {
        "claims": [
            {"text": "one", "claimReview": [{"url": "https://example.org/review"}]},
            {"text": "two", "claimReview": [{"url": "https://example.org/review"}]},
        ]
    }
    out = parse("google_fact_check", data, "r")
    assert len(out) == 2 and out[0].id != out[1].id


def test_claimreview_preserves_rating_and_appearance():
    row = {
        "@type": "ClaimReview",
        "claimReviewed": "example",
        "url": "https://example.org/review",
        "reviewRating": {"alternateName": "Publisher scale unchanged"},
        "itemReviewed": {
            "author": {"name": "Dana"},
            "appearance": [{"url": "https://example.org/clip"}],
        },
    }
    out = parse("claimreview", row, "r")[0]
    assert out.kind == "external_review" and out.reported_speaker == "Dana"
    assert out.links == ["https://example.org/clip"]
    assert out.raw_payload["reviewRating"]["alternateName"] == "Publisher scale unchanged"


def test_jsonld_graph():
    assert (
        len(
            parse(
                "claimreview",
                {
                    "@graph": [
                        {"@type": "Person", "name": "Not a review"},
                        {
                            "@type": "ClaimReview",
                            "url": "https://example.org/a",
                            "claimReviewed": "x",
                        },
                    ]
                },
                "r",
            )
        )
        == 1
    )


def test_fci_without_type():
    assert (
        len(
            parse(
                "fact_check_insights",
                {"id": "fci-id", "url": "https://example.org/a", "claimReviewed": "x"},
                "r",
            )
        )
        == 1
    )


def test_archive_metadata():
    o = parse(
        "internet_archive",
        {"metadata": {"identifier": "abc", "title": ["a", "b"], "date": "1968"}},
        "r",
    )[0]
    assert o.title == "a; b" and o.published_at is None


def test_aapb_shape():
    o = parse("aapb", {"response": {"docs": [{"id": "cpb-aacip_test", "title": ["Test"]}]}}, "r")[0]
    assert o.kind == "metadata"
    with pytest.raises(ParseError):
        parse("aapb", {"unexpected": []}, "r")


@pytest.mark.parametrize(
    "source_id", ["tveyes", "critical_mention", "sprinklr", "full_fact_ai", "vanderbilt"]
)
def test_unimplemented_connector_explicit(source_id):
    with pytest.raises(ParseError):
        parse(source_id, {}, "r")


def test_manual_envelope_can_preserve_actual_source():
    o = parse(
        "manual_import",
        {
            "source_id": "tveyes",
            "native_id": "licensed-id",
            "kind": "transcript_lead",
            "url": "https://example.org/t",
            "text": "permitted export",
        },
        "r",
    )[0]
    assert o.source_id == "tveyes"


def test_source_registry_unique():
    rows = sources()
    assert len(rows) == len({r["id"] for r in rows})
    assert all(not r["enabled_by_default"] for r in rows)
    assert len(rows) >= 47


@pytest.mark.parametrize(
    "suffix,opener", [(".jsonl", open), (".jsonl.gz", gzip.open), (".jsonl.bz2", bz2.open)]
)
def test_stream_formats(tmp_path, suffix, opener):
    path = tmp_path / f"sample{suffix}"
    with opener(path, "wt", encoding="utf-8") as f:
        for i in range(3):
            f.write(json.dumps({"i": i}) + "\n")
    assert list(iter_rows(path, max_records=2)) == [{"i": 0}, {"i": 1}]


def test_bounded_array(tmp_path):
    p = tmp_path / "a.json"
    p.write_text('[{"i":1},{"i":2}]')
    assert len(list(iter_rows(p))) == 2
    with pytest.raises(ParseError):
        list(iter_rows(p, max_json_bytes=3))


def test_line_limit(tmp_path):
    p = tmp_path / "a.jsonl"
    p.write_text(json.dumps({"x": "a" * 100}))
    with pytest.raises(ParseError):
        list(iter_rows(p, max_line=20))


def test_malformed_row_not_silent(tmp_path):
    p = tmp_path / "a.jsonl"
    p.write_text('{"good":1}\nnot json\n')
    it = iter_rows(p)
    assert next(it) == {"good": 1}
    with pytest.raises(ParseError):
        next(it)


def test_ingest_idempotence_and_revision(ledger, tmp_path):
    ledger.put(
        "rights",
        {
            "id": "q-rights",
            "source_id": "quotebank",
            "basis": "Synthetic fixture",
            "allowed": ["store_text"],
            "reviewed_by": "test",
        },
    )
    p = tmp_path / "q.jsonl"
    p.write_text(json.dumps(QUOTATION) + "\n")
    r = ingest_file(ledger, p, "quotebank", "q-rights", archive_root=tmp_path / "archive")
    assert r["created"] == 1 and Path(r["archive_path"]).exists()
    r = ingest_file(ledger, p, "quotebank", "q-rights", archive_root=tmp_path / "archive")
    assert r["unchanged"] == 1
    q = {**QUOTATION, "quotation": "A corrected synthetic quotation."}
    p.write_text(json.dumps(q) + "\n")
    r = ingest_file(ledger, p, "quotebank", "q-rights", archive_root=tmp_path / "archive")
    assert r["revised"] == 1


def test_ingest_errors_reported(ledger, tmp_path):
    ledger.put(
        "rights",
        {
            "id": "q-rights",
            "source_id": "quotebank",
            "basis": "Synthetic",
            "allowed": ["store_text"],
            "reviewed_by": "test",
        },
    )
    p = tmp_path / "q.jsonl"
    p.write_text("{}\n")
    r = ingest_file(ledger, p, "quotebank", "q-rights", archive_root=tmp_path / "archive")
    assert not r["success"] and r["errors"][0]["row"] == 1
