"""Layer 1 Deterministic Compliance Engine executing mathematical and rule-based checks."""
import json
import logging
import time
from pathlib import Path
from typing import Any

from backend.app.core.config import settings
from backend.app.models.audit import AuditFinding, FindingCategory
from backend.app.models.tech_pack import ComplianceStatus, Discipline, GarmentType, TechPackSpec

logger = logging.getLogger(__name__)


class DeterministicEngine:
    """Executes quantitative, zero-hallucination compliance audits directly in Python."""

    def __init__(self, catalog_path: str | None = None):
        self.catalog_path = Path(catalog_path or settings.RULES_CATALOG_PATH)
        self.rules: list[dict[str, Any]] = self._load_catalog()

    def _load_catalog(self) -> list[dict[str, Any]]:
        if not self.catalog_path.exists():
            logger.warning("Rules catalog missing at %s; initializing empty rules", self.catalog_path)
            return []
        with open(self.catalog_path, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("rules", [])

    def audit(self, spec: TechPackSpec) -> list[AuditFinding]:
        """Evaluate tech pack specification against quantitative rules in catalog."""
        start_time = time.time()
        findings: list[AuditFinding] = []
        discipline_val = spec.metadata.discipline.value if isinstance(spec.metadata.discipline, Discipline) else str(spec.metadata.discipline)

        # 1. Branding & Logo Area Checks
        for idx, logo in enumerate(spec.logos, start=1):
            loc = logo.location.lower()
            area = logo.calculated_area_cm2

            # Collar Logo Rule
            if "collar" in loc:
                limit = 60.0
                rule_id = "FEI-DRESS-LOGO-COLLAR" if discipline_val == "DRESSAGE" else "FEI-JUMP-LOGO-COLLAR"
                rulebook = "FEI Dressage Rules, Art. 427.3.1" if discipline_val == "DRESSAGE" else "FEI Jumping Rules, Art. 256.3.1"
                citation = (
                    "Brand manufacturer identification on jackets is restricted to one single emblem on the collar of maximum sixty square centimeters (60 cm²)."
                    if discipline_val == "DRESSAGE"
                    else "The total surface area of this identification must not exceed sixty square centimeters (60 cm²)."
                )

                if area > limit:
                    delta = round(area - limit, 2)
                    findings.append(
                        AuditFinding(
                            finding_id=f"det_logo_collar_{idx}",
                            rule_id=rule_id,
                            category=FindingCategory.BRANDING_LOGO,
                            severity=ComplianceStatus.VIOLATION,
                            title="Collar Brand Identification Exceeds FEI Surface Area Limit",
                            observed_value=f"{area:.1f} cm² ({logo.width_cm:.1f} cm x {logo.height_cm:.1f} cm)",
                            allowed_threshold=f"<= {limit:.1f} cm²",
                            delta_explanation=f"Observed collar logo area is {delta:+.1f} cm² over the 60.0 cm² legal maximum.",
                            source_citation=citation,
                            source_rulebook=rulebook,
                            remedy_suggestion="Reduce collar logo dimensions to ensure total surface area is at or below 60.0 cm².",
                            page_number=1,
                        )
                    )

            # Chest Logo Rule
            elif "chest" in loc or "pocket" in loc:
                limit = 200.0
                if area > limit:
                    delta = round(area - limit, 2)
                    findings.append(
                        AuditFinding(
                            finding_id=f"det_logo_chest_{idx}",
                            rule_id="FEI-JUMP-LOGO-CHEST",
                            category=FindingCategory.BRANDING_LOGO,
                            severity=ComplianceStatus.VIOLATION,
                            title="Chest Emblem Surface Area Exceeds FEI Maximum",
                            observed_value=f"{area:.1f} cm²",
                            allowed_threshold="<= 200.0 cm²",
                            delta_explanation=f"Observed chest logo is {delta:+.1f} cm² over the 200.0 cm² legal threshold.",
                            source_citation="A sponsor or manufacturer logo may appear on the chest/pocket area of the competition jacket on one side only. The total surface area of this logo must not exceed two hundred square centimeters (200 cm²).",
                            source_rulebook="FEI Jumping Rules, Art. 256.3.2",
                            remedy_suggestion="Scale down chest artwork so total area does not exceed 200 cm².",
                            page_number=1,
                        )
                    )

            # Sleeve Logo Rule
            elif "sleeve" in loc or "arm" in loc:
                limit = 100.0
                if area > limit:
                    delta = round(area - limit, 2)
                    findings.append(
                        AuditFinding(
                            finding_id=f"det_logo_sleeve_{idx}",
                            rule_id="FEI-JUMP-LOGO-SLEEVE",
                            category=FindingCategory.BRANDING_LOGO,
                            severity=ComplianceStatus.VIOLATION,
                            title="Sleeve Brand Logo Exceeds Maximum Area",
                            observed_value=f"{area:.1f} cm²",
                            allowed_threshold="<= 100.0 cm²",
                            delta_explanation=f"Observed sleeve logo is {delta:+.1f} cm² over the 100.0 cm² maximum per sleeve.",
                            source_citation="A brand or sponsor logo may appear on each sleeve of the competition jacket, with each logo not exceeding one hundred square centimeters (100 cm²).",
                            source_rulebook="FEI Jumping Rules, Art. 256.3.3",
                            remedy_suggestion="Scale down sleeve artwork so area is at or below 100 cm² per sleeve.",
                            page_number=1,
                        )
                    )

        # Check for multiple collar or chest logos exceeding single emblem allowance
        collar_logos = [logo for logo in spec.logos if "collar" in logo.location.lower()]
        if len(collar_logos) > 1:
            findings.append(
                AuditFinding(
                    finding_id="det_logo_collar_count_violation",
                    rule_id="FEI-DRESS-LOGO-COLLAR" if discipline_val == "DRESSAGE" else "FEI-JUMP-LOGO-COLLAR",
                    category=FindingCategory.BRANDING_LOGO,
                    severity=ComplianceStatus.VIOLATION,
                    title="Multiple Collar Logos Exceed Single Emblem Limit",
                    observed_value=f"{len(collar_logos)} collar emblems specified",
                    allowed_threshold="<= 1 single emblem",
                    delta_explanation=f"FEI regulations restrict collar branding to one single emblem; {len(collar_logos)} were found.",
                    source_citation="Brand manufacturer identification on jackets is restricted to one single emblem on the collar of maximum sixty square centimeters (60 cm²).",
                    source_rulebook="FEI Dressage Rules, Art. 427.3.1" if discipline_val == "DRESSAGE" else "FEI Jumping Rules, Art. 256.3.1",
                    remedy_suggestion="Remove secondary collar emblems to ensure only one emblem is placed on the collar.",
                    page_number=1,
                )
            )

        chest_logos = [logo for logo in spec.logos if "chest" in logo.location.lower() or "pocket" in logo.location.lower()]
        if len(chest_logos) > 1:
            findings.append(
                AuditFinding(
                    finding_id="det_logo_chest_count_violation",
                    rule_id="FEI-JUMP-LOGO-CHEST",
                    category=FindingCategory.BRANDING_LOGO,
                    severity=ComplianceStatus.VIOLATION,
                    title="Multiple Chest Logos Exceed Single Side Limit",
                    observed_value=f"{len(chest_logos)} chest/pocket logos specified",
                    allowed_threshold="<= 1 chest/pocket logo on one side only",
                    delta_explanation=f"FEI regulations permit chest logo on one side only; {len(chest_logos)} were found.",
                    source_citation="A sponsor or manufacturer logo may appear on the chest/pocket area of the competition jacket on one side only. The total surface area of this logo must not exceed two hundred square centimeters (200 cm²).",
                    source_rulebook="FEI Jumping Rules, Art. 256.3.2",
                    remedy_suggestion="Remove secondary chest or pocket emblems so identification appears on one side only.",
                    page_number=1,
                )
            )

        # 2. Piping Width Check
        if spec.aesthetic.piping_present and spec.aesthetic.piping_width_mm:
            width = spec.aesthetic.piping_width_mm
            limit = 4.0 if discipline_val == "DRESSAGE" else 3.5
            if width > limit:
                delta = round(width - limit, 2)
                findings.append(
                    AuditFinding(
                        finding_id="det_aesthetic_piping",
                        rule_id="FEI-DRESS-PIPING-WIDTH" if discipline_val == "DRESSAGE" else "BRAND-SOP-PIPING-01",
                        category=FindingCategory.AESTHETICS,
                        severity=ComplianceStatus.VIOLATION if discipline_val == "DRESSAGE" else ComplianceStatus.WARNING,
                        title="Contrast Piping Width Exceeds Prescribed Limit",
                        observed_value=f"{width:.1f} mm",
                        allowed_threshold=f"<= {limit:.1f} mm",
                        delta_explanation=f"Observed piping width is {delta:+.1f} mm wider than permissible maximum.",
                        source_citation="Subtle contrast piping along the collar, lapels, and pockets is permitted, provided the piping width does not exceed four millimeters (4 mm)." if discipline_val == "DRESSAGE" else "Contrast piping on lapels or collar must not exceed 3.5 mm width to maintain subtle understated luxury.",
                        source_rulebook="FEI Dressage Rules, Art. 427.1.4" if discipline_val == "DRESSAGE" else "Maison Équestre Brand SOP, Sec. 4",
                        remedy_suggestion=f"Reduce piping cord to <= {limit:.1f} mm.",
                        page_number=1,
                    )
                )

        # 3. Financial & Costing Check
        actual_fob = spec.costing.actual_fob_usd
        target_fob = spec.costing.target_fob_usd
        if actual_fob > 0 and target_fob > 0:
            cogs_ceiling = 65.0
            if spec.metadata.garment_type == GarmentType.TAILCOAT:
                cogs_ceiling = 95.0
            elif spec.metadata.garment_type == GarmentType.COMPETITION_SHIRT:
                cogs_ceiling = 28.0

            if actual_fob > cogs_ceiling:
                delta = round(actual_fob - cogs_ceiling, 2)
                findings.append(
                    AuditFinding(
                        finding_id="det_cogs_ceiling_exceeded",
                        rule_id="BRAND-SOP-COGS-01",
                        category=FindingCategory.COSTING_FOB,
                        severity=ComplianceStatus.VIOLATION,
                        title="Actual Quoted FOB Exceeds Brand Hard Cost Ceiling",
                        observed_value=f"${actual_fob:.2f} USD",
                        allowed_threshold=f"<= ${cogs_ceiling:.2f} USD",
                        delta_explanation=f"Actual FOB is +${delta:.2f} USD over the hard financial ceiling.",
                        source_citation="Maximum Target FOB is $55.00 USD. Hard ceiling is $65.00 USD. Any tech pack with actual FOB exceeding $65.00 USD is marked as a critical financial violation.",
                        source_rulebook="Maison Équestre Quality SOP, Sec. 1",
                        remedy_suggestion="Renegotiate CMT production fees or alter outer shell sourcing to reduce FOB below $65.00 USD.",
                        page_number=1,
                    )
                )
            elif actual_fob > target_fob * 1.05:
                delta = round(actual_fob - target_fob, 2)
                findings.append(
                    AuditFinding(
                        finding_id="det_cogs_target_warning",
                        rule_id="BRAND-SOP-COGS-01",
                        category=FindingCategory.COSTING_FOB,
                        severity=ComplianceStatus.WARNING,
                        title="Actual FOB Exceeds Target Costing Ceiling by > 5%",
                        observed_value=f"${actual_fob:.2f} USD",
                        allowed_threshold=f"<= ${target_fob:.2f} USD",
                        delta_explanation=f"Quoted FOB is +${delta:.2f} USD (+{round(delta/target_fob*100, 1)}%) above commercial target.",
                        source_citation="Target FOB cost target for show coat production.",
                        source_rulebook="Maison Équestre Quality SOP, Sec. 1",
                        remedy_suggestion="Review bill of materials and trim costs with vendor to achieve target margin.",
                        page_number=1,
                    )
                )

        # 4. Fabric Performance Minimums
        if spec.fabric.breathability_g_m2_24h is not None and spec.fabric.breathability_g_m2_24h < 10000.0:
            findings.append(
                AuditFinding(
                    finding_id="det_fabric_breathability",
                    rule_id="BRAND-SOP-FABRIC-01",
                    category=FindingCategory.FABRIC_PERFORMANCE,
                    severity=ComplianceStatus.WARNING,
                    title="Fabric Breathability (WVTR) Below Brand Performance Minimum",
                    observed_value=f"{spec.fabric.breathability_g_m2_24h:.0f} g/m²/24h",
                    allowed_threshold=">= 10000 g/m²/24h",
                    delta_explanation=f"Fabric moisture transmission is {10000.0 - spec.fabric.breathability_g_m2_24h:.0f} g/m²/24h below technical minimum.",
                    source_citation="All primary performance fabrics for competition show jackets and tailcoats must achieve a water vapor transmission rate (breathability) of at least 10,000 g/m²/24h.",
                    source_rulebook="Maison Équestre Quality SOP, Sec. 2",
                    remedy_suggestion="Specify technical micro-porous membrane or high-gauge knit achieving >= 10,000 g/m²/24h.",
                    page_number=1,
                )
            )

        # 5. Collar Height Tolerance Check
        collar_pom = next((item for item in spec.measurements if "collar" in item.description.lower()), None)
        if collar_pom and collar_pom.tolerance_plus_minus_cm > 0.5:
            findings.append(
                AuditFinding(
                    finding_id="det_tol_collar_stand",
                    rule_id="BRAND-SOP-TOL-01",
                    category=FindingCategory.TAILORING_MEASUREMENTS,
                    severity=ComplianceStatus.WARNING,
                    title="Collar Stand Production Tolerance Wider Than Luxury Standard",
                    observed_value=f"+/- {collar_pom.tolerance_plus_minus_cm:.2f} cm",
                    allowed_threshold="<= +/- 0.50 cm",
                    delta_explanation=f"Tolerance is +/- {collar_pom.tolerance_plus_minus_cm - 0.5:.2f} cm looser than acceptable tailoring tolerance.",
                    source_citation="Production tolerance for collar stand height must not exceed +/- 0.5 cm from the graded specification.",
                    source_rulebook="Maison Équestre Quality SOP, Sec. 3",
                    remedy_suggestion="Tighten collar stand grading tolerance to +/- 0.5 cm on production POM chart.",
                    page_number=1,
                )
            )

        elapsed = time.time() - start_time
        logger.debug("Layer 1 deterministic evaluation completed in %.4fs with %d findings", elapsed, len(findings))
        return findings


deterministic_engine = DeterministicEngine()
