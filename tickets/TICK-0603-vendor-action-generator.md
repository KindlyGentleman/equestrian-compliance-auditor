# Ticket: TICK-0603
## Automated Vendor Action Generator

- **Ticket ID**: `TICK-0603`
- **Stage**: Stage 6: Verifier Gate & Vendor Action Generator
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0602`

---

### Description
Implement the supplier communication generator in `backend/app/engine/vendor_action_generator.py` (FR-6). When a tech pack contains non-compliant specifications, this service generates clear, professional, actionable revision notes formatted specifically for garment manufacturers, pattern cutters, and mill suppliers.

### Subtasks
- [x] Implement `VendorActionGenerator.generate_notes(scorecard: AuditScorecard) -> VendorRevisionDocument`.
- [x] Format revision notes with exact technical instructions (e.g. *"Reduce collar logo width from 8.2cm to 6.8cm to achieve total surface area <= 60cm² (FEI Show Jumping Art 256.3)"*).
- [x] Group actions by recipient:
  - Pattern Maker (adjusting measurements/dimensions)
  - Embroidery / Trim Supplier (resizing logos, changing buttons)
  - Fabric Mill (breathability and stretch certifications)
  - Sourcing Lead (FOB price target renegotiation)
- [x] Provide output templates in both Markdown and formatted plain-text email draft.

### AI Testing Plan
- Test generation on a scorecard with 3 mixed violations.
- Verify generated text contains exact numerical targets and actionable instructions.

### Human Review Checklist
- [ ] Review tone of generated notes for professional luxury brand communication.
- [ ] Confirm actionable remedies are realistic for garment production facilities.

### Work Log & Evidence
- Status: `[TESTED_BY_AI]`
- Automated tests in `backend/tests/test_verifier_and_actions.py`:
  - `test_vendor_action_generator`: PASSED (verified action routing across departments, markdown report synthesis, and clean email draft generation).
