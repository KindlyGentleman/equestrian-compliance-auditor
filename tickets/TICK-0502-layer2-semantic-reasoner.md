# Ticket: TICK-0502
## Layer 2 Semantic Reasoner

- **Ticket ID**: `TICK-0502`
- **Stage**: Stage 5: Dual-Layer Comparative Audit Engine
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0302`, `TICK-0405`

---

### Description
Implement the Layer 2 Semantic Reasoning Engine in `backend/app/engine/semantic_reasoner.py` using Gemini 2.0 Flash. This layer evaluates qualitative, aesthetic, and context-dependent regulations that cannot be checked by simple numerical operators:
- Legality of collar contrast colors (e.g. velvet collar vs body color in Dressage vs Jumping).
- Contrast piping rules along lapels and pockets.
- Button styling, count, and crest embossing guidelines.
- Discreet sponsor logo placement standards.

### Subtasks
- [x] Implement `SemanticReasoner.audit(spec: TechPackSpec, relevant_rules: List[RuleChunk]) -> List[AuditFinding]`.
- [x] Prompt engineering: Enforce strict grounding. The LLM is instructed to only flag an issue if it can quote the exact sentence from the provided `relevant_rules` context.
- [x] Output structured finding objects with fields: `rule_id`, `category`, `severity`, `rationale`, `verbatim_source_quote`.
- [x] Prevent ambiguous hallucinations: instruct model that if a rule does not explicitly prohibit a design feature, it must remain `PASS`.

### AI Testing Plan
- Test with known qualitative violation:
  - White contrast velvet collar on a Dressage jacket (prohibited under Dressage Art 427 -> should trigger VIOLATION with exact citation).
- Test with fully compliant jacket: assert zero false positives generated.
- Measure latency: assert execution $< 2.5\text{ seconds}$.

### Human Review Checklist
- [ ] Inspect semantic prompt constraints for evidence-based reasoning.
- [ ] Verify that aesthetic findings cite verbatim FEI text passages.

### Work Log & Evidence
- Status: `[TESTED_BY_AI]`
- Unit tests executed in `backend/tests/test_audit_engine.py`:
  - `test_semantic_reasoner_dressage_collar_color`: PASSED (flags non-conservative bright collar in Dressage).
  - `test_semantic_reasoner_zero_false_positives`: PASSED (compliant jacket yields 0 false positives).
