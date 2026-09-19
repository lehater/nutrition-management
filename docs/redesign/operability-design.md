# Operability Design — Runtime Evidence Contract

Status: research candidate; pre-code evidence for the runtime/operational-design experiment.

## Responsibility

This artifact owns the runtime evidence contract required to diagnose one execution of Nutrition Management without changing product/domain/interface semantics. It defines what an operator or developer must be able to distinguish from runtime evidence. It does not select logging/telemetry libraries, exception classes, metric names, configuration APIs or deployment tooling.

## Upstream ownership retained

- Product/domain/application design owns accepted domain outcomes and the distinction between domain infeasibility and technical failure.
- System architecture owns the one-process local runtime topology and coherent-capture boundary.
- Interface Design owns CLI inputs, stdout success representation and the external success/non-success process boundary.
- Engineering Policy owns general fail-fast, dependency and hidden-state constraints.
- Security/privacy design truth owns the prohibition on exposing member profiles or complete planning snapshots in diagnostics.
- Quality design truth owns reliability/performance objectives. The current local MVP has no accepted availability SLO that requires a new runtime target.

Operability consumes those decisions and defines the evidence needed to observe them at runtime.

## Operational event model

Every invocation has one `operation_id` created at the outer execution boundary and propagated through application, persistence and optimization diagnostic context. The identifier is diagnostic identity only; it has no domain meaning and is not persisted as business state.

Runtime evidence uses structured events with stable semantic fields. Physical encoding (JSON, key/value, native structured-record API), logging library and formatter remain implementation choices provided the fields remain machine-distinguishable.

Every operational event carries, when applicable: event kind; severity class; operation id; owning component/boundary; outcome/failure category; elapsed duration for completed operations; dependency identity for infrastructure interactions; and safe diagnostic attributes. Free-form message text is supplementary and is not a contract.

## Event taxonomy

The minimum semantic event classes are:

- `operation.started` and `operation.completed` for one CLI planning invocation;
- `planning_input.capture.completed` or `.failed`;
- `optimization.completed` or `.failed`, preserving policy-optimal, hard-model-infeasible, timeout, cancellation, unknown status, numeric failure and other technical failure;
- `persistence.operation.failed` for datastore failures relevant to the invocation;
- `application.failed` for an unexpected technical application failure reaching the outer boundary;
- `startup.failed` when required technical construction input/dependency initialization is invalid.

Accepted domain outcomes such as `no_executable_plan` are completion outcomes, not error events.

Severity semantics are: diagnostic/detail for optional non-abnormal detail; informational for lifecycle/success; warning for recoverable/degraded technical conditions that do not invalidate the result; error when the operation cannot produce an accepted result; critical when the runtime cannot safely initialize or continue. Concrete framework level names/numbers may differ if this ordering and meaning remain preserved.

## Failure and diagnostic contract

Failures remain distinguishable along two axes:

1. externally accepted result vs CLI usage failure vs technical execution failure;
2. diagnostic technical category sufficient to locate the failing boundary.

Runtime evidence must never translate timeout, cancellation, unknown solver status, numeric failure, persistence failure or unexpected defect into a domain result. Exception class hierarchies and translation mechanics are implementation freedom; preservation of semantic categories at boundaries is required.

The CLI contract requires a non-success process result for usage/technical failures. Exact numeric non-zero exit-code allocation remains implementation freedom for the first slice because no accepted upstream contract assigns stable codes. Diagnostic stderr text is likewise not stable API.

## Configuration contract

The current MVP has no independent application-configuration surface beyond accepted explicit invocation/runtime construction inputs:

- database path is supplied explicitly by the CLI;
- household id, derivation date and market-as-of are explicit semantic inputs;
- current clock must not supply semantic defaults;
- no environment-variable, config-file, named-environment, feature-flag or runtime-reload contract is required;
- no application secret is required by the accepted local MVP.

Therefore configuration-source precedence, hot reload, feature-flag lifecycle and secret-provider integration are absent decisions, not defaults for the coding agent to invent. Adding any of them requires reopening the owning interface/architecture/security decision before implementation relies on it.

Reading/parsing already accepted inputs with language/library mechanisms remains implementation freedom.

## Sensitive diagnostic data

Operational evidence must not contain by default full member profiles, complete Planning Input snapshots, complete Purchase Plan payloads, imported source payloads, database contents, credentials, tokens or secrets if later introduced.

Use opaque identifiers, counts, bounded categorical values and explicitly safe provenance identifiers where diagnosis needs context. A future requirement for audit-grade user/activity records is a separate security/product concern and is not created here.

## Metrics, traces and health

For the single-process, on-demand local CLI MVP, a continuously scraped metrics endpoint, distributed traces, liveness/readiness endpoints and alerting rules have no accepted consumer and are not required.

The semantic evidence model is signal-neutral: elapsed duration, failure category, dependency identity and operation correlation may later be projected to logs, metrics or traces without changing the owned decision. If deployment becomes long-running, remote or multi-process, health/readiness, dependency observability, SLIs/SLO-derived indicators and trace propagation must be reconsidered.

## Lifecycle and resilience

Startup validates required technical construction input before invoking domain/application work and fails before partial execution when construction is invalid.

The current synchronous CLI has no accepted background worker or long-running request lifecycle. It therefore requires no project-specific retry/backoff policy, readiness state machine or graceful-degradation mode.

Automatic retries of state-changing provider commands or solver execution are not authorized. A coding agent may not add retries merely as a library default because retryability depends on operation semantics and idempotency. Local resource cleanup must occur on success, failure and cancellation; concrete language mechanics are implementation freedom.

Cancellation delivered to in-progress optimization remains a technical failure category and must not be reported as an accepted plan. Signal-handler mechanics remain implementation freedom.

## External dependency evidence

Persistence and optimization are the runtime technical dependencies that materially affect plan generation. Diagnostic evidence identifies which boundary failed and preserves a safe dependency status/category without leaking native SQLAlchemy/SQLite/SCIP objects into application/domain contracts.

## Implementation freedoms

Coding may choose the Python logging/structured-event library and formatter; concrete exception classes/private hierarchy; context propagation mechanism for `operation_id`; exact non-zero exit codes for the first slice; physical metric/span/log names for optional local instrumentation; resource-cleanup syntax; and parsing APIs for accepted explicit inputs.

Coding may not choose new semantic failure categories, collapse required distinctions, add hidden configuration/default time, introduce retry/recovery policy, expose sensitive diagnostic payloads, or create a new operational interface without upstream design.

## Verification obligations

Verification/test design must be able to derive evidence that one invocation's events are correlatable; hard infeasibility is distinguishable from solver technical uncertainty/failure; usage and technical failures cannot masquerade as domain outcomes; sensitive profile/snapshot payloads are absent from default diagnostics; invalid startup construction fails before application execution; resources are released after success/failure/cancellation; no implicit current-time/configuration source changes semantic inputs; and no unapproved retry changes operation semantics.

## Atomicity result

This artifact is intentionally narrower than a general `Runtime Design` boundary. Configuration semantics, external failure representation, reliability targets and runtime topology remain with their existing owners. The coherent residual responsibility is **operability**: what runtime evidence must exist so accepted behavior and technical failure are diagnosable in operation.
