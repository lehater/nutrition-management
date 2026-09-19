from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from nutrition_management.food_knowledge.infrastructure.bls_v4_source_codes import (
    BlsV4SourceCodeError,
    extract_bls_v4_source_codes,
)


def write_workbook(path: Path, codes: tuple[str, ...]) -> str:
    workbook = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="BLS" sheetId="1" r:id="rId1"/></sheets>
</workbook>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"
    Target="worksheets/sheet1.xml"/>
</Relationships>"""
    rows = [
        '<row r="1"><c r="A1" t="inlineStr"><is><t>BLS Code</t></is></c></row>'
    ]
    for index, code in enumerate(codes, start=2):
        rows.append(
            f'<row r="{index}"><c r="A{index}" t="inlineStr"><is><t>{code}</t></is></c></row>'
        )
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{''.join(rows)}</sheetData></worksheet>"
    )

    with ZipFile(path, "w", ZIP_DEFLATED) as book:
        book.writestr("xl/workbook.xml", workbook)
        book.writestr("xl/_rels/workbook.xml.rels", rels)
        book.writestr("xl/worksheets/sheet1.xml", sheet)
    return sha256(path.read_bytes()).hexdigest()


def test_extracts_sorted_exact_source_codes_from_pinned_ooxml(tmp_path):
    path = tmp_path / "bls.xlsx"
    digest = write_workbook(path, ("F110100", "B111000", "C131000"))

    result = extract_bls_v4_source_codes(
        path,
        expected_sha256=digest,
        expected_count=3,
    )

    assert result == {
        "source_version": "4.0",
        "source_sha256": digest,
        "source_codes": ["B111000", "C131000", "F110100"],
    }


def test_rejects_wrong_source_digest(tmp_path):
    path = tmp_path / "bls.xlsx"
    write_workbook(path, ("B111000",))

    with pytest.raises(BlsV4SourceCodeError, match="digest mismatch"):
        extract_bls_v4_source_codes(
            path,
            expected_sha256="0" * 64,
            expected_count=1,
        )


def test_rejects_duplicate_or_wrong_count_source_codes(tmp_path):
    path = tmp_path / "bls.xlsx"
    digest = write_workbook(path, ("B111000", "B111000"))

    with pytest.raises(BlsV4SourceCodeError, match="must be unique"):
        extract_bls_v4_source_codes(
            path,
            expected_sha256=digest,
            expected_count=2,
        )

    digest = write_workbook(path, ("B111000",))
    with pytest.raises(BlsV4SourceCodeError, match="expected 2"):
        extract_bls_v4_source_codes(
            path,
            expected_sha256=digest,
            expected_count=2,
        )
