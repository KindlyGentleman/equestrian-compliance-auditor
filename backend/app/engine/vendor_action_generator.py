"""Automated Vendor Action Generator synthesizing supplier revision notes and email drafts."""
import logging
from datetime import UTC, datetime

from backend.app.models.audit import (
    AuditScorecard,
    FindingCategory,
    VendorRevisionDocument,
    VendorRevisionItem,
    VerifiedFinding,
)
from backend.app.models.tech_pack import ComplianceStatus

logger = logging.getLogger(__name__)


class VendorActionGenerator:
    """Generates structured revision notes, markdown reports, and email drafts for suppliers."""

    def _determine_target_team(self, finding: VerifiedFinding) -> str:
        """Route finding to the responsible vendor or atelier team."""
        cat = finding.category
        title_lower = finding.title.lower()

        if cat == FindingCategory.BRANDING_LOGO:
            return "Embroidery & Trim Supplier"
        if cat == FindingCategory.COSTING_FOB:
            return "Sourcing & Commercial Lead"
        if cat == FindingCategory.FABRIC_PERFORMANCE:
            return "Fabric Mill & Materials Lab"
        if cat == FindingCategory.TAILORING_MEASUREMENTS:
            return "Pattern Maker & Sample Room"
        if cat == FindingCategory.AESTHETICS:
            if "piping" in title_lower or "seam" in title_lower:
                return "Pattern Maker & Sample Room"
            if "button" in title_lower or "embellishment" in title_lower:
                return "Embroidery & Trim Supplier"
            return "Design & Production Team"

        return "Production & Quality Assurance"

    def _determine_component_name(self, finding: VerifiedFinding) -> str:
        """Extract succinct component name from finding."""
        if "collar" in finding.title.lower():
            return "Collar Construction & Stand"
        if "chest" in finding.title.lower():
            return "Chest Emblem Placement"
        if "sleeve" in finding.title.lower():
            return "Sleeve Identification"
        if "piping" in finding.title.lower():
            return "Lapel & Collar Piping Trim"
        if "fob" in finding.title.lower() or "cost" in finding.title.lower():
            return "Unit Costing (FOB / CMT)"
        if "breathability" in finding.title.lower() or "fabric" in finding.title.lower():
            return "Shell Performance Fabric"
        if "tolerance" in finding.title.lower():
            return "Grading & POM Tolerances"
        return finding.title

    def generate_notes(self, scorecard: AuditScorecard) -> VendorRevisionDocument:
        """Generate structured action items, markdown report, and email draft."""
        action_items: list[VendorRevisionItem] = []

        # Only create action items for non-PASS findings
        actionable_findings = [
            f for f in scorecard.findings if f.severity in (ComplianceStatus.VIOLATION, ComplianceStatus.WARNING, ComplianceStatus.MANUAL_REVIEW)
        ]

        for finding in actionable_findings:
            target_team = self._determine_target_team(finding)
            component = self._determine_component_name(finding)
            current_issue = (
                f"{finding.title}. Observed: {finding.observed_value} "
                f"(Allowed: {finding.allowed_threshold}). {finding.delta_explanation}"
            )
            required_action = finding.remedy_suggestion
            citation_ref = f"{finding.source_rulebook} ({finding.rule_id})"

            action_items.append(
                VendorRevisionItem(
                    target_team=target_team,
                    component=component,
                    current_issue=current_issue,
                    required_action=required_action,
                    citation_reference=citation_ref,
                )
            )

        # Generate Markdown Document
        today_str = datetime.now(UTC).strftime("%Y-%m-%d")
        md_lines = [
            f"# Technical Package Revision Request: {scorecard.style_name} ({scorecard.style_code})",
            f"**Audit Status:** {scorecard.overall_status.value} | **Compliance Score:** {scorecard.overall_score_pct}% | **Date:** {today_str}",
            "",
            "## Executive Summary",
            f"Technical compliance review for style {scorecard.style_code} ({scorecard.garment_type.value}, {scorecard.discipline.value}) "
            f"identified {len(actionable_findings)} specification item(s) requiring immediate supplier correction before production sign-off.",
            "",
            "## Required Action Items by Department",
            "",
        ]

        # Group by target team
        teams: dict[str, list[VendorRevisionItem]] = {}
        for item in action_items:
            teams.setdefault(item.target_team, []).append(item)

        if not teams:
            md_lines.append("No technical revisions required. Specification approved for production sampling.")
        else:
            for team, items in teams.items():
                md_lines.append(f"### {team}")
                for idx, item in enumerate(items, start=1):
                    md_lines.append(f"#### {idx}. {item.component}")
                    md_lines.append(f"- **Issue:** {item.current_issue}")
                    md_lines.append(f"- **Required Action:** {item.required_action}")
                    md_lines.append(f"- **Regulatory Reference:** {item.citation_reference}")
                    md_lines.append("")

        markdown_content = "\n".join(md_lines)

        # Generate Clean Professional Plain-Text Email Draft
        email_lines = [
            f"Subject: Revision Required: Technical Specification for Style {scorecard.style_code} ({scorecard.style_name})",
            "",
            "Dear Partner,",
            "",
            f"The compliance review for technical specification {scorecard.style_code} ({scorecard.style_name}) has concluded.",
            f"Current Compliance Status: {scorecard.overall_status.value} ({scorecard.overall_score_pct}%).",
            "",
            "Please apply the following technical revisions prior to the next sample submission:",
            "",
        ]

        for idx, item in enumerate(action_items, start=1):
            email_lines.append(f"{idx}. [{item.target_team}] {item.component}")
            email_lines.append(f"   Issue: {item.current_issue}")
            email_lines.append(f"   Action Required: {item.required_action}")
            email_lines.append(f"   Reference: {item.citation_reference}")
            email_lines.append("")

        email_lines.append("Please confirm receipt and provide an updated tech pack and revised POM chart within 48 hours.")
        email_lines.append("")
        email_lines.append("Technical Quality & Compliance Team")
        email_lines.append("Maison Équestre Technical Sportswear")

        email_draft_content = "\n".join(email_lines)

        return VendorRevisionDocument(
            tech_pack_id=scorecard.tech_pack_id,
            style_code=scorecard.style_code,
            style_name=scorecard.style_name,
            generated_date=today_str,
            summary=f"{len(action_items)} revision item(s) generated across {len(teams)} department(s).",
            action_items=action_items,
            markdown_content=markdown_content,
            email_draft_content=email_draft_content,
        )


vendor_action_generator = VendorActionGenerator()
