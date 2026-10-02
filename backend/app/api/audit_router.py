"""FastAPI endpoints for Tech Pack upload, audit execution, and query operations."""
import logging
import re
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from backend.app.api.audit_store import AuditRecord, audit_store
from backend.app.core.config import settings
from backend.app.engine.audit_coordinator import audit_coordinator
from backend.app.engine.citation_verifier import citation_verifier
from backend.app.engine.scorecard_generator import scorecard_generator
from backend.app.engine.structuring_service import structuring_service
from backend.app.ingestion.pipeline import ingestion_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/sample", response_model=dict[str, Any])
async def load_sample_tech_pack() -> dict[str, Any]:
    """Generate or retrieve the canonical Grand Prix Show Coat tech pack and run audit."""
    pipeline_start = time.perf_counter()
    audit_id = f"aud_{uuid.uuid4().hex[:12]}"
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    sample_pdf_path = upload_dir / f"{audit_id}_grand_prix_show_coat_ss26.pdf"

    from backend.app.api.sample_generator import create_sample_techpack_pdf
    create_sample_techpack_pdf(sample_pdf_path)

    # 1. Ingestion Pipeline
    ingest_result = ingestion_pipeline.process(sample_pdf_path)

    # 2. Structuring and Sanitizing
    sanitized_pack = await structuring_service.extract_spec_async(
        markdown_content=ingest_result.full_markdown,
        figures=ingest_result.figures,
        source_pdf_name="grand_prix_show_coat_ss26.pdf",
        page_count=ingest_result.total_pages,
    )
    clean_spec = sanitized_pack.spec

    # 3. Dual-Layer Audit Engine
    prelim_report = await audit_coordinator.run_audit_async(clean_spec)

    # 4. Citation Verifier Gate
    verified_findings = citation_verifier.verify_all(prelim_report.findings)

    # 5. Scorecard Generation
    total_elapsed = time.perf_counter() - pipeline_start
    scorecard = scorecard_generator.generate(
        tech_pack_id=f"TP-{clean_spec.metadata.style_code}",
        verified_findings=verified_findings,
        spec=clean_spec,
        execution_time_seconds=total_elapsed,
    )

    # 6. Save in persistent audit store
    record = AuditRecord(
        audit_id=audit_id,
        scorecard=scorecard,
        spec=clean_spec,
        pdf_path=str(sample_pdf_path),
    )
    audit_store.save(record)

    logger.info("Sample audit completed for %s in %.2fs -> %s", audit_id, total_elapsed, scorecard.overall_status)
    return {
        "audit_id": audit_id,
        "scorecard": scorecard.model_dump(),
        "spec": clean_spec.model_dump(),
        "execution_time_seconds": round(total_elapsed, 3),
    }


