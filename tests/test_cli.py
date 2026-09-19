import json

from nutrition_management.adapters.cli.main import main

from fixture_loader import DERIVATION_DATE, HOUSEHOLD_ID, MARKET_AS_OF, load_acceptance_fixture


def test_cli_drives_same_use_case_and_emits_canonical_json(engine, db_path, capsys):
    load_acceptance_fixture(engine)
    argv = [
        "--db",
        str(db_path),
        "--household",
        HOUSEHOLD_ID,
        "--derivation-date",
        DERIVATION_DATE.isoformat(),
        "--market-as-of",
        MARKET_AS_OF.isoformat(),
    ]

    assert main(argv) == 0
    first = capsys.readouterr().out.strip()
    assert main(argv) == 0
    second = capsys.readouterr().out.strip()

    assert first == second
    payload = json.loads(first)
    assert payload["household_id"] == HOUSEHOLD_ID
    assert payload["outcome"] == "mapped_complete"
    assert payload["derivation_date"] == DERIVATION_DATE.isoformat()
    assert payload["market_as_of"] == MARKET_AS_OF.isoformat()
    assert payload["lines"]

