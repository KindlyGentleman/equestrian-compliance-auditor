"""Data models for Compliance Findings, Scorecards, and Vendor Actions."""
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from backend.app.models.tech_pack import ComplianceStatus, Discipline, GarmentType


class FindingCategory(str):
    BRANDING_LOGO = "Branding & Logos"
    FABRIC_PERFORMANCE = "Fabric & Performance"
    COSTING_FOB = "Costing & FOB"
    TAILORING_MEASUREMENTS = "Tailoring & Dimensions"
    AESTHETICS = "Aesthetics & Elegance"


# Domain Aliases
AuditSeverity = ComplianceStatus
AuditRuleType = FindingCategory


class AuditFinding(BaseModel):
    finding_id: str = Field(description="Unique finding identifier")
    rule_id: str = Field(description="Associated rule ID e.g. FEI-JUMP-LOGO-COLLAR")
    category: str = Field(description="Finding category")
    severity: ComplianceStatus = Field(description="PASS, WARNING, VIOLATION, MANUAL_REVIEW")
    title: str = Field(description="Brief issue title")
    observed_value: str = Field(description="Extracted value from tech pack")
    allowed_threshold: str = Field(description="Threshold from FEI rules or Brand SOP")
    delta_explanation: str = Field(description="Quantitative or qualitative delta")
    source_citation: str = Field(description="Verbatim excerpt from rulebook or SOP")
    source_rulebook: str = Field(description="e.g. FEI Jumping Rules, Art. 256.3.1")
    remedy_suggestion: str = Field(description="Actionable advice for vendor or designer")
    page_number: int | None = Field(default=1, description="Source page in tech pack PDF")
    bounding_box: list[float] | None = Field(default=None, description="[x0, y0, x1, y1] on page")


class VerifiedFinding(AuditFinding):
    is_verbatim_verified: bool = Field(default=False)
    verification_notes: str | None = None


class CategoryScore(BaseModel):
    category_name: str
    status: ComplianceStatus
    compliance_score_pct: float = Field(ge=0.0, le=100.0)
    issue_count: int = 0


class PreliminaryAuditReport(BaseModel):
    tech_pack_id: str
    style_code: str
    style_name: str
    discipline: Discipline
    garment_type: GarmentType
    overall_status: ComplianceStatus
    overall_score_pct: float = Field(ge=0.0, le=100.0)
    execution_time_seconds: float
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    category_scores: list[CategoryScore] = Field(default_factory=list)
    findings: list[AuditFinding] = Field(default_factory=list)


class AuditScorecard(BaseModel):
    tech_pack_id: str
    style_code: str
    style_name: str
    discipline: Discipline
    garment_type: GarmentType
    overall_status: ComplianceStatus
    overall_score_pct: float = Field(ge=0.0, le=100.0)
    execution_time_seconds: float
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    category_scores: list[CategoryScore] = Field(default_factory=list)
    findings: list[VerifiedFinding] = Field(default_factory=list)
    vendor_revision_notes: str | None = None


class VendorRevisionItem(BaseModel):
    target_team: str = Field(description="Pattern Maker, Mill, Trim Supplier, Sourcing")
    component: str = Field(description="e.g. Collar Crest Embroidery")
    current_issue: str
    required_action: str
    citation_reference: str


class VendorRevisionDocument(BaseModel):
    tech_pack_id: str
    style_code: str
    style_name: str
    generated_date: str = Field(default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%d"))
    summary: str
    action_items: list[VendorRevisionItem] = Field(default_factory=list)
    markdown_content: str
    email_draft_content: str


VendorActionNote = VendorRevisionItem

