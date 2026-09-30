"""Automated test suite for Stage 3: Pydantic schemas, Gemini structuring engine, and sanitization."""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from pydantic import ValidationError

from backend.app.models.tech_pack import (
    AestheticDetails,
    BOMItem,
    CostingSpec,
    Discipline,
    FabricSpec,
    GarmentMetadata,
    GarmentType,
    LogoPlacement,
    MeasurementItem,
    TechPackSpec,
)
from backend.app.engine.sanitizer import (
    SanitizedTechPack,
    TechPackSanitizer,
    tech_pack_sanitizer,
)
from backend.app.engine.structuring_service import (
    StructuringService,
    structuring_service,
)


def test_tech_pack_pydantic_schemas():
    """Verify validation, automatic field calculations, and alias handling."""
    logo = LogoPlacement(
        location="collar",
        width_cm=7.5,
        height_cm=8.0,
    )
    assert logo.calculated_area_cm2 == 60.0

    bom_item = BOMItem(
        item_name="Main Fabric Shell",
        placement="Body",
        material="78% PA 22% EA",
        unit_cost_usd=18.50,
    )
    assert bom_item.item_type == "Main Fabric Shell"

    spec = TechPackSpec(
        metadata=GarmentMetadata(
            style_code="ME-2026-SJ01",
            style_name="Grand Prix Show Coat",
            discipline=Discipline.JUMPING,
            garment_type=GarmentType.SHOW_JACKET,
        ),
        fabric=FabricSpec(
            primary_composition="78% Polyamide, 22% Elastane",
            weight_gsm=295.0,
        ),
        costing=CostingSpec(
            target_fob_usd=55.0,
            actual_fob_usd=58.5,
        ),
    )
    assert spec.metadata.style_code == "ME-2026-SJ01"
    assert spec.fabric.weight_gsm == 295.0
    assert len(spec.bom) == 0

    with pytest.raises(ValidationError):
        TechPackSpec(
            metadata=GarmentMetadata(style_code="FAIL-01", style_name="Bad Spec"),
            fabric=FabricSpec(primary_composition="100% Wool", weight_gsm="not_a_number"),
            costing=CostingSpec(target_fob_usd=50.0, actual_fob_usd=50.0),
        )


def test_sanitizer_unit_conversions():
    """Verify imperial-to-metric conversions and fiber standardizations."""
    sanitizer = TechPackSanitizer()

    assert sanitizer.convert_inches_to_cm(2.0) == 5.08
    assert sanitizer.convert_inches_to_cm(0.5) == 1.27
    assert sanitizer.convert_oz_to_gsm(8.5) == 288.2

    norm_comp, notes = sanitizer.normalize_composition_string("78% PA, 22% EA")
    assert "Polyamide" in norm_comp
    assert "Elastane" in norm_comp
    assert len(notes) == 2

    norm_comp2, _ = sanitizer.normalize_composition_string("85% Wool / 15% Spandex")
    assert "85% Wool" in norm_comp2
    assert "15% Elastane" in norm_comp2


def test_sanitizer_missing_specs_audit():
    """Verify completeness scoring and explicit MISSING_SPEC warnings."""
    sanitizer = TechPackSanitizer()

    incomplete_spec = TechPackSpec(
        metadata=GarmentMetadata(
            style_code="INC-01",
            style_name="Incomplete Jacket",
            discipline=Discipline.JUMPING,
        ),
        fabric=FabricSpec(
            primary_composition="",
            weight_gsm=0.0,
        ),
        costing=CostingSpec(
            target_fob_usd=0.0,
            actual_fob_usd=0.0,
        ),
    )

    sanitized = sanitizer.sanitize(incomplete_spec)
    assert isinstance(sanitized, SanitizedTechPack)
    assert sanitized.spec.fabric.primary_composition == "MISSING_SPEC"
    assert "fabric.primary_composition" in sanitized.report.missing_critical_specs
    assert "fabric.weight_gsm" in sanitized.report.missing_critical_specs
    assert "costing.target_fob_usd" in sanitized.report.missing_critical_specs
    assert sanitized.report.completeness_score_pct < 60.0
    assert len(sanitized.report.warnings) >= 3


