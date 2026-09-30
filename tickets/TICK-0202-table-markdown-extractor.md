# Ticket: TICK-0202
## Tabular Data Extraction & Markdown Normalizer

- **Ticket ID**: `TICK-0202`
- **Stage**: Stage 2: SOTA Ingestion & OCR Pipeline
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0201`

---

### Description
Implement a specialized table extractor and normalizer in `backend/app/ingestion/table_extractor.py`. Tech packs contain dense tables: Bill of Materials (BOM), measurement charts with size grading (XS-XL), and fabric composition specs. This module converts raw extracted tables into clean, deterministic markdown tables and JSON dictionary matrices.

### Subtasks
- [x] Implement multi-column table detection and borderless table alignment using `pdfplumber` / `pymupdf4llm`.
- [x] Normalize table headers (e.g., standardizing "POM", "Point of Measure", "Spec", "Tol +/-", "Size S").
- [x] Output tables both as standard GitHub-Flavored Markdown (for LLM ingestion) and structured dicts (for deterministic evaluation).
- [x] Handle merged cells, empty cells, and numeric values with unit suffixes (e.g. `240gsm`, `2.5cm`, `15%`).

### AI Testing Plan
- Unit test with complex synthetic BOM and grading tables.
- Assert 100% extraction accuracy on row and column headers with zero shifted columns.

### Human Review Checklist
- [ ] Inspect generated markdown tables for visual alignment and correctness.
- [ ] Confirm tolerance and numeric fields retain sign conventions (`+/-`).

### Work Log & Evidence
- **2026-09-29**: Implemented `backend/app/ingestion/table_extractor.py` using `pdfplumber`.
- **2026-09-29**: Added automated header synonym normalization (`pom_code`, `spec_cm`, `tolerance_cm`, `item_name`, `material`, `unit_cost`) and automatic table classification (`BOM`, `MEASUREMENTS`, `GRADING`, `GENERIC`).
- **2026-09-29**: Executed `backend/tests/test_table_extractor.py` (2 passed in 0.98s; verified BOM and POM extraction and header normalization). Status updated to `[TESTED_BY_AI]`.
