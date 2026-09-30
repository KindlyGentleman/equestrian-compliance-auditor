# Ticket: TICK-0403
## Pre-compiled Structured Quantitative Rule Catalog

- **Ticket ID**: `TICK-0403`
- **Stage**: Stage 4: Regulatory Knowledge Base & RAG
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0401`, `TICK-0402`

---

### Description
Implement the pre-compiled structured rule catalog in `backend/app/data/rules_catalog.json`. This catalog codifies all quantitative, mathematically evaluable constraints (area limits, tolerances, cost caps, performance metrics) with exact numeric thresholds, comparison operators (`<=`, `>=`, `==`, `in_range`), units, and canonical source citations. This is the backbone of Layer 1 (Deterministic) compliance, guaranteeing 0% hallucinations.

### Subtasks
- [x] Define JSON schema for rule entries (`rule_id`, `source`, `discipline`, `target_field`, `operator`, `threshold`, `unit`, `severity_if_violated`, `verbatim_citation`, `remedy_template`).
- [x] Codify all quantitative FEI and Brand rules into `rules_catalog.json`.

### AI Testing Plan
- Validate `rules_catalog.json` syntax and schema with automated assertions.
- Ensure all rule IDs are unique and all target fields exist on `TechPackSpec`.

### Human Review Checklist
- [ ] Verify quantitative thresholds against the official FEI guidelines.
- [ ] Confirm severity rankings (e.g. Logo over 60cm² is an immediate competition `VIOLATION`, not just a warning).

### Work Log & Evidence
- Status changed from `[BACKLOG]` to `[TESTED_BY_AI]`.
- Implemented `rules_catalog.json` with 11 quantitative rules spanning Show Jumping, Dressage, Eventing, Fabric, and Costing.
- Verified in `backend/tests/test_rag.py::test_rules_catalog_json_schema`.
