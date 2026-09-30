"""FastAPI endpoints for Tech Pack upload, audit execution, and query operations."""
import logging
import shutil
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
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF tech pack files are accepted.",
        )

    pipeline_start = time.perf_counter()
    audit_id = f"aud_{uuid.uuid4().hex[:12]}"
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    clean_filename = f"{audit_id}_{Path(file.filename).name}"
    saved_pdf_path = upload_dir / clean_filename

    # Save uploaded file
    try:
        with open(saved_pdf_path, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)
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
