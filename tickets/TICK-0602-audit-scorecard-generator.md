# Ticket: TICK-0602
## Audit Scorecard Model & Visual Status Aggregator

- **Ticket ID**: `TICK-0602`
- **Stage**: Stage 6: Verifier Gate & Vendor Action Generator
- **Status**: `[BACKLOG]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0601`

---

### Description
Implement the final scorecard generator in `backend/app/engine/scorecard_generator.py`. This module packages verified findings into the user-facing `AuditScorecard` model with category summaries (Branding/Logo, Fabric, Costing, Aesthetics, Measurements), executive compliance scores (0–100%), and page-level source references for split-screen navigation.

### Subtasks
- [ ] Implement `ScorecardGenerator.generate(tech_pack_id: str, verified_findings: List[VerifiedFinding], spec: TechPackSpec) -> AuditScorecard`.
- [ ] Calculate category sub-scores:
  - Branding Compliance (0-100%)
  - Fabric & Performance Compliance (0-100%)
  - Costing & BOM Compliance (0-100%)
  - Aesthetic & Tailoring Compliance (0-100%)
- [ ] Attach page coordinates and sketch image references to each finding for UI linking.
- [ ] Output clean JSON representation ready for frontend ingestion.

### AI Testing Plan
- Test scorecard generation on 3 test audit scenarios (Full Pass, Minor Warnings, Severe Violations).
- Assert all sub-scores compute properly and JSON serializes without error.

### Human Review Checklist
- [ ] Review scorecard layout and executive summary readability.
- [ ] Verify category compliance score calculation logic.

### Work Log & Evidence
- Status: `[BACKLOG]`
