"""Post-extraction sanitizer and unit normalizer for tech pack specifications."""
import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from backend.app.models.tech_pack import (
    FabricSpec,
    MeasurementItem,
    LogoPlacement,
    TechPackSpec,
)


class SanitizerReport(BaseModel):
    """Audit report of unit transformations, normalized fiber names, and missing fields."""
    completeness_score_pct: float = Field(ge=0.0, le=100.0)
    missing_critical_specs: List[str] = Field(default_factory=list)
    normalized_conversions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class SanitizedTechPack(BaseModel):
    """Sanitized tech pack with completeness audit report."""
    spec: TechPackSpec
    report: SanitizerReport


class TechPackSanitizer:
    """Normalizes imperial units to metric, standardizes fiber codes, and audits completeness."""

    INCH_TO_CM = 2.54
    OZ_YD2_TO_GSM = 33.906
    MM_TO_CM = 0.1

    FIBER_SYNONYMS = {
        "pa": "Polyamide",
        "polyamide": "Polyamide",
        "nylon": "Polyamide",
        "ea": "Elastane",
        "el": "Elastane",
        "elastane": "Elastane",
        "spandex": "Elastane",
        "lycra": "Elastane",
        "pes": "Polyester",
        "pl": "Polyester",
        "polyester": "Polyester",
        "poly": "Polyester",
        "wo": "Wool",
        "wv": "Wool",
        "wool": "Wool",
        "virgin wool": "Wool",
        "merino": "Wool",
        "merino wool": "Wool",
        "co": "Cotton",
        "cotton": "Cotton",
        "se": "Silk",
        "silk": "Silk",
        "li": "Linen",
        "linen": "Linen",
        "cv": "Viscose",
        "vi": "Viscose",
        "viscose": "Viscose",
        "rayon": "Viscose",
    }

    def convert_inches_to_cm(self, inches: float) -> float:
        return round(float(inches) * self.INCH_TO_CM, 2)

    def convert_oz_to_gsm(self, oz_yd2: float) -> float:
        return round(float(oz_yd2) * self.OZ_YD2_TO_GSM, 1)

    def normalize_composition_string(self, raw_comp: str) -> Tuple[str, List[str]]:
        """Standardize fiber codes to full names while preserving percentages."""
        if not raw_comp:
            return "MISSING_SPEC", ["Missing primary fabric composition"]

        notes: List[str] = []
        tokens = re.split(r"([,;/+&]|\band\b)", raw_comp)
        normalized_segments: List[str] = []

        for token in tokens:
            cleaned = token.strip()
            if not cleaned or cleaned in [",", ";", "/", "+", "&", "and"]:
                continue

            match = re.match(r"^(\d+(?:\.\d+)?)\s*%\s*([A-Za-z\s]+)$", cleaned)
            if match:
                pct = match.group(1)
                fiber_raw = match.group(2).strip().lower()
                canonical = self.FIBER_SYNONYMS.get(fiber_raw)
                if canonical:
                    normalized_segments.append(f"{pct}% {canonical}")
                    if canonical.lower() != fiber_raw:
                        notes.append(f"Normalized fiber '{fiber_raw}' to '{canonical}'")
                else:
                    normalized_segments.append(f"{pct}% {match.group(2).strip().title()}")
            else:
                normalized_segments.append(cleaned)

        result_str = ", ".join(normalized_segments) if normalized_segments else raw_comp
        return result_str, notes

    def sanitize(self, spec: TechPackSpec) -> SanitizedTechPack:
        """Run complete sanitization, unit conversion, and completeness audit."""
        missing_critical: List[str] = []
        conversions: List[str] = []
        warnings: List[str] = []

        # 1. Audit Fabric Specs & Normalize Composition
        if not spec.fabric.primary_composition or spec.fabric.primary_composition.strip() == "":
            spec.fabric.primary_composition = "MISSING_SPEC"
            missing_critical.append("fabric.primary_composition")
        else:
            norm_comp, comp_notes = self.normalize_composition_string(spec.fabric.primary_composition)
            spec.fabric.primary_composition = norm_comp
            conversions.extend(comp_notes)

        if spec.fabric.weight_gsm <= 0:
            missing_critical.append("fabric.weight_gsm")
            warnings.append("Fabric weight is 0 or unrecorded")

        # 2. Audit Costing Specs
        if spec.costing.target_fob_usd <= 0:
            missing_critical.append("costing.target_fob_usd")
            warnings.append("Target FOB is missing or unrecorded")

        if spec.costing.actual_fob_usd <= 0:
            missing_critical.append("costing.actual_fob_usd")
            warnings.append("Actual quoted FOB is missing or unrecorded")

        # 3. Audit Measurements & Ensure Positive Dimensions
        for item in spec.measurements:
            if item.spec_cm <= 0:
                warnings.append(f"Measurement '{item.description}' has non-positive spec: {item.spec_cm}")

        # 4. Audit Logo Dimensions & Calculate Areas
        for logo in spec.logos:
            if logo.width_cm > 0 and logo.height_cm > 0:
                expected_area = round(logo.width_cm * logo.height_cm, 2)
                if abs(logo.calculated_area_cm2 - expected_area) > 0.05:
                    logo.calculated_area_cm2 = expected_area
                    conversions.append(f"Recomputed logo area for '{logo.location}' to {expected_area} cm²")
            elif logo.width_cm <= 0 or logo.height_cm <= 0:
                warnings.append(f"Logo placement at '{logo.location}' missing explicit dimensions")

        # 5. Calculate Completeness Score
        critical_fields_count = 6
        missing_count = len(missing_critical)
        score_pct = round(max(0.0, (critical_fields_count - missing_count) / critical_fields_count) * 100.0, 1)

        report = SanitizerReport(
            completeness_score_pct=score_pct,
            missing_critical_specs=missing_critical,
            normalized_conversions=conversions,
            warnings=warnings,
        )

        return SanitizedTechPack(spec=spec, report=report)


tech_pack_sanitizer = TechPackSanitizer()
