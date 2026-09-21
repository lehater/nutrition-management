# CLI Contract

Status: accepted for the first implementation slice.

## Purpose

Provide the smallest external adapter that exercises the complete accepted planning path without introducing an HTTP/UI framework.

Executable command: `nutrition-plan`.

## Invocation

```text
nutrition-plan --db <sqlite-file> --household <household-id> --derivation-date <YYYY-MM-DD> --market-as-of <ISO-8601-instant>
```

All four arguments are required.

## Inputs

- `--db`: path to the local file-backed SQLite database;
- `--household`: opaque household identifier;
- `--derivation-date`: nutrition-target derivation date;
- `--market-as-of`: explicit market observation instant used for offer executability.

The two time inputs are intentionally separate. The adapter must not silently replace either with the current clock.

## Success output

On success stdout contains exactly one canonical JSON representation of the Purchase Plan.

Serialization rules:

- object keys are sorted;
- output is compact and deterministic;
- `Decimal` values are strings, preserving decimal semantics;
- dates/timestamps are ISO-8601 strings;
- enum values use their canonical string value.

The CLI does not reinterpret or summarize provider/domain facts.

## Failure boundary

Argument/date/time parsing errors are CLI usage failures.

Application, persistence and solver technical failures remain failures and must produce a non-success process result; they must not be serialized as accepted `partial` or `no_executable_plan` outcomes.

Accepted domain outcomes are represented by the application result contract and canonical JSON.

No stability guarantee is made for Python exception text or diagnostic stderr in the first slice.

## Dependency boundary

The CLI is an outer adapter. It may:

- parse invocation arguments;
- create composition/infrastructure dependencies;
- invoke the application use case;
- serialize its returned result.

It may not query context tables, construct solver policy, derive nutrition semantics or contain business ranking rules.

## Scope

No HTTP API, browser UI, interactive shell, authentication or remote transport is required for the first implementation slice. Adding one later creates a separate interface contract while preserving the application boundary.

## Compatibility contract

The first-slice machine contract is the documented command shape, required flags, accepted value semantics, exit success/failure distinction and canonical JSON result semantics.

Compatibility rules:

- adding an optional flag may be backward-compatible only when omission preserves current semantics;
- removing or renaming a required flag, changing a flag's semantic meaning, or changing canonical result-field semantics is a breaking contract change and requires an explicit Interface Design revision;
- diagnostic stderr wording and Python exception text are not compatibility contracts;
- accepted domain outcomes and technical failures must remain distinguishable across compatible revisions;
- a future HTTP/UI adapter does not replace or silently redefine this CLI contract.
