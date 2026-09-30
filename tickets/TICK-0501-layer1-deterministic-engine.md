# Ticket: TICK-0501
## Layer 1 Deterministic Audit Engine

- **Ticket ID**: `TICK-0501`
- **Stage**: Stage 5: Dual-Layer Comparative Audit Engine
- **Status**: `[BACKLOG]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0301`, `TICK-0403`

---

### Description
Implement the code-level Layer 1 Deterministic Audit Engine in `backend/app/engine/deterministic_engine.py`. This engine evaluates quantitative parameters directly in Python against `rules_catalog.json`. Because it uses pure mathematical comparisons, it executes in under 10ms with **0% hallucination risk**.

### Subtasks
- [ ] Implement `DeterministicEngine.audit(spec: TechPackSpec) -> List[AuditFinding]`.
- [ ] Implement rule evaluators:
  - **Logo Area**: Calculate surface area for every logo placement (Collar $\le 60\text{ cm}^2$, Chest/Pocket $\le 200\text{ cm}^2$, Sleeve $\le 100\text{ cm}^2$).
  - **Collar Dimensions**: Height min/max and tolerance limits ($\pm 0.5\text{ cm}$).
  - **Costing & FOB**: Target vs Actual FOB comparison (flag `VIOLATION` if actual > target by > 5%).
  - **Fabric Performance**: Breathability check (flag `WARNING` if $< 10,000\text{ g/m}^2/\text{24h}$), stretch % minimums.
- [ ] Attach exact source citations and rule IDs to every finding.

### AI Testing Plan
- Unit test with synthetic tech packs containing known violations:
  - Oversized collar logo (65 cm² -> should trigger VIOLATION on `FEI-JUMP-LOGO-COLLAR`).
  - FOB over budget ($68 vs $60 -> should trigger VIOLATION on `BRAND-SOP-COGS-01`).
- Assert 100% detection rate and execution time $< 15\text{ ms}$.

### Human Review Checklist
- [ ] Verify arithmetic calculations for logo area and tolerances.
- [ ] Confirm findings provide clear quantitative deltas (e.g. *"Observed: 68.0cm², Limit: 60.0cm², Delta: +8.0cm²"*).

### Work Log & Evidence
- Status: `[BACKLOG]`
