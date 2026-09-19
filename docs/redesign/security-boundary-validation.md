# Security boundary validation — Nutrition Management

Status: research evidence only. No production code is used as design authority.

## Case

Nutrition Management first MVP is a local, single-operator CLI with local persistence and imported external/provider data. Accepted redesign already states that there is no network listener or remote authentication boundary, member/profile data is personal, diagnostics must avoid complete profiles/snapshots, and imported data is untrusted until validated.

## Applicability result

A separate authentication/session architecture is **NOT_APPLICABLE** for the accepted local MVP. Adding users, passwords, sessions, OAuth, network ACLs or a secret store would invent a runtime and threat boundary that accepted architecture does not contain.

Security is still applicable as constraints projected into existing owners:

- PRODUCT/DOMAIN: accepted member/household semantics and what data/actions mean;
- SYSTEM/INTERFACE: local CLI and import trust boundary;
- DATA: local datastore/output representation and integrity constraints;
- OPERABILITY: diagnostic non-disclosure;
- ENGINEERING-POLICY/IMPLEMENTATION: safe parsing and dependency discipline where selected;
- VERIFICATION/TEST: prove invalid/untrusted import does not become canonical state and protected personal payloads are not emitted diagnostically.

## Threat/control analysis

| Concern | Accepted control/owner | Result |
| --- | --- | --- |
| Remote identity spoofing | No remote identity boundary exists | NOT_APPLICABLE |
| Untrusted imported data becomes canonical state | Validation/normalization before commit; semantic owner remains provider/application/data design | COVERED |
| Personal profile/planning data leaks through diagnostics | Security/privacy constraint consumed by Operability | COVERED |
| Local database/file access by another OS principal | Host permissions are the accepted trust boundary | OUTSIDE_APP_BOUNDARY for MVP |
| Hidden permissive security configuration | No independent app security/configuration surface is accepted | NOT_APPLICABLE |
| Invalid input causes partial canonical mutation | Existing application/data atomicity and validation semantics must be verified | COVERED_BY_EXISTING_OWNERS |

## Boundary evidence

This case is negative evidence against a mandatory SECURITY-ARCHITECTURE instance. Security concerns do not justify inventing an Authority when all applicable decisions are coherently owned elsewhere and no independent trust/enforcement architecture exists.

SECURITY-ANALYSIS remains useful even when SECURITY-ARCHITECTURE is absent: it can establish applicability, confirm coverage, and route gaps. Therefore analysis and architecture have independent lifecycles.

## Blocking-question test

No new security blocker is demonstrated by this case if accepted local/single-operator, validation, personal-data non-disclosure and host-permission boundaries remain authoritative.

Implementation would be blocked if a network/multi-user boundary were introduced without accepted identity/authentication/authorization semantics, or if imported data could trigger privileged interpretation/execution beyond the accepted data parser contract.

## Harness conclusion from this case

- SECURITY-ARCHITECTURE is conditional, not baseline.
- SECURITY-ANALYSIS can be applicable without SECURITY-ARCHITECTURE.
- Security analysis must be able to return NOT_APPLICABLE/covered rather than manufacture controls.
- No Security Core entity is required.
