# Ticket: TICK-0703
## Scorecard Query & History Endpoints

- **Ticket ID**: `TICK-0703`
- **Stage**: Stage 7: FastAPI Backend & API Integration
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0702`

---

### Description
Implement query endpoints in `backend/app/api/audit_router.py`:
- `GET /api/audit/{id}`: Retrieves existing scorecard, structured tech pack specs, and figure URLs by audit UUID.
- `GET /api/audit/{id}/pdf`: Serves the raw PDF for the in-browser PDF viewer.
- `GET /api/audit/history`: Returns recent audit runs with thumbnail metadata and compliance status for executive dashboards.

### Subtasks
- [x] Implement `GET /api/audit/{id}` returning full audit data.
- [x] Implement `GET /api/audit/{id}/pdf` with `FileResponse` supporting HTTP range requests for smooth PDF streaming.
- [x] Implement `GET /api/audit/history` listing historical audits with timestamps and pass/fail stats.
- [x] Handle 404 Not Found for non-existent IDs.

### AI Testing Plan
- Test retrieval of created audit by ID.
- Test PDF byte-streaming response.
- Test 404 handling.

### Human Review Checklist
- [ ] Test PDF streaming with browser client.
- [ ] Confirm audit history lists recent audits in chronological order.

### Work Log & Evidence
- Status: `[TESTED_BY_AI]`
- Automated tests in `backend/tests/test_api_endpoints.py`:
  - `test_upload_and_audit_pdf`: PASSED (verified GET by ID, history list, and PDF streaming).
  - `test_get_nonexistent_audit`: PASSED (asserts 404 on invalid audit ID).
