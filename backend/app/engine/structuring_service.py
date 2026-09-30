"""Structured schema extraction engine using Gemini 2.0 Flash."""
import json
import logging
import re
from pathlib import Path
from typing import List, Optional

from google.genai import types

from backend.app.core.config import settings
from backend.app.core.gemini_client import gemini_wrapper
from backend.app.engine.sanitizer import SanitizedTechPack, tech_pack_sanitizer
from backend.app.ingestion.image_cropper import ExtractedFigure
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

logger = logging.getLogger(__name__)

TECHPACK_SYSTEM_INSTRUCTION = """
You are an expert Technical Designer and Equestrian Apparel Compliance Auditor for luxury performance wear.
Extract all garment specifications from the provided Markdown, tables, and figure notes into the strict TechPackSpec schema.

Domain Guidelines:
- Discipline: Must be JUMPING, DRESSAGE, EVENTING, or ALL. Infer from garment category if unstated (Tailcoat -> DRESSAGE; Competition Coat -> JUMPING).
- Garment Type: SHOW_JACKET, TAILCOAT, COMPETITION_SHIRT, BREECHES, or ACCESSORY.
- Fiber Composition: Preserve exact percentage numbers, translating abbreviations (PA -> Polyamide, EA -> Elastane, PES -> Polyester, WO -> Wool, CO -> Cotton, SE -> Silk).
- Branding & Logos: Record all collar, chest, and sleeve logos with width_cm, height_cm, and technique.
- Measurements: Extract Points of Measure (POM code, description, spec in cm, and tolerance).
- Aesthetic Trims: Note collar contrast velvet or satin, piping width in mm, and front button count.
- Costing: Capture target FOB and vendor actual FOB in USD.
"""


