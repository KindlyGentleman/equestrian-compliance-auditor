# Ticket: TICK-0601
## Automated Verbatim Citation Verifier Gate

- **Ticket ID**: `TICK-0601`
- **Stage**: Stage 6: Verifier Gate & Vendor Action Generator
- **Status**: `[BACKLOG]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0503`

---

### Description
Implement the Constitutional Verifier Gate in `backend/app/engine/citation_verifier.py`. This is the core architectural safeguard that guarantees **Zero False Positives**. For every finding produced by the Layer 2 Semantic Reasoner, the verifier performs a string search against the source knowledge chunk. If the cited article number or verbatim quote does not strictly exist in the authentic FEI/SOP text, or if the rationale is unsupported, the finding is automatically downgraded from `VIOLATION` to `MANUAL_REVIEW` and flagged with an audit warning.

### Subtasks
- [ ] Implement `CitationVerifier.verify(finding: AuditFinding, source_chunks: List[RuleChunk]) -> VerifiedFinding`.
- [ ] Perform exact normalized substring matching between `verbatim_source_quote` and the authentic regulatory chunk.
- [ ] Implement fuzzy similarity fallback check (threshold $\ge 0.92$) to account for minor whitespace or punctuation variances.
- [ ] If citation cannot be verified, change severity to `MANUAL_REVIEW` and append notice: *"Warning: Citation unverified against ground truth text; downgraded to avoid false positive."*

### AI Testing Plan
- Test with valid citation: assert finding remains `VIOLATION` / `WARNING` with verified badge.
- Test with hallucinated/fabricated citation: assert finding is strictly downgraded to `MANUAL_REVIEW`.
- Test with slightly varied whitespace: assert fuzzy verifier accepts valid quote.

### Human Review Checklist
- [ ] Verify that no unverified or hallucinated citation can pass through as a confirmed `VIOLATION`.
- [ ] Review criteria for downgrading to `MANUAL_REVIEW`.

### Work Log & Evidence
- Status: `[BACKLOG]`
