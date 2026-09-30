# Ticket: TICK-0403
## Pre-compiled Structured Quantitative Rule Catalog

- **Ticket ID**: `TICK-0403`
- **Stage**: Stage 4: Regulatory Knowledge Base & RAG
- **Status**: `[BACKLOG]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0401`, `TICK-0402`

---

### Description
Implement the pre-compiled structured rule catalog in `backend/app/data/rules_catalog.json`. This catalog codifies all quantitative, mathematically evaluable constraints (area limits, tolerances, cost caps, performance metrics) with exact numeric thresholds, comparison operators (`<=`, `>=`, `==`, `in_range`), units, and canonical source citations. This is the backbone of Layer 1 (Deterministic) compliance, guaranteeing 0% hallucinations.

### Subtasks
- [ ] Define JSON schema for rule entries:
  - `rule_id`: String (e.g. `FEI-JUMP-LOGO-COLLAR`)
  - `source`: FEI or Brand
  - `discipline`: Jumping, Dressage, Eventing, or ALL
  - `target_field`: Path in `TechPackSpec` (e.g. `branding.logos[location=collar].calculated_area_cm2`)
  - `operator`: `<=`, `>=`, `==`, `range`
  - `threshold`: Float or string
  - `unit`: `cm2`, `cm`, `usd`, `gsm`
  - `severity_if_violated`: `VIOLATION` or `WARNING`
  - `verbatim_citation`: Official text excerpt
  - `remedy_template`: Actionable revision advice
- [ ] Codify all quantitative FEI and Brand rules into `rules_catalog.json`.

### AI Testing Plan
- Validate `rules_catalog.json` syntax and schema with a Pydantic validator.
- Ensure all rule IDs are unique and all target fields exist on `TechPackSpec`.

### Human Review Checklist
- [ ] Verify quantitative thresholds against the official FEI guidelines.
- [ ] Confirm severity rankings (e.g., Logo over 60cm² is an immediate competition `VIOLATION`, not just a warning).

### Work Log & Evidence
- Status: `[BACKLOG]`
