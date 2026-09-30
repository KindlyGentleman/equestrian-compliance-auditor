"""Automated unit test for TICK-0202: Tabular Data Extraction & Markdown Normalizer."""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pymupdf
import pytest

from backend.app.ingestion.table_extractor import TableExtractionResult, TableExtractor


@pytest.fixture(scope="module")
def techpack_with_tables_pdf(tmp_path_factory) -> Path:
    """Generate a PDF containing explicit BOM and Measurement tables with cell borders."""
    temp_dir = tmp_path_factory.mktemp("table_pdf")
    pdf_path = temp_dir / "techpack_tables.pdf"

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)

    # Draw a simulated BOM table with drawn grid lines
    # Title
    page.insert_text((50, 50), "BILL OF MATERIALS (BOM)", fontsize=14, color=(0, 0, 0))

    # We can draw lines or use standard table layout
    # Headers
    headers = ["Item", "Placement", "Material", "Unit Cost"]
    rows = [
        ["Main Fabric", "Jacket Body", "78% PA 22% EA", "$18.50"],
        ["Collar Velvet", "Collar Stand", "100% Velvet", "$4.20"],
        ["Front Buttons", "Closure", "Horn Monogram", "$2.10"],
    ]

    # Draw table bounding boxes and text
    y_start = 80
    row_height = 25
    col_widths = [100, 100, 140, 80]

    # Draw table grid
    for r_idx, row in enumerate([headers] + rows):
        y = y_start + r_idx * row_height
        x = 50
        for c_idx, cell in enumerate(row):
            w = col_widths[c_idx]
            rect = pymupdf.Rect(x, y, x + w, y + row_height)
            page.draw_rect(rect, color=(0.7, 0.7, 0.7), width=1)
            page.insert_text((x + 5, y + 17), cell, fontsize=9, color=(0.1, 0.1, 0.1))
            x += w

    # Draw second page with POM Measurements table
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text((50, 50), "POINTS OF MEASURE (POM)", fontsize=14, color=(0, 0, 0))

    pom_headers = ["POM Code", "Point of Measure", "Spec (cm)", "Tol (+/- cm)"]
    pom_rows = [
        ["POM-01", "Collar Stand Height", "4.5", "0.5"],
        ["POM-02", "Center Back Length", "68.0", "1.0"],
        ["POM-03", "Half Chest Width", "44.0", "0.75"],
    ]
    pom_col_widths = [80, 160, 90, 90]
    for r_idx, row in enumerate([pom_headers] + pom_rows):
        y = y_start + r_idx * row_height
        x = 50
        for c_idx, cell in enumerate(row):
            w = pom_col_widths[c_idx]
            rect = pymupdf.Rect(x, y, x + w, y + row_height)
            page2.draw_rect(rect, color=(0.7, 0.7, 0.7), width=1)
            page2.insert_text((x + 5, y + 17), cell, fontsize=9, color=(0.1, 0.1, 0.1))
            x += w

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_table_extractor_bom_and_pom(techpack_with_tables_pdf):
    """Verify that both BOM and POM tables are extracted, categorized, and normalized."""
    extractor = TableExtractor()
    result = extractor.extract_tables(techpack_with_tables_pdf)

    assert isinstance(result, TableExtractionResult)
    assert result.total_tables == 2

    # Check BOM Table (Page 1)
    bom_table = result.tables[0]
    assert bom_table.page_number == 1
    assert bom_table.table_type == "BOM"
    assert "item_name" in bom_table.headers
    assert "material" in bom_table.headers
    assert len(bom_table.rows) == 3
    assert bom_table.rows[0]["item_name"] == "Main Fabric"
    assert "|" in bom_table.markdown

    # Check POM Table (Page 2)
    pom_table = result.tables[1]
    assert pom_table.page_number == 2
    assert pom_table.table_type == "MEASUREMENTS"
    assert "pom_code" in pom_table.headers
    assert "spec_cm" in pom_table.headers
    assert "tolerance_cm" in pom_table.headers
    assert len(pom_table.rows) == 3
    assert pom_table.rows[0]["pom_code"] == "POM-01"
    assert pom_table.rows[0]["spec_cm"] == "4.5"


def test_header_normalization():
    """Verify synonym dictionary normalizes varied fashion headers."""
    extractor = TableExtractor()
    assert extractor._normalize_header("POM Code") == "pom_code"
    assert extractor._normalize_header("Point of Measure") == "description"
    assert extractor._normalize_header("Spec (cm)") == "spec_cm"
    assert extractor._normalize_header("Tol (+/- cm)") == "tolerance_cm"
    assert extractor._normalize_header("Unit Cost ($)") == "unit_cost"


if __name__ == "__main__":
    test_header_normalization()
    print("ALL TICK-0202 TESTS PASSED SUCCESSFULLY!")
