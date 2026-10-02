"""Adversarial stress testing for the constitutional Zero-False-Positive Verifier Gate.

Tests whether the verifier gate automatically downgrades 100% of fabricated,
hallucinated, or subtly altered citations to MANUAL_REVIEW.
"""
import pytest

from backend.app.engine.citation_verifier import CitationVerifier
from backend.app.models.audit import AuditFinding, FindingCategory
from backend.app.models.tech_pack import ComplianceStatus

ADVERSARIAL_HALLUCINATED_FINDINGS = [
    AuditFinding(
        finding_id="adv_fake_art_01",
        rule_id="FEI-JUMP-FAKE-01",
        category=FindingCategory.BRANDING_LOGO,
        severity=ComplianceStatus.VIOLATION,
        title="Collar Logo Violates Synthetic Article",
        observed_value="55.0 cm²",
        allowed_threshold="<= 30.0 cm²",
        delta_explanation="Collar logo exceeds invented 30 cm² threshold.",
        source_citation="FEI Jumping Rules Article 999.4 strictly prohibits collar emblems exceeding 30 cm².",
        source_rulebook="FEI Jumping Rules, Art. 999.4",
        remedy_suggestion="Reduce collar logo to under 30 cm².",
        page_number=1,
    ),
    AuditFinding(
        finding_id="adv_fake_art_02",
        rule_id="FEI-DRESS-FAKE-02",
        category=FindingCategory.AESTHETICS,
        severity=ComplianceStatus.VIOLATION,
        title="Lapel Shape Prohibited by Fictitious Rule",
        observed_value="Peak Lapel",
        allowed_threshold="Notched Lapel Only",
        delta_explanation="Peak lapels are not allowed according to invented Dressage code.",
        source_citation="FEI Dressage Rules Article 888.1 specifies that athletes must only wear notched lapels.",
        source_rulebook="FEI Dressage Rules, Art. 888.1",
        remedy_suggestion="Switch lapel construction to notched design.",
        page_number=2,
    ),
    AuditFinding(
        finding_id="adv_altered_threshold_03",
        rule_id="FEI-JUMP-LOGO-COLLAR",
        category=FindingCategory.BRANDING_LOGO,
        severity=ComplianceStatus.VIOLATION,
        title="Collar Logo Over Claimed 45 cm² Limit",
        observed_value="50.0 cm²",
        allowed_threshold="<= 45.0 cm²",
        delta_explanation="Logo exceeds subtly altered threshold of 45 cm².",
        source_citation="The total surface area of this identification must not exceed forty-five square centimeters (45 cm²).",
        source_rulebook="FEI Jumping Rules, Art. 256.3.1",
        remedy_suggestion="Reduce collar logo area to 45 cm².",
        page_number=1,
    ),
    AuditFinding(
        finding_id="adv_myth_button_04",
        rule_id="FEI-EQUESTRIAN-MYTH-01",
        category=FindingCategory.AESTHETICS,
        severity=ComplianceStatus.VIOLATION,
        title="Buttons Fail Golden Ratio Rule",
        observed_value="4 Horn Buttons",
        allowed_threshold="Must feature exactly 5 engraved brass buttons",
        delta_explanation="Buttons violate fictitious Olympic tradition.",
        source_citation="Olympic Equestrian Protocol Art. 12 mandates five brass buttons on all formal jackets.",
        source_rulebook="FEI General Regulations, Annex 99",
        remedy_suggestion="Replace buttons with 5 brass buttons.",
        page_number=3,
    ),
    AuditFinding(
        finding_id="adv_invented_brand_sop_05",
        rule_id="BRAND-SOP-FAKE-FABRIC",
        category=FindingCategory.FABRIC_PERFORMANCE,
        severity=ComplianceStatus.VIOLATION,
        title="Fabric Composition Lacks Silk Threading",
        observed_value="78% Polyamide, 22% Elastane",
        allowed_threshold="Minimum 15% Mulberry Silk",
        delta_explanation="Fabric fails invented luxury specification.",
        source_citation="Maison Équestre Technical Standard 109 requires 15% mulberry silk in all competition coats.",
        source_rulebook="Maison Équestre Quality SOP, Sec. 99",
        remedy_suggestion="Add 15% silk to yarn blend.",
        page_number=4,
    ),
    AuditFinding(
        finding_id="adv_empty_citation_06",
        rule_id="FEI-JUMP-UNKNOWN",
        category=FindingCategory.BRANDING_LOGO,
        severity=ComplianceStatus.VIOLATION,
        title="Violation with Empty Citation String",
        observed_value="Excessive width",
        allowed_threshold="Standard width",
        delta_explanation="No citation supplied by reasoner.",
        source_citation="",
        source_rulebook="",
        remedy_suggestion="Add citation.",
        page_number=1,
    ),
    AuditFinding(
        finding_id="adv_whitespace_citation_07",
        rule_id="FEI-JUMP-UNKNOWN",
        category=FindingCategory.BRANDING_LOGO,
        severity=ComplianceStatus.VIOLATION,
        title="Violation with Blank Whitespace Citation",
        observed_value="Non-compliant piping",
        allowed_threshold="Standard piping",
        delta_explanation="Only whitespace citation supplied.",
        source_citation="   \t\n   ",
        source_rulebook="FEI Jumping",
        remedy_suggestion="Supply genuine citation.",
        page_number=2,
    ),
]


