"""Layer 2 Semantic Reasoner evaluating qualitative and aesthetic compliance using Gemini 2.0 Flash."""
import json
import logging
import time
from typing import List, Optional

from google.genai import types
from pydantic import BaseModel, Field

from backend.app.core.config import settings
from backend.app.core.gemini_client import gemini_wrapper
from backend.app.models.audit import AuditFinding, FindingCategory
from backend.app.models.tech_pack import ComplianceStatus, Discipline, GarmentType, TechPackSpec
from backend.app.rag.vector_store import RuleChunk

logger = logging.getLogger(__name__)

SEMANTIC_REASONER_SYSTEM = """
You are a Principal Equestrian Apparel Compliance Auditor for Olympic competitions (FEI) and luxury fashion.
Evaluate the aesthetic, stylistic, and qualitative features of the provided garment tech pack against the provided regulation excerpts.

STRICT GROUNDING & ZERO FALSE POSITIVES:
1. You may ONLY flag a finding if you can cite the exact verbatim sentence from the provided regulation excerpts.
2. If an aesthetic feature is NOT explicitly prohibited in the regulation text, it is COMPLIANT. Do not invent prohibitions.
3. Contrast velvet collars, lapel piping (<= 4mm), and metal monogram buttons are permitted under FEI Dressage Art 427 and Jumping Art 256.
4. Output your findings strictly matching the SemanticFindingsPayload schema.
"""


class SemanticFindingsPayload(BaseModel):
    findings: List[AuditFinding] = Field(default_factory=list)


class SemanticReasoner:
    """Evaluates qualitative apparel regulations using grounded LLM semantic reasoning."""

    def __init__(self, client_wrapper=None):
        self.gemini = client_wrapper or gemini_wrapper

    def _mock_semantic_eval(self, spec: TechPackSpec, rules: List[RuleChunk]) -> List[AuditFinding]:
        """Deterministic heuristic evaluation for offline testing."""
        findings: List[AuditFinding] = []
        discipline_val = spec.metadata.discipline.value if isinstance(spec.metadata.discipline, Discipline) else str(spec.metadata.discipline)

        # Rule check: Prohibited neon/bright colors in Dressage
        contrast_color = (spec.aesthetic.collar_contrast_color or "").lower()
        if discipline_val == "DRESSAGE" and any(bad in contrast_color for bad in ["neon", "fluorescent", "bright yellow", "hot pink"]):
            findings.append(
                AuditFinding(
                    finding_id="sem_dress_collar_color",
                    rule_id="FEI-DRESS-COLOR-COLLAR",
                    category=FindingCategory.AESTHETICS,
                    severity=ComplianceStatus.VIOLATION,
                    title="Non-Conservative High-Contrast Collar Color in Dressage",
                    observed_value=f"Collar Contrast: {spec.aesthetic.collar_contrast_color}",
                    allowed_threshold="Conservative tones complementing jacket",
                    delta_explanation="Bright, non-conservative colors on collar trim are strictly forbidden in CDI competition.",
                    source_citation="Extreme neon colors or distracting multi-color patterns are strictly prohibited.",
                    source_rulebook="FEI Dressage Rules, Art. 427.1.3",
                    remedy_suggestion="Change collar trim to black velvet, navy satin, or matching tonal self-fabric.",
                    page_number=1,
                )
            )

        # Rule check: Sleeveless shirt prohibited
        if spec.metadata.garment_type == GarmentType.COMPETITION_SHIRT and "sleeveless" in str(spec).lower():
            findings.append(
                AuditFinding(
                    finding_id="sem_shirt_sleeveless",
                    rule_id="FEI-DRESS-SHIRT-SLEEVE",
                    category=FindingCategory.AESTHETICS,
                    severity=ComplianceStatus.VIOLATION,
                    title="Sleeveless Competition Shirt Prohibited in Competition Arena",
                    observed_value="Sleeveless silhouette",
                    allowed_threshold="Short or long sleeves mandatory",
                    delta_explanation="Sleeveless shirts are banned under FEI regulations even in extreme heat exemptions.",
                    source_citation="Shirts must have sleeves. Short sleeves or long sleeves are permitted. Sleeveless shirts are strictly prohibited in the competition arena even when riding without a jacket.",
                    source_rulebook="FEI Dressage Rules, Art. 427.2.3",
                    remedy_suggestion="Update pattern to cap sleeve or short sleeve with finished rib or hem.",
                    page_number=1,
                )
            )

        return findings

    async def audit_async(
        self,
        spec: TechPackSpec,
        relevant_rules: List[RuleChunk],
    ) -> List[AuditFinding]:
        """Perform semantic audit using Gemini 2.0 Flash or deterministic fallback."""
        start_time = time.time()

        if not self.gemini.use_mock and self.gemini.client is not None:
            try:
                # Format context
                rule_context = "\n\n".join(
                    f"[{c.rulebook} - {c.article_id}]: {c.title}\n{c.content}"
                    for c in relevant_rules
                )
                prompt = (
                    f"Evaluate this garment for qualitative compliance:\n\n"
                    f"GARMENT SPECIFICATION:\n"
                    f"- Style: {spec.metadata.style_name} ({spec.metadata.style_code})\n"
                    f"- Discipline: {spec.metadata.discipline}\n"
                    f"- Garment Type: {spec.metadata.garment_type}\n"
                    f"- Collar: {spec.aesthetic.collar_type} (Contrast: {spec.aesthetic.collar_contrast_color})\n"
                    f"- Piping: {spec.aesthetic.piping_present} ({spec.aesthetic.piping_width_mm} mm)\n"
                    f"- Buttons: {spec.aesthetic.button_count} ({spec.aesthetic.button_material})\n\n"
                    f"REGULATION EXCERPTS:\n{rule_context}"
                )

                parsed = await self.gemini.generate_structured(
                    prompt=prompt,
                    response_schema=SemanticFindingsPayload,
                    system_instruction=SEMANTIC_REASONER_SYSTEM,
                )
                if isinstance(parsed, SemanticFindingsPayload):
                    return parsed.findings
                if isinstance(parsed, dict) and "findings" in parsed:
                    return [AuditFinding.model_validate(f) for f in parsed["findings"]]
            except Exception as exc:
                logger.warning("Gemini live semantic audit call failed (%s); reverting to heuristic", exc)

        return self._mock_semantic_eval(spec, relevant_rules)

    def audit(self, spec: TechPackSpec, relevant_rules: List[RuleChunk]) -> List[AuditFinding]:
        """Synchronous wrapper for audit_async."""
        import asyncio
        try:
            return asyncio.run(self.audit_async(spec, relevant_rules))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.audit_async(spec, relevant_rules))


semantic_reasoner = SemanticReasoner()
