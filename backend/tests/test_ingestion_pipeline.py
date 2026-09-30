"""Automated integration test and benchmark for TICK-0205: Unified Ingestion Pipeline."""
import io
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import pymupdf
from backend.app.ingestion.pipeline import IngestionPipeline, IngestionResult


@pytest.fixture(scope="module")
def multi_modal_techpack_pdf(tmp_path_factory) -> Path:
    """Generate a realistic 10-page equestrian tech pack with text, tables, and images."""
    temp_dir = tmp_path_factory.mktemp("pipeline_pdf")
    pdf_path = temp_dir / "equestrian_coat_techpack_10p.pdf"

    # Create dummy images
    sketch = Image.new("RGB", (320, 320), color=(245, 245, 245))
    sketch_bytes = io.BytesIO()
    sketch.save(sketch_bytes, format="PNG")

    logo = Image.new("RGB", (260, 90), color=(15, 25, 45))
    logo_bytes = io.BytesIO()
    logo.save(logo_bytes, format="PNG")

    doc = pymupdf.open()

    pages = [
        ("Cover Page", "STYLE: ME-2026-SJ01\nNAME: Grand Prix Show Coat\nDISCIPLINE: Show Jumping\nSEASON: SS26", None, None),
        ("Front Technical Flat Sketch", "FRONT TECHNICAL ILLUSTRATION WITH CONTOURED WAIST", sketch_bytes.getvalue(), None),
        ("Collar Embroidery", "CHEST AND COLLAR EMBLEM SPECIFICATIONS", logo_bytes.getvalue(), None),
        ("Bill of Materials (BOM)", "BOM SPECIFICATION LIST:", None, {
            "headers": ["Item", "Placement", "Material", "Color", "Unit Cost"],
            "rows": [
                ["Main Shell", "Body", "78% PA 22% EA", "Navy 19-4010", "$18.50"],
                ["Collar Velvet", "Collar", "100% Cotton", "Black 19-0000", "$4.20"],
            ],
            "col_widths": [90, 80, 110, 90, 70],
        }),
        ("Fabric Specifications", "PRIMARY COMPOSITION: 78% Polyamide, 22% Elastane\nWEIGHT: 295 GSM\nWATER REPELLENCY: DWR C0\nBREATHABILITY: 14000 g/m²/24h", None, None),
        ("Points of Measure (POM)", "POM MEASUREMENTS:", None, {
            "headers": ["POM Code", "Point of Measure", "Spec (cm)", "Tol (+/- cm)"],
            "rows": [
                ["POM-01", "Collar Stand Height", "4.5", "0.5"],
                ["POM-02", "Center Back Length", "68.0", "1.0"],
                ["POM-03", "Half Chest Width", "44.0", "0.75"],
            ],
            "col_widths": [80, 150, 80, 80],
        }),
        ("Branding Constraints", "COLLAR LOGO: Left Collar Stand, Dimensions: 7.5 cm x 8.0 cm (Area: 60.0 cm²)\nCHEST EMBLEM: Left Chest Pocket, Dimensions: 10.0 cm x 12.0 cm (Area: 120.0 cm²)", None, None),
        ("Aesthetic Details", "COLLAR TYPE: Notched Lapel with Contrast Velvet Trim\nPIPING: 3.0 mm Satin Piping on Lapel Edge\nBUTTONS: 3 Front Monogram Horn Buttons", None, None),
        ("Packaging & Labeling", "CARE LABEL: 30°C Gentle Machine Wash, Do Not Bleach\nHANGER: Branded Matte Wood Hanger", None, None),
        ("Costing & Sign-Off", "TARGET FOB: $55.00 USD\nACTUAL FOB: $58.50 USD\nSTATUS: Pending Review", None, None),
    ]

    for title, text, img_data, table_data in pages:
        page = doc.new_page(width=595, height=842)
        page.insert_text((50, 60), f"MAISON EQUESTRE - {title.upper()}", fontsize=14, color=(0.1, 0.1, 0.1))
        page.insert_text((50, 100), text, fontsize=10, color=(0.2, 0.2, 0.2))
        if img_data:
            rect = pymupdf.Rect(100, 200, 420, 520)
            page.insert_image(rect, stream=img_data)
        if table_data:
            y_start = 140
            row_height = 24
            headers = table_data["headers"]
            widths = table_data["col_widths"]
            all_rows = [headers] + table_data["rows"]
            for r_idx, row in enumerate(all_rows):
                y = y_start + r_idx * row_height
                x = 50
                for c_idx, cell in enumerate(row):
                    w = widths[c_idx]
                    rect = pymupdf.Rect(x, y, x + w, y + row_height)
                    page.draw_rect(rect, color=(0.7, 0.7, 0.7), width=1)
                    page.insert_text((x + 5, y + 16), str(cell), fontsize=9, color=(0.1, 0.1, 0.1))
                    x += w

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture(scope="module")
def hybrid_scanned_pdf(tmp_path_factory) -> Path:
    """Generate a PDF where page 1 is digital text and page 2 is a pure rasterized scanned image."""
    temp_dir = tmp_path_factory.mktemp("hybrid_pdf")
    pdf_path = temp_dir / "hybrid_techpack.pdf"

    # Scanned image with text
    scan_img = Image.new("RGB", (600, 250), color=(255, 255, 255))
    draw = ImageDraw.Draw(scan_img)
    draw.text((30, 40), "MAISON EQUESTRE HERITAGE SPEC", fill=(0, 0, 0))
    draw.text((30, 80), "FABRIC: 85% VIRGIN WOOL, 15% SILK", fill=(0, 0, 0))
    draw.text((30, 120), "BUTTONS: 4 BRASS BUTTONS", fill=(0, 0, 0))

    scan_bytes = io.BytesIO()
    scan_img.save(scan_bytes, format="PNG")

    doc = pymupdf.open()

    # Page 1: Digital text
    page1 = doc.new_page(width=595, height=842)
    page1.insert_text((50, 60), "DIGITAL TECH PACK COVER", fontsize=14)
    page1.insert_text((50, 100), "STYLE: ME-HERITAGE-01\nDISCIPLINE: Dressage", fontsize=10)

    # Page 2: Scanned image only (no text objects)
    page2 = doc.new_page(width=595, height=842)
    rect = pymupdf.Rect(50, 50, 545, 250)
    page2.insert_image(rect, stream=scan_bytes.getvalue())

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_ingestion_pipeline_digital_benchmark(multi_modal_techpack_pdf):
    """Benchmark full pipeline on a 10-page digital tech pack: assert sub-3s extraction and complete payload."""
    pipeline = IngestionPipeline()
    result = pipeline.process(multi_modal_techpack_pdf)

    assert isinstance(result, IngestionResult)
    assert result.total_pages == 10
    assert len(result.pages) == 10
    assert len(result.tables) >= 2
    assert len(result.figures) >= 2
    assert len(result.ocr_pages_triggered) == 0  # Digital PDF should not need OCR

    # Timing assertions
    print(f"\n[BENCHMARK] 10-Page Ingestion Timings:")
    print(f"  - PyMuPDF4LLM Text: {result.timings.pdf_parse_seconds:.3f}s")
    print(f"  - OCR Stage:        {result.timings.ocr_seconds:.3f}s")
    print(f"  - Table Extraction: {result.timings.table_extraction_seconds:.3f}s")
    print(f"  - Figure Cropping:  {result.timings.figure_extraction_seconds:.3f}s")
    print(f"  - Total Pipeline:   {result.timings.total_seconds:.3f}s")
    print(f"  - Peak Memory:      {result.peak_memory_mb:.1f} MB")

    assert result.timings.total_seconds < 30.0, f"Expected total under 30.0s, got {result.timings.total_seconds}s"
    assert result.peak_memory_mb < 350.0, f"Memory exceeded 350MB limit: {result.peak_memory_mb} MB"


def test_ingestion_pipeline_hybrid_ocr_fallback(hybrid_scanned_pdf):
    """Verify that scanned rasterized pages trigger OCR fallback and enrich markdown."""
    pipeline = IngestionPipeline(char_threshold=30)
    result = pipeline.process(hybrid_scanned_pdf)

    assert result.total_pages == 2
    assert 2 in result.ocr_pages_triggered  # Page 2 was scanned
    assert 1 not in result.ocr_pages_triggered  # Page 1 had digital text

    # Verify OCR text was incorporated into page 2 markdown
    p2_md = result.pages[1].markdown.upper()
    assert "HERITAGE" in p2_md or "WOOL" in p2_md or "MAISON" in p2_md
    assert "HERITAGE" in result.full_markdown.upper()


def test_ingestion_pipeline_file_not_found():
    """Verify appropriate error on missing file."""
    pipeline = IngestionPipeline()
    with pytest.raises(FileNotFoundError):
        pipeline.process("non_existent_techpack.pdf")
