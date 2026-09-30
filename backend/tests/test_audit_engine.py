"""Comprehensive automated tests for Stage 5 Dual-Layer Comparative Audit Engine."""
import time
import pytest

from backend.app.engine.audit_coordinator import AuditCoordinator
from backend.app.engine.deterministic_engine import DeterministicEngine
from backend.app.engine.semantic_reasoner import SemanticReasoner
from backend.app.models.tech_pack import (
    AestheticDetails,
    BOMItem,
    ComplianceStatus,
    CostingSpec,
    Discipline,
    FabricSpec,
    GarmentMetadata,
    GarmentType,
    LogoPlacement,
    MeasurementItem,
    TechPackSpec,
)


@pytest.fixture
def base_compliant_spec() -> TechPackSpec:
    """Returns a fully compliant Show Jumping jacket specification."""
    return TechPackSpec(
        metadata=GarmentMetadata(
            style_code="ME-SJ-2026-01",
            style_name="Monaco Grand Prix Show Jacket",
            discipline=Discipline.JUMPING,
            garment_type=GarmentType.SHOW_JACKET,
            season="SS26",
            gender="Women",
        ),
        fabric=FabricSpec(
            primary_composition="72% Wool, 25% Polyamide, 3% Elastane",
            weight_gsm=240.0,
            breathability_g_m2_24h=12500.0,
            stretch_weft_pct=22.0,
        ),
        bom=[
            BOMItem(item_type="Shell Fabric", placement="Body & Sleeves", quantity=1.0),
            BOMItem(item_type="Buttons", placement="Front Closure", quantity=4.0),
        ],
        measurements=[
            MeasurementItem(pom_code="POM01", description="Chest Width", spec_cm=48.0, tolerance_plus_minus_cm=0.5),
            MeasurementItem(pom_code="POM02", description="Collar Stand Height", spec_cm=4.2, tolerance_plus_minus_cm=0.4),
        ],
        logos=[
            LogoPlacement(
                location="Left Collar",
                width_cm=4.0,
                height_cm=5.0,
                technique="Tonal embroidery",
            ),
            LogoPlacement(
                location="Chest Pocket",
                width_cm=6.0,
                height_cm=6.0,
                technique="Laser etched patch",
            ),
        ],
        aesthetic=AestheticDetails(
            collar_type="Stand Collar with Notch",
            collar_contrast_color="Self Fabric (Tonal Navy)",
            piping_present=True,
            piping_width_mm=2.5,
            button_count=4,
            button_material="Matte horn",
        ),
        costing=CostingSpec(
            target_fob_usd=52.00,
            actual_fob_usd=51.50,
        ),
    )


def test_deterministic_collar_logo_violation(base_compliant_spec: TechPackSpec):
    """Verify that a collar logo exceeding 60 cm² triggers an FEI VIOLATION finding."""
    engine = DeterministicEngine()

    spec = base_compliant_spec.model_copy(deep=True)
    spec.logos = [
        LogoPlacement(
            location="Right Collar Stand",
            width_cm=8.0,
            height_cm=8.0,
            technique="Gold embroidery",
        )
    ]

    findings = engine.audit(spec)
    collar_findings = [f for f in findings if "collar" in f.finding_id]

    assert len(collar_findings) == 1
    finding = collar_findings[0]
    assert finding.severity == ComplianceStatus.VIOLATION
    assert finding.rule_id == "FEI-JUMP-LOGO-COLLAR"
    assert "64.0 cm²" in finding.observed_value
    assert "+4.0 cm²" in finding.delta_explanation
    assert "Art. 256" in finding.source_rulebook


def test_deterministic_fob_costing_ceiling_violation(base_compliant_spec: TechPackSpec):
    """Verify that FOB exceeding the $65.00 USD hard ceiling triggers a brand VIOLATION."""
    engine = DeterministicEngine()

    spec = base_compliant_spec.model_copy(deep=True)
    spec.costing.actual_fob_usd = 72.50
    spec.costing.target_fob_usd = 55.00

    findings = engine.audit(spec)
    costing_findings = [f for f in findings if f.rule_id == "BRAND-SOP-COGS-01"]

    assert len(costing_findings) == 1
    finding = costing_findings[0]
    assert finding.severity == ComplianceStatus.VIOLATION
    assert "$72.50 USD" in finding.observed_value
    assert "+$7.50 USD" in finding.delta_explanation


