# Ticket: TICK-0405
## Hybrid Retrieval Engine & Query Synthesizer

- **Ticket ID**: `TICK-0405`
- **Stage**: Stage 4: Regulatory Knowledge Base & RAG
- **Status**: `[BACKLOG]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0404`

---

### Description
Implement the hybrid retrieval service in `backend/app/rag/retriever.py`. When an equestrian tech pack is audited, this engine analyzes the garment type and discipline, synthesizes targeted queries (e.g., *"Show Jumping collar contrast and piping regulations"*, *"Dressage tailcoat button count rules"*), executes hybrid search against Qdrant, and returns the top relevant regulation chunks with confidence scores and source metadata.

### Subtasks
- [ ] Implement `HybridRetriever.retrieve_rules(query: str, discipline: Discipline, garment_type: str, top_k: int = 5) -> List[RuleChunk]`.
- [ ] Implement payload pre-filtering by `discipline` (e.g. only search Jumping rules when auditing a Show Jumping jacket, while including common logo rules).
- [ ] Support hybrid scoring combining semantic vector similarity with exact keyword matching (for article numbers like `Art. 256.3`).
- [ ] Deduplicate retrieved chunks and format them into clean LLM context blocks.

### AI Testing Plan
- Test retrieval queries for Jumping, Dressage, and Eventing.
- Assert that query for "Collar piping" returns Article 256.3 and Article 427 with high similarity score.
- Assert retrieval execution time is $< 200\text{ ms}$.

### Human Review Checklist
- [ ] Verify retrieved chunks contain the exact legal passages relevant to test garment features.
- [ ] Confirm discipline filtering strictly avoids cross-discipline false matches.

### Work Log & Evidence
- Status: `[BACKLOG]`
