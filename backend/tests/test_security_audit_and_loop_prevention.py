"""Comprehensive security audit, infinite loop prevention, ReDoS, and anti-tampering test suite."""
import io
import time
from pathlib import Path

import pymupdf
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.engine.citation_verifier import CitationVerifier
from backend.app.engine.sanitizer import TechPackSanitizer
from backend.app.ingestion.image_cropper import ImageCropper
from backend.app.ingestion.pdf_parser import PDFParser
from backend.app.main import app

client = TestClient(app)


def test_reject_fake_pdf_without_magic_bytes():
    """Verify that files with a .pdf extension but lacking the %PDF- magic signature are rejected with 400."""
    fake_stream = io.BytesIO(b"MALICIOUS_SCRIPT_OR_EXE_PAYLOAD_WITHOUT_PDF_HEADER")
    response = client.post(
        "/api/audit/upload",
        files={"file": ("exploit.pdf", fake_stream, "application/pdf")},
    )

    assert response.status_code == 400
    assert "PDF header signature" in response.json()["detail"]


@pytest.mark.parametrize("reserved_name", ["CON.pdf", "NUL.pdf", "PRN.pdf", "AUX.pdf", "COM1.pdf"])
def test_windows_reserved_device_names_sanitization(reserved_name: str, tmp_path: Path):
    """Verify Windows reserved device filenames are sanitized and do not trigger filesystem locking."""
    pdf_path = tmp_path / "sample.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), "MAISON EQUESTRE - RESERVED FILENAME TEST", fontsize=12)
    doc.save(str(pdf_path))
    doc.close()

    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/audit/upload",
            files={"file": (reserved_name, f, "application/pdf")},
        )

    assert response.status_code == 200
    audit_id = response.json()["audit_id"]

    upload_dir = Path(settings.UPLOAD_DIR)
    matching_files = list(upload_dir.glob(f"*{audit_id}*"))
    assert len(matching_files) == 1
    # Filename must have been prefixed with safe_ to disarm Windows device locks
    assert "safe_" in matching_files[0].name


def test_sanitizer_redos_backtracking_immunity():
    """Ensure regex parsing of fiber composition is immune to exponential catastrophic backtracking."""
    sanitizer = TechPackSanitizer()

    # Adversarial ReDoS payload with deep whitespace repetition
    evil_payload = "10% " + (" " * 500) + "Wool and 90% " + (" " * 500) + "Silk"

    t0 = time.perf_counter()
    normalized, _ = sanitizer.normalize_composition_string(evil_payload)
    elapsed = time.perf_counter() - t0

    # Must execute in under 15 milliseconds without hanging
    assert elapsed < 0.015, f"Regex evaluation took too long ({elapsed:.4f}s); vulnerable to ReDoS"
    assert "Wool" in normalized or "Silk" in normalized


def test_citation_verifier_word_cap_and_cpu_loop_defense():
    """Verify that massive texts do not freeze CPU threads in windowed SequenceMatcher loop."""
    verifier = CitationVerifier()

    # Generate a massive document of 20,000 words
    huge_text = " ".join(["equestrian", "saddle", "competition", "jacket", "leather"] * 4000)
    query = "The total surface area of this identification must not exceed sixty square centimeters (60 cm²)."

    t0 = time.perf_counter()
    matched = verifier._fuzzy_match(query, huge_text, threshold=0.92)
    elapsed = time.perf_counter() - t0

    # Word cap and fast token overlap filter must ensure termination in under 100 milliseconds
    assert elapsed < 0.10, f"SequenceMatcher loop took {elapsed:.4f}s on massive text"
    assert matched is False


def test_pdf_parser_rejects_decompression_page_bomb(tmp_path: Path):
    """Verify that PDFs exceeding 100 pages are rejected to prevent memory exhaustion."""
    large_pdf = tmp_path / "bomb_105_pages.pdf"
    doc = pymupdf.open()
    for _ in range(105):
        doc.new_page(width=300, height=300)
    doc.save(str(large_pdf))
    doc.close()

    parser = PDFParser()
    with pytest.raises(ValueError, match="exceeds maximum page limit"):
        parser.parse(large_pdf)


def test_image_cropper_caps_at_50_figures(tmp_path: Path):
    """Verify that PDFs with an excessive number of images are capped at 50 figures to protect disk storage."""
    flood_pdf = tmp_path / "flood_images.pdf"
    doc = pymupdf.open()

    from PIL import Image
    blank = Image.new("RGB", (100, 100), color=(200, 200, 200))
    img_bytes = io.BytesIO()
    blank.save(img_bytes, format="PNG")

    for _p in range(10):
        page = doc.new_page(width=595, height=842)
        for i in range(8):  # 10 pages * 8 images = 80 images
            page.insert_image(pymupdf.Rect(i * 50, 100, (i + 1) * 50, 150), stream=img_bytes.getvalue())

    doc.save(str(flood_pdf))
    doc.close()

    cropper = ImageCropper()
    result = cropper.extract_figures(flood_pdf)

    assert result.total_figures <= 50


def test_cannot_delete_baseline_fei_rules():
    """Verify that core Olympic FEI regulatory articles cannot be deleted via the API (403 Forbidden)."""
    response = client.delete("/api/rules/FEI-JUMP-LOGO-COLLAR")
    assert response.status_code == 403
    assert "Cannot delete baseline Olympic FEI regulation" in response.json()["detail"]


def test_cors_header_hardening():
    """Verify CORS does not reflect unauthorized origins when credentials are supported."""
    response = client.get(
        "/api/health",
        headers={"Origin": "http://malicious-site.com"},
    )
    assert response.status_code == 200
    allow_origin = response.headers.get("access-control-allow-origin")
    # Must NOT reflect the malicious origin
    assert allow_origin != "http://malicious-site.com"
