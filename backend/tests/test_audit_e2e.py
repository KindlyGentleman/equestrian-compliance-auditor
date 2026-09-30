"""End-to-End Audit Pipeline Benchmark and Zero-False-Positive Accuracy Test (TICK-0604)."""
import io
import time
from pathlib import Path
from PIL import Image
import pymupdf
import pytest

from backend.app.engine.audit_coordinator import AuditCoordinator
from backend.app.engine.citation_verifier import CitationVerifier
from backend.app.engine.sanitizer import TechPackSanitizer
from backend.app.engine.scorecard_generator import ScorecardGenerator
from backend.app.engine.structuring_service import StructuringService
from backend.app.engine.vendor_action_generator import VendorActionGenerator
from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.models.tech_pack import ComplianceStatus


@pytest.fixture(scope="module")
def sample_10p_techpack_pdf(tmp_path_factory) -> Path:
    """Generate a realistic 10-page equestrian tech pack for end-to-end testing."""
    temp_dir = tmp_path_factory.mktemp("e2e_pdf")
    pdf_path = temp_dir / "equestrian_coat_e2e_10p.pdf"

    sketch = Image.new("RGB", (300, 300), color=(240, 240, 240))
    sketch_bytes = io.BytesIO()
    sketch.save(sketch_bytes, format="PNG")

    doc = pymupdf.open()
    pages_data = [
        ("Cover", "STYLE: ME-2026-SJ01\nNAME: Grand Prix Show Coat\nDISCIPLINE: Show Jumping\nSEASON: SS26\nGARMENT TYPE: Show Jacket\nGENDER: Women's"),
        ("Technical Flat", "FRONT AND BACK TECHNICAL SKETCHES WITH CONTOURED FIT"),
        ("Bill of Materials", "BOM SPECIFICATION LIST:\nMain Shell: 78% Polyamide 22% Elastane ($18.50)\nCollar Velvet: 100% Cotton ($4.20)\nButtons: 4 Matte Horn Buttons ($3.80)"),
        ("Fabric Technical Data", "FABRIC SPECIFICATION:\nPRIMARY COMPOSITION: 78% Polyamide, 22% Elastane\nWEIGHT: 295 GSM\nBREATHABILITY: 14000 g/m²/24h\nSTRETCH: 24% Weft"),
        ("Points of Measure", "POM MEASUREMENTS:\nPOM-01 Collar Stand Height: 4.5 cm (Tol: +/- 0.5 cm)\nPOM-02 Chest Width: 46.0 cm (Tol: +/- 0.75 cm)"),
        ("Branding & Artwork", "BRANDING SPECIFICATION:\nCollar Logo: Left Collar Stand, Dimensions: 6.0 cm x 8.0 cm (Area: 48.0 cm²)\nChest Emblem: Left Pocket, Dimensions: 10.0 cm x 12.0 cm (Area: 120.0 cm²)"),
        ("Aesthetics & Trims", "AESTHETICS:\nCollar Type: Notched Lapel with Tonal Velvet Collar\nPiping: 3.0 mm Satin Piping along Lapel\nButtons: 4 Front Monogram Buttons"),
        ("Construction Details", "SEAM SPECIFICATION:\n4-thread safety stitch with stretch thread\nReinforced taped lapel edges"),
        ("Labeling & Packaging", "CARE LABEL: 30°C Hand Wash Only\nHanger: Branded Walnut Finish"),
        ("Costing & Sign-Off", "COMMERCIAL COSTING:\nTARGET FOB: $55.00 USD\nACTUAL FOB: $53.80 USD\nRETAIL PRICE: $480.00 USD"),
    ]

    for title, text in pages_data:
        page = doc.new_page(width=595, height=842)
        page.insert_text((50, 60), f"MAISON ÉQUESTRE - {title.upper()}", fontsize=14)
        page.insert_text((50, 110), text, fontsize=10)
        page.insert_image(pymupdf.Rect(400, 50, 520, 170), stream=sketch_bytes.getvalue())

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.mark.asyncio
async def test_full_audit_pipeline_benchmark(sample_10p_techpack_pdf: Path):
    """Benchmark full pipeline execution and assert strict latency (< 30s) and 0% false positives."""
    pipeline_start = time.perf_counter()

    # Step 1: Ingestion & OCR Pipeline
    t0 = time.perf_counter()
    ingestion = IngestionPipeline()
    ingest_result = ingestion.process(sample_10p_techpack_pdf)
    t_ingest = time.perf_counter() - t0

    assert ingest_result.total_pages == 10
    assert len(ingest_result.full_markdown) > 200

    # Step 2: Structuring & Sanitization
    t0 = time.perf_counter()
    structuring = StructuringService()
    sanitized_pack = await structuring.extract_spec_async(
        markdown_content=ingest_result.full_markdown,
        figures=ingest_result.figures,
        source_pdf_name=ingest_result.file_name,
        page_count=ingest_result.total_pages,
    )
    clean_spec = sanitized_pack.spec
    t_structure = time.perf_counter() - t0

    assert clean_spec.metadata.style_code == "ME-2026-SJ01"
    assert clean_spec.fabric.weight_gsm == 295.0

    # Step 3: Dual-Layer Comparative Audit
    t0 = time.perf_counter()
    coordinator = AuditCoordinator()
    prelim_report = await coordinator.run_audit_async(clean_spec)
    t_audit = time.perf_counter() - t0

    # Step 4: Citation Verifier Gate
    t0 = time.perf_counter()
    verifier = CitationVerifier()
    verified_findings = verifier.verify_all(prelim_report.findings)
    t_verify = time.perf_counter() - t0

    # Step 5: Scorecard Generation
    t0 = time.perf_counter()
    scorecard_gen = ScorecardGenerator()
    scorecard = scorecard_gen.generate(
        tech_pack_id=f"TP-{clean_spec.metadata.style_code}",
        verified_findings=verified_findings,
        spec=clean_spec,
        execution_time_seconds=time.perf_counter() - pipeline_start,
    )
    t_scorecard = time.perf_counter() - t0

    # Step 6: Vendor Action Generator
    t0 = time.perf_counter()
    action_gen = VendorActionGenerator()
    vendor_doc = action_gen.generate_notes(scorecard)
    t_actions = time.perf_counter() - t0

    total_pipeline_time = time.perf_counter() - pipeline_start

    # Benchmarks and assertions
    print(f"\n--- End-to-End Pipeline Performance Benchmark ---")
    print(f"1. Ingestion (10 pages): {t_ingest:.3f}s")
    print(f"2. Structuring & Sanitizing: {t_structure:.3f}s")
    print(f"3. Dual-Layer Audit: {t_audit:.3f}s")
    print(f"4. Citation Verifier Gate: {t_verify:.3f}s")
    print(f"5. Scorecard Compilation: {t_scorecard:.3f}s")
    print(f"6. Vendor Action Generator: {t_actions:.3f}s")
    print(f"TOTAL PIPELINE EXECUTION: {total_pipeline_time:.3f}s (Budget: < 30.0s)")

    assert total_pipeline_time < 30.0, f"Pipeline exceeded 30s budget: {total_pipeline_time:.2f}s"
    assert scorecard.overall_status in (ComplianceStatus.PASS, ComplianceStatus.WARNING)
    assert scorecard.overall_score_pct >= 90.0

    # Zero False Positives:
    # 48 cm² collar logo is <= 60 cm² limit -> must NOT be flagged as VIOLATION
    collar_violations = [
        f for f in scorecard.findings
        if "collar" in f.title.lower() and f.severity == ComplianceStatus.VIOLATION
    ]
    assert len(collar_violations) == 0

    # Actual FOB $53.80 is <= $55.00 Target FOB -> must NOT trigger costing violation
    cogs_violations = [
        f for f in scorecard.findings
        if "fob" in f.title.lower() and f.severity == ComplianceStatus.VIOLATION
    ]
    assert len(cogs_violations) == 0

    # Vendor document structure check
    assert vendor_doc.tech_pack_id == "TP-ME-2026-SJ01"
    assert len(vendor_doc.email_draft_content) > 50
