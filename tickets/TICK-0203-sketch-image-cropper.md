# Ticket: TICK-0203
## Technical Sketch & Logo Artwork Cropper

- **Ticket ID**: `TICK-0203`
- **Stage**: Stage 2: SOTA Ingestion & OCR Pipeline
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0201`

---

### Description
Implement an image and visual figure extraction module in `backend/app/ingestion/image_cropper.py`. In equestrian wear, flat sketches (front/back views, contrast collar details, sleeve badges) carry critical compliance visual information. This module extracts embedded raster images and bounding-boxed vector drawings, saves them to an artifact cache, and generates metadata linking them to their corresponding page and callout text.

### Subtasks
- [x] Implement `extract_figures(pdf_path: Path) -> List[ExtractedFigure]`.
- [x] Filter out insignificant icons, background artifacts, and lines (retain drawings > 150x150 px).
- [x] Extract bounding boxes `[x0, y0, x1, y1]` for each figure to enable UI highlighting in the split-screen PDF viewer.
- [x] Save cropped images in optimized PNG format with structured naming (`page_{N}_fig_{M}.png`).

### AI Testing Plan
- Test extraction on sample PDFs containing front/back jacket technical flats.
- Verify bounding boxes accurately correspond to the visual coordinates.

### Human Review Checklist
- [ ] Check cropped flat sketches for visual fidelity and clarity.
- [ ] Verify image paths and bounding box coordinates match source PDF locations.

### Work Log & Evidence
- **2026-09-29**: Implemented `backend/app/ingestion/image_cropper.py` using PyMuPDF.
- **2026-09-29**: Added automatic figure type classification (`SKETCH`, `LOGO`, `DIAGRAM`, `SWATCH`), size threshold filtering, and canvas bounding box calculation.
- **2026-09-29**: Executed `backend/tests/test_image_cropper.py` (passed in 0.83s; verified sketch and logo cropping and PNG caching). Status updated to `[TESTED_BY_AI]`.
