"""Boundary Value Analysis (BVA) and multi-logo constraint tests for Layer 1 Deterministic Engine.

Validates exact mathematical limits across all quantitative regulatory and brand SOP rules.
"""
import pytest

from backend.app.engine.deterministic_engine import DeterministicEngine
from backend.app.models.tech_pack import (
    AestheticDetails,
    ComplianceStatus,
    CostingSpec,
    Discipline,
    FabricSpec,
    GarmentMetadata,
    GarmentType,
    LogoPlacement,
    TechPackSpec,
)


@pytest.fixture
def base_spec() -> TechPackSpec:
    """Minimal compliant specification for boundary testing."""
    return TechPackSpec(
        metadata=GarmentMetadata(
            style_code="BVA-2026-TEST",
            style_name="Boundary Test Garment",
            discipline=Discipline.JUMPING,
            garment_type=GarmentType.SHOW_JACKET,
            season="SS26",
            gender="Unisex",
        ),
        fabric=FabricSpec(
            primary_composition="78% Polyamide, 22% Elastane",
            weight_gsm=280.0,
            breathability_g_m2_24h=12000.0,
        ),
        costing=CostingSpec(
            target_fob_usd=50.00,
            actual_fob_usd=50.00,
        ),
        logos=[],
        aesthetic=AestheticDetails(
            piping_present=False,
        ),
        measurements=[],
    )


@pytest.mark.parametrize("width,height,expected_violation", [
    (7.0, 8.5, False),      # 59.50 cm² <= 60.0 cm²
    (6.0, 10.0, False),     # 60.00 cm² <= 60.0 cm²
    (6.0, 10.01, True),     # 60.06 cm² > 60.0 cm²
    (7.75, 7.75, True),     # 60.06 cm² > 60.0 cm²
    (8.0, 8.0, True),       # 64.00 cm² > 60.0 cm²
])
def test_collar_logo_area_exact_boundaries(base_spec: TechPackSpec, width: float, height: float, expected_violation: bool):
    """Test boundary values for collar logo area (legal threshold 60.0 cm²)."""
    engine = DeterministicEngine()
    spec = base_spec.model_copy(deep=True)
    spec.logos = [
        LogoPlacement(
            location="Left Collar",
            width_cm=width,
            height_cm=height,
        )
    ]
    findings = engine.audit(spec)
    collar_findings = [f for f in findings if "collar" in f.finding_id and "count" not in f.finding_id]

    if expected_violation:
        assert len(collar_findings) == 1
        assert collar_findings[0].severity == ComplianceStatus.VIOLATION
        assert "60.0 cm²" in collar_findings[0].allowed_threshold
    else:
        assert len(collar_findings) == 0


@pytest.mark.parametrize("width,height,expected_violation", [
    (10.0, 19.9, False),    # 199.0 cm² <= 200.0 cm²
    (10.0, 20.0, False),    # 200.0 cm² <= 200.0 cm²
    (10.0, 20.05, True),    # 200.5 cm² > 200.0 cm²
    (14.2, 14.2, True),     # 201.64 cm² > 200.0 cm²
])
def test_chest_logo_area_exact_boundaries(base_spec: TechPackSpec, width: float, height: float, expected_violation: bool):
    """Test boundary values for chest logo area (legal threshold 200.0 cm²)."""
    engine = DeterministicEngine()
    spec = base_spec.model_copy(deep=True)
    spec.logos = [
        LogoPlacement(
            location="Left Chest Pocket",
            width_cm=width,
            height_cm=height,
        )
    ]
    findings = engine.audit(spec)
    chest_findings = [f for f in findings if "chest" in f.finding_id and "count" not in f.finding_id]

    if expected_violation:
        assert len(chest_findings) == 1
        assert chest_findings[0].severity == ComplianceStatus.VIOLATION
    else:
        assert len(chest_findings) == 0


@pytest.mark.parametrize("width,height,expected_violation", [
    (10.0, 9.9, False),     # 99.0 cm² <= 100.0 cm²
    (10.0, 10.0, False),    # 100.0 cm² <= 100.0 cm²
    (10.0, 10.05, True),    # 100.5 cm² > 100.0 cm²
    (11.0, 10.0, True),     # 110.0 cm² > 100.0 cm²
])
def test_sleeve_logo_area_exact_boundaries(base_spec: TechPackSpec, width: float, height: float, expected_violation: bool):
    """Test boundary values for sleeve logo area (legal threshold 100.0 cm²)."""
    engine = DeterministicEngine()
    spec = base_spec.model_copy(deep=True)
    spec.logos = [
        LogoPlacement(
            location="Right Upper Sleeve",
            width_cm=width,
            height_cm=height,
        )
    ]
    findings = engine.audit(spec)
    sleeve_findings = [f for f in findings if "sleeve" in f.finding_id]

    if expected_violation:
        assert len(sleeve_findings) == 1
        assert sleeve_findings[0].severity == ComplianceStatus.VIOLATION
    else:
        assert len(sleeve_findings) == 0


