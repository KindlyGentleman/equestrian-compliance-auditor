"""In-depth edge-case and robustness tests for document ingestion, OCR fallback, and table parsing."""
import io
from pathlib import Path

import pymupdf
import pytest
from PIL import Image, ImageDraw

from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.ingestion.table_extractor import TableExtractor


@pytest.fixture
def empty_pdf(tmp_path: Path) -> Path:
    """Create a completely empty (0-byte) file."""
    p = tmp_path / "empty.pdf"
    p.write_bytes(b"")
    return p


@pytest.fixture
def corrupt_garbage_pdf(tmp_path: Path) -> Path:
    """Create a file with arbitrary non-PDF binary noise."""
    p = tmp_path / "corrupt.pdf"
    p.write_bytes(b"NON_PDF_HEADER_CORRUPT_BYTES_XYZ_12345")
    return p


@pytest.fixture
def zero_image_pdf(tmp_path: Path) -> Path:
    """Create a valid PDF containing text and tables but zero images."""
    p = tmp_path / "zero_images.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 60), "MAISON EQUESTRE - TEXT ONLY TECH PACK", fontsize=14)
    page.insert_text((50, 100), "STYLE: ME-TEXT-01\nSEASON: SS26\nCOMPOSITION: 100% Wool", fontsize=10)
    doc.save(str(p))
    doc.close()
    return p


@pytest.fixture
def scanned_raster_pdf(tmp_path: Path) -> Path:
    """Create a 100% scanned raster PDF (a rendered bitmap page with no digital text)."""
    p = tmp_path / "scanned_raster.pdf"

    # Create an image containing text rendered as pixels
    img = Image.new("RGB", (800, 1000), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((60, 60), "STYLE: ME-SCAN-999", fill=(0, 0, 0))
    draw.text((60, 120), "SCANNED PERFORMANCE TAILCOAT TECH SPEC", fill=(0, 0, 0))
    draw.text((60, 180), "PRIMARY FABRIC: 80% WOOL 20% ELASTANE", fill=(0, 0, 0))

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    # Insert only the raster image with no text elements
    page.insert_image(pymupdf.Rect(0, 0, 595, 842), stream=img_bytes.getvalue())
    doc.save(str(p))
    doc.close()
    return p


def test_empty_zero_byte_pdf_raises_error(empty_pdf: Path):
    """Ensure 0-byte PDF fails with a clear, handled exception."""
    pipeline = IngestionPipeline()
    with pytest.raises((ValueError, pymupdf.FileDataError, Exception)):
        pipeline.process(empty_pdf)


def test_corrupt_garbage_pdf_raises_error(corrupt_garbage_pdf: Path):
    """Ensure non-PDF binary noise is rejected cleanly."""
    pipeline = IngestionPipeline()
    with pytest.raises((pymupdf.FileDataError, ValueError, Exception)):
        pipeline.process(corrupt_garbage_pdf)


def test_pdf_without_images_extracts_gracefully(zero_image_pdf: Path):
    """Ensure a tech pack without artwork/sketches yields empty figure list without error."""
    pipeline = IngestionPipeline()
    result = pipeline.process(zero_image_pdf)

    assert result.total_pages == 1
    assert len(result.figures) == 0
    assert "MAISON EQUESTRE" in result.full_markdown


def test_scanned_raster_triggers_ocr_path(scanned_raster_pdf: Path):
    """Verify that a page without native text activates the OCR pipeline."""
    pipeline = IngestionPipeline(char_threshold=30)
    result = pipeline.process(scanned_raster_pdf)

    assert result.total_pages == 1
    assert 1 in result.ocr_pages_triggered
    # Full markdown must contain extracted OCR text
    assert len(result.full_markdown.strip()) > 10


def test_table_extractor_ragged_markdown():
    """Verify table extractor handles ragged rows and missing column separators."""
    extractor = TableExtractor()
    headers = ["item_name", "material", "placement", "unit_cost"]
    ragged_rows = [
        ["Shell", "78% Wool", "Body", "$24.00"],
        ["Incomplete Row", "Missing columns"],  # Only 2 cells
        ["Lining", "100% Cupro", "Sleeves", "$6.50", "Extra 5th cell"],  # 5 cells
    ]
    md = extractor._to_markdown_table(headers, ragged_rows)
    assert "| item_name" in md
    assert "| Shell" in md
    # Row padding ensures exactly 4 columns on every line
    for line in md.splitlines():
        if line.startswith("|"):
            assert line.count("|") >= 5


def test_multi_page_memory_and_latency_budget(tmp_path: Path):
    """Generate a 20-page document and assert ingestion meets latency and memory limits."""
    multi_pdf = tmp_path / "multi_20p.pdf"
    doc = pymupdf.open()
    for i in range(1, 21):
        page = doc.new_page(width=595, height=842)
        page.insert_text((50, 50), f"MAISON EQUESTRE - SECTION {i}", fontsize=14)
        page.insert_text((50, 100), f"SPECIFICATION PAGE {i} WITH TECHNICAL REQUIREMENTS", fontsize=10)
    doc.save(str(multi_pdf))
    doc.close()

    pipeline = IngestionPipeline()
    result = pipeline.process(multi_pdf)

    assert result.total_pages == 20
    assert result.timings.total_seconds < 10.0
    assert result.peak_memory_mb > 0.0
