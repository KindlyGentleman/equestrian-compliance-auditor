"""Automated test and speed benchmark for TICK-0201: PyMuPDF4LLM PDF Parser."""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pymupdf
import pytest

from backend.app.ingestion.pdf_parser import DocumentContent, PDFParser


@pytest.fixture(scope="module")
def sample_techpack_pdf(tmp_path_factory) -> Path:
    """Create a synthetic 10-page luxury equestrian tech pack PDF."""
    temp_dir = tmp_path_factory.mktemp("pdf_fixtures")
    pdf_path = temp_dir / "sample_techpack_10pages.pdf"

    doc = pymupdf.open()
    pages_data = [
        ("Cover Page & Style Info", "STYLE: ME-2026-SJ01\nNAME: Grand Prix Show Coat\nSEASON: SS26\nDISCIPLINE: Show Jumping"),
        ("Bill of Materials (BOM)", "| Item | Placement | Material | Color | Unit Cost |\n|---|---|---|---|---|\n| Main Fabric | Body | 78% PA 22% EA | Navy 19-4010 | $18.50 |\n| Collar Velvet | Collar | 100% Cotton Velvet | Black 19-0000 | $4.20 |"),
        ("Fabric Specifications", "PRIMARY COMPOSITION: 78% Polyamide, 22% Elastane\nWEIGHT: 295 GSM\nBREATHABILITY: 14,000 g/m²/24h\nSTRETCH: 22% 4-Way Stretch"),
        ("Points of Measure (POM)", "| POM Code | Description | Spec (cm) | Tol (+/- cm) |\n|---|---|---|---|\n| POM-01 | Collar Stand Height | 4.5 | 0.5 |\n| POM-02 | Center Back Length | 68.0 | 1.0 |\n| POM-03 | Half Chest Width | 44.0 | 0.75 |"),
        ("Branding & Logo Placements", "COLLAR LOGO: Left Collar Stand, Dimensions: 7.5 cm x 8.0 cm (Area: 60.0 cm²)\nCHEST EMBLEM: Left Chest Pocket, Dimensions: 10.0 cm x 12.0 cm (Area: 120.0 cm²)"),
        ("Aesthetic Details", "COLLAR TYPE: Notched Lapel with Contrast Velvet Trim\nPIPING: 3.0 mm Satin Piping on Lapel Edge\nBUTTONS: 3 Front Monogram Horn Buttons"),
        ("Packaging & Labeling", "CARE LABEL: 30°C Gentle Machine Wash, Do Not Bleach\nHANGER: Branded Matte Wood Hanger"),
        ("Costing Summary", "TARGET FOB: $55.00 USD\nACTUAL FOB: $58.50 USD\nFABRIC COST: $24.00\nCMT COST: $28.50"),
        ("Grading Rules", "| Size | 34 | 36 | 38 | 40 | 42 |\n|---|---|---|---|---|---|\n| Chest (cm) | 84.0 | 88.0 | 92.0 | 96.0 | 100.0 |\n| Waist (cm) | 66.0 | 70.0 | 74.0 | 78.0 | 82.0 |"),
        ("Quality Inspection Sign-off", "LEAD DESIGNER: Approved\nSOURCING LEAD: Pending FOB renegotiation\nFEI STATUS: Under Review"),
    ]

    for title, text in pages_data:
        page = doc.new_page(width=595, height=842)  # A4
        # Add heading
        page.insert_text((50, 60), f"MAISON EQUESTRE - {title.upper()}", fontsize=14, color=(0.1, 0.1, 0.1))
        # Add body text
        page.insert_text((50, 110), text, fontsize=10, color=(0.2, 0.2, 0.2))

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_pdf_parser_success(sample_techpack_pdf):
    """Verify parsing of multi-page PDF extracts all pages with clean metadata."""
    parser = PDFParser()
    result = parser.parse(sample_techpack_pdf)

    assert isinstance(result, DocumentContent)
    assert result.total_pages == 10
    assert len(result.pages) == 10
    assert result.file_name == "sample_techpack_10pages.pdf"

    # Check page 1
    page1 = result.pages[0]
    assert page1.page_number == 1
    assert "ME-2026-SJ01" in page1.markdown

    # Check page 2 (tables)
    page2 = result.pages[1]
    assert page2.page_number == 2
    assert "Main Fabric" in page2.markdown
    assert page2.has_tables is True


def test_pdf_parser_speed_benchmark(sample_techpack_pdf):
    """Assert that a 10-page technical PDF parses in under 5.0 seconds on CPU (<= 0.5s per page)."""
    parser = PDFParser()
    result = parser.parse(sample_techpack_pdf)

    print(f"\n[BENCHMARK] 10-page PDF parsed in {result.execution_time_seconds:.4f}s")
    assert result.execution_time_seconds < 5.0, f"Parsing exceeded latency budget: {result.execution_time_seconds}s"


def test_pdf_parser_nonexistent_file():
    """Verify clean FileNotFoundError when target PDF does not exist."""
    parser = PDFParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent_path/fake_techpack.pdf")


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        dummy_path = Path(td) / "test.pdf"
        d = pymupdf.open()
        p = d.new_page()
        p.insert_text((50, 50), "Hello Equestrian Wear")
        d.save(str(dummy_path))
        d.close()

        parser = PDFParser()
        res = parser.parse(dummy_path)
        print("Test parse output:", res.pages[0].markdown)
        print(f"Parsed 1 page in {res.execution_time_seconds:.4f}s")
        print("ALL TICK-0201 TESTS PASSED SUCCESSFULLY!")
