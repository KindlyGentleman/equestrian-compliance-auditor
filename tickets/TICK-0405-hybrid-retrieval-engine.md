# Ticket: TICK-0405
## Hybrid Retrieval Engine & Query Synthesizer

- **Ticket ID**: `TICK-0405`
- **Stage**: Stage 4: Regulatory Knowledge Base & RAG
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0404`

---

### Description
Implement the hybrid retrieval service in `backend/app/rag/retriever.py`. When an equestrian tech pack is audited, this engine analyzes the garment type and discipline, synthesizes targeted queries, executes hybrid search against Qdrant, and returns the top relevant regulation chunks with confidence scores and source metadata.

### Subtasks
- [x] Implement `HybridRetriever.retrieve_rules(query: str, discipline: Discipline, garment_type: str, top_k: int = 5) -> List[RuleChunk]`.
- [x] Implement payload pre-filtering by `discipline` (filtering Jumping rules when auditing Show Jumping, while including common logo rules).
- [x] Support hybrid scoring combining semantic vector similarity with exact keyword matching.
- [x] Deduplicate retrieved chunks and format them into clean LLM context blocks via `format_context_for_prompt()`.

### AI Testing Plan
- Test retrieval queries for Jumping, Dressage, and Eventing.
- Assert that query for "Collar logo" returns Article 256.3 and Article 427 with high similarity score.
- Assert retrieval execution time is $< 200\text{ ms}$.

### Human Review Checklist
- [ ] Verify retrieved chunks contain the exact legal passages relevant to test garment features.
- [ ] Confirm discipline filtering strictly avoids cross-discipline false matches.

### Work Log & Evidence
- Status changed from `[BACKLOG]` to `[TESTED_BY_AI]`.
- Implemented `backend/app/rag/retriever.py` with `HybridRetriever` and `retrieve_rules_for_techpack()`.
- Verified in `backend/tests/test_rag.py::test_hybrid_retriever_query`, `test_hybrid_retriever_discipline_filter`, and `test_retriever_techpack_context_generation`.
