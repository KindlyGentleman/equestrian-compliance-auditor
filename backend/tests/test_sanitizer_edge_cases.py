"""In-depth edge-case testing for TechPackSanitizer and unit normalizer.

Tests complex fiber synonym standardizations, unit conversions, stale logo area recomputation,
and completeness scoring logic.
"""
import pytest

from backend.app.engine.sanitizer import TechPackSanitizer
from backend.app.models.tech_pack import (
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
def sanitizer() -> TechPackSanitizer:
    return TechPackSanitizer()


@pytest.mark.parametrize("raw_input,expected_output", [
    ("78% PA / 22% EA", "78% Polyamide, 22% Elastane"),
    ("95% co, 5% el", "95% Cotton, 5% Elastane"),
    ("100% WV", "100% Wool"),
    ("80% wo & 20% se", "80% Wool, 20% Silk"),
    ("70% PES; 30% VI", "70% Polyester, 30% Viscose"),
    ("85% nylon, 15% spandex", "85% Polyamide, 15% Elastane"),
    ("92% poly + 8% lycra", "92% Polyester, 8% Elastane"),
    ("100% Merino Wool", "100% Wool"),
    ("60% Cotton and 40% Linen", "60% Cotton, 40% Linen"),
])
def test_fiber_synonym_normalization(sanitizer: TechPackSanitizer, raw_input: str, expected_output: str):
    """Test ISO/trade textile fiber abbreviations mapped to standard English names."""
    normalized, notes = sanitizer.normalize_composition_string(raw_input)
    assert normalized == expected_output


def test_unknown_fiber_graceful_preservation(sanitizer: TechPackSanitizer):
    """Exotic or proprietary fibers must be title-cased without raising errors."""
    raw = "85% Cordura, 15% Spandex"
    normalized, notes = sanitizer.normalize_composition_string(raw)
    assert "85% Cordura" in normalized
    assert "15% Elastane" in normalized


@pytest.mark.parametrize("inches,expected_cm", [
    (1.0, 2.54),
    (2.5, 6.35),
    (10.0, 25.4),
    (0.5, 1.27),
])
def test_imperial_inches_to_cm_conversion(sanitizer: TechPackSanitizer, inches: float, expected_cm: float):
    """Verify inch to centimeter conversion factor."""
    assert sanitizer.convert_inches_to_cm(inches) == expected_cm


@pytest.mark.parametrize("oz_yd2,expected_gsm", [
    (5.0, 169.5),
    (8.5, 288.2),
    (10.0, 339.1),
])
def test_imperial_oz_yd2_to_gsm_conversion(sanitizer: TechPackSanitizer, oz_yd2: float, expected_gsm: float):
    """Verify ounce per square yard to grams per square meter conversion."""
    assert sanitizer.convert_oz_to_gsm(oz_yd2) == expected_gsm


def test_stale_or_missing_logo_area_recomputed(sanitizer: TechPackSanitizer):
    """Verify that inconsistent or zero logo area is automatically corrected."""
    spec = TechPackSpec(
        metadata=GarmentMetadata(
            style_code="SAN-TEST-01",
            style_name="Sanitizer Test Jacket",
            discipline=Discipline.JUMPING,
            garment_type=GarmentType.SHOW_JACKET,
        ),
        fabric=FabricSpec(
            primary_composition="78% PA, 22% EA",
            weight_gsm=280.0,
        ),
        costing=CostingSpec(
            target_fob_usd=55.0,
            actual_fob_usd=52.0,
        ),
        logos=[
            LogoPlacement(
                location="Collar",
                width_cm=6.0,
                height_cm=8.0,
                calculated_area_cm2=10.0,  # Deliberately stale area
            )
        ],
    )

    result = sanitizer.sanitize(spec)
    assert result.spec.logos[0].calculated_area_cm2 == 48.0
    assert any("Recomputed logo area" in c for c in result.report.normalized_conversions)


def test_completeness_scoring_with_missing_critical_data(sanitizer: TechPackSanitizer):
    """Verify completeness score formula when critical specifications are missing."""
    spec = TechPackSpec(
        metadata=GarmentMetadata(
            style_code="SAN-TEST-MISSING",
            style_name="Incomplete Spec",
            discipline=Discipline.DRESSAGE,
            garment_type=GarmentType.TAILCOAT,
        ),
        fabric=FabricSpec(
            primary_composition="",  # Missing
            weight_gsm=0.0,          # Missing
        ),
        costing=CostingSpec(
            target_fob_usd=0.0,      # Missing
            actual_fob_usd=0.0,      # Missing
        ),
    )

    result = sanitizer.sanitize(spec)
    report = result.report

    assert "fabric.primary_composition" in report.missing_critical_specs
    assert "fabric.weight_gsm" in report.missing_critical_specs
    assert "costing.target_fob_usd" in report.missing_critical_specs
    assert "costing.actual_fob_usd" in report.missing_critical_specs
    assert len(report.missing_critical_specs) == 4
    # With 4 of 6 critical specs missing: max(0, (6-4)/6) * 100 = 33.3%
    assert report.completeness_score_pct == 33.3


def test_measurement_non_positive_warnings(sanitizer: TechPackSanitizer):
    """Verify that zero or negative POM dimensions emit diagnostic warnings."""
    spec = TechPackSpec(
        metadata=GarmentMetadata(
            style_code="SAN-POM-TEST",
            style_name="POM Warning Test",
            discipline=Discipline.JUMPING,
            garment_type=GarmentType.SHOW_JACKET,
        ),
        fabric=FabricSpec(primary_composition="100% Wool", weight_gsm=300.0),
        costing=CostingSpec(target_fob_usd=60.0, actual_fob_usd=58.0),
        measurements=[
            MeasurementItem(pom_code="POM01", description="Chest Width", spec_cm=-10.0, tolerance_plus_minus_cm=0.5),
            MeasurementItem(pom_code="POM02", description="Collar Height", spec_cm=0.0, tolerance_plus_minus_cm=0.5),
        ],
    )

    result = sanitizer.sanitize(spec)
    assert any("non-positive spec: -10.0" in w for w in result.report.warnings)
    assert any("non-positive spec: 0.0" in w for w in result.report.warnings)