GENUINE_GROUND_TRUTH_FINDINGS = [
    AuditFinding(
        finding_id="gen_collar_logo_01",
        rule_id="FEI-JUMP-LOGO-COLLAR",
        category=FindingCategory.BRANDING_LOGO,
        severity=ComplianceStatus.VIOLATION,
        title="Collar Brand Identification Exceeds FEI Surface Area Limit",
        observed_value="72.0 cm²",
        allowed_threshold="<= 60.0 cm²",
        delta_explanation="Observed collar logo area is +12.0 cm² over legal limit.",
        source_citation="The total surface area of this identification must not exceed sixty square centimeters (60 cm²).",
        source_rulebook="FEI Jumping Rules, Art. 256.3.1",
        remedy_suggestion="Reduce collar logo dimensions to <= 60 cm².",
        page_number=1,
    ),
    AuditFinding(
        finding_id="gen_dressage_collar_02",
        rule_id="FEI-DRESS-LOGO-COLLAR",
        category=FindingCategory.BRANDING_LOGO,
        severity=ComplianceStatus.VIOLATION,
        title="Collar Identification Exceeds Dressage Allowance",
        observed_value="68.0 cm²",
        allowed_threshold="<= 60.0 cm²",
        delta_explanation="Collar emblem is +8.0 cm² over limit.",
        source_citation="Brand manufacturer identification on jackets is restricted to one single emblem on the collar of maximum sixty square centimeters (60 cm²).",
        source_rulebook="FEI Dressage Rules, Art. 427.3.1",
        remedy_suggestion="Scale down collar emblem.",
        page_number=1,
    ),
    AuditFinding(
        finding_id="gen_cogs_ceiling_03",
        rule_id="BRAND-SOP-COGS-01",
        category=FindingCategory.COSTING_FOB,
        severity=ComplianceStatus.VIOLATION,
        title="Actual Quoted FOB Exceeds Brand Hard Cost Ceiling",
        observed_value="$74.50 USD",
        allowed_threshold="<= $65.00 USD",
        delta_explanation="FOB exceeds brand hard ceiling by $9.50 USD.",
        source_citation="Maximum Target FOB is $55.00 USD. Hard ceiling is $65.00 USD. Any tech pack with actual FOB exceeding $65.00 USD is marked as a critical financial violation.",
        source_rulebook="Maison Équestre Quality SOP, Sec. 1",
        remedy_suggestion="Renegotiate CMT fees.",
        page_number=1,
    ),
    AuditFinding(
        finding_id="gen_fabric_breathability_04",
        rule_id="BRAND-SOP-FABRIC-01",
        category=FindingCategory.FABRIC_PERFORMANCE,
        severity=ComplianceStatus.WARNING,
        title="Fabric Breathability Below Brand Standard",
        observed_value="8500 g/m²/24h",
        allowed_threshold=">= 10000 g/m²/24h",
        delta_explanation="Breathability is 1500 g/m²/24h below minimum.",
        source_citation="All primary performance fabrics for competition show jackets and tailcoats must achieve a water vapor transmission rate (breathability) of at least 10,000 g/m²/24h.",
        source_rulebook="Maison Équestre Quality SOP, Sec. 2",
        remedy_suggestion="Select higher-gauge knit.",
        page_number=1,
    ),
]


