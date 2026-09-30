# Ticket: TICK-0705
## Regulatory Catalog & Brand SOP Inspection Endpoints

- **Ticket ID**: `TICK-0705`
- **Stage**: Stage 7: FastAPI Backend & API Integration
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0403`, `TICK-0701`

---

### Description
Implement reference inspection endpoints in `backend/app/api/rules_router.py`:
- `GET /api/rules`: Lists all codified rules in the structured catalog with discipline and category filters.
- `GET /api/rules/{id}`: Returns the complete rule definition, source text excerpt, and applicable disciplines.
- `POST /api/rules/search`: Performs ad-hoc hybrid semantic search across the FEI regulation and Brand SOP knowledge base.

### Subtasks
- [x] Implement `GET /api/rules` with query filters (`discipline`, `category`).
- [x] Implement `GET /api/rules/{id}` returning specific rule details.
- [x] Implement `POST /api/rules/search` exposing the hybrid retriever for user reference queries.

### AI Testing Plan
- Test rules listing endpoint: verify all catalog rules are returned.
- Test ad-hoc rule search: verify query for "Jumping collar" returns relevant FEI Article 256 chunks.

### Human Review Checklist
- [ ] Review API responses for clarity and metadata completeness.
- [ ] Verify search endpoint accurately handles user queries.

### Work Log & Evidence
- Status: `[TESTED_BY_AI]`
- Automated tests in `backend/tests/test_api_endpoints.py`:
  - `test_rules_catalog_endpoints`: PASSED (verified rules listing, discipline filtering, ID lookup, and hybrid semantic search).
