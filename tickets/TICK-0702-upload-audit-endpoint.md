# Ticket: TICK-0702
## Tech Pack Upload & Audit Execution Endpoint

- **Ticket ID**: `TICK-0702`
- **Stage**: Stage 7: FastAPI Backend & API Integration
- **Status**: `[BACKLOG]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0701`, `TICK-0604`

---

### Description
Implement the primary audit endpoint in `backend/app/api/audit_router.py`: `POST /api/audit/upload`. This endpoint accepts multipart PDF file uploads, validates file format and size (< 50MB), triggers the end-to-end ingestion and dual-layer audit pipeline asynchronously, and returns the comprehensive `AuditScorecard`.

### Subtasks
- [ ] Implement `POST /api/audit/upload` accepting `UploadFile`.
- [ ] Save uploaded PDF to secure transient storage with unique UUID.
- [ ] Trigger `IngestionPipeline`, `StructuringService`, and `AuditCoordinator`.
- [ ] Store audit result in local memory/file cache for fast subsequent retrieval.
- [ ] Return JSON payload with overall status, category breakdown, issues, and execution time.

### AI Testing Plan
- Test endpoint using `httpx.AsyncClient` uploading synthetic PDF.
- Assert response status HTTP 200 and schema matches `AuditScorecard`.
- Test upload with invalid file format (e.g. `.exe`): assert HTTP 400 Bad Request.

### Human Review Checklist
- [ ] Verify file upload security and cleanup routines for transient files.
- [ ] Confirm response payload contains all necessary frontend fields.

### Work Log & Evidence
- Status: `[BACKLOG]`
