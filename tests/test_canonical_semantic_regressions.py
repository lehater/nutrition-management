from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def canonical_paths():
    text = (ROOT / ".harness/graph.yaml").read_text(encoding="utf-8")
    return [
        match.group(1).strip()
        for match in re.finditer(r"^\s+path:\s+(.+?)\s*$", text, re.MULTILINE)
    ]


def test_canonical_artifacts_are_not_branch_scoped():
    offenders = []
    for rel in canonical_paths():
        path = ROOT / rel
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "accepted for the Harness pilot branch" in text:
            offenders.append(rel)
    assert offenders == []


def test_data_design_does_not_own_concrete_implementation_stack():
    text = (ROOT / "docs/data/data-design.md").read_text(encoding="utf-8")
    for forbidden in ("SQLite", "SQLAlchemy", "Alembic", "synchronous=FULL"):
        assert forbidden not in text


def test_frontend_member_creation_contract_is_explicit():
    contracts = (ROOT / "docs/application/frontend-application-contracts.md").read_text(
        encoding="utf-8"
    )
    journey = (ROOT / "docs/application/user-journeys.md").read_text(encoding="utf-8")
    tests = (ROOT / "docs/redesign/frontend-test-design.md").read_text(encoding="utf-8")

    assert "### CreateMember(household_id, profile)" in contracts
    assert "Nutrition Targeting generates/owns the new opaque `member_id`" in contracts
    assert "SaveMemberProfile(household_id, member_id, profile)" in contracts
    assert "does not create Member identity implicitly" in contracts
    assert "provider-owned opaque Member identity" in journey
    assert "## FUI-000 — New member creation" in tests
