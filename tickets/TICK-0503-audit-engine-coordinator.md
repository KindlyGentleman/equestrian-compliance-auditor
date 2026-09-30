# Ticket: TICK-0503
## Audit Engine Coordinator

- **Ticket ID**: `TICK-0503`
- **Stage**: Stage 5: Dual-Layer Comparative Audit Engine
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0501`, `TICK-0502`

---

### Description
Implement the unified coordinator in `backend/app/engine/audit_coordinator.py`. This service runs Layer 1 (Deterministic) and Layer 2 (Semantic) concurrently, merges and deduplicates findings, calculates overall garment compliance status, and tags findings with execution timestamps and confidence scores.

### Subtasks
- [x] Implement `AuditCoordinator.run_audit(spec: TechPackSpec) -> PreliminaryAuditReport`.
- [x] Execute Layer 1 and Layer 2 asynchronously via `asyncio.gather`.
- [x] Deduplicate findings where both deterministic and semantic layers flag the same component.
- [x] Compute overall status: `VIOLATION` if any violation exists; else `WARNING` if warnings exist; else `PASS`.

### AI Testing Plan
- Test concurrent execution of Layer 1 + Layer 2.
- Verify status roll-up logic (assert single violation sets overall status to `VIOLATION`).
- Measure total coordinator execution time: assert $< 3.0$ seconds.

### Human Review Checklist
- [ ] Verify error handling if one layer encounters an exception.
- [ ] Confirm findings list is sorted by severity (`VIOLATION` > `WARNING` > `PASS`).

### Work Log & Evidence
- Status: `[TESTED_BY_AI]`
- Unit tests executed in `backend/tests/test_audit_engine.py`:
  - `test_audit_coordinator_overall_roll_up_violation`: PASSED (rolls up single violation to overall VIOLATION in < 3.0s).
  - `test_audit_coordinator_clean_pass`: PASSED (awards 100% and PASS to compliant spec).
