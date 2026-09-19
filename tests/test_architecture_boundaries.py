import ast
from pathlib import Path

from sqlalchemy import inspect

ROOT = Path("src/nutrition_management")
CONTEXTS = {"nutrition_targeting", "food_knowledge", "market_catalog", "purchase_planning"}


def _imports(path: Path):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


def _context_from_import(name: str):
    parts = name.split(".")
    if len(parts) >= 2 and parts[0] == "nutrition_management" and parts[1] in CONTEXTS:
        return parts[1], parts[2:] if len(parts) > 2 else []
    return None, []


def test_domain_layers_are_framework_free_and_context_local():
    forbidden_roots = {"sqlalchemy", "pyscipopt", "alembic", "argparse", "sqlite3"}
    for context in CONTEXTS:
        for path in (ROOT / context / "domain").glob("*.py"):
            for imported in _imports(path):
                assert imported.split(".")[0] not in forbidden_roots, (path, imported)
                other_context, _ = _context_from_import(imported)
                assert other_context in {None, context}, (path, imported)


def test_application_layers_do_not_import_infrastructure():
    for context in CONTEXTS:
        for path in (ROOT / context / "application").glob("*.py"):
            for imported in _imports(path):
                imported_context, rest = _context_from_import(imported)
                if imported_context == context:
                    assert not rest or rest[0] != "infrastructure", (path, imported)
                elif imported_context is not None:
                    assert rest and rest[0] == "application", (path, imported)


def test_context_infrastructure_does_not_import_other_context_infrastructure():
    for context in CONTEXTS:
        for path in (ROOT / context / "infrastructure").glob("*.py"):
            for imported in _imports(path):
                imported_context, rest = _context_from_import(imported)
                if imported_context not in {None, context}:
                    assert not rest or rest[0] != "infrastructure", (path, imported)


def test_database_foreign_keys_never_cross_context_prefixes(engine):
    inspector = inspect(engine)
    for table in inspector.get_table_names():
        source_prefix = table.split("_", 1)[0]
        for foreign_key in inspector.get_foreign_keys(table):
            target = foreign_key["referred_table"]
            target_prefix = target.split("_", 1)[0]
            assert source_prefix == target_prefix, (table, target)


def test_purchase_planning_solver_adapter_does_not_import_provider_infrastructure():
    path = ROOT / "purchase_planning" / "infrastructure" / "solver_adapter.py"
    for imported in _imports(path):
        imported_context, rest = _context_from_import(imported)
        if imported_context in {"nutrition_targeting", "food_knowledge", "market_catalog"}:
            assert not rest or rest[0] != "infrastructure", (path, imported)
