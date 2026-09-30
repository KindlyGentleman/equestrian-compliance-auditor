"""End-to-End Stakeholder Demonstration Verification Test (<90s SLA) (TICK-0805).

Verifies the two key presentation scenarios:
- Scenario A: Show Jumping Competition Coat with oversized collar logo (65 cm² vs 60 cm² max)
  and piping exceeding threshold, verifying verbatim citation gate and vendor note generation.
- Scenario B: Fully compliant Dressage garment meeting all FEI Art. 427 and brand SOP standards.
"""
import time
from pathlib import Path

import pymupdf
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.rag.vector_store import vector_store_manager

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_vector_store():
    """Ensure vector store has indexed regulations."""
    vector_store_manager.index_all_regulations()


@pytest.fixture(scope="module")
def scenario_a_pdf(tmp_path_factory) -> Path:
    """Scenario A: Show Jumping Coat with Violations (Collar Logo 65cm², Piping 3.5mm, FOB $62 vs $55)."""
    temp_dir = tmp_path_factory.mktemp("demo_scenarios")
    pdf_path = temp_dir / "scenario_a_sj_coat_violations.pdf"

    doc = pymupdf.open()

    # 1. Cover
    p1 = doc.new_page(width=595, height=842)
    p1.insert_text((50, 60), "MAISON ÉQUESTRE - TECHNICAL SPECIFICATION", fontsize=14)
    p1.insert_text((50, 100), "STYLE: ME-2026-SJ-DEMO\nNAME: Sovereign Grand Prix Coat\nDISCIPLINE: Show Jumping\nGARMENT TYPE: Show Jacket\nSEASON: SS26", fontsize=10)

    # 2. Fabric & BOM
    p2 = doc.new_page(width=595, height=842)
    p2.insert_text((50, 60), "FABRIC & MATERIAL SPECIFICATION", fontsize=12)
    p2.insert_text((50, 100), "PRIMARY COMPOSITION: 75% Polyamide, 25% Elastane\nWEIGHT: 290 GSM\nBREATHABILITY: 12000 g/m²/24h\nWATER RESISTANCE: 4000 mm", fontsize=10)

    # 3. Branding (With Violation: Collar Logo 65 cm² > 60 cm² limit)
    p3 = doc.new_page(width=595, height=842)
    p3.insert_text((50, 60), "BRANDING SPECIFICATION", fontsize=12)
    p3.insert_text((50, 100), "COLLAR LOGO: Left collar stand, Dimensions: 6.5 cm x 10.0 cm (Area: 65.0 cm²)\nCHEST EMBLEM: Left chest pocket, Dimensions: 10.0 cm x 12.0 cm (Area: 120.0 cm²)", fontsize=10)

    # 4. Trims & Piping (With Violation: Piping 3.5 mm > 3.0 mm limit)
    p4 = doc.new_page(width=595, height=842)
    p4.insert_text((50, 60), "TRIMS & AESTHETICS", fontsize=12)
    p4.insert_text((50, 100), "COLLAR TYPE: Stand Collar with Contrast Velvet\nPIPING: 3.5 mm Gold Satin Piping along lapel\nBUTTONS: 4 Horn Front Buttons", fontsize=10)

    # 5. Costing (With Violation: Actual FOB $62.00 > Target FOB $55.00)
    p5 = doc.new_page(width=595, height=842)
    p5.insert_text((50, 60), "COMMERCIAL COSTING", fontsize=12)
    p5.insert_text((50, 100), "TARGET FOB: $55.00 USD\nACTUAL FOB: $62.00 USD\nRETAIL: $520.00 USD", fontsize=10)

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture(scope="module")
def scenario_b_pdf(tmp_path_factory) -> Path:
    """Scenario B: Fully Compliant Dressage Jacket."""
    temp_dir = tmp_path_factory.mktemp("demo_scenarios")
    pdf_path = temp_dir / "scenario_b_dressage_compliant.pdf"

    doc = pymupdf.open()

    # 1. Cover
    p1 = doc.new_page(width=595, height=842)
    p1.insert_text((50, 60), "MAISON ÉQUESTRE - DRESSAGE TECHNICAL SPECIFICATION", fontsize=14)
    p1.insert_text((50, 100), "STYLE: ME-2026-DR-COMPLIANT\nNAME: Étoile Dressage Tailcoat\nDISCIPLINE: Dressage\nGARMENT TYPE: Show Jacket\nSEASON: SS26", fontsize=10)

    # 2. Fabric & Performance
    p2 = doc.new_page(width=595, height=842)
    p2.insert_text((50, 60), "FABRIC & MATERIAL SPECIFICATION", fontsize=12)
    p2.insert_text((50, 100), "PRIMARY COMPOSITION: 80% Wool, 18% Polyamide, 2% Elastane\nWEIGHT: 310 GSM\nBREATHABILITY: 15000 g/m²/24h\nWATER RESISTANCE: 3000 mm", fontsize=10)

    # 3. Branding (Compliant: Collar Logo 45 cm² <= 60 cm² limit)
    p3 = doc.new_page(width=595, height=842)
    p3.insert_text((50, 60), "BRANDING SPECIFICATION", fontsize=12)
    p3.insert_text((50, 100), "COLLAR LOGO: Single Collar Emblem, Dimensions: 5.0 cm x 9.0 cm (Area: 45.0 cm²)", fontsize=10)

    # 4. Trims & Aesthetics (Compliant: Piping 2.0 mm <= 3.0 mm limit)
    p4 = doc.new_page(width=595, height=842)
    p4.insert_text((50, 60), "TRIMS & AESTHETICS", fontsize=12)
    p4.insert_text((50, 100), "COLLAR TYPE: Velvet Collar Insert\nPIPING: 2.0 mm Subtle Tone-on-Tone Piping\nBUTTONS: 6 Front Weighted Tailcoat Buttons", fontsize=10)

    # 5. Costing (Compliant: Actual FOB $78.00 <= Target FOB $80.00)
    p5 = doc.new_page(width=595, height=842)
    p5.insert_text((50, 60), "COMMERCIAL COSTING", fontsize=12)
    p5.insert_text((50, 100), "TARGET FOB: $80.00 USD\nACTUAL FOB: $78.00 USD\nRETAIL: $690.00 USD", fontsize=10)

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_scenario_a_demonstration_workflow(scenario_a_pdf: Path):
    """Test full stakeholder demonstration for Scenario A in under 90 seconds."""
    demo_start = time.perf_counter()

    # Step 1: Upload and audit
    with open(scenario_a_pdf, "rb") as f:
        upload_res = client.post("/api/audit/upload", files={"file": ("sovereign_coat.pdf", f, "application/pdf")})

    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    audit_data = upload_res.json()
    audit_id = audit_data["audit_id"]
    scorecard = audit_data["scorecard"]

    # Assert violations flagged
    assert scorecard["overall_status"] in ("VIOLATION", "WARNING")
    findings = scorecard["findings"]
    assert len(findings) > 0

    # Assert verbatim citation presence for collar logo violation
    collar_finding = next((f for f in findings if "collar" in f["title"].lower() or "logo" in f["title"].lower()), None)
    assert collar_finding is not None
    assert "FEI" in collar_finding["source_rulebook"]
    assert len(collar_finding["source_citation"]) > 20

    # Step 2: Export Vendor Revision Notes in 3 formats
    md_res = client.post(f"/api/audit/{audit_id}/export-vendor-notes?format=markdown")
    assert md_res.status_code == 200
    assert "Revision Request" in md_res.text
    assert "Sovereign Grand Prix Coat" in md_res.text
    assert "FEI-JUMP-LOGO-COLLAR" in md_res.text

    txt_res = client.post(f"/api/audit/{audit_id}/export-vendor-notes?format=text")
    assert txt_res.status_code == 200
    assert "Subject:" in txt_res.text

    pdf_res = client.post(f"/api/audit/{audit_id}/export-vendor-notes?format=pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000

    total_demo_elapsed = time.perf_counter() - demo_start
    # Assert demonstration completes well under the 90-second SLA
    assert total_demo_elapsed < 90.0, f"Demo exceeded 90s SLA: {total_demo_elapsed:.2f}s"


def test_scenario_b_compliant_demonstration_workflow(scenario_b_pdf: Path):
    """Test full stakeholder demonstration for Scenario B (Compliant Garment)."""
    demo_start = time.perf_counter()

    with open(scenario_b_pdf, "rb") as f:
        upload_res = client.post("/api/audit/upload", files={"file": ("etoile_tailcoat.pdf", f, "application/pdf")})

    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    audit_data = upload_res.json()
    scorecard = audit_data["scorecard"]

    # Assert compliant status
    assert scorecard["overall_status"] == "PASS"
    assert scorecard["overall_score_pct"] >= 95.0

    total_demo_elapsed = time.perf_counter() - demo_start
    assert total_demo_elapsed < 90.0


def test_sample_one_click_demo_endpoint():
    """Verify one-click sample demonstration endpoint works instantaneously."""
    sample_start = time.perf_counter()
    res = client.post("/api/audit/sample")
    assert res.status_code == 200
    data = res.json()
    assert "audit_id" in data
    assert "scorecard" in data
    assert data["scorecard"]["overall_score_pct"] > 0
    total_sample_elapsed = time.perf_counter() - sample_start
    assert total_sample_elapsed < 30.0
