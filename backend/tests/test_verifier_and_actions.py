"""Unit and integration tests for Stage 6 Verifier Gate and Vendor Action Generator."""
import pytest

from backend.app.engine.citation_verifier import CitationVerifier
from backend.app.engine.scorecard_generator import ScorecardGenerator
from backend.app.engine.vendor_action_generator import VendorActionGenerator
from backend.app.models.audit import (
    AuditFinding,
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
    """Sample show jacket spec for testing."""
    return TechPackSpec(
        metadata=GarmentMetadata(
            style_code="ME-SJ-2026-TEST",
            style_name="Test Sovereign Jacket",
            discipline=Discipline.JUMPING,
            garment_type=GarmentType.SHOW_JACKET,
        ),
        fabric=FabricSpec(
            primary_composition="78% Polyamide, 22% Elastane",
            weight_gsm=240.0,
            breathability_g_m2_24h=14000.0,
        ),
        costing=CostingSpec(
            target_fob_usd=55.00,
            actual_fob_usd=54.00,
        ),
    )


def test_citation_verifier_valid_known_citation():
    """Verify that an authentic catalog citation passes verification."""
    verifier = CitationVerifier()
    finding = AuditFinding(
        finding_id="det_logo_collar_1",
        rule_id="FEI-JUMP-LOGO-COLLAR",
        category=FindingCategory.BRANDING_LOGO,
        severity=ComplianceStatus.VIOLATION,
        title="Collar Logo Area Exceeds FEI Maximum",
        observed_value="65.0 cm²",
        allowed_threshold="<= 60.0 cm²",
        delta_explanation="+5.0 cm² over limit",
        source_citation="The total surface area of this identification must not exceed sixty square centimeters (60 cm²).",
        source_rulebook="FEI Jumping Rules, Art. 256.3.1",
        remedy_suggestion="Scale down logo to <= 60 cm²",
    )

    verified = verifier.verify_finding(finding)
    assert verified.is_verbatim_verified is True
    assert verified.severity == ComplianceStatus.VIOLATION
    assert "verified" in verified.verification_notes.lower()


def test_citation_verifier_hallucinated_citation_downgrade():
    """Verify that a fabricated or unsupported citation is downgraded to MANUAL_REVIEW."""
    verifier = CitationVerifier()
    fake_finding = AuditFinding(
        finding_id="sem_fake_01",
        rule_id="FEI-JUMP-FAKE-RULE",
        category=FindingCategory.AESTHETICS,
        severity=ComplianceStatus.VIOLATION,
        title="Invented Button Color Prohibition",
        observed_value="Gold buttons prohibited",
        allowed_threshold="Silver buttons only",
        delta_explanation="Fabricated rule violation",
        source_citation="All gold or brass buttons are strictly banned under FEI emergency decree 999.4.",
        source_rulebook="FEI Imaginary Handbook",
        remedy_suggestion="Replace buttons",
    )

    verified = verifier.verify_finding(fake_finding)
    assert verified.is_verbatim_verified is False
    assert verified.severity == ComplianceStatus.MANUAL_REVIEW
    assert "downgraded" in verified.verification_notes.lower()


def test_scorecard_generator(sample_spec: TechPackSpec):
    """Verify scorecard compilation, category score calculations, and status derivation."""
    generator = ScorecardGenerator()

    verified_findings = [
        VerifiedFinding(
            finding_id="f1",
            rule_id="FEI-JUMP-LOGO-COLLAR",
            category=FindingCategory.BRANDING_LOGO,
            severity=ComplianceStatus.VIOLATION,
            title="Collar Logo Exceeded",
            observed_value="68.0 cm²",
            allowed_threshold="<= 60.0 cm²",
            delta_explanation="+8.0 cm²",
            source_citation="The total surface area must not exceed 60 cm²",
            source_rulebook="FEI Jumping Art 256",
            remedy_suggestion="Resize logo",
            is_verbatim_verified=True,
        ),
        VerifiedFinding(
            finding_id="f2",
            rule_id="BRAND-SOP-FABRIC-01",
            category=FindingCategory.FABRIC_PERFORMANCE,
            severity=ComplianceStatus.WARNING,
            title="Low Breathability",
            observed_value="8500 g/m²/24h",
            allowed_threshold=">= 10000 g/m²/24h",
            delta_explanation="-1500 g/m²/24h",
            source_citation="Minimum breathability is 10,000 g/m²/24h",
            source_rulebook="Brand SOP Sec 2",
            remedy_suggestion="Upgrade membrane",
            is_verbatim_verified=True,
        ),
    ]

    scorecard = generator.generate(
        tech_pack_id="TP-ME-SJ-2026-TEST",
        verified_findings=verified_findings,
        spec=sample_spec,
        execution_time_seconds=1.25,
    )

    assert scorecard.overall_status == ComplianceStatus.VIOLATION
    assert scorecard.overall_score_pct < 100.0
    assert len(scorecard.category_scores) == 5
    assert len(scorecard.findings) == 2
    assert scorecard.execution_time_seconds == 1.25
    assert "revisions required" in scorecard.vendor_revision_notes.lower()


def test_vendor_action_generator(sample_spec: TechPackSpec):
    """Verify action item routing by team, markdown content, and email draft formatting."""
    scorecard_gen = ScorecardGenerator()
    action_gen = VendorActionGenerator()

    verified_findings = [
        VerifiedFinding(
            finding_id="f_logo",
            rule_id="FEI-JUMP-LOGO-COLLAR",
            category=FindingCategory.BRANDING_LOGO,
            severity=ComplianceStatus.VIOLATION,
            title="Collar Brand Emblem Exceeds Maximum",
            observed_value="65.0 cm²",
            allowed_threshold="<= 60.0 cm²",
            delta_explanation="+5.0 cm² over legal maximum",
            source_citation="Collar emblem max 60 cm²",
            source_rulebook="FEI Jumping Rules, Art. 256.3.1",
            remedy_suggestion="Reduce collar logo width to 5.0 cm and height to 6.0 cm (total 30 cm²).",
            is_verbatim_verified=True,
        ),
        VerifiedFinding(
            finding_id="f_cogs",
            rule_id="BRAND-SOP-COGS-01",
            category=FindingCategory.COSTING_FOB,
            severity=ComplianceStatus.VIOLATION,
            title="Actual FOB Exceeds Cost Ceiling",
            observed_value="$70.00 USD",
            allowed_threshold="<= $65.00 USD",
            delta_explanation="+$5.00 USD over ceiling",
            source_citation="Hard ceiling $65.00 USD",
            source_rulebook="Brand SOP, Sec. 1",
            remedy_suggestion="Renegotiate shell fabric consumption and CMT rates.",
            is_verbatim_verified=True,
        ),
        VerifiedFinding(
            finding_id="f_tol",
            rule_id="BRAND-SOP-TOL-01",
            category=FindingCategory.TAILORING_MEASUREMENTS,
            severity=ComplianceStatus.WARNING,
            title="Collar Stand Tolerance Too Loose",
            observed_value="+/- 0.8 cm",
            allowed_threshold="<= +/- 0.5 cm",
            delta_explanation="+0.3 cm looser than acceptable",
            source_citation="Collar stand tolerance +/- 0.5 cm",
            source_rulebook="Brand SOP, Sec. 3",
            remedy_suggestion="Tighten collar stand grading tolerance to +/- 0.5 cm.",
            is_verbatim_verified=True,
        ),
    ]

    scorecard = scorecard_gen.generate(
        tech_pack_id="TP-ME-SJ-2026-TEST",
        verified_findings=verified_findings,
        spec=sample_spec,
    )

    doc = action_gen.generate_notes(scorecard)

    assert len(doc.action_items) == 3
    teams = {item.target_team for item in doc.action_items}
    assert "Embroidery & Trim Supplier" in teams
    assert "Sourcing & Commercial Lead" in teams
    assert "Pattern Maker & Sample Room" in teams

    # Check Markdown Document
    assert "# Technical Package Revision Request" in doc.markdown_content
    assert "### Embroidery & Trim Supplier" in doc.markdown_content
    assert "### Sourcing & Commercial Lead" in doc.markdown_content
    assert "### Pattern Maker & Sample Room" in doc.markdown_content

    # Check Email Draft
    assert "Subject: Revision Required:" in doc.email_draft_content
    assert "Dear Partner," in doc.email_draft_content
    assert "Technical Quality & Compliance Team" in doc.email_draft_content
    assert "within 48 hours" in doc.email_draft_content
