from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from nutrition_management.food_knowledge.application.contracts import NutrientEvidenceStatus
from nutrition_management.food_knowledge.application.source_data import (
    ComponentDefinition,
    SourceFood,
    SourceNutrientEvidence,
)
from nutrition_management.food_knowledge.domain.model import TOP_LEVEL_CATEGORIES
from nutrition_management.food_knowledge.infrastructure.bls_v4_semantics import (
    BlsV4SemanticError,
    normalize_bls_value,
)

MAIN_ID_HEADERS = ("BLS Code", "Lebensmittelbezeichnung", "Food name")
COMPONENT_COLUMN_COUNT = 9
PRODUCTION_COMPONENT_COUNT = 138
PRODUCTION_FOOD_COUNT = 7140


class BlsV4WorkbookStructureError(ValueError):
    pass


def _display_text(value: object, field: str) -> str | None:
    """Require an extractor to preserve the source-displayed cell text.

    The workbook boundary deliberately does not coerce Python numeric values. BLS 4.0
    uses source precision/rounding as provenance, so an XLSX adapter must expose the
    displayed text (or an equivalent lossless textual representation) before semantic
    normalization is allowed.
    """

    if value is None:
        return None
    if not isinstance(value, str):
        raise BlsV4WorkbookStructureError(
            f"{field} must be source-displayed text or null, got {type(value).__name__}"
        )
    return value.strip()


def _required_text(value: object, field: str) -> str:
    text = _display_text(value, field)
    if not text:
        raise BlsV4WorkbookStructureError(f"{field} must be a non-empty string")
    return text


def _optional_text(value: object, field: str) -> str | None:
    text = _display_text(value, field)
    return text or None


def _row(row: Sequence[object], expected_columns: int, field: str) -> tuple[object, ...]:
    values = tuple(row)
    if len(values) != expected_columns:
        raise BlsV4WorkbookStructureError(
            f"{field} must contain exactly {expected_columns} columns, got {len(values)}"
        )
    return values


def _normalized_header(value: object, field: str) -> str:
    return " ".join(_required_text(value, field).split()).casefold()


def _validate_component_header(row: Sequence[object]) -> None:
    values = _row(row, COMPONENT_COLUMN_COUNT, "component header")
    normalized = tuple(
        _normalized_header(value, f"component header[{index}]")
        for index, value in enumerate(values)
    )
    checks = (
        normalized[0] == "index",
        "nährstoffcode" in normalized[1] and "component code" in normalized[1],
        "nährstoffbezeichnung" in normalized[2],
        "component name" in normalized[3],
        "einheit" in normalized[4] and "unit" in normalized[4],
        "nährstoffgruppe" in normalized[5],
        "component group" in normalized[6],
        "formula" in normalized[7],
        "formelanwendung" in normalized[8] and "formula application" in normalized[8],
    )
    if not all(checks):
        raise BlsV4WorkbookStructureError(
            "component workbook header does not match the documented BLS 4.0 A-I structure"
        )


def normalize_component_rows(
    rows: Iterable[Sequence[object]],
    *,
    expected_component_count: int = PRODUCTION_COMPONENT_COUNT,
) -> tuple[ComponentDefinition, ...]:
    iterator = iter(rows)
    try:
        header = next(iterator)
    except StopIteration as exc:
        raise BlsV4WorkbookStructureError("component workbook is empty") from exc
    _validate_component_header(header)

    components: list[ComponentDefinition] = []
    codes: set[str] = set()
    for row_number, raw_row in enumerate(iterator, start=2):
        values = _row(raw_row, COMPONENT_COLUMN_COUNT, f"component row {row_number}")
        if all(_optional_text(value, f"component row {row_number}") is None for value in values):
            continue
        code = _required_text(values[1], f"component row {row_number}.code")
        if code in codes:
            raise BlsV4WorkbookStructureError(f"duplicate BLS component code: {code}")
        try:
            component = ComponentDefinition(
                component_code=code,
                name_de=_required_text(values[2], f"component row {row_number}.name_de"),
                name_en=_required_text(values[3], f"component row {row_number}.name_en"),
                unit=_required_text(values[4], f"component row {row_number}.unit"),
                group_de=_optional_text(values[5], f"component row {row_number}.group_de"),
                group_en=_optional_text(values[6], f"component row {row_number}.group_en"),
                formula=_optional_text(values[7], f"component row {row_number}.formula"),
                formula_application=_optional_text(
                    values[8], f"component row {row_number}.formula_application"
                ),
            )
        except ValueError as exc:
            raise BlsV4WorkbookStructureError(
                f"invalid BLS component row {row_number}: {exc}"
            ) from exc
        components.append(component)
        codes.add(code)

    if len(components) != expected_component_count:
        raise BlsV4WorkbookStructureError(
            f"expected {expected_component_count} BLS component rows, got {len(components)}"
        )
    return tuple(components)


