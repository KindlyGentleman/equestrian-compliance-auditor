# Ticket: TICK-0204
## RapidOCR-ONNX Fallback Parser for Scanned Elements

- **Ticket ID**: `TICK-0204`
- **Stage**: Stage 2: SOTA Ingestion & OCR Pipeline
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0201`

---

### Description
Implement an automated fallback OCR pipeline in `backend/app/ingestion/ocr_fallback.py` using `rapidocr-onnxruntime`. If a page or callout contains rasterized text (scanned PDF pages, flattened Illustrator callouts, fabric mill swatch certificates) with no selectable text, `RapidOCR` detects text lines, computes confidence scores, and converts text into Markdown without requiring a dedicated GPU.

### Subtasks
- [x] Implement image-based OCR detector using `RapidOCR` (ONNX CPU model).
- [x] Implement heuristic detector to identify pages with low or zero selectable text density.
- [x] Reconstruct OCR text blocks into logical paragraphs and markdown tables.
- [x] Benchmark CPU inference time per page to guarantee it stays within limits.

### AI Testing Plan
- Test on a flattened/rasterized 1-page tech pack image.
- Assert OCR text extraction accurately captures style codes, fiber percentages, and measurements.

### Human Review Checklist
- [ ] Confirm fallback triggers appropriately when given scanned/rasterized documents.
- [ ] Verify CPU resource utilization remains low during OCR inference.

### Work Log & Evidence
- **2026-09-29**: Implemented `backend/app/ingestion/ocr_fallback.py` with lazy `RapidOCR` initialization.
- **2026-09-29**: Added heuristic `is_scanned_page()` text density detector and `ocr_page()` with confidence scoring.
- **2026-09-29**: Executed `backend/tests/test_ocr_fallback.py` (2 passed in 6.81s; successfully extracted text lines from flattened raster image with 0.98 confidence). Status updated to `[TESTED_BY_AI]`.