def test_multiple_collar_logos_rejected(base_spec: TechPackSpec):
    """Ensure placing 2 collar logos triggers a single-emblem count violation."""
    engine = DeterministicEngine()
    spec = base_spec.model_copy(deep=True)
    spec.logos = [
        LogoPlacement(location="Left Collar Point", width_cm=3.0, height_cm=3.0),
        LogoPlacement(location="Right Collar Stand", width_cm=4.0, height_cm=4.0),
    ]
    findings = engine.audit(spec)
    count_findings = [f for f in findings if "collar_count" in f.finding_id]

    assert len(count_findings) == 1
    assert count_findings[0].severity == ComplianceStatus.VIOLATION
    assert "2 collar emblems" in count_findings[0].observed_value


def test_multiple_chest_logos_rejected(base_spec: TechPackSpec):
    """Ensure placing logos on both chests triggers a single-side limit violation."""
    engine = DeterministicEngine()
    spec = base_spec.model_copy(deep=True)
    spec.logos = [
        LogoPlacement(location="Left Chest", width_cm=5.0, height_cm=5.0),
        LogoPlacement(location="Right Chest", width_cm=5.0, height_cm=5.0),
    ]
    findings = engine.audit(spec)
    count_findings = [f for f in findings if "chest_count" in f.finding_id]

    assert len(count_findings) == 1
    assert count_findings[0].severity == ComplianceStatus.VIOLATION
    assert "2 chest/pocket logos" in count_findings[0].observed_value


@pytest.mark.parametrize("discipline,width_mm,expected_severity", [
    (Discipline.JUMPING, 3.5, None),
    (Discipline.JUMPING, 3.6, ComplianceStatus.WARNING),
    (Discipline.DRESSAGE, 4.0, None),
    (Discipline.DRESSAGE, 4.1, ComplianceStatus.VIOLATION),
])
def test_piping_width_discipline_boundaries(base_spec: TechPackSpec, discipline: Discipline, width_mm: float, expected_severity):
    """Verify piping limits (Jumping <= 3.5 mm brand warning vs Dressage <= 4.0 mm FEI violation)."""
    engine = DeterministicEngine()
    spec = base_spec.model_copy(deep=True)
    spec.metadata.discipline = discipline
    spec.aesthetic.piping_present = True
    spec.aesthetic.piping_width_mm = width_mm

    findings = engine.audit(spec)
    piping_findings = [f for f in findings if "piping" in f.finding_id]

    if expected_severity is None:
        assert len(piping_findings) == 0
    else:
        assert len(piping_findings) == 1
        assert piping_findings[0].severity == expected_severity


@pytest.mark.parametrize("garment_type,actual_fob,expected_severity", [
    (GarmentType.SHOW_JACKET, 65.00, None),
    (GarmentType.SHOW_JACKET, 65.05, ComplianceStatus.VIOLATION),
    (GarmentType.TAILCOAT, 95.00, None),
    (GarmentType.TAILCOAT, 95.50, ComplianceStatus.VIOLATION),
    (GarmentType.COMPETITION_SHIRT, 28.00, None),
    (GarmentType.COMPETITION_SHIRT, 28.50, ComplianceStatus.VIOLATION),
])
def test_cogs_hard_ceiling_per_garment_type(base_spec: TechPackSpec, garment_type: GarmentType, actual_fob: float, expected_severity):
    """Test hard financial ceilings by garment category ($65 jacket, $95 tailcoat, $28 shirt)."""
    engine = DeterministicEngine()
    spec = base_spec.model_copy(deep=True)
    spec.metadata.garment_type = garment_type
    spec.costing.target_fob_usd = 50.00
    spec.costing.actual_fob_usd = actual_fob

    findings = engine.audit(spec)
    cogs_findings = [f for f in findings if "cogs_ceiling" in f.finding_id]

    if expected_severity is None:
        assert len(cogs_findings) == 0
    else:
        assert len(cogs_findings) == 1
        assert cogs_findings[0].severity == expected_severity


@pytest.mark.parametrize("breathability,expected_warning", [
    (10000.0, False),
    (9999.0, True),
    (14500.0, False),
    (7500.0, True),
])
def test_fabric_breathability_boundary(base_spec: TechPackSpec, breathability: float, expected_warning: bool):
    """Verify WVTR breathability threshold (>= 10,000 g/m²/24h)."""
    engine = DeterministicEngine()
    spec = base_spec.model_copy(deep=True)
    spec.fabric.breathability_g_m2_24h = breathability

    findings = engine.audit(spec)
    breath_findings = [f for f in findings if "breathability" in f.finding_id]

    if expected_warning:
        assert len(breath_findings) == 1
        assert breath_findings[0].severity == ComplianceStatus.WARNING
    else:
        assert len(breath_findings) == 0
