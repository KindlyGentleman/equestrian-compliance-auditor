"""Deep mathematical scoring and vendor action generation routing tests."""
import pytest

from backend.app.engine.scorecard_generator import ScorecardGenerator
from backend.app.engine.vendor_action_generator import VendorActionGenerator
from backend.app.models.audit import (
    FindingCategory,
    VerifiedFinding,
)
from backend.app.models.tech_pack import (
    ComplianceStatus,
    CostingSpec,
    Discipline,
    FabricSpec,
    GarmentMetadata,
    GarmentType,
    TechPackSpec,
)


@pytest.fixture
def sample_spec() -> TechPackSpec:
    return TechPackSpec(
        metadata=GarmentMetadata(
            style_code="MATH-2026-01",
            style_name="Scorecard Test Jacket",
            discipline=Discipline.JUMPING,
            garment_type=GarmentType.SHOW_JACKET,
        ),
        fabric=FabricSpec(primary_composition="78% Wool, 22% Polyamide", weight_gsm=280.0),
        costing=CostingSpec(target_fob_usd=55.0, actual_fob_usd=52.0),
    )


def test_scorecard_clean_pass_scores_100_percent(sample_spec: TechPackSpec):
    """Ensure a tech pack with 0 issues scores 100.0% and status PASS across all categories."""
    generator = ScorecardGenerator()
    scorecard = generator.generate(
        tech_pack_id="TP-CLEAN",
        verified_findings=[],
        spec=sample_spec,
    )

    assert scorecard.overall_status == ComplianceStatus.PASS
    assert scorecard.overall_score_pct == 100.0
    assert len(scorecard.category_scores) == 5
    for cat in scorecard.category_scores:
        assert cat.status == ComplianceStatus.PASS
        assert cat.compliance_score_pct == 100.0
        assert cat.issue_count == 0


def test_scorecard_single_violation_drops_overall_status(sample_spec: TechPackSpec):
    """A single regulatory violation must force overall status to VIOLATION."""
    generator = ScorecardGenerator()
    finding = VerifiedFinding(
        finding_id="f_single_violation",
        rule_id="FEI-JUMP-LOGO-COLLAR",
        category=FindingCategory.BRANDING_LOGO,
        severity=ComplianceStatus.VIOLATION,
        title="Collar Logo Exceeds 60 cm²",
        observed_value="75.0 cm²",
        allowed_threshold="<= 60.0 cm²",
        delta_explanation="+15.0 cm² over limit",
        source_citation="Identification must not exceed sixty square centimeters (60 cm²).",
        source_rulebook="FEI Jumping Rules",
        remedy_suggestion="Scale down logo.",
        page_number=1,
        is_verbatim_verified=True,
        verification_notes="Verified against rules catalog.",
    )

    scorecard = generator.generate(
        tech_pack_id="TP-VIOLATION",
        verified_findings=[finding],
        spec=sample_spec,
    )

    assert scorecard.overall_status == ComplianceStatus.VIOLATION
    branding_cat = next(c for c in scorecard.category_scores if c.category_name == FindingCategory.BRANDING_LOGO)
    assert branding_cat.status == ComplianceStatus.VIOLATION
    assert branding_cat.compliance_score_pct == 50.0  # 100 - 50 deduction
    # Clean categories remain 100.0%
    clean_cats = [c for c in scorecard.category_scores if c.category_name != FindingCategory.BRANDING_LOGO]
    assert all(c.compliance_score_pct == 100.0 for c in clean_cats)
    # Overall score is average: (50 + 100 + 100 + 100 + 100) / 5 = 90.0%
    assert scorecard.overall_score_pct == 90.0


def test_scorecard_catastrophic_failure_floors_at_zero(sample_spec: TechPackSpec):
    """Ensure heavy deductions never produce negative percentage scores."""
    generator = ScorecardGenerator()
    # 5 severe violations in one category: 5 * 50 = 250 deduction points
    heavy_findings = [
        VerifiedFinding(
            finding_id=f"f_severe_{i}",
            rule_id=f"RULE-HEAVY-{i}",
            category=FindingCategory.BRANDING_LOGO,
            severity=ComplianceStatus.VIOLATION,
            title=f"Critical Branding Breach {i}",
            observed_value="Non-compliant",
            allowed_threshold="Compliant",
            delta_explanation="Exceeds limit",
            source_citation="Regulatory text.",
            source_rulebook="Rulebook",
            remedy_suggestion="Remedy",
            page_number=1,
            is_verbatim_verified=True,
            verification_notes="Verified.",
        )
        for i in range(5)
    ]

    scorecard = generator.generate(
        tech_pack_id="TP-HEAVY",
        verified_findings=heavy_findings,
        spec=sample_spec,
    )

    branding_cat = next(c for c in scorecard.category_scores if c.category_name == FindingCategory.BRANDING_LOGO)
    assert branding_cat.compliance_score_pct == 0.0  # Bounded at 0.0%, not negative


