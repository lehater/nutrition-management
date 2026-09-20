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
