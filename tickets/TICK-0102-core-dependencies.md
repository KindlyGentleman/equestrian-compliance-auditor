# Ticket: TICK-0102
## Core Dependencies Installation & Verification

- **Ticket ID**: `TICK-0102`
- **Stage**: Stage 1: Environment Setup & Scaffolding
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0101`

---

### Description
Install and pin all core Python dependencies needed for the free, lightweight, CPU-optimized stack:
`pymupdf4llm`, `rapidocr-onnxruntime`, `pdfplumber`, `pydantic>=2.7`, `fastapi`, `uvicorn`, `qdrant-client`, `google-genai`, `python-dotenv`, `pytest`, `httpx`. Ensure compatibility on Windows with Intel UHD CPU environment.

### Subtasks
- [x] Create `backend/requirements.txt` with pinned compatible versions.
- [x] Install packages inside `.venv`.
- [x] Verify ONNX runtime CPU execution for `rapidocr-onnxruntime`.
- [x] Verify `pymupdf4llm` imports and runs without C++ build tool errors.
- [x] Verify `qdrant-client` local in-memory/file mode functions without external Docker container.

### AI Testing Plan
- Create an automated smoke test script `backend/tests/test_env_smoke.py` importing all core packages and initializing lightweight instances.
- Assert 0 errors and execution time < 1s.

### Human Review Checklist
- [ ] Check `backend/requirements.txt` cleanliness and version pinning.
- [ ] Confirm `pytest backend/tests/test_env_smoke.py` passes cleanly on local machine.

### Work Log & Evidence
- **2026-09-29**: Created `backend/requirements.txt` with pinned core dependencies.
- **2026-09-29**: Installed all wheels into `.venv` including `rapidocr-onnxruntime-1.4.4`, `pymupdf4llm-1.28.2`, `qdrant-client-1.19.1`, and `google-genai-2.25.0`.
- **2026-09-29**: Executed `backend/tests/test_env_smoke.py`:
  - RapidOCR ONNX CPU runtime initialized successfully.
  - Qdrant embedded in-memory client verified without Docker.
  - PyMuPDF4LLM and core dependencies verified.
  - All tests passed with exit code 0. Status updated to `[TESTED_BY_AI]`.
