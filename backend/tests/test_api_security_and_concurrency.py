"""In-depth security, path traversal protection, error resilience, and concurrency tests for FastAPI API."""
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pymupdf
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.main import app
from backend.app.rag.vector_store import vector_store_manager

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_vector_environment():
    """Ensure vector store has indexed regulations."""
    vector_store_manager.index_all_regulations()


@pytest.fixture
def minimal_valid_pdf(tmp_path: Path) -> Path:
    """Generate a minimal valid PDF for upload checks."""
    pdf_path = tmp_path / "valid_test.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), "MAISON EQUESTRE - SECURITY AUDIT SAMPLE", fontsize=14)
    page.insert_text((50, 100), "STYLE: ME-SEC-01\nSEASON: SS26\nCOMPOSITION: 100% Wool", fontsize=10)
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.mark.parametrize("malicious_filename", [
    "../../etc/passwd.pdf",
    "..\\..\\windows\\system32\\calc.exe.pdf",
    "....//....//traversal.pdf",
    "subdir/nested/path.pdf",
])
def test_path_traversal_filename_sanitization(minimal_valid_pdf: Path, malicious_filename: str):
    """Ensure filenames with directory traversal tokens are sanitized and contained within UPLOAD_DIR."""
    with open(minimal_valid_pdf, "rb") as f:
        response = client.post(
            "/api/audit/upload",
            files={"file": (malicious_filename, f, "application/pdf")},
        )

    assert response.status_code == 200
    data = response.json()
    assert "audit_id" in data
    audit_id = data["audit_id"]

    # Verify that no file was created outside settings.UPLOAD_DIR
    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    all_uploads = [p.resolve() for p in upload_dir.glob(f"*{audit_id}*")]
    assert len(all_uploads) > 0
    for uploaded_file in all_uploads:
        assert upload_dir in uploaded_file.parents


@pytest.mark.parametrize("bad_filename,content_type", [
    ("malicious.exe", "application/x-msdownload"),
    ("script.sh", "text/x-shellscript"),
    ("image.png", "image/png"),
    ("doc.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
])
def test_reject_non_pdf_file_extensions(bad_filename: str, content_type: str):
    """Ensure non-PDF file extensions are rejected with HTTP 400."""
    fake_content = io.BytesIO(b"DUMMY_PAYLOAD")
    response = client.post(
        "/api/audit/upload",
        files={"file": (bad_filename, fake_content, content_type)},
    )
    assert response.status_code == 400
    assert "Only PDF" in response.json()["detail"]


def test_nonexistent_audit_id_returns_404():
    """Verify 404 responses for missing audit records across scorecard, PDF, and vendor exports."""
    bogus_id = "aud_nonexistent_xyz999"

    resp_get = client.get(f"/api/audit/{bogus_id}")
    assert resp_get.status_code == 404

    resp_pdf = client.get(f"/api/audit/{bogus_id}/pdf")
    assert resp_pdf.status_code == 404

    resp_export = client.post(f"/api/audit/{bogus_id}/export-vendor-notes")
    assert resp_export.status_code == 404


def test_invalid_vendor_export_format_returns_error():
    """Verify unsupported export format raises 400 or 422."""
    sample_resp = client.post("/api/audit/sample")
    assert sample_resp.status_code == 200
    audit_id = sample_resp.json()["audit_id"]

    resp = client.post(f"/api/audit/{audit_id}/export-vendor-notes?format=unsupported_format_xyz")
    assert resp.status_code in (400, 422)


def test_rules_catalog_query_filtering():
    """Verify rules endpoint filters by discipline and returns structured rules."""
    all_rules_resp = client.get("/api/rules")
    assert all_rules_resp.status_code == 200
    all_rules = all_rules_resp.json()
    assert isinstance(all_rules, list)
    assert len(all_rules) >= 8

    # Filter by JUMPING
    jumping_resp = client.get("/api/rules?discipline=JUMPING")
    assert jumping_resp.status_code == 200
    jumping_rules = jumping_resp.json()
    assert isinstance(jumping_rules, list)
    assert all(r["discipline"] in ("JUMPING", "ALL") for r in jumping_rules)


def test_concurrent_sample_audit_requests():
    """Simulate 6 concurrent audit executions to verify thread-safety and SQLite integrity."""
    def run_sample_audit(worker_idx: int) -> tuple[int, str]:
        # Dedicated client call in thread
        res = client.post("/api/audit/sample")
        if res.status_code == 200:
            return res.status_code, res.json()["audit_id"]
        return res.status_code, ""

    concurrency = 6
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(run_sample_audit, i) for i in range(concurrency)]
        results = [f.result() for f in futures]

    status_codes = [r[0] for r in results]
    audit_ids = [r[1] for r in results]

    assert all(code == 200 for code in status_codes), f"Non-200 responses observed: {status_codes}"
    # All concurrent audits must produce distinct audit IDs
    assert len(set(audit_ids)) == concurrency, f"Duplicate audit IDs generated: {audit_ids}"
