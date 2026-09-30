# Ticket: TICK-0702
## Tech Pack Upload & Audit Execution Endpoint

- **Ticket ID**: `TICK-0702`
- **Stage**: Stage 7: FastAPI Backend & API Integration
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0701`, `TICK-0604`

---

### Description
Implement the primary audit endpoint in `backend/app/api/audit_router.py`: `POST /api/audit/upload`. This endpoint accepts multipart PDF file uploads, validates file format and size (< 50MB), triggers the end-to-end ingestion and dual-layer audit pipeline asynchronously, and returns the comprehensive `AuditScorecard`.

### Subtasks
- [x] Implement `POST /api/audit/upload` accepting `UploadFile`.
- [x] Save uploaded PDF to secure transient storage with unique UUID.
- [x] Trigger `IngestionPipeline`, `StructuringService`, and `AuditCoordinator`.
- [x] Store audit result in local memory/file cache for fast subsequent retrieval.
- [x] Return JSON payload with overall status, category breakdown, issues, and execution time.

### AI Testing Plan
- Test endpoint using `httpx.AsyncClient` uploading synthetic PDF.
- Assert response status HTTP 200 and schema matches `AuditScorecard`.
- Test upload with invalid file format (e.g. `.exe`): assert HTTP 400 Bad Request.

### Human Review Checklist
- [ ] Verify file upload security and cleanup routines for transient files.
- [ ] Confirm response payload contains all necessary frontend fields.

### Work Log & Evidence
- Status: `[TESTED_BY_AI]`
- Automated tests in `backend/tests/test_api_endpoints.py`:
  - `test_upload_invalid_extension`: PASSED (asserts HTTP 400 on non-PDF upload).
  - `test_upload_and_audit_pdf`: PASSED (executes full pipeline, returns AuditScorecard with 5 category scores).
