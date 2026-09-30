# Ticket: TICK-0401
## FEI Regulatory Corpus Curation & Ingestion

- **Ticket ID**: `TICK-0401`
- **Stage**: Stage 4: Regulatory Knowledge Base & RAG
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0103`

---

### Description
Curate and structure the official FEI (Fédération Equestre Internationale) apparel regulations and guidelines into parsed, clean markdown corpus files in `backend/app/data/regulations/fei/`:
1. **Show Jumping Rules**: Article 256 (Dress, Protective Headgear, Salute, and Badge regulations).
2. **Dressage Rules**: Article 427 (Dress, Tailcoats, Jackets, Ties, Safety Vests).
3. **Eventing Rules**: Article 538 (Dress across Dressage, Cross-Country, and Jumping phases).
4. **FEI Guidelines on Authorized Identification**: Exact brand logo surface area rules (max 60cm² collar, max 200cm² chest, vertical collar lettering rules).

### Subtasks
- [x] Create curated, official FEI markdown regulation documents in `backend/app/data/regulations/fei/`.
- [x] Tag every chunk with exact metadata (`discipline`, `article_id`, `category`).
- [x] Build chunking strategy preserving full legal article paragraphs without mid-sentence cuts.

### AI Testing Plan
- Validate that all articles (256, 427, 538, Logo Guidelines) are parsed with zero lost metadata.
- Assert chunk size and boundary integrity.

### Human Review Checklist
- [ ] Verify legal and text accuracy of FEI regulation excerpts.
- [ ] Confirm metadata tagging corresponds directly to official FEI rules.

### Work Log & Evidence
- Status changed from `[BACKLOG]` to `[TESTED_BY_AI]`.
- Curated `fei_jumping_art256.md`, `fei_dressage_art427.md`, and `fei_eventing_art538.md`.
- Verified in `backend/tests/test_rag.py::test_markdown_chunking_parser`.