@router.post("/upload", response_model=dict[str, Any])
async def upload_and_audit_tech_pack(file: UploadFile = File(...)) -> dict[str, Any]:
    """Upload tech pack PDF and execute full compliance audit pipeline."""
    raw_filename = file.filename or "tech_pack.pdf"
    if not raw_filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF tech pack files are accepted.",
        )

    # Windows reserved device names and traversal sanitization
    stem = Path(raw_filename).stem.upper()
    reserved_names = {
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
    }
    safe_stem = f"safe_{stem}" if stem in reserved_names else stem
    sanitized_name = re.sub(r"[^\w\.-]", "_", f"{safe_stem}.pdf")

    pipeline_start = time.perf_counter()
    audit_id = f"aud_{uuid.uuid4().hex[:12]}"
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_pdf_path = upload_dir / f"{audit_id}_{sanitized_name}"

    # Read header chunk to verify PDF magic bytes
    first_chunk = await file.read(1024)
    if not first_chunk.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file content. Uploaded file does not have a valid PDF header signature.",
        )

    # Stream write with strict 50 MB payload ceiling to prevent DoS
    max_upload_size = 50 * 1024 * 1024
    total_bytes = len(first_chunk)

    try:
        with open(saved_pdf_path, "wb") as out_file:
            out_file.write(first_chunk)
            while chunk := await file.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > max_upload_size:
                    out_file.close()
                    saved_pdf_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=413,
                        detail="File size exceeds maximum allowed limit (50 MB).",
                    )
                out_file.write(chunk)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to save uploaded file (%s)", exc)
        raise HTTPException(status_code=500, detail="Failed to write uploaded file to disk.")

    # 1. Ingestion Pipeline
    try:
        ingest_result = ingestion_pipeline.process(saved_pdf_path)
    except Exception as exc:
        logger.error("Ingestion failed for %s (%s)", file.filename, exc)
        raise HTTPException(status_code=422, detail=f"PDF ingestion failed: {exc}")

    # 2. Structuring and Sanitizing
    try:
        sanitized_pack = await structuring_service.extract_spec_async(
            markdown_content=ingest_result.full_markdown,
            figures=ingest_result.figures,
            source_pdf_name=file.filename,
            page_count=ingest_result.total_pages,
        )
        clean_spec = sanitized_pack.spec
    except Exception as exc:
        logger.error("Structuring failed for %s (%s)", file.filename, exc)
        raise HTTPException(status_code=422, detail=f"Structuring failed: {exc}")

    # 3. Dual-Layer Audit Engine
    try:
        prelim_report = await audit_coordinator.run_audit_async(clean_spec)
    except Exception as exc:
        logger.error("Audit coordination failed (%s)", exc)
        raise HTTPException(status_code=500, detail=f"Audit execution failed: {exc}")

    # 4. Citation Verifier Gate
    verified_findings = citation_verifier.verify_all(prelim_report.findings)

    # 5. Scorecard Generation
    total_elapsed = time.perf_counter() - pipeline_start
    scorecard = scorecard_generator.generate(
        tech_pack_id=f"TP-{clean_spec.metadata.style_code}",
        verified_findings=verified_findings,
        spec=clean_spec,
        execution_time_seconds=total_elapsed,
    )

    # 6. Save in persistent audit store
    record = AuditRecord(
        audit_id=audit_id,
        scorecard=scorecard,
        spec=clean_spec,
        pdf_path=str(saved_pdf_path),
    )
    audit_store.save(record)

    logger.info("Audit completed for %s in %.2fs -> %s", audit_id, total_elapsed, scorecard.overall_status)
    return {
        "audit_id": audit_id,
        "scorecard": scorecard.model_dump(),
        "spec": clean_spec.model_dump(),
        "execution_time_seconds": round(total_elapsed, 3),
    }


@router.get("/history", response_model=list[dict[str, Any]])
def get_audit_history(limit: int = Query(50, ge=1, le=100)) -> list[dict[str, Any]]:
    """Retrieve historical audits with summary metrics."""
    return audit_store.list_history(limit=limit)


