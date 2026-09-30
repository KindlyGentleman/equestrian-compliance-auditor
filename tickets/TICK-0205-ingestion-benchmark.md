# Ticket: TICK-0205
## Ingestion Pipeline Integration Test & Speed Benchmark

- **Ticket ID**: `TICK-0205`
- **Stage**: Stage 2: SOTA Ingestion & OCR Pipeline
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0201`, `TICK-0202`, `TICK-0203`, `TICK-0204`

---

### Description
Integrate `PDFParser`, `TableExtractor`, `ImageCropper`, and `OCRFallback` into a unified `IngestionPipeline` service in `backend/app/ingestion/pipeline.py`. Run end-to-end performance benchmarks to prove that 10–30 page tech packs process completely with granular stage timings and low memory footprint on an Intel CPU.

### Subtasks
- [x] Build `IngestionPipeline.process(pdf_path: Path) -> IngestionResult`.
- [x] Ensure `IngestionResult` encapsulates full document markdown, individual page objects, extracted tables, and cropped figures with bounding boxes.
- [x] Measure and log granular timing for each stage (text, tables, figures, OCR).
- [x] Validate memory consumption stays $< 350\text{ MB}$.

### AI Testing Plan
- Execute automated integration benchmark over a 10-page synthetic equestrian show coat tech pack.
- Assert total execution time is under target threshold and memory stays $< 350\text{ MB}$.
- Assert all tables and figures are extracted and linked to correct page numbers.
- Assert selective OCR fallback triggers only on rasterized/scanned pages and enriches document markdown.

### Human Review Checklist
- [ ] Review benchmark execution logs.
- [ ] Confirm ingestion latency satisfies the < 30s overall requirement.

### Work Log & Evidence
- Status changed from `[BACKLOG]` to `[TESTED_BY_AI]`.
- Implemented `backend/app/ingestion/pipeline.py` with `IngestionPipeline`, `IngestionResult`, and `IngestionStageTiming`.
- Exported unified pipeline components in `backend/app/ingestion/__init__.py`.
- Automated test suite in `backend/tests/test_ingestion_pipeline.py`:
  - `test_ingestion_pipeline_digital_benchmark`: 10 pages parsed in 4.965s total (PyMuPDF4LLM text 4.737s, table extraction 0.203s, figure extraction 0.024s, 224.5 MB peak memory).
  - `test_ingestion_pipeline_hybrid_ocr_fallback`: Selective OCR fallback triggered exclusively on scanned page 2, extracting rasterized text and updating full markdown.
  - `test_ingestion_pipeline_file_not_found`: Properly raises `FileNotFoundError`.
- All 21 backend unit and integration tests passing.
