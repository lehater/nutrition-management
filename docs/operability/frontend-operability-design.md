# Frontend Operability Design

Status: accepted for the frontend design target.

Owner: OPERABILITY-DESIGN.

## Responsibility

Define the minimum runtime evidence and diagnosability contract for the local browser frontend without re-owning product, application, security or reliability semantics.

## Configuration

Accepted semantic configuration for the frontend consists of:

- the existing application database/configuration needed by composition;
- loopback-only listener binding;
- one explicit local port.

The process must resolve exactly one effective value for required startup configuration or fail startup. Configuration source mechanics may be command line, environment or composition defaults, but precedence must be deterministic and tested. Runtime configuration reload and feature flags are not part of this slice.

## Logging and diagnostic evidence

The frontend must emit enough diagnostic evidence to distinguish:

- startup/configuration/schema failure;
- listener startup/shutdown;
- rejected Host/origin/CSRF request category;
- request/application technical failure;
- solver/planning technical failure surfaced through the web adapter.

Diagnostics must identify the failing boundary and operation class without logging complete member profiles, full Planning Input Snapshots, raw imported source content, CSRF tokens or complete generated plans by default.

A request-scoped correlation identifier may be generated at the presentation boundary and propagated into diagnostic events; its representation and logging library remain implementation choices.

## Health/readiness

No public or remote health endpoint is required for the local MVP.

Frontend readiness means:

1. required startup configuration is resolved;
2. composition/provider dependencies initialize;
3. the database is accessible with the expected schema/migration state;
4. the loopback listener binds successfully.

Failure of any prerequisite is a startup failure rather than a falsely healthy listener. Liveness is represented by the local process/listener continuing to run; no orchestrator-specific probe contract is introduced.

## Incident handling

The local MVP has no pager/on-call/incident-management system.

An operational incident is a startup or runtime technical failure that prevents the accepted user operation. The process must:

- fail closed on invalid startup/security configuration;
- expose a non-domain technical failure to the local user;
- retain safe diagnostic evidence sufficient to identify the failing boundary;
- permit restart after the underlying configuration/dependency problem is corrected.

Automatic retry loops, hidden background recovery and alert delivery are not introduced.

## Explicit non-requirements

For the current local single-user topology:

- dedicated metrics are not required;
- distributed tracing is not required;
- alerting/paging is not required;
- remote health endpoints are not required;
- runtime configuration reload is not required.

Reopen Operability Design if the frontend becomes remotely hosted, multi-process, background-job based, externally monitored or subject to accepted SLI/SLO objectives.

## Verification obligations

Verification must prove deterministic configuration resolution, fail-closed startup, safe diagnostic redaction, distinguishable technical failures and readiness behavior without depending on private logging-library structure.
