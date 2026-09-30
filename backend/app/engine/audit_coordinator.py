"""Audit Coordinator orchestrating Layer 1 deterministic and Layer 2 semantic compliance engines."""
import asyncio
import logging
import time

from backend.app.engine.deterministic_engine import DeterministicEngine, deterministic_engine
from backend.app.engine.semantic_reasoner import SemanticReasoner, semantic_reasoner
from backend.app.models.audit import (
    AuditFinding,
    CategoryScore,
    FindingCategory,
    PreliminaryAuditReport,
)
from backend.app.models.tech_pack import ComplianceStatus, TechPackSpec
from backend.app.rag.retriever import HybridRetriever, retriever

logger = logging.getLogger(__name__)

SEVERITY_ORDER = {
    ComplianceStatus.VIOLATION: 1,
    ComplianceStatus.WARNING: 2,
    ComplianceStatus.MANUAL_REVIEW: 3,
    ComplianceStatus.PASS: 4,
}

CORE_CATEGORIES = [
    FindingCategory.BRANDING_LOGO,
    FindingCategory.AESTHETICS,
    FindingCategory.FABRIC_PERFORMANCE,
    FindingCategory.COSTING_FOB,
    FindingCategory.TAILORING_MEASUREMENTS,
]


class AuditCoordinator:
    """Coordinates dual-layer compliance audit with asynchronous execution and findings deduplication."""

    def __init__(
        self,
        deterministic: DeterministicEngine | None = None,
        semantic: SemanticReasoner | None = None,
        rule_retriever: HybridRetriever | None = None,
    ):
        self.deterministic = deterministic or deterministic_engine
        self.semantic = semantic or semantic_reasoner
        self.retriever = rule_retriever or retriever

    def _deduplicate_findings(
        self,
        layer1_findings: list[AuditFinding],
        layer2_findings: list[AuditFinding],
    ) -> list[AuditFinding]:
        """Merge Layer 1 and Layer 2 findings, prioritizing Layer 1 deterministic findings on overlap."""
        seen_rules: set[str] = {f.rule_id for f in layer1_findings if f.rule_id}
        merged: list[AuditFinding] = list(layer1_findings)

        for finding in layer2_findings:
            if finding.rule_id in seen_rules:
                logger.debug(
                    "Deduplicating semantic finding %s; covered by deterministic rule %s",
                    finding.finding_id,
                    finding.rule_id,
                )
                continue
            merged.append(finding)

        merged.sort(key=lambda f: SEVERITY_ORDER.get(f.severity, 99))
        return merged

    def _compute_category_scores(self, findings: list[AuditFinding]) -> list[CategoryScore]:
        """Compute category compliance breakdown and scores."""
        scores: list[CategoryScore] = []

        for category in CORE_CATEGORIES:
            cat_findings = [f for f in findings if f.category == category]
            issue_count = len(cat_findings)
            violations = sum(1 for f in cat_findings if f.severity == ComplianceStatus.VIOLATION)
            warnings = sum(1 for f in cat_findings if f.severity == ComplianceStatus.WARNING)

            if violations > 0:
                status = ComplianceStatus.VIOLATION
                score = max(0.0, 100.0 - (violations * 50.0 + warnings * 20.0))
            elif warnings > 0:
                status = ComplianceStatus.WARNING
                score = max(40.0, 100.0 - (warnings * 25.0))
            else:
                status = ComplianceStatus.PASS
                score = 100.0

            scores.append(
                CategoryScore(
                    category_name=category,
                    status=status,
                    compliance_score_pct=round(score, 1),
                    issue_count=issue_count,
                )
            )

        return scores

    def _compute_overall_status(self, findings: list[AuditFinding]) -> ComplianceStatus:
        """Derive highest-precedence compliance status across all findings."""
        if any(f.severity == ComplianceStatus.VIOLATION for f in findings):
            return ComplianceStatus.VIOLATION
        if any(f.severity == ComplianceStatus.WARNING for f in findings):
            return ComplianceStatus.WARNING
        if any(f.severity == ComplianceStatus.MANUAL_REVIEW for f in findings):
            return ComplianceStatus.MANUAL_REVIEW
        return ComplianceStatus.PASS

    async def run_audit_async(self, spec: TechPackSpec) -> PreliminaryAuditReport:
        """Run Layer 1 deterministic and Layer 2 semantic audits concurrently."""
        start_time = time.time()

        async def _run_layer1() -> list[AuditFinding]:
            return self.deterministic.audit(spec)

        async def _run_layer2() -> list[AuditFinding]:
            try:
                rule_chunks = self.retriever.retrieve_rules_for_techpack(spec, top_k=6)
                return await self.semantic.audit_async(spec, rule_chunks)
            except Exception as exc:
                logger.error("Layer 2 semantic reasoning failed (%s); proceeding with Layer 1", exc)
                return []

        results = await asyncio.gather(_run_layer1(), _run_layer2(), return_exceptions=True)

        layer1_findings = results[0] if isinstance(results[0], list) else []
        layer2_findings = results[1] if isinstance(results[1], list) else []

        if isinstance(results[0], Exception):
            logger.error("Layer 1 deterministic audit encountered error: %s", results[0])
        if isinstance(results[1], Exception):
            logger.error("Layer 2 semantic audit encountered error: %s", results[1])

        merged_findings = self._deduplicate_findings(layer1_findings, layer2_findings)
        category_scores = self._compute_category_scores(merged_findings)
        overall_status = self._compute_overall_status(merged_findings)

        overall_score = (
            round(sum(c.compliance_score_pct for c in category_scores) / len(category_scores), 1)
            if category_scores
            else 100.0
        )

        elapsed = round(time.time() - start_time, 4)
        logger.info(
            "Preliminary audit completed for %s in %.3fs with status %s (%d findings)",
            spec.metadata.style_code,
            elapsed,
            overall_status,
            len(merged_findings),
        )

        return PreliminaryAuditReport(
            tech_pack_id=f"TP-{spec.metadata.style_code}",
            style_code=spec.metadata.style_code,
            style_name=spec.metadata.style_name,
            discipline=spec.metadata.discipline,
            garment_type=spec.metadata.garment_type,
            overall_status=overall_status,
            overall_score_pct=overall_score,
            execution_time_seconds=elapsed,
            category_scores=category_scores,
            findings=merged_findings,
        )

    def run_audit(self, spec: TechPackSpec) -> PreliminaryAuditReport:
        """Synchronous wrapper for run_audit_async."""
        try:
            return asyncio.run(self.run_audit_async(spec))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.run_audit_async(spec))


audit_coordinator = AuditCoordinator()
