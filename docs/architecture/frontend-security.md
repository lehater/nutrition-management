# Frontend Security Architecture

Status: accepted for the frontend design target.

Owner: SECURITY-ARCHITECTURE.

## Trust boundary

The first frontend is a local browser client talking to the Nutrition Management process over a loopback-only HTTP listener.

The MVP remains single-user and has no identity/account authorization model.

## Required controls

- bind to loopback only by default; fail closed rather than silently widening to LAN/public interfaces;
- validate Host against configured local hosts;
- state-changing form requests require same-origin validation plus a server-generated CSRF token;
- CSRF state is presentation security state only and conveys no user identity/authorization;
- browser inputs, uploaded/manual text and query/form values are untrusted representations validated before application commands;
- never accept client-supplied trusted provenance, calculated target, optimization result, price-normalization result or domain authority;
- response templates escape untrusted text by default;
- no domain/application object is serialized wholesale into pages/logs merely for convenience;
- diagnostics avoid full member profiles, complete planning snapshots and raw imported source content by default.

## Session/authentication

No login, bearer token, refresh token or durable browser session is introduced.

A short-lived/local presentation cookie may be used only for CSRF or non-semantic UI continuity. It must not become the owner of product/domain state.

## State-changing semantics

Browser confirmation cannot substitute for domain validation.

A successful UI response is shown only after the application command commits successfully. Unknown/technical failure is never represented as confirmed mutation.

## Reopening conditions

Reopen Security Architecture before:
- binding beyond loopback;
- exposing the UI to another machine/user;
- adding authentication/accounts;
- storing credentials;
- introducing third-party browser origins or remote APIs;
- changing the threat boundary from local single-user use.

## Availability-abuse controls

The local trust model still prevents browser-origin abuse from becoming an unbounded expensive-work trigger:

- Generate Plan and other state-changing/expensive operations require accepted same-origin/CSRF validation before application dispatch;
- the listener remains loopback-only, so remote network clients are outside the accepted exposure boundary;
- presentation endpoints do not introduce unbounded file upload, background-job creation or queued work;
- request/form parsing must apply finite implementation limits appropriate to the accepted input shapes rather than accepting unbounded representation size;
- security rejection occurs before domain mutation or solver invocation where the rejected property is known at the presentation boundary.

Remote multi-user denial-of-service protection, rate limiting and distributed abuse controls are reopening conditions, not current requirements.
