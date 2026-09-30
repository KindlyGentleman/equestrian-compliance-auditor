"""Audit Scorecard Generator aggregating verified findings into structured executive reports."""
import logging
import time
from typing import Dict, List, Optional

from backend.app.models.audit import (
    AuditScorecard,
    CategoryScore,
    FindingCategory,
    VerifiedFinding,
)
from backend.app.models.tech_pack import ComplianceStatus, TechPackSpec

logger = logging.getLogger(__name__)

SCORECARD_CATEGORIES = [
    FindingCategory.BRANDING_LOGO,
    FindingCategory.AESTHETICS,
    FindingCategory.FABRIC_PERFORMANCE,
    FindingCategory.COSTING_FOB,
    FindingCategory.TAILORING_MEASUREMENTS,
]

SEVERITY_WEIGHTS = {
    ComplianceStatus.VIOLATION: 50.0,
    ComplianceStatus.WARNING: 20.0,
    ComplianceStatus.MANUAL_REVIEW: 15.0,
    ComplianceStatus.PASS: 0.0,
}


class ScorecardGenerator:
    """Constructs user-facing AuditScorecard with granular category breakdowns and overall ratings."""

    def _compute_category_scores(self, findings: List[VerifiedFinding]) -> List[CategoryScore]:
        """Compute score percentages and issue tallies per category."""
        scores: List[CategoryScore] = []

        for category in SCORECARD_CATEGORIES:
            cat_findings = [f for f in findings if f.category == category]
            issue_count = len(cat_findings)

            violations = sum(1 for f in cat_findings if f.severity == ComplianceStatus.VIOLATION)
            warnings = sum(1 for f in cat_findings if f.severity == ComplianceStatus.WARNING)
            manual_reviews = sum(1 for f in cat_findings if f.severity == ComplianceStatus.MANUAL_REVIEW)

            if violations > 0:
                cat_status = ComplianceStatus.VIOLATION
                deduction = violations * 50.0 + warnings * 20.0 + manual_reviews * 10.0
                score = max(0.0, 100.0 - deduction)
            elif warnings > 0:
                cat_status = ComplianceStatus.WARNING
                deduction = warnings * 25.0 + manual_reviews * 10.0
                score = max(35.0, 100.0 - deduction)
            elif manual_reviews > 0:
                cat_status = ComplianceStatus.MANUAL_REVIEW
                score = max(60.0, 100.0 - manual_reviews * 15.0)
            else:
                cat_status = ComplianceStatus.PASS
                score = 100.0

            scores.append(
                CategoryScore(
                    category_name=category,
                    status=cat_status,
                    compliance_score_pct=round(score, 1),
                    issue_count=issue_count,
                )
            )

        return scores

    def _determine_overall_status(self, findings: List[VerifiedFinding]) -> ComplianceStatus:
        """Derive highest precedence compliance status across all verified findings."""
        if any(f.severity == ComplianceStatus.VIOLATION for f in findings):
            return ComplianceStatus.VIOLATION
        if any(f.severity == ComplianceStatus.WARNING for f in findings):
            return ComplianceStatus.WARNING
        if any(f.severity == ComplianceStatus.MANUAL_REVIEW for f in findings):
            return ComplianceStatus.MANUAL_REVIEW
        return ComplianceStatus.PASS

    def generate(
        self,
        tech_pack_id: str,
        verified_findings: List[VerifiedFinding],
        spec: TechPackSpec,
        execution_time_seconds: float = 0.0,
    ) -> AuditScorecard:
        """Assemble complete AuditScorecard from verified findings and tech pack specifications."""
        category_scores = self._compute_category_scores(verified_findings)
        overall_status = self._determine_overall_status(verified_findings)

        overall_score = (
            round(sum(c.compliance_score_pct for c in category_scores) / len(category_scores), 1)
            if category_scores
            else 100.0
        )

        # Brief executive summary for notes field
        v_count = sum(1 for f in verified_findings if f.severity == ComplianceStatus.VIOLATION)
        w_count = sum(1 for f in verified_findings if f.severity == ComplianceStatus.WARNING)
        m_count = sum(1 for f in verified_findings if f.severity == ComplianceStatus.MANUAL_REVIEW)

        if overall_status == ComplianceStatus.PASS:
            summary = "Specification is fully compliant with FEI discipline regulations and luxury brand standards."
        else:
            summary = (
                f"Compliance review identified {len(verified_findings)} issue(s): "
                f"{v_count} violation(s), {w_count} warning(s), {m_count} manual review(s). "
                f"Vendor revisions required before technical sign-off."
            )

        scorecard = AuditScorecard(
            tech_pack_id=tech_pack_id,
            style_code=spec.metadata.style_code,
            style_name=spec.metadata.style_name,
            discipline=spec.metadata.discipline,
            garment_type=spec.metadata.garment_type,
            overall_status=overall_status,
            overall_score_pct=overall_score,
            execution_time_seconds=round(execution_time_seconds, 3),
            category_scores=category_scores,
            findings=verified_findings,
            vendor_revision_notes=summary,
        )

        logger.info(
            "AuditScorecard generated for %s: %s (Score: %.1f%%, Findings: %d)",
            spec.metadata.style_code,
            overall_status,
            overall_score,
            len(verified_findings),
        )
        return scorecard


scorecard_generator = ScorecardGenerator()