class StructuringService:
    """Service transforming unstructured tech pack Markdown into validated Pydantic models."""

    def __init__(self, client_wrapper=None, sanitizer=None):
        self.gemini = client_wrapper or gemini_wrapper
        self.sanitizer = sanitizer or tech_pack_sanitizer

    def _mock_heuristic_extract(
        self,
        markdown: str,
        source_pdf_name: Optional[str] = None,
        page_count: int = 1,
    ) -> TechPackSpec:
        """Heuristic rule-based extractor providing deterministic offline results."""
        # 1. Metadata
        style_match = re.search(r"(?:STYLE|STYLE CODE)[:\s]+([A-Z0-9\-_]+)", markdown, re.I)
        style_code = style_match.group(1).strip() if style_match else "ME-2026-SJ01"

        name_match = re.search(r"(?:NAME|STYLE NAME)[:\s]+([^\n]+)", markdown, re.I)
        style_name = name_match.group(1).strip() if name_match else "Grand Prix Show Coat"

        season_match = re.search(r"SEASON[:\s]+([A-Z0-9]+)", markdown, re.I)
        season = season_match.group(1).strip() if season_match else "SS26"

        disc_match = re.search(r"DISCIPLINE[:\s]+(JUMPING|DRESSAGE|EVENTING)", markdown, re.I)
        discipline = Discipline(disc_match.group(1).upper()) if disc_match else Discipline.JUMPING

        garment_type = GarmentType.SHOW_JACKET
        if "TAILCOAT" in markdown.upper():
            garment_type = GarmentType.TAILCOAT
        elif "SHIRT" in markdown.upper():
            garment_type = GarmentType.COMPETITION_SHIRT
        elif "BREECHES" in markdown.upper():
            garment_type = GarmentType.BREECHES

        metadata = GarmentMetadata(
            style_code=style_code,
            style_name=style_name,
            season=season,
            discipline=discipline,
            garment_type=garment_type,
            gender="Women's",
        )

        # 2. Fabric Specs
        comp_match = re.search(r"(?:COMPOSITION|PRIMARY COMPOSITION)[:\s]+([^\n]+)", markdown, re.I)
        primary_comp = comp_match.group(1).strip() if comp_match else "78% Polyamide, 22% Elastane"

        weight_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:GSM|g/m²)", markdown, re.I)
        weight_gsm = float(weight_match.group(1)) if weight_match else 295.0

        breath_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:g/m²/24h|WVTR)", markdown, re.I)
        breathability = float(breath_match.group(1)) if breath_match else 14000.0

        fabric = FabricSpec(
            primary_composition=primary_comp,
            weight_gsm=weight_gsm,
            breathability_g_m2_24h=breathability,
            stretch_warp_pct=18.0,
            stretch_weft_pct=22.0,
        )

        # 3. BOM Items
        bom_items: List[BOMItem] = []
        bom_matches = re.findall(
            r"\|\s*([^|\n]+?)\s*\|\s*([^|\n]+?)\s*\|\s*([^|\n]+?)\s*\|\s*([^|\n]*?)\s*\|\s*\$?(\d+(?:\.\d+)?)\s*\|",
            markdown,
        )
        for m in bom_matches:
            item_name, placement, material, color, cost = m
            if "item" in item_name.lower() or "---" in item_name:
                continue
            bom_items.append(
                BOMItem(
                    item_type=item_name.strip(),
                    placement=placement.strip(),
                    material=material.strip(),
                    color_code=color.strip(),
                    unit_cost_usd=float(cost),
                )
            )

        if not bom_items:
            bom_items = [
                BOMItem(item_type="Main Shell", placement="Body", material="78% PA 22% EA", color_code="Navy", unit_cost_usd=18.50),
                BOMItem(item_type="Collar Velvet", placement="Collar", material="100% Cotton", color_code="Black", unit_cost_usd=4.20),
            ]

        # 4. Measurements
        measurements: List[MeasurementItem] = []
        pom_matches = re.findall(
            r"\|\s*(POM-\d+)\s*\|\s*([^|\n]+?)\s*\|\s*(\d+(?:\.\d+)?)\s*\|\s*(\d+(?:\.\d+)?)\s*\|",
            markdown,
        )
        for pm in pom_matches:
            code, desc, spec_cm, tol_cm = pm
            measurements.append(
                MeasurementItem(
                    pom_code=code.strip(),
                    description=desc.strip(),
                    spec_cm=float(spec_cm),
                    tolerance_plus_minus_cm=float(tol_cm),
                )
            )

        if not measurements:
            measurements = [
                MeasurementItem(pom_code="POM-01", description="Collar Stand Height", spec_cm=4.5, tolerance_plus_minus_cm=0.5),
                MeasurementItem(pom_code="POM-02", description="Center Back Length", spec_cm=68.0, tolerance_plus_minus_cm=1.0),
                MeasurementItem(pom_code="POM-03", description="Half Chest Width", spec_cm=44.0, tolerance_plus_minus_cm=0.75),
            ]

        # 5. Logos & Branding
        logos: List[LogoPlacement] = []
        logo_matches = re.findall(
            r"([A-Z\s]+(?:LOGO|EMBLEM))[:\s]+.*?(\d+(?:\.\d+)?)\s*cm\s*x\s*(\d+(?:\.\d+)?)\s*cm",
            markdown,
            re.I,
        )
        for lm in logo_matches:
            raw_loc, w, h = lm
            location = "collar" if "collar" in raw_loc.lower() else "chest"
            w_val, h_val = float(w), float(h)
            logos.append(
                LogoPlacement(
                    location=location,
                    width_cm=w_val,
                    height_cm=h_val,
                    calculated_area_cm2=round(w_val * h_val, 2),
                    description=raw_loc.strip(),
                )
            )

        if not logos:
            logos = [
                LogoPlacement(location="collar", width_cm=7.5, height_cm=8.0, calculated_area_cm2=60.0),
                LogoPlacement(location="chest", width_cm=10.0, height_cm=12.0, calculated_area_cm2=120.0),
            ]

        # 6. Aesthetic Details
        collar_type = "Notched Lapel"
        if "MANDARIN" in markdown.upper() or "STAND-UP" in markdown.upper():
            collar_type = "Stand-up"

        piping_match = re.search(r"PIPING[:\s]+(\d+(?:\.\d+)?)\s*mm", markdown, re.I)
        piping_width = float(piping_match.group(1)) if piping_match else 3.0
        piping_present = "PIPING" in markdown.upper()

        btn_match = re.search(r"(?:BUTTONS?|BUTTON COUNT)[:\s]+(\d+)", markdown, re.I)
        if not btn_match:
            btn_match = re.search(r"\b(\d+)\s*(?:Front\s*)?(?:[A-Za-z]+\s*){0,2}Buttons\b", markdown, re.I)
        btn_count = int(btn_match.group(1)) if btn_match else 3

        contrast_color = "Black Velvet" if "VELVET" in markdown.upper() else None

        aesthetic = AestheticDetails(
            collar_type=collar_type,
            collar_contrast_color=contrast_color,
            piping_present=piping_present,
            piping_width_mm=piping_width,
            button_count=btn_count,
        )

        # 7. Costing
        target_fob_match = re.search(r"TARGET FOB[:\s]+\$?(\d+(?:\.\d+)?)", markdown, re.I)
        target_fob = float(target_fob_match.group(1)) if target_fob_match else 55.0

        actual_fob_match = re.search(r"ACTUAL FOB[:\s]+\$?(\d+(?:\.\d+)?)", markdown, re.I)
        actual_fob = float(actual_fob_match.group(1)) if actual_fob_match else 58.50

        costing = CostingSpec(
            target_fob_usd=target_fob,
            actual_fob_usd=actual_fob,
            fabric_cost_usd=24.0,
            cmt_cost_usd=28.5,
        )

        return TechPackSpec(
            metadata=metadata,
            fabric=fabric,
            bom=bom_items,
            measurements=measurements,
            logos=logos,
            aesthetic=aesthetic,
            costing=costing,
            source_pdf_name=source_pdf_name,
            page_count=page_count,
        )

    async def extract_spec_async(
        self,
        markdown_content: str,
        figures: Optional[List[ExtractedFigure]] = None,
        source_pdf_name: Optional[str] = None,
        page_count: int = 1,
    ) -> SanitizedTechPack:
        """Extract structured TechPackSpec via Gemini 2.0 Flash or deterministic fallback."""
        if not markdown_content or not markdown_content.strip():
            raise ValueError("Markdown content cannot be empty for spec extraction")

        extracted_spec: Optional[TechPackSpec] = None

        if not self.gemini.use_mock and self.gemini.client is not None:
            try:
                prompt = f"Extract complete technical package specifications from this tech pack:\n\n{markdown_content}"
                image_parts = []
                if figures:
                    for fig in figures[:3]:
                        fig_path = Path(fig.file_path)
                        if fig_path.exists():
                            mime = "image/png" if fig_path.suffix.lower() == ".png" else "image/jpeg"
                            image_parts.append(
                                types.Part.from_bytes(data=fig_path.read_bytes(), mime_type=mime)
                            )

                parsed = await self.gemini.generate_structured(
                    prompt=prompt,
                    response_schema=TechPackSpec,
                    images=image_parts if image_parts else None,
                    system_instruction=TECHPACK_SYSTEM_INSTRUCTION,
                )
                if isinstance(parsed, TechPackSpec):
                    extracted_spec = parsed
                elif isinstance(parsed, dict):
                    extracted_spec = TechPackSpec.model_validate(parsed)
            except Exception as exc:
                logger.warning("Gemini live structured generation failed (%s); reverting to heuristic extraction", exc)
                extracted_spec = None

        if extracted_spec is None:
            extracted_spec = self._mock_heuristic_extract(
                markdown=markdown_content,
                source_pdf_name=source_pdf_name,
                page_count=page_count,
            )

        extracted_spec.source_pdf_name = source_pdf_name
        extracted_spec.page_count = page_count

        return self.sanitizer.sanitize(extracted_spec)

    def extract_spec(
        self,
        markdown_content: str,
        figures: Optional[List[ExtractedFigure]] = None,
        source_pdf_name: Optional[str] = None,
        page_count: int = 1,
    ) -> SanitizedTechPack:
        """Synchronous wrapper for extract_spec_async."""
        import asyncio
        try:
            return asyncio.run(
                self.extract_spec_async(markdown_content, figures, source_pdf_name, page_count)
            )
        except RuntimeError:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                self.extract_spec_async(markdown_content, figures, source_pdf_name, page_count)
            )


structuring_service = StructuringService()
