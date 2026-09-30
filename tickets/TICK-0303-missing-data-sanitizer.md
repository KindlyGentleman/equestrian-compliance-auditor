# Ticket: TICK-0303
## Missing Data Sanitizer & Unit Normalizer

- **Ticket ID**: `TICK-0303`
- **Stage**: Stage 3: Pydantic Schema Structuring & Modeling
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0301`

---

### Description
Implement a post-extraction sanitizer in `backend/app/engine/sanitizer.py`. Tech packs from different garment vendors often mix measurement units (inches vs cm, ounces/yd² vs GSM) or omit optional fields. This module normalizes units, flags missing critical specs, and handles edge cases before sending data to the audit engine.

### Subtasks
- [x] Implement unit converter: inches to centimeters, ounces/yd² to GSM, mm to cm.
- [x] Implement fiber composition normalizer (converting `Elastane`, `Spandex`, `Lycra`, `EA` into standardized canonical fiber names).
- [x] Add completeness scoring: flag whether required audit fields (collar height, logo dimensions, FOB, fabric composition) are present or missing.
- [x] Annotate missing specs with explicit warning tags (`MISSING_SPEC`) rather than allowing silent `None` failures.

### AI Testing Plan
- Test unit conversions against known imperial test fixtures.
- Test incomplete tech pack payload: assert missing specs are accurately flagged with `MISSING_SPEC` warnings.

### Human Review Checklist
- [ ] Review unit conversion factors for accuracy.
- [ ] Verify handling of incomplete tech packs does not crash downstream audit stages.

### Work Log & Evidence
- Status changed from `[BACKLOG]` to `[TESTED_BY_AI]`.
- Implemented `backend/app/engine/sanitizer.py` with `TechPackSanitizer`, `SanitizerReport`, and `SanitizedTechPack`.
- Verified in `backend/tests/test_structuring.py::test_sanitizer_unit_conversions` and `test_sanitizer_missing_specs_audit`.
