# Operator API — v0.2 implemented contract

This API is a single-owner research interface. It is not a public, tenant-isolated SaaS API. Static shell and `/healthz` are public; every `/api/*` operation requires `Authorization: Bearer <SL_API_TOKEN>`. Startup refuses a token shorter than 32 characters. Generate a random secret rather than copying documentation placeholders.

| Method | Path | Operation |
|---|---|---|
| `GET` | `/healthz` | Health |
| `GET` | `/` | Index |
| `GET` | `/static/{name}` | Static |
| `GET` | `/api/openapi.json` | Openapi |
| `GET` | `/api/sources` | Registry |
| `GET` | `/api/counts` | Counts |
| `GET` | `/api/schema/{kind}` | Schema |
| `GET` | `/api/records/{kind}` | Records |
| `POST` | `/api/records/{kind}` | Write |
| `GET` | `/api/records/{kind}/{record_id}` | Record |
| `GET` | `/api/history/{kind}/{record_id}` | History |
| `GET` | `/api/people/{person_id}/ledger` | Person |
| `POST` | `/api/discovery/plan` | Plan |
| `POST` | `/api/scope/compare` | Scope |
| `POST` | `/api/clips/plan` | Clips |
| `GET` | `/api/integrity` | Integrity |

Machine-readable route document: [OpenAPI](../contracts/openapi.json). Per-kind payload schemas are also exported alongside it. The generic write endpoint has a generic object body in OpenAPI and validates that object against the selected kind in the service; consult the per-kind JSON Schema for exact fields. This is not falsely described as a discriminated-union OpenAPI client contract.

## Create, inspect and update

```bash
curl --fail --silent http://127.0.0.1:8765/api/records/person \
  -H "Authorization: Bearer $SL_API_TOKEN" \
  -H 'Content-Type: application/json' \
  --data '{"expected_revision":0,"record":{"id":"demo-new-person","display_name":"A Fictional Example","synthetic":true}}'

curl --fail --silent http://127.0.0.1:8765/api/records/person/demo-new-person \
  -H "Authorization: Bearer $SL_API_TOKEN"
```

The response envelope supplies the revision. To update, preserve the record ID and send the complete replacement payload with the current `expected_revision`. An out-of-date expected revision yields HTTP 409 even when the submitted payload otherwise appears identical. Clients must refetch and reconcile rather than blindly retrying an overwritten edit.

Creation uses expected revision 0. Identical retries at the correct revision do not create unnecessary revisions. Unknown extra payload fields fail validation. Revision history and an explicit historical revision are available without changing the current head.

## Discovery and analysis commands

```bash
curl --fail --silent http://127.0.0.1:8765/api/discovery/plan \
  -H "Authorization: Bearer $SL_API_TOKEN" -H 'Content-Type: application/json' \
  --data '{"name":"Scott Jennings","aliases":[]}'

curl --fail --silent http://127.0.0.1:8765/api/clips/plan \
  -H "Authorization: Bearer $SL_API_TOKEN" -H 'Content-Type: application/json' \
  --data '{"start_ms":30000,"end_ms":45000,"duration_ms":60000,"padding_ms":15000}'
```

A discovery plan does not execute network requests. A clip plan returns coordinates; it neither downloads nor publishes media. Actual media processing is a local CLI action with provenance and rights checks. Scope comparison is conservative exact normalized matching, not a semantic adjudicator.

## Error contract and limits

401 is missing/invalid authentication; 404 is missing record, schema or asset path; 409 is optimistic concurrency conflict; 413 is a request body over 4 MiB; 422 is invalid shape, unsafe scope/relationship or domain invariant. The list route permits 1–1,000 records per page with nonnegative offset. Errors contain bounded detail rather than echoing entire submitted records. Network clients use separate timeout, retry and response-byte limits.

The inspector token stays in browser memory. No CORS wildcard is enabled. API responses are no-store. Public docs endpoints are disabled; the generated OpenAPI route is authenticated. This does not replace TLS, external authentication, actor-specific roles, rate limiting, request deadlines, CSRF/origin assessment, or production review.

## Event boundary

Writes place outbox entries in the same database transaction as the revision. The included queue library has lease fencing, but no continuously running outbox dispatcher is wired into the CLI. Do not assume an observation insertion automatically transcribes, indexes, evaluates or publishes anything. The complete event/workflow contract is specified in the full specification and implemented in later gated work.


## Acceleration routes added in v0.2

All routes below require the same server-side bearer authentication. Typed request shapes
are generated in OpenAPI; they are not arbitrary model prompts.

| Method | Path | Behavior |
|---|---|---|
| POST | `/api/profiles/build` | Build a reproducible phrase profile from accepted target/background turns |
| POST | `/api/profiles/{profile_id}/refresh` | Explicit refresh with comparison people and holdout exclusions |
| POST | `/api/localization/plan` | Create shadow/assist window plan; remote Jev only when explicitly requested and configured |
| POST | `/api/localization/combine` | Union selected intervals by source asset, not across different timebases |
| POST | `/api/claims/search` | Person-independent lexical claim retrieval with review-card status |
| GET | `/api/claims/cards/{card_id}` | Inspect scoped review provenance, expiry and correction blockers |
| POST | `/api/claims/match` | Optional typed Jev compatibility proposal, never an automatic verdict |
| GET | `/api/acceleration/status` | Provider configuration state and receipt integrity without returning secrets |

`GET /api/integrity` now includes provider receipt hashes. The five new canonical record
kinds also use generic record/history endpoints. Full media execution, raw corpus import
and calibration reports remain explicit local CLI actions, not arbitrary server file APIs.
No route converts a phrase score into an accepted identity or publishes a new assessment.
