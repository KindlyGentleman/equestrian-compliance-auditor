"""Deep testing for AuditCoordinator: findings deduplication, severity sorting, and fault tolerance."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.engine.audit_coordinator import AuditCoordinator
from backend.app.models.audit import AuditFinding, FindingCategory
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
def coordinator_spec() -> TechPackSpec:
    return TechPackSpec(
        metadata=GarmentMetadata(
            style_code="COORD-2026",
            style_name="Coordinator Test Coat",
            discipline=Discipline.JUMPING,
            garment_type=GarmentType.SHOW_JACKET,
        ),
        fabric=FabricSpec(primary_composition="78% Wool, 22% Polyamide", weight_gsm=290.0),
        costing=CostingSpec(target_fob_usd=55.0, actual_fob_usd=52.0),
    )


def test_deduplication_preserves_deterministic_on_overlap():
    """Verify that when Layer 1 and Layer 2 both report on the same rule_id, Layer 1 takes precedence."""
    coordinator = AuditCoordinator()

    layer1_findings = [
        AuditFinding(
            finding_id="l1_collar_violation",
            rule_id="FEI-JUMP-LOGO-COLLAR",
            category=FindingCategory.BRANDING_LOGO,
            severity=ComplianceStatus.VIOLATION,
            title="Layer 1 Collar Area Violation",
            observed_value="72.0 cm²",
            allowed_threshold="<= 60.0 cm²",
            delta_explanation="+12.0 cm² over limit",
            source_citation="Identification must not exceed 60 cm².",
            source_rulebook="FEI Jumping",
            remedy_suggestion="Reduce collar logo.",
            page_number=1,
        )
    ]

    layer2_findings = [
        AuditFinding(
            finding_id="l2_collar_warning",
            rule_id="FEI-JUMP-LOGO-COLLAR",  # Overlapping rule_id
            category=FindingCategory.BRANDING_LOGO,
            severity=ComplianceStatus.WARNING,
            title="Layer 2 Semantic Collar Concern",
            observed_value="72 cm²",
            allowed_threshold="60 cm²",
            delta_explanation="Logo appears visually oversized",
            source_citation="Identification must not exceed 60 cm².",
            source_rulebook="FEI Jumping",
            remedy_suggestion="Check logo sizing.",
            page_number=1,
        ),
        AuditFinding(
            finding_id="l2_distinct_lapel",
            rule_id="FEI-JUMP-LAPEL-CUT",  # Distinct rule_id
            category=FindingCategory.AESTHETICS,
            severity=ComplianceStatus.WARNING,
            title="Lapel Cut Contrast",
            observed_value="Contrast Velvet",
            allowed_threshold="Tonal",
            delta_explanation="Contrast collar on jumping coat",
            source_citation="Aesthetic styling guideline.",
            source_rulebook="Brand SOP",
            remedy_suggestion="Verify velvet tone.",
            page_number=2,
        ),
    ]

    merged = coordinator._deduplicate_findings(layer1_findings, layer2_findings)

    # Must contain 2 findings: Layer 1 collar violation and Layer 2 distinct lapel finding
    assert len(merged) == 2
    finding_ids = [f.finding_id for f in merged]
    assert "l1_collar_violation" in finding_ids
    assert "l2_distinct_lapel" in finding_ids
    assert "l2_collar_warning" not in finding_ids


def test_severity_ordering_precedence():
    """Verify that deduplicated findings are sorted strictly by severity precedence: VIOLATION > WARNING > MANUAL_REVIEW > PASS."""
    coordinator = AuditCoordinator()

    mixed_findings = [
        AuditFinding(
            finding_id="f_pass",
            rule_id="R-PASS",
            category=FindingCategory.BRANDING_LOGO,
            severity=ComplianceStatus.PASS,
            title="Pass item",
            observed_value="Compliant",
            allowed_threshold="Compliant",
            delta_explanation="None",
            source_citation="Rule.",
            source_rulebook="Book",
            remedy_suggestion="None",
            page_number=1,
        ),
        AuditFinding(
            finding_id="f_violation",
            rule_id="R-VIOLATION",
            category=FindingCategory.COSTING_FOB,
            severity=ComplianceStatus.VIOLATION,
            title="Violation item",
            observed_value="Breach",
            allowed_threshold="Limit",
            delta_explanation="Over limit",
            source_citation="Rule.",
            source_rulebook="Book",
            remedy_suggestion="Fix",
            page_number=1,
        ),
        AuditFinding(
            finding_id="f_manual_review",
            rule_id="R-REVIEW",
            category=FindingCategory.AESTHETICS,
            severity=ComplianceStatus.MANUAL_REVIEW,
            title="Review item",
            observed_value="Ambiguous",
            allowed_threshold="Standard",
            delta_explanation="Unclear",
            source_citation="Rule.",
            source_rulebook="Book",
            remedy_suggestion="Inspect",
            page_number=1,
        ),
        AuditFinding(
            finding_id="f_warning",
            rule_id="R-WARNING",
            category=FindingCategory.FABRIC_PERFORMANCE,
            severity=ComplianceStatus.WARNING,
            title="Warning item",
            observed_value="Borderline",
            allowed_threshold="Threshold",
            delta_explanation="Close",
            source_citation="Rule.",
            source_rulebook="Book",
            remedy_suggestion="Monitor",
            page_number=1,
        ),
    ]

    sorted_findings = coordinator._deduplicate_findings(mixed_findings, [])
    severities = [f.severity for f in sorted_findings]

    assert severities == [
        ComplianceStatus.VIOLATION,
        ComplianceStatus.WARNING,
        ComplianceStatus.MANUAL_REVIEW,
        ComplianceStatus.PASS,
    ]


@pytest.mark.asyncio
async def test_coordinator_fault_tolerance_on_semantic_reasoner_crash(coordinator_spec: TechPackSpec):
    """Ensure that if Layer 2 raises an unhandled exception or network timeout, the audit gracefully continues with Layer 1."""
    mock_deterministic = MagicMock()
    mock_deterministic.audit.return_value = [
        AuditFinding(
            finding_id="det_valid_finding",
            rule_id="FEI-JUMP-LOGO-COLLAR",
            category=FindingCategory.BRANDING_LOGO,
            severity=ComplianceStatus.VIOLATION,
            title="Collar Logo Violation",
            observed_value="70.0 cm²",
            allowed_threshold="<= 60.0 cm²",
            delta_explanation="+10 cm²",
            source_citation="Must not exceed 60 cm².",
            source_rulebook="FEI Jumping",
            remedy_suggestion="Scale down.",
            page_number=1,
        )
    ]

    mock_semantic = MagicMock()
    # Simulate LLM API crash / timeout
    mock_semantic.audit_async = AsyncMock(side_effect=TimeoutError("Gemini API connection timed out"))

    mock_retriever = MagicMock()
    mock_retriever.retrieve_rules_for_techpack.return_value = []

    coordinator = AuditCoordinator(
        deterministic=mock_deterministic,
        semantic=mock_semantic,
        rule_retriever=mock_retriever,
    )

    report = await coordinator.run_audit_async(coordinator_spec)

    assert report.overall_status == ComplianceStatus.VIOLATION
    assert len(report.findings) == 1
    assert report.findings[0].finding_id == "det_valid_finding"
    assert report.execution_time_seconds > 0.0
