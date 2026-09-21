# Frontend Security Analysis

Status: accepted for the frontend design target.

Owner: SECURITY-ANALYSIS.

## Scope

Evaluate the accepted local browser trust boundary and security-control coverage without redefining Frontend Security Architecture.

Accepted boundary: one local browser communicates with a loopback-only HTTP listener in the same single-user deployment. There is no account identity or authorization model.

## Threat and control coverage

### Cross-origin state change

Applicable. A malicious/untrusted browser origin must not trigger accepted state changes or expensive planning work.

Covered by:
- loopback/Host validation;
- same-origin validation;
- server-generated CSRF proof before state-changing/expensive dispatch.

### Host/bind widening

Applicable. Misconfiguration must not silently expose the listener beyond the accepted local boundary.

Covered by loopback-only default/bind policy and fail-closed configuration validation.

### Untrusted rendered/input content

Applicable. Human-entered/catalog/source text and browser form input are untrusted representations.

Covered by explicit request parsing/application validation and default template escaping. Client-supplied calculated/provenance/domain-authority values are never trusted.

### Sensitive diagnostic disclosure

Applicable. Member/profile and planning data may contain personal or sensitive domain facts.

Covered by the Security Architecture diagnostic-minimization rule and Frontend Operability redaction contract.

### Identity/authorization abuse

Not applicable to the accepted slice because there is no multi-user/account boundary. Reopen before remote/multi-user exposure or authentication.

### Availability abuse

Applicable only within the local-browser boundary. Cross-origin triggering of expensive work is controlled before solver dispatch; remote/multi-user denial-of-service controls and rate limiting are outside the accepted exposure model.

## Vulnerability-management contract

Frontend runtime dependencies are pinned through the existing lockfile. On dependency introduction/update and before release, known material security advisories affecting the accepted runtime path must be reviewed.

A material unresolved advisory that changes the accepted trust/control assumptions blocks release or becomes an explicit Security Question with rationale and reopening condition. Security Analysis does not invent a universal CVSS threshold.

## Secure-development contract

Security-sensitive changes must preserve:

- loopback-only/fail-closed binding behavior;
- Host/origin/CSRF checks before mutation or expensive work;
- autoescaping/untrusted-input validation;
- no credential/authentication subsystem unless explicitly reopened;
- no secrets or CSRF tokens in diagnostics;
- security verification contracts for the changed boundary.

Framework defaults are not treated as proof unless the accepted verification demonstrates the required behavior.

## Verification obligations

Maintain executable evidence for Host/origin/CSRF rejection, template escaping, fail-closed listener configuration, diagnostic minimization and the absence of unintended authentication/remote exposure.

## Reopening conditions

Re-run Security Analysis before remote/multi-user hosting, authentication, third-party browser origins, public API exposure, credential storage, background jobs or a materially different framework/security boundary.