def test_adversarial_hallucinations_auto_downgraded():
    """Verify that every fabricated or altered citation is downgraded to MANUAL_REVIEW."""
    verifier = CitationVerifier()
    verified_results = verifier.verify_all(ADVERSARIAL_HALLUCINATED_FINDINGS)

    assert len(verified_results) == len(ADVERSARIAL_HALLUCINATED_FINDINGS)

    for item in verified_results:
        assert item.is_verbatim_verified is False, f"Hallucinated finding incorrectly marked verified: {item.finding_id}"
        assert item.severity == ComplianceStatus.MANUAL_REVIEW, f"Severity was not downgraded: {item.finding_id}"
        assert "unverified" in item.verification_notes.lower() or "missing" in item.verification_notes.lower()


def test_zero_false_positive_rate_on_adversarial_dataset():
    """Calculate empirical false positive rate and assert it is strictly 0.0%."""
    verifier = CitationVerifier()
    all_findings = ADVERSARIAL_HALLUCINATED_FINDINGS + GENUINE_GROUND_TRUTH_FINDINGS
    verified = verifier.verify_all(all_findings)

    # An adversarial finding that remains a VIOLATION is a false positive
    adversarial_ids = {f.finding_id for f in ADVERSARIAL_HALLUCINATED_FINDINGS}
    false_positives = [
        vf for vf in verified
        if vf.finding_id in adversarial_ids and vf.severity == ComplianceStatus.VIOLATION
    ]

    false_positive_rate = len(false_positives) / len(ADVERSARIAL_HALLUCINATED_FINDINGS)
    assert false_positive_rate == 0.0, f"False positive rate exceeded 0%: {false_positives}"


def test_genuine_citations_retain_verified_status():
    """Ensure authentic citations from regulations and catalog stay verified."""
    verifier = CitationVerifier()
    verified_results = verifier.verify_all(GENUINE_GROUND_TRUTH_FINDINGS)

    for item in verified_results:
        assert item.is_verbatim_verified is True, f"Authentic finding failed verification: {item.finding_id}"
        assert item.severity in (ComplianceStatus.VIOLATION, ComplianceStatus.WARNING)
        assert "verified" in item.verification_notes.lower()


@pytest.mark.parametrize("typo_citation", [
    "The total surface area of this identification must not exceed sixty square centimeters (60 cm2).",
    "the total surface area of this identification must not exceed sixty square centimeters (60 cm²)",
    "  THE TOTAL SURFACE AREA OF THIS IDENTIFICATION MUST NOT EXCEED SIXTY SQUARE CENTIMETERS (60 CM²).  ",
])
def test_minor_typographic_and_case_invariance(typo_citation: str):
    """Test that minor case, whitespace, and typographic symbol variants still verify correctly."""
    verifier = CitationVerifier()
    finding = AuditFinding(
        finding_id="typo_test",
        rule_id="FEI-JUMP-LOGO-COLLAR",
        category=FindingCategory.BRANDING_LOGO,
        severity=ComplianceStatus.VIOLATION,
        title="Collar Brand Identification Exceeds FEI Surface Area Limit",
        observed_value="75.0 cm²",
        allowed_threshold="<= 60.0 cm²",
        delta_explanation="Collar logo is over limit.",
        source_citation=typo_citation,
        source_rulebook="FEI Jumping Rules, Art. 256.3.1",
        remedy_suggestion="Reduce collar logo dimensions.",
        page_number=1,
    )
    result = verifier.verify_finding(finding)
    assert result.is_verbatim_verified is True
    assert result.severity == ComplianceStatus.VIOLATION
