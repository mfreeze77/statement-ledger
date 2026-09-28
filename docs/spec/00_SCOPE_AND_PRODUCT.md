## 00. Product definition, boundaries, and interpretation

### 00.1 The problem being solved

An appearance, a quotation, a transcript, a video upload, and a fact-check are different
observations of public communication. They are currently scattered across sources with
different coverage, timing, access, formats, and editorial selection. Statement Ledger
uses them as cooperating inputs to reconstruct an inspectable history of a person's
public statements. The system starts from a subject and a declared research scope. It
follows leads into original events, locates speaking turns, preserves exact words and
context, separates propositions from their occurrences, and attaches documented evidence
and review history without rewriting the source record.

The product is not an article aggregator with a name filter. Its central value is the
ability to open a statement and reconstruct why the system associates those words with
that speaker, which event they belong to, which copies represent the same occurrence,
what question or qualification surrounded the words, and what evidence a reviewer used.

### 00.2 Independence is an architectural requirement

This is a new application with an independent repository, package namespace, source
registry, requirements, database, object storage, job state, API, user interface, model
configuration, deployment, security policy, and release history. No other private
application is a prerequisite, a system of record, or an implicit source of configuration.
No external project's ticket numbers, migrations, identifiers, tables, schemas, data,
credentials, or runtime imports belong in this repository. General design ideas may be
reused, but implementation decisions are made and tested here.

A future integration is a separately authorized adapter across a documented versioned
boundary. It must be removable without breaking local ingestion, review, or export.
The reference implementation has no mandatory external retrieval or model dependency.
The standalone namespace check in `scripts/check-standalone.py` guards against accidental
imports and configuration coupling. It is a regression check, not a complete static
proof of independence.

### 00.3 Primary users and jobs

The initial user is a single researcher operating a private workspace. Their jobs are to
scope an investigation, inspect coverage gaps, acquire permitted material, resolve an
appearance and speaker, review claim extraction, inspect evidence, record findings, and
correct mistakes. A source operator maintains connector credentials and contractual
limits. A reviewer checks context and evidence. In v0.1 these responsibilities may be
performed by one authenticated owner; they are not represented as independently verified
roles. Later collaborative releases must distinguish them through actual principals and
server-side permissions rather than trusting a supplied reviewer name.

The subject may be a pundit, interviewer, public official, expert, executive, or another
person making relevant public statements. The collection scope is public communication,
not private correspondence or surveillance of private life. The included Scott Jennings
configuration is a name-only discovery example. It does not assert current employment,
accounts, identities in recordings, statements, or findings. Synthetic fixtures use a
fictional speaker and are never merged into a real research workspace.

### 00.4 Required product outputs

The target product produces a source inventory, a coverage ledger, an original-event and
asset map, an attributed speaking-turn timeline, a statement ledger, scoped propositions,
assertion occurrence groups, evidence bundles, attributed external reviews, internal
review records, correction history, and provenance exports. Every summarized number must
be expandable to records and the eligibility rules that produced it. A collection with
no material is an empty or blocked collection, not evidence that the person never spoke.

The product must allow inspection without requiring a published conclusion. Unresolved
identity, incomplete context, inaccessible source material, conflicting evidence, and
unmatched quotations are valuable states. They must remain visible instead of being
converted into confident outputs merely to fill a dashboard.

### 00.5 Non-goals

There is no universal honesty score, inferred intent classifier, political endorsement,
character rating, fabricated certainty, or cross-person ranking. An inaccurate statement
and deliberate deception are different propositions. Source reputation and political
labels do not substitute for evidence about a particular claim. The system does not
promise access to all YouTube appearances, all historical broadcasts, or all statements.
It does not bypass platform access controls, acquire third-party media without approved
rights, or automatically redistribute full transcripts and recordings.

### 00.6 Specification versus implementation

**Target requirement** means the desired product behavior, not a completion claim.
**Implemented** means code exists and its stated local tests have been run.
**Mock-verified** means protocol behavior was exercised without a live provider.
**Access-dependent** means credentials, a license, or a verified export shape is missing.
**Planned** means the required code is not in v0.1. The status matrix and validation report
are authoritative. Listing a source in the registry never upgrades its implementation
status. The v0.1 deliverable is a runnable reference vertical slice with a full design and
backlog, not a fully deployed national-media monitoring service.