def _main_component_order(
    header: Sequence[object],
    components: Sequence[ComponentDefinition],
) -> tuple[str, ...]:
    expected_columns = len(MAIN_ID_HEADERS) + 3 * len(components)
    values = _row(header, expected_columns, "main workbook header")
    for index, expected in enumerate(MAIN_ID_HEADERS):
        actual = " ".join(_required_text(values[index], f"main header[{index}]").split())
        if actual != expected:
            raise BlsV4WorkbookStructureError(
                f"main workbook identification header {index + 1} must be {expected!r}, got {actual!r}"
            )

    known_codes = {component.component_code for component in components}
    ordered_codes: list[str] = []
    for component_index in range(len(components)):
        offset = 3 + component_index * 3
        value_header = " ".join(
            _required_text(values[offset], f"main header[{offset}]").split()
        )
        origin_header = " ".join(
            _required_text(values[offset + 1], f"main header[{offset + 1}]").split()
        )
        reference_header = " ".join(
            _required_text(values[offset + 2], f"main header[{offset + 2}]").split()
        )
        suffix = " Datenherkunft"
        if not origin_header.endswith(suffix):
            raise BlsV4WorkbookStructureError(
                f"main workbook column {offset + 2} must be a '<CODE> Datenherkunft' column"
            )
        code = origin_header[: -len(suffix)]
        if code not in known_codes:
            raise BlsV4WorkbookStructureError(
                f"main workbook references unknown BLS component code {code!r}"
            )
        if not (value_header == code or value_header.startswith(f"{code} ")):
            raise BlsV4WorkbookStructureError(
                f"main workbook value header {value_header!r} does not match component {code}"
            )
        if reference_header != f"{code} Referenz":
            raise BlsV4WorkbookStructureError(
                f"main workbook reference header for {code} must be '{code} Referenz'"
            )
        ordered_codes.append(code)

    if len(ordered_codes) != len(set(ordered_codes)):
        raise BlsV4WorkbookStructureError("main workbook component triplets must be unique")
    if set(ordered_codes) != known_codes:
        missing = sorted(known_codes - set(ordered_codes))
        extra = sorted(set(ordered_codes) - known_codes)
        raise BlsV4WorkbookStructureError(
            f"main workbook component coverage must be exact; missing={missing}, extra={extra}"
        )
    return tuple(ordered_codes)


def normalize_food_rows(
    rows: Iterable[Sequence[object]],
    *,
    components: Sequence[ComponentDefinition],
    category_by_code: Mapping[str, str],
    expected_food_count: int = PRODUCTION_FOOD_COUNT,
    source_version: str = "4.0",
) -> tuple[SourceFood, ...]:
    if not components:
        raise BlsV4WorkbookStructureError("component definitions are required before food rows")
    iterator = iter(rows)
    try:
        header = next(iterator)
    except StopIteration as exc:
        raise BlsV4WorkbookStructureError("main workbook is empty") from exc
    ordered_codes = _main_component_order(header, components)
    expected_columns = len(MAIN_ID_HEADERS) + 3 * len(ordered_codes)

    foods: list[SourceFood] = []
    seen_codes: set[str] = set()
    for row_number, raw_row in enumerate(iterator, start=2):
        values = _row(raw_row, expected_columns, f"food row {row_number}")
        if all(_optional_text(value, f"food row {row_number}") is None for value in values):
            continue
        source_code = _required_text(values[0], f"food row {row_number}.source_code")
        if source_code in seen_codes:
            raise BlsV4WorkbookStructureError(f"duplicate BLS food code: {source_code}")
        category = category_by_code.get(source_code)
        if category is None:
            raise BlsV4WorkbookStructureError(
                f"BLS food {source_code} has no explicit ADR-005 category mapping"
            )
        if category not in TOP_LEVEL_CATEGORIES:
            raise BlsV4WorkbookStructureError(
                f"BLS food {source_code} maps to unsupported ADR-005 category {category!r}"
            )

        nutrients: list[SourceNutrientEvidence] = []
        for component_index, component_code in enumerate(ordered_codes):
            offset = 3 + component_index * 3
            source_value_text = _optional_text(
                values[offset], f"food row {row_number}.{component_code}.value"
            )
            value_origin = _optional_text(
                values[offset + 1], f"food row {row_number}.{component_code}.origin"
            )
            source_reference = _optional_text(
                values[offset + 2], f"food row {row_number}.{component_code}.reference"
            )
            try:
                status, amount = normalize_bls_value(source_value_text, value_origin)
            except BlsV4SemanticError as exc:
                raise BlsV4WorkbookStructureError(
                    f"invalid BLS evidence at food={source_code}, component={component_code}: {exc}"
                ) from exc
            if status == NutrientEvidenceStatus.MISSING:
                if source_reference is not None:
                    raise BlsV4WorkbookStructureError(
                        f"missing BLS evidence must not carry a reference: food={source_code}, component={component_code}"
                    )
                continue
            nutrients.append(
                SourceNutrientEvidence(
                    component_code=component_code,
                    status=status,
                    amount_per_100g=amount,
                    source_value_text=source_value_text or "",
                    value_origin=value_origin or "",
                    source_reference=source_reference,
                )
            )

        foods.append(
            SourceFood(
                base_food_id=f"bls:{source_version}:{source_code}",
                source_code=source_code,
                name_de=_required_text(values[1], f"food row {row_number}.name_de"),
                name_en=_optional_text(values[2], f"food row {row_number}.name_en"),
                category=category,
                nutrients=tuple(nutrients),
            )
        )
        seen_codes.add(source_code)

    if len(foods) != expected_food_count:
        raise BlsV4WorkbookStructureError(
            f"expected {expected_food_count} BLS food rows, got {len(foods)}"
        )
    if set(category_by_code) != seen_codes:
        missing = sorted(seen_codes - set(category_by_code))
        extra = sorted(set(category_by_code) - seen_codes)
        raise BlsV4WorkbookStructureError(
            f"category registry must cover BLS foods exactly; missing={missing}, extra={extra}"
        )
    return tuple(foods)
