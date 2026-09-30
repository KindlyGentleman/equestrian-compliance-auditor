"""Automated unit test for TICK-0204: RapidOCR-ONNX Fallback Parser."""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import pymupdf
from PIL import Image, ImageDraw
import io
from backend.app.ingestion.ocr_fallback import OCRFallback, OCRPageResult


@pytest.fixture(scope="module")
def rasterized_scanned_pdf(tmp_path_factory) -> Path:
    """Generate a PDF containing only a rasterized image of text (no selectable digital text)."""
    temp_dir = tmp_path_factory.mktemp("scanned_pdf")
    pdf_path = temp_dir / "scanned_techpack.pdf"

    # Create image with text drawn on pixels
    img = Image.new("RGB", (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((30, 40), "MAISON EQUESTRE PARIS", fill=(0, 0, 0))
    draw.text((30, 80), "STYLE CODE: ME-SCANNED-01", fill=(0, 0, 0))
    draw.text((30, 120), "COMPOSITION: 100% MERINO WOOL", fill=(0, 0, 0))
    draw.text((30, 160), "ACTUAL FOB: $45.00 USD", fill=(0, 0, 0))

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Insert into PDF as pure image
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    rect = pymupdf.Rect(50, 50, 545, 295)
    page.insert_image(rect, stream=img_bytes.getvalue())
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_is_scanned_page_detection():
    """Verify scanner detector distinguishes digital vs scanned text."""
    fallback = OCRFallback(char_threshold=30)
    assert fallback.is_scanned_page("") is True
    assert fallback.is_scanned_page("   \n\t  ") is True
    assert fallback.is_scanned_page("Short") is True
    assert fallback.is_scanned_page("This is a full page with plenty of selectable technical text and specifications.") is False


def test_ocr_page_fallback(rasterized_scanned_pdf):
    """Verify RapidOCR extracts text from rasterized page."""
    fallback = OCRFallback()
    doc = pymupdf.open(str(rasterized_scanned_pdf))
    page = doc[0]

    # Verify that standard text extraction returns empty or near empty
    raw_text = page.get_text()
    assert fallback.is_scanned_page(raw_text) is True

    # Run OCR fallback
    ocr_result = fallback.ocr_page(page, page_number=1)
    doc.close()

    assert isinstance(ocr_result, OCRPageResult)
    assert ocr_result.line_count >= 2
    assert ocr_result.average_confidence > 0.60
    assert "EQUESTRE" in ocr_result.text.upper() or "STYLE" in ocr_result.text.upper()
    print(f"\n[OK] OCR extracted {ocr_result.line_count} lines in {ocr_result.execution_time_seconds:.3f}s with conf {ocr_result.average_confidence:.2f}")


if __name__ == "__main__":
    print("ALL TICK-0204 TESTS DEFINED!")
