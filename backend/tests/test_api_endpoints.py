"""Comprehensive integration tests for Stage 7 FastAPI API endpoints."""
import io
from pathlib import Path
from PIL import Image
import pymupdf
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.rag.vector_store import vector_store_manager

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_api_test_environment():
    """Ensure vector store has indexed regulations for search tests."""
    vector_store_manager.index_all_regulations()


@pytest.fixture(scope="module")
def api_test_pdf(tmp_path_factory) -> Path:
    """Generate a sample PDF file for API upload testing."""
    temp_dir = tmp_path_factory.mktemp("api_pdf")
    pdf_path = temp_dir / "api_sample_techpack.pdf"

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 60), "MAISON ÉQUESTRE - GRAND PRIX SHOW COAT", fontsize=14)
    page.insert_text((50, 100), "STYLE: ME-2026-API01\nDISCIPLINE: Show Jumping\nGARMENT TYPE: Show Jacket\nPRIMARY COMPOSITION: 78% Polyamide 22% Elastane\nWEIGHT: 280 GSM\nBREATHABILITY: 12000 g/m²/24h\nTARGET FOB: $55.00 USD\nACTUAL FOB: $52.00 USD", fontsize=10)
    page.insert_text((50, 200), "COLLAR LOGO: Dimensions 5.0 cm x 6.0 cm (Area: 30.0 cm²)\nCHEST EMBLEM: Dimensions 8.0 cm x 10.0 cm (Area: 80.0 cm²)", fontsize=10)
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_health_check_endpoint():
    """Verify health endpoint responds with 200 and operational status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Equestrian" in data["app"]


def test_upload_invalid_extension():
    """Verify uploading non-PDF rejects with HTTP 400."""
    fake_file = io.BytesIO(b"Not a real PDF file")
    response = client.post(
        "/api/audit/upload",
        files={"file": ("invalid.txt", fake_file, "text/plain")},
    )
    assert response.status_code == 400
    assert "Only PDF" in response.json()["detail"]


def test_upload_and_audit_pdf(api_test_pdf: Path):
    """Verify PDF upload triggers pipeline and returns scorecard and audit_id."""
    with open(api_test_pdf, "rb") as f:
        response = client.post(
            "/api/audit/upload",
            files={"file": ("api_sample_techpack.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    data = response.json()
    assert "audit_id" in data
    assert "scorecard" in data
    assert "spec" in data
    audit_id = data["audit_id"]

    # Verify Scorecard Schema
    sc = data["scorecard"]
    assert sc["overall_status"] in ("PASS", "WARNING", "VIOLATION")
    assert sc["overall_score_pct"] >= 0.0
    assert len(sc["category_scores"]) == 5

    # Verify History endpoint
    hist_resp = client.get("/api/audit/history")
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert any(h["audit_id"] == audit_id for h in history)

    # Verify GET by ID
    get_resp = client.get(f"/api/audit/{audit_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["audit_id"] == audit_id

    # Verify PDF stream
    pdf_resp = client.get(f"/api/audit/{audit_id}/pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 100

    # Verify Vendor Export - Markdown
    exp_md = client.post(f"/api/audit/{audit_id}/export-vendor-notes?format=markdown")
    assert exp_md.status_code == 200
    assert "text/markdown" in exp_md.headers["content-type"]
    assert "# Technical Package Revision Request" in exp_md.text

    # Verify Vendor Export - Plain Text Email
    exp_txt = client.post(f"/api/audit/{audit_id}/export-vendor-notes?format=text")
    assert exp_txt.status_code == 200
    assert "text/plain" in exp_txt.headers["content-type"]
    assert "Subject: Revision Required:" in exp_txt.text

    # Verify Vendor Export - PDF
    exp_pdf = client.post(f"/api/audit/{audit_id}/export-vendor-notes?format=pdf")
    assert exp_pdf.status_code == 200
    assert exp_pdf.headers["content-type"] == "application/pdf"
    assert exp_pdf.content.startswith(b"%PDF")


def test_get_nonexistent_audit():
    """Verify 404 for non-existent audit UUID."""
    response = client.get("/api/audit/aud_nonexistent_123")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_rules_catalog_endpoints():
    """Verify rules listing and inspection endpoints."""
    # List all rules
    resp = client.get("/api/rules")
    assert resp.status_code == 200
    rules = resp.json()
    assert len(rules) >= 9

    # Filter by discipline
    resp_jump = client.get("/api/rules?discipline=JUMPING")
    assert resp_jump.status_code == 200
    jump_rules = resp_jump.json()
    assert len(jump_rules) > 0
    assert all(r["discipline"] in ("JUMPING", "ALL") or "JUMPING" in r.get("applicable_disciplines", []) for r in jump_rules)

    # Inspect specific rule
    rule_id = rules[0]["rule_id"]
    rule_resp = client.get(f"/api/rules/{rule_id}")
    assert rule_resp.status_code == 200
    assert rule_resp.json()["rule_id"] == rule_id

    # Search rules
    search_resp = client.post("/api/rules/search", json={"query": "Collar logo maximum area", "discipline": "JUMPING"})
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) > 0
