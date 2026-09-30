# Ticket: TICK-0602
## Audit Scorecard Model & Visual Status Aggregator

- **Ticket ID**: `TICK-0602`
- **Stage**: Stage 6: Verifier Gate & Vendor Action Generator
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0601`

---

### Description
Implement the final scorecard generator in `backend/app/engine/scorecard_generator.py`. This module packages verified findings into the user-facing `AuditScorecard` model with category summaries (Branding/Logo, Fabric, Costing, Aesthetics, Measurements), executive compliance scores (0–100%), and page-level source references for split-screen navigation.

### Subtasks
- [x] Implement `ScorecardGenerator.generate(tech_pack_id: str, verified_findings: List[VerifiedFinding], spec: TechPackSpec) -> AuditScorecard`.
- [x] Calculate category sub-scores:
  - Branding Compliance (0-100%)
  - Fabric & Performance Compliance (0-100%)
  - Costing & BOM Compliance (0-100%)
  - Aesthetic & Tailoring Compliance (0-100%)
- [x] Attach page coordinates and sketch image references to each finding for UI linking.
- [x] Output clean JSON representation ready for frontend ingestion.

### AI Testing Plan
- Test scorecard generation on 3 test audit scenarios (Full Pass, Minor Warnings, Severe Violations).
- Assert all sub-scores compute properly and JSON serializes without error.

### Human Review Checklist
- [ ] Review scorecard layout and executive summary readability.
- [ ] Verify category compliance score calculation logic.

### Work Log & Evidence
- Status: `[TESTED_BY_AI]`
- Automated tests in `backend/tests/test_verifier_and_actions.py`:
  - `test_scorecard_generator`: PASSED (verified scorecard compilation, 5 category scores, overall score calculation).