@pytest.mark.parametrize("category,title,expected_team", [
    (FindingCategory.BRANDING_LOGO, "Collar Embroidery Exceeds Area", "Embroidery & Trim Supplier"),
    (FindingCategory.COSTING_FOB, "FOB Price Overrun", "Sourcing & Commercial Lead"),
    (FindingCategory.FABRIC_PERFORMANCE, "Breathability Below Standard", "Fabric Mill & Materials Lab"),
    (FindingCategory.TAILORING_MEASUREMENTS, "Collar Height Tolerance Too Wide", "Pattern Maker & Sample Room"),
    (FindingCategory.AESTHETICS, "Contrast Piping Too Wide", "Pattern Maker & Sample Room"),
    (FindingCategory.AESTHETICS, "Button Monogram Defect", "Embroidery & Trim Supplier"),
    (FindingCategory.AESTHETICS, "Lapel Cut Asymmetry", "Design & Production Team"),
])
def test_vendor_action_departmental_routing(sample_spec: TechPackSpec, category: FindingCategory, title: str, expected_team: str):
    """Verify that findings are accurately routed to the appropriate supplier or atelier team."""
    generator = ScorecardGenerator()
    action_gen = VendorActionGenerator()

    finding = VerifiedFinding(
        finding_id="f_routing_test",
        rule_id="RULE-ROUTE",
        category=category,
        severity=ComplianceStatus.WARNING,
        title=title,
        observed_value="Observed issue",
        allowed_threshold="Allowed spec",
        delta_explanation="Delta issue",
        source_citation="Standard text.",
        source_rulebook="Official Manual",
        remedy_suggestion="Immediate correction required.",
        page_number=1,
        is_verbatim_verified=True,
        verification_notes="Verified citation.",
    )

    scorecard = generator.generate(
        tech_pack_id="TP-ROUTING",
        verified_findings=[finding],
        spec=sample_spec,
    )

    doc = action_gen.generate_notes(scorecard)
    assert len(doc.action_items) == 1
    assert doc.action_items[0].target_team == expected_team


def test_vendor_action_document_formatting_and_email_draft(sample_spec: TechPackSpec):
    """Ensure generated markdown and email drafts contain all required structure without placeholder leaks."""
    generator = ScorecardGenerator()
    action_gen = VendorActionGenerator()

    findings = [
        VerifiedFinding(
            finding_id="f_doc_1",
            rule_id="FEI-JUMP-LOGO-COLLAR",
            category=FindingCategory.BRANDING_LOGO,
            severity=ComplianceStatus.VIOLATION,
            title="Collar Logo Exceeds 60 cm²",
            observed_value="70.0 cm²",
            allowed_threshold="<= 60.0 cm²",
            delta_explanation="+10.0 cm²",
            source_citation="Collar emblem must not exceed 60 cm².",
            source_rulebook="FEI Jumping Rules, Art. 256.3.1",
            remedy_suggestion="Scale down collar artwork.",
            page_number=1,
            is_verbatim_verified=True,
            verification_notes="Verified.",
        ),
    ]

    scorecard = generator.generate(
        tech_pack_id="TP-DOC-TEST",
        verified_findings=findings,
        spec=sample_spec,
    )

    doc = action_gen.generate_notes(scorecard)

    # Markdown checks
    assert f"# Technical Package Revision Request: {sample_spec.metadata.style_name}" in doc.markdown_content
    assert "## Executive Summary" in doc.markdown_content
    assert "## Required Action Items by Department" in doc.markdown_content
    assert "### Embroidery & Trim Supplier" in doc.markdown_content
    assert "- **Issue:**" in doc.markdown_content
    assert "- **Required Action:**" in doc.markdown_content

    # Email draft checks
    assert f"Subject: Revision Required: Technical Specification for Style {sample_spec.metadata.style_code}" in doc.email_draft_content
    assert "Dear Partner," in doc.email_draft_content
    assert "[Embroidery & Trim Supplier]" in doc.email_draft_content

    # Ensure no placeholder leaks
    for text in [doc.markdown_content, doc.email_draft_content]:
        assert "[object Object]" not in text
        assert "undefined" not in text
        assert "None" not in text