def test_deterministic_fabric_and_tolerance_warnings(base_compliant_spec: TechPackSpec):
    """Verify that low breathability and loose collar tolerance trigger WARNING findings."""
    engine = DeterministicEngine()

    spec = base_compliant_spec.model_copy(deep=True)
    spec.fabric.breathability_g_m2_24h = 8200.0
    spec.measurements = [
        MeasurementItem(pom_code="POM02", description="Collar Stand Height", spec_cm=4.2, tolerance_plus_minus_cm=0.8)
    ]

    findings = engine.audit(spec)
    rule_ids = {f.rule_id for f in findings}

    assert "BRAND-SOP-FABRIC-01" in rule_ids
    assert "BRAND-SOP-TOL-01" in rule_ids

    breath_finding = next(f for f in findings if f.rule_id == "BRAND-SOP-FABRIC-01")
    assert breath_finding.severity == ComplianceStatus.WARNING
    assert "8200 g/m²/24h" in breath_finding.observed_value

    tol_finding = next(f for f in findings if f.rule_id == "BRAND-SOP-TOL-01")
    assert tol_finding.severity == ComplianceStatus.WARNING
    assert "+/- 0.80 cm" in tol_finding.observed_value


def test_deterministic_performance_latency(base_compliant_spec: TechPackSpec):
    """Ensure Layer 1 deterministic execution completes well within 15ms budget."""
    engine = DeterministicEngine()
    start = time.perf_counter()
    findings = engine.audit(base_compliant_spec)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert elapsed_ms < 15.0
    assert len(findings) == 0


def test_semantic_reasoner_dressage_collar_color():
    """Verify that non-conservative bright collar color in Dressage triggers semantic finding."""
    reasoner = SemanticReasoner()
    spec = TechPackSpec(
        metadata=GarmentMetadata(
            style_code="ME-DR-2026-03",
            style_name="Elysée Dressage Tailcoat",
            discipline=Discipline.DRESSAGE,
            garment_type=GarmentType.TAILCOAT,
        ),
        fabric=FabricSpec(primary_composition="Wool", weight_gsm=280.0),
        aesthetic=AestheticDetails(
            collar_type="Velvet Collar",
            collar_contrast_color="Neon Yellow Velvet",
        ),
        costing=CostingSpec(target_fob_usd=80.0, actual_fob_usd=78.0),
    )

    findings = reasoner._mock_semantic_eval(spec, [])
    assert len(findings) == 1
    finding = findings[0]
    assert finding.severity == ComplianceStatus.VIOLATION
    assert finding.rule_id == "FEI-DRESS-COLOR-COLLAR"
    assert "Neon Yellow" in finding.observed_value


def test_semantic_reasoner_zero_false_positives(base_compliant_spec: TechPackSpec):
    """Verify that a compliant garment produces zero false positives in semantic reasoner."""
    reasoner = SemanticReasoner()
    findings = reasoner._mock_semantic_eval(base_compliant_spec, [])
    assert len(findings) == 0


@pytest.mark.asyncio
async def test_audit_coordinator_overall_roll_up_violation(base_compliant_spec: TechPackSpec):
    """Verify coordinator rolls up a single violation to overall VIOLATION status."""
    coordinator = AuditCoordinator()

    spec = base_compliant_spec.model_copy(deep=True)
    spec.logos = [
        LogoPlacement(
            location="Collar Crest",
            width_cm=8.0,
            height_cm=8.0,
        )
    ]

    report = await coordinator.run_audit_async(spec)

    assert report.overall_status == ComplianceStatus.VIOLATION
    assert report.execution_time_seconds < 3.0
    assert len(report.findings) >= 1
    assert any(f.severity == ComplianceStatus.VIOLATION for f in report.findings)
    assert report.overall_score_pct < 100.0

    cat_names = {c.category_name for c in report.category_scores}
    assert "Branding & Logos" in cat_names
    assert "Fabric & Performance" in cat_names
    assert "Costing & FOB" in cat_names


@pytest.mark.asyncio
async def test_audit_coordinator_clean_pass(base_compliant_spec: TechPackSpec):
    """Verify coordinator awards 100% and PASS to fully compliant specification."""
    coordinator = AuditCoordinator()
    report = await coordinator.run_audit_async(base_compliant_spec)

    assert report.overall_status == ComplianceStatus.PASS
    assert report.overall_score_pct == 100.0
    assert len(report.findings) == 0
    assert all(c.status == ComplianceStatus.PASS for c in report.category_scores)
