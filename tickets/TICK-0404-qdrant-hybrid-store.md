# Ticket: TICK-0404
## Qdrant Hybrid Vector Store Setup

- **Ticket ID**: `TICK-0404`
- **Stage**: Stage 4: Regulatory Knowledge Base & RAG
- **Status**: `[BACKLOG]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0103`, `TICK-0401`, `TICK-0402`

---

### Description
Implement the vector store manager in `backend/app/rag/vector_store.py` using `qdrant-client`. Configure local storage mode (running directly via disk/in-memory without external Docker containers), create collection `equestrian_regulations`, and configure hybrid search indices:
1. Dense vector index (`text-embedding-004`, 768 dimensions, cosine distance).
2. Sparse / Payload schema indexes for `discipline`, `article_id`, and `category` to allow strict metadata filtering.

### Subtasks
- [ ] Initialize Qdrant client in embedded / local storage mode (`path=settings.QDRANT_STORAGE_PATH`).
- [ ] Create collection with vector configuration and payload index schemas.
- [ ] Build embedding generation pipeline using Google Gemini Embeddings (`text-embedding-004`).
- [ ] Implement chunk indexing script that populates Qdrant from the FEI and Brand markdown documents.

### AI Testing Plan
- Test local collection creation and indexing of sample chunks.
- Measure embedding generation time: assert indexing of the entire regulation corpus completes in $< 10$ seconds.

### Human Review Checklist
- [ ] Verify Qdrant local persistence works across application restarts without data loss.
- [ ] Confirm no external Docker or cloud database dependency is required for local dev.

### Work Log & Evidence
- Status: `[BACKLOG]`