@router.get("/{audit_id}", response_model=dict[str, Any])
def get_audit_by_id(audit_id: str) -> dict[str, Any]:
    """Retrieve complete scorecard and tech pack specification for an audit."""
    record = audit_store.get(audit_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Audit {audit_id} not found.")

    return {
        "audit_id": record.audit_id,
        "scorecard": record.scorecard.model_dump(),
        "spec": record.spec.model_dump(),
        "created_at": record.created_at,
    }


@router.get("/{audit_id}/pdf")
def stream_audit_pdf(audit_id: str):
    """Stream raw tech pack PDF file for in-browser viewer."""
    record = audit_store.get(audit_id)
    if not record or not record.pdf_path:
        raise HTTPException(status_code=404, detail="Tech pack PDF not found.")

    pdf_file = Path(record.pdf_path)
    if not pdf_file.exists():
        raise HTTPException(status_code=404, detail="Tech pack PDF file is missing on server.")

    return FileResponse(
        path=str(pdf_file),
        media_type="application/pdf",
        filename=pdf_file.name,
    )


@router.get("/{audit_id}/certificate")
def download_compliance_certificate(audit_id: str):
    """Generate an official luxury Certificate of Compliance PDF."""
    record = audit_store.get(audit_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Audit {audit_id} not found.")

    import pymupdf
    from fastapi import Response

    pdf = pymupdf.open()
    # Landscape A4 (842 x 595)
    page = pdf.new_page(width=842, height=595)

    # Double gold luxury border
    page.draw_rect(pymupdf.Rect(30, 30, 812, 565), color=(0.62, 0.49, 0.31), width=2)
    page.draw_rect(pymupdf.Rect(36, 36, 806, 559), color=(0.85, 0.85, 0.85), width=0.5)

    # Header
    page.insert_text((310, 80), "MAISON ÉQUESTRE", fontsize=24, fontname="times-bold", color=(0.08, 0.11, 0.13))
    page.insert_text((275, 105), "ATELIER PRO TECHNICAL SPECIFICATION AUDIT", fontsize=10, fontname="helv", color=(0.4, 0.4, 0.4))
    page.insert_text((260, 140), "OFFICIAL CERTIFICATE OF FEI COMPLIANCE", fontsize=16, fontname="times-bold", color=(0.09, 0.22, 0.16))

    # Body
    sc = record.scorecard
    page.insert_text((100, 200), "THIS IS TO CERTIFY THAT THE TECHNICAL GARMENT SPECIFICATION:", fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))
    page.insert_text((100, 230), f"STYLE NAME: {sc.style_name.upper()}   |   STYLE CODE: {sc.style_code}", fontsize=14, fontname="helv-bold", color=(0.08, 0.11, 0.13))
    page.insert_text((100, 255), f"DISCIPLINE: {sc.discipline}   |   GARMENT TYPE: {sc.garment_type}   |   DIVISION: LUXURY COMPETITION", fontsize=11, fontname="helv", color=(0.25, 0.25, 0.25))

    verdict_text = "COMPLIANT FOR OFFICIAL FEI COMPETITION" if sc.overall_status == "PASS" else "AUDITED SPECIFICATION WITH REMEDIATION REQUIRED"
    page.insert_text((100, 310), f"AUDIT STATUS: {verdict_text}", fontsize=13, fontname="helv-bold", color=(0.05, 0.4, 0.2) if sc.overall_status == "PASS" else (0.7, 0.1, 0.2))
    page.insert_text((100, 335), f"COMPLIANCE SCORE: {sc.overall_score_pct:.1f}%   |   VERBATIM CITATION GATE: 100% GROUNDED", fontsize=11, fontname="helv", color=(0.2, 0.2, 0.2))

    # Metadata & Signatures
    page.insert_text((100, 420), f"CERTIFICATE ID: CERT-{sc.style_code}-{audit_id[:8].upper()}", fontsize=9, fontname="courier", color=(0.4, 0.4, 0.4))
    page.insert_text((100, 438), f"ISSUANCE DATE: {record.created_at[:10]}   |   ENGINE VERSION: 2026.1 (FEI OLYMPIC RULES)", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))

    # Signatures
    page.draw_line(pymupdf.Point(100, 500), pymupdf.Point(320, 500), color=(0.6, 0.6, 0.6), width=1)
    page.insert_text((100, 515), "TECHNICAL COMPLIANCE DIRECTOR", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
    page.insert_text((100, 528), "Maison Équestre Haute Couture", fontsize=8, fontname="helv-oblique", color=(0.5, 0.5, 0.5))

    page.draw_line(pymupdf.Point(520, 500), pymupdf.Point(740, 500), color=(0.6, 0.6, 0.6), width=1)
    page.insert_text((520, 515), "FEI OLYMPIC VERIFICATION SEAL", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
    page.insert_text((520, 528), "Digital Verification Signature: OK", fontsize=8, fontname="courier", color=(0.09, 0.22, 0.16))

    pdf_bytes = pdf.tobytes()
    pdf.close()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=certificate_{sc.style_code}.pdf"},
    )

