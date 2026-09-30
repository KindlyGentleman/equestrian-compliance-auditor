"""Domain data models and schemas for Equestrian Tech Pack Specifications."""
from enum import Enum
from typing import Dict, List, Optional
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
    weave_type: Optional[str] = Field(default="4-way stretch technical twill")
    stretch_warp_pct: Optional[float] = Field(default=18.0)
    stretch_weft_pct: Optional[float] = Field(default=22.0)
    breathability_g_m2_24h: Optional[float] = Field(default=12000.0, description="WVTR breathability")
    water_resistance_mm: Optional[float] = Field(default=5000.0)
    uv_rating: Optional[str] = Field(default="UPF 50+")


class BOMItem(BaseModel):
    item_type: str = Field(description="Main Fabric, Lining, Buttons, Zipper, Trim")
    placement: str = Field(description="Body, Collar, Front Closure, Cuffs")
    supplier_code: Optional[str] = None
    material: Optional[str] = None
    color_code: Optional[str] = None
    unit_cost_usd: Optional[float] = None
    quantity: Optional[float] = 1.0


class MeasurementItem(BaseModel):
    pom_code: str = Field(description="Point of Measure code e.g. POM-01")
    description: str = Field(description="e.g. Collar Stand Height, Chest Width")
    spec_cm: float = Field(description="Base size specification in centimeters")
    tolerance_plus_minus_cm: float = Field(default=0.5)
    size_grading: Dict[str, float] = Field(default_factory=dict)


class LogoPlacement(BaseModel):
    location: str = Field(description="collar, chest, left_sleeve, right_sleeve, nape")
    width_cm: float = Field(ge=0.0)
    height_cm: float = Field(ge=0.0)
    calculated_area_cm2: float = Field(default=0.0, description="Computed surface area (width * height)")
    description: Optional[str] = None
    technique: Optional[str] = Field(default="Embroidery")

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
    collar_contrast_color: Optional[str] = Field(default=None, description="e.g. Tonal, Black Velvet, Navy")
    collar_fabric_type: Optional[str] = Field(default="Self-fabric")
    piping_present: bool = Field(default=False)
    piping_width_mm: Optional[float] = Field(default=0.0)
    piping_color: Optional[str] = None
    button_count: Optional[int] = Field(default=3)
    button_material: Optional[str] = Field(default="Matte horn with engraved brand crest")


class CostingSpec(BaseModel):
    target_fob_usd: float = Field(description="Brand target FOB cost ceiling")
    actual_fob_usd: float = Field(description="Vendor quoted actual FOB cost")
    fabric_cost_usd: Optional[float] = None
    trim_cost_usd: Optional[float] = None
    cmt_cost_usd: Optional[float] = None


class TechPackSpec(BaseModel):
    """Master structured technical package specification."""
    metadata: GarmentMetadata
    fabric: FabricSpec
    bom: List[BOMItem] = Field(default_factory=list)
    measurements: List[MeasurementItem] = Field(default_factory=list)
    logos: List[LogoPlacement] = Field(default_factory=list)
    aesthetic: AestheticDetails = Field(default_factory=AestheticDetails)
    costing: CostingSpec
    source_pdf_name: Optional[str] = None
    page_count: int = 1