def test_structuring_service_extract_jumping_coat():
    """Verify extraction of complete Show Jumping Coat from markdown input."""
    md_content = """
    # MAISON EQUESTRE PARIS
    STYLE: ME-2026-SJ01
    NAME: Grand Prix Technical Show Coat
    SEASON: SS26
    DISCIPLINE: Show Jumping

    FABRIC SPECIFICATIONS:
    PRIMARY COMPOSITION: 78% PA, 22% EA
    WEIGHT: 295 GSM
    BREATHABILITY: 14000 g/m²/24h

    BILL OF MATERIALS:
    | Item | Placement | Material | Color | Unit Cost |
    |---|---|---|---|---|
    | Main Fabric | Jacket Body | 78% PA 22% EA | Navy 19-4010 | $18.50 |
    | Collar Velvet | Lapel Trim | 100% Cotton Velvet | Black 19-0000 | $4.20 |

    MEASUREMENTS (POM):
    | POM-01 | Collar Stand Height | 4.5 | 0.5 |
    | POM-02 | Center Back Length | 68.0 | 1.0 |
    | POM-03 | Half Chest Width | 44.0 | 0.75 |

    BRANDING & LOGOS:
    COLLAR LOGO: Left Collar Stand, Dimensions: 7.5 cm x 8.0 cm (Area: 60.0 cm²)
    CHEST EMBLEM: Left Chest Pocket, Dimensions: 10.0 cm x 12.0 cm (Area: 120.0 cm²)

    AESTHETICS:
    COLLAR TYPE: Notched Lapel with Contrast Velvet Trim
    PIPING: 3.0 mm Satin Piping
    BUTTONS: 3 Front Horn Buttons

    COSTING:
    TARGET FOB: $55.00 USD
    ACTUAL FOB: $58.50 USD
    """

    service = StructuringService()
    result = service.extract_spec(
        markdown_content=md_content,
        source_pdf_name="sample_sj_coat.pdf",
        page_count=6,
    )

    assert isinstance(result, SanitizedTechPack)
    spec = result.spec
    assert spec.metadata.style_code == "ME-2026-SJ01"
    assert spec.metadata.discipline == Discipline.JUMPING
    assert spec.metadata.garment_type == GarmentType.SHOW_JACKET
    assert "Polyamide" in spec.fabric.primary_composition
    assert "Elastane" in spec.fabric.primary_composition
    assert spec.fabric.weight_gsm == 295.0
    assert len(spec.bom) >= 2
    assert len(spec.measurements) >= 3
    assert len(spec.logos) >= 2
    assert spec.aesthetic.collar_contrast_color == "Black Velvet"
    assert spec.aesthetic.button_count == 3
    assert spec.costing.target_fob_usd == 55.0
    assert spec.costing.actual_fob_usd == 58.5
    assert result.report.completeness_score_pct >= 80.0


def test_structuring_service_extract_dressage_tailcoat():
    """Verify extraction handles Dressage Tailcoat discipline and garment category."""
    md_content = """
    STYLE: ME-2026-DR02
    NAME: Olympic Presentation Tailcoat
    DISCIPLINE: Dressage
    GARMENT: Tailcoat

    PRIMARY COMPOSITION: 85% Virgin Wool, 15% Silk
    WEIGHT: 320 GSM
    TARGET FOB: $110.00 USD
    ACTUAL FOB: $125.00 USD
    BUTTONS: 6 Front Brass Buttons
    """

    service = StructuringService()
    result = service.extract_spec(markdown_content=md_content)

    assert result.spec.metadata.discipline == Discipline.DRESSAGE
    assert result.spec.metadata.garment_type == GarmentType.TAILCOAT
    assert result.spec.aesthetic.button_count == 6
    assert result.spec.costing.actual_fob_usd == 125.0


def test_structuring_service_empty_input():
    """Verify ValueError is raised on empty markdown payload."""
    service = StructuringService()
    with pytest.raises(ValueError):
        service.extract_spec("")
