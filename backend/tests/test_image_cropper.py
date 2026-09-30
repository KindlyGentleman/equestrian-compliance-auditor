"""Automated test for TICK-0203: Technical Sketch & Logo Artwork Cropper."""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import pymupdf
from PIL import Image
import io
from backend.app.ingestion.image_cropper import ImageCropper, ImageCropperResult


@pytest.fixture(scope="module")
def techpack_with_sketches_pdf(tmp_path_factory) -> Path:
    """Create a PDF with embedded technical flat sketch and collar badge images."""
    temp_dir = tmp_path_factory.mktemp("cropper_pdf")
    pdf_path = temp_dir / "techpack_sketches.pdf"

    # Create dummy PIL images
    sketch_img = Image.new("RGB", (300, 300), color=(240, 240, 245))
    sketch_bytes = io.BytesIO()
    sketch_img.save(sketch_bytes, format="PNG")
    sketch_bytes.seek(0)

    logo_img = Image.new("RGB", (250, 80), color=(10, 25, 40))
    logo_bytes = io.BytesIO()
    logo_img.save(logo_bytes, format="PNG")
    logo_bytes.seek(0)

    # Insert into PDF
    doc = pymupdf.open()
    
    # Page 1: Flat sketch
    page1 = doc.new_page(width=595, height=842)
    page1.insert_text((50, 50), "FRONT & BACK TECHNICAL SKETCH", fontsize=14, color=(0, 0, 0))
    rect_sketch = pymupdf.Rect(100, 100, 400, 400)
    page1.insert_image(rect_sketch, stream=sketch_bytes.getvalue())

    # Page 2: Collar Logo artwork
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text((50, 50), "COLLAR EMBROIDERY ARTWORK", fontsize=14, color=(0, 0, 0))
    rect_logo = pymupdf.Rect(100, 120, 350, 200)
    page2.insert_image(rect_logo, stream=logo_bytes.getvalue())

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_image_cropper_extraction(techpack_with_sketches_pdf, tmp_path):
    """Verify that embedded sketches and logos are cropped, cached, and classified."""
    output_dir = tmp_path / "figures_cache"
    cropper = ImageCropper(output_dir=str(output_dir), min_size=50)
    result = cropper.extract_figures(techpack_with_sketches_pdf)

    assert isinstance(result, ImageCropperResult)
    assert result.total_figures == 2

    # Check figure 1 (Flat sketch on page 1)
    fig1 = result.figures[0]
    assert fig1.page_number == 1
    assert Path(fig1.file_path).exists()
    assert fig1.width_px == 300
    assert fig1.height_px == 300
    assert fig1.figure_type == "SKETCH"
    assert len(fig1.bounding_box) == 4

    # Check figure 2 (Logo on page 2)
    fig2 = result.figures[1]
    assert fig2.page_number == 2
    assert Path(fig2.file_path).exists()
    assert fig2.width_px == 250
    assert fig2.height_px == 80
    assert fig2.figure_type == "LOGO"


if __name__ == "__main__":
    print("ALL TICK-0203 TESTS DEFINED!")
