"""FastAPI endpoints for generating and exporting vendor revision documents."""
import io
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel
import pymupdf

from backend.app.api.audit_store import audit_store
from backend.app.engine.vendor_action_generator import vendor_action_generator

logger = logging.getLogger(__name__)

router = APIRouter()


class ExportNotesRequest(BaseModel):
    custom_notes: Optional[str] = None


def generate_vendor_pdf_letterhead(doc_data) -> bytes:
    """Generate a clean luxury letterhead PDF using PyMuPDF."""
    pdf = pymupdf.open()
    page = pdf.new_page(width=595, height=842)

    # Header
    page.insert_text((50, 55), "MAISON ÉQUESTRE", fontsize=15, fontname="helv", color=(0.1, 0.1, 0.2))
    page.insert_text((50, 72), "TECHNICAL COMPLIANCE & ATELIER QUALITY ASSURANCE", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
    page.draw_line(pymupdf.Point(50, 82), pymupdf.Point(545, 82), color=(0.8, 0.8, 0.8), width=1)

    # Document Metadata
    page.insert_text((50, 105), f"STYLE: {doc_data.style_name} ({doc_data.style_code})", fontsize=11, fontname="helv")
    page.insert_text((50, 120), f"DATE: {doc_data.generated_date} | TECH PACK ID: {doc_data.tech_pack_id}", fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))

    y = 150
    page.insert_text((50, y), "REQUIRED SUPPLIER ACTION ITEMS", fontsize=10, fontname="helv", color=(0.1, 0.1, 0.2))
    page.draw_line(pymupdf.Point(50, y + 4), pymupdf.Point(545, y + 4), color=(0.85, 0.85, 0.85), width=0.5)
    y += 24

    for idx, item in enumerate(doc_data.action_items, start=1):
        if y > 760:
            page = pdf.new_page(width=595, height=842)
            y = 50

        page.insert_text((50, y), f"{idx}. [{item.target_team}] {item.component}", fontsize=10, fontname="helv")
        y += 14
        page.insert_text((65, y), f"Issue: {item.current_issue}", fontsize=8.5, fontname="helv", color=(0.25, 0.25, 0.25))
        y += 13
        page.insert_text((65, y), f"Required: {item.required_action}", fontsize=8.5, fontname="helv", color=(0.1, 0.35, 0.1))
        y += 13
        page.insert_text((65, y), f"Rule Reference: {item.citation_reference}", fontsize=8.0, fontname="helv", color=(0.4, 0.4, 0.4))
        y += 20

    # Footer
    page.insert_text((50, 810), "CONFIDENTIAL - PROPERTY OF MAISON ÉQUESTRE - FOR SUPPLIER REMEDIATION ONLY", fontsize=7.5, fontname="helv", color=(0.5, 0.5, 0.5))

    pdf_bytes = pdf.tobytes()
    pdf.close()
    return pdf_bytes


@router.post("/{audit_id}/export-vendor-notes")
def export_vendor_notes(
    audit_id: str,
    format: str = Query("markdown", pattern="^(markdown|text|pdf)$"),
    body: Optional[ExportNotesRequest] = None,
):
    """Export supplier revision instructions in Markdown, Plain Text, or PDF format."""
    record = audit_store.get(audit_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Audit {audit_id} not found.")

    doc = vendor_action_generator.generate_notes(record.scorecard)

    if body and body.custom_notes:
        doc.markdown_content += f"\n\n### Reviewer Notes\n{body.custom_notes}"
        doc.email_draft_content += f"\n\nAdditional Notes from Technical Reviewer:\n{body.custom_notes}"

    if format == "markdown":
        return Response(
            content=doc.markdown_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=revisions_{record.scorecard.style_code}.md"},
        )

    if format == "text":
        return Response(
            content=doc.email_draft_content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=email_draft_{record.scorecard.style_code}.txt"},
        )

    if format == "pdf":
        pdf_bytes = generate_vendor_pdf_letterhead(doc)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=revisions_{record.scorecard.style_code}.pdf"},
        )

    return doc.model_dump()
