"""Domain data models and schemas for Equestrian Tech Pack Specifications."""
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class ComplianceStatus(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    VIOLATION = "VIOLATION"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class Discipline(str, Enum):
    JUMPING = "JUMPING"
    DRESSAGE = "DRESSAGE"
    EVENTING = "EVENTING"
    ALL = "ALL"


class GarmentType(str, Enum):
    SHOW_JACKET = "SHOW_JACKET"
    TAILCOAT = "TAILCOAT"
    COMPETITION_SHIRT = "COMPETITION_SHIRT"
    BREECHES = "BREECHES"
    ACCESSORY = "ACCESSORY"


class GarmentMetadata(BaseModel):
    style_code: str = Field(description="Unique style/article code e.g. ME-2026-SJ01")
    style_name: str = Field(description="Commercial name e.g. Grand Prix Technical Show Coat")
    season: str = Field(default="SS26", description="Collection season e.g. SS26, FW26")
    discipline: Discipline = Field(default=Discipline.JUMPING)
    garment_type: GarmentType = Field(default=GarmentType.SHOW_JACKET)
    gender: str = Field(default="Women's")


class FabricSpec(BaseModel):
    primary_composition: str = Field(description="e.g. 78% Polyamide, 22% Elastane")
    weight_gsm: float = Field(description="Fabric weight in grams per square meter")
    lining: str | None = Field(default=None, description="Lining composition or specification")
    weave_type: str | None = Field(default="4-way stretch technical twill")
    stretch_warp_pct: float | None = Field(default=18.0)
    stretch_weft_pct: float | None = Field(default=22.0)
    breathability_g_m2_24h: float | None = Field(default=12000.0, description="WVTR breathability")
    water_resistance_mm: float | None = Field(default=5000.0)
    uv_rating: str | None = Field(default="UPF 50+")


class BOMItem(BaseModel):
    item_type: str = Field(default="Main Fabric", description="Main Fabric, Lining, Buttons, Zipper, Trim")
    item_name: str | None = Field(default=None, description="Component name or description")
    placement: str = Field(description="Body, Collar, Front Closure, Cuffs")
    supplier_code: str | None = None
    material: str | None = None
    color_code: str | None = None
    unit_cost_usd: float | None = None
    quantity: float | None = 1.0

    @model_validator(mode="before")
    @classmethod
    def sync_name_and_type(cls, values: dict) -> dict:
        if isinstance(values, dict):
            name = values.get("item_name")
            itype = values.get("item_type")
            if name and not itype:
                values["item_type"] = name
            elif itype and not name:
                values["item_name"] = itype
        return values


class MeasurementItem(BaseModel):
    pom_code: str = Field(description="Point of Measure code e.g. POM-01")
    description: str = Field(description="e.g. Collar Stand Height, Chest Width")
    spec_cm: float = Field(description="Base size specification in centimeters")
    tolerance_plus_minus_cm: float = Field(default=0.5)
    size_grading: dict[str, float] = Field(default_factory=dict)


class LogoPlacement(BaseModel):
    location: str = Field(description="collar, chest, left_sleeve, right_sleeve, nape")
    width_cm: float = Field(ge=0.0)
    height_cm: float = Field(ge=0.0)
    calculated_area_cm2: float = Field(default=0.0, description="Computed surface area (width * height)")
    description: str | None = None
    technique: str | None = Field(default="Embroidery")
    colors: list[str] | None = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def calculate_area(cls, values: dict) -> dict:
        """Automatically compute surface area if width and height are provided."""
        if isinstance(values, dict):
            w = values.get("width_cm", 0.0) or 0.0
            h = values.get("height_cm", 0.0) or 0.0
            if "calculated_area_cm2" not in values or not values.get("calculated_area_cm2"):
                values["calculated_area_cm2"] = round(float(w) * float(h), 2)
        return values


class AestheticDetails(BaseModel):
    collar_type: str = Field(default="Notched Lapel", description="Stand-up, Notched, Peaked, Mandarin")
    collar_contrast_color: str | None = Field(default=None, description="e.g. Tonal, Black Velvet, Navy")
    collar_fabric_type: str | None = Field(default="Self-fabric")
    piping_present: bool = Field(default=False)
    piping_width_mm: float | None = Field(default=0.0)
    piping_color: str | None = None
    button_count: int | None = Field(default=3)
    button_material: str | None = Field(default="Matte horn with engraved brand crest")


class CostingSpec(BaseModel):
    target_fob_usd: float = Field(description="Brand target FOB cost ceiling")
    actual_fob_usd: float = Field(description="Vendor quoted actual FOB cost")
    fabric_cost_usd: float | None = None
    trim_cost_usd: float | None = None
    cmt_cost_usd: float | None = None


class TechPackSpec(BaseModel):
    """Master structured technical package specification."""
    metadata: GarmentMetadata
    fabric: FabricSpec
    bom: list[BOMItem] = Field(default_factory=list)
    measurements: list[MeasurementItem] = Field(default_factory=list)
    logos: list[LogoPlacement] = Field(default_factory=list)
    aesthetic: AestheticDetails = Field(default_factory=AestheticDetails)
    costing: CostingSpec
    source_pdf_name: str | None = None
    page_count: int = 1


# Domain Model Aliases for downstream convenience
BOMComponent = BOMItem
BrandingLogoSpec = LogoPlacement
MeasurementSpec = list[MeasurementItem]
TechPackMetadata = GarmentMetadata

