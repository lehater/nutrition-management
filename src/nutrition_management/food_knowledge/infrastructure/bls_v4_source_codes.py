from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET

BLS_V4_MAIN_SHA256 = "524bbefe25b691f5cb3de7a9f3e27fa2967aebfeabf217d99414ba7806e78c60"
BLS_V4_SOURCE_VERSION = "4.0"
PRODUCTION_FOOD_COUNT = 7140

_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
_CELL_RE = re.compile(r"([A-Z]+)([0-9]+)$")


class BlsV4SourceCodeError(ValueError):
    pass


def _digest(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise BlsV4SourceCodeError(f"cannot read BLS workbook: {exc}") from exc
    return sha256(data).hexdigest()


def _shared_strings(book: ZipFile) -> tuple[str, ...]:
    try:
        payload = book.read("xl/sharedStrings.xml")
    except KeyError:
        return ()
    root = ET.fromstring(payload)
    values: list[str] = []
    for item in root.findall(f"{{{_NS}}}si"):
        text = "".join(node.text or "" for node in item.iter(f"{{{_NS}}}t"))
        values.append(text)
    return tuple(values)


def _first_sheet_target(book: ZipFile) -> str:
    workbook = ET.fromstring(book.read("xl/workbook.xml"))
    sheets = workbook.find(f"{{{_NS}}}sheets")
    if sheets is None or len(sheets) != 1:
        raise BlsV4SourceCodeError("pinned BLS main workbook must contain exactly one worksheet")
    sheet = sheets[0]
    relation_id = sheet.attrib.get(f"{{{_REL_NS}}}id")
    if not relation_id:
        raise BlsV4SourceCodeError("worksheet relationship id is missing")

    relations = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
    for relation in relations.findall(f"{{{_PACKAGE_REL_NS}}}Relationship"):
        if relation.attrib.get("Id") != relation_id:
            continue
        target = relation.attrib.get("Target")
        if not target:
            break
        normalized = target.lstrip("/")
        if not normalized.startswith("xl/"):
            normalized = f"xl/{normalized}"
        return normalized
    raise BlsV4SourceCodeError("worksheet target cannot be resolved")


def _cell_text(cell: ET.Element, shared: tuple[str, ...]) -> str | None:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        inline = cell.find(f"{{{_NS}}}is")
        if inline is None:
            return None
        return "".join(node.text or "" for node in inline.iter(f"{{{_NS}}}t"))

    value = cell.find(f"{{{_NS}}}v")
    if value is None or value.text is None:
        return None
    if cell_type == "s":
        try:
            return shared[int(value.text)]
        except (ValueError, IndexError) as exc:
            raise BlsV4SourceCodeError("invalid shared-string index in BLS workbook") from exc
    return value.text


def extract_bls_v4_source_codes(
    path: Path,
    *,
    expected_sha256: str = BLS_V4_MAIN_SHA256,
    expected_count: int = PRODUCTION_FOOD_COUNT,
) -> dict[str, object]:
    actual_digest = _digest(path)
    if actual_digest != expected_sha256:
        raise BlsV4SourceCodeError(
            f"BLS workbook digest mismatch: expected {expected_sha256}, got {actual_digest}"
        )

    try:
        with ZipFile(path) as book:
            shared = _shared_strings(book)
            sheet = ET.fromstring(book.read(_first_sheet_target(book)))
    except (BadZipFile, KeyError, ET.ParseError) as exc:
        raise BlsV4SourceCodeError(f"invalid BLS XLSX OOXML structure: {exc}") from exc

    sheet_data = sheet.find(f"{{{_NS}}}sheetData")
    if sheet_data is None:
        raise BlsV4SourceCodeError("BLS worksheet has no sheetData")

    header: str | None = None
    codes: list[str] = []
    for row in sheet_data.findall(f"{{{_NS}}}row"):
        row_number = int(row.attrib.get("r", "0"))
        first_cell = None
        for cell in row.findall(f"{{{_NS}}}c"):
            ref = cell.attrib.get("r", "")
            match = _CELL_RE.fullmatch(ref)
            if match and match.group(1) == "A":
                first_cell = cell
                break
        if first_cell is None:
            continue
        value = _cell_text(first_cell, shared)
        if value is None:
            continue
        value = value.strip()
        if row_number == 1:
            header = value
            continue
        if value:
            codes.append(value)

    if header != "BLS Code":
        raise BlsV4SourceCodeError(f"unexpected BLS code header: {header!r}")
    if len(codes) != expected_count:
        raise BlsV4SourceCodeError(
            f"expected {expected_count} BLS food codes, got {len(codes)}"
        )
    if len(codes) != len(set(codes)):
        raise BlsV4SourceCodeError("BLS food codes must be unique")

    return {
        "source_version": BLS_V4_SOURCE_VERSION,
        "source_sha256": actual_digest,
        "source_codes": sorted(codes),
    }
