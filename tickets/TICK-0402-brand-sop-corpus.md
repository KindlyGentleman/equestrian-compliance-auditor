# Ticket: TICK-0402
## Luxury Brand Quality & Production SOP Corpus

- **Ticket ID**: `TICK-0402`
- **Stage**: Stage 4: Regulatory Knowledge Base & RAG
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0103`

---

### Description
Curate internal Luxury Equestrian Brand SOPs in `backend/app/data/regulations/brand/` defining strict quality, costing, and manufacturing thresholds:
- Target FOB / COGS ceilings per product category (Show Jackets FOB max $65.00, Shirt FOB max $28.00).
- Performance fabric minimums: Breathability $\ge 10,000\text{ g/m}^2/\text{24h}$, 4-way stretch $\ge 15\%$, UV rating $\ge \text{UPF } 50+$.
- Construction tolerances: Collar height variance $\pm 0.5\text{ cm}$, hem variance $\pm 1.0\text{ cm}$.
- Seam and stitch standards: 12–14 stitches per inch (SPI).

### Subtasks
- [x] Create structured brand SOP documentation files in `backend/app/data/regulations/brand/`.
- [x] Structure SOP sections into auditable rule paragraphs with unique identifiers (`BRAND-SOP-COGS-01`, `BRAND-SOP-FABRIC-01`, `BRAND-SOP-TOL-01`).
- [x] Add category tagging (`Costing & FOB`, `Fabric & Performance`, `Tailoring & Dimensions`).

### AI Testing Plan
- Test chunking and metadata parser across all brand SOP files.
- Assert all SOP rules have distinct unique rule IDs and clear quantitative or qualitative definitions.

### Human Review Checklist
- [ ] Review brand SOP guidelines for alignment with luxury performance outerwear expectations.
- [ ] Confirm rule IDs follow a consistent naming convention.

### Work Log & Evidence
- Status changed from `[BACKLOG]` to `[TESTED_BY_AI]`.
- Implemented `brand_quality_standards.md` in `backend/app/data/regulations/brand/`.
- Verified in `backend/tests/test_rag.py::test_markdown_chunking_parser`.
