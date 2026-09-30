# Ticket: TICK-0301
## Comprehensive Pydantic v2 Domain Schemas

- **Ticket ID**: `TICK-0301`
- **Stage**: Stage 3: Pydantic Schema Structuring & Modeling
- **Status**: `[BACKLOG]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0103`

---

### Description
Implement domain models using Pydantic v2 in `backend/app/models/tech_pack.py`. The models represent the complete anatomy of technical luxury equestrian garments across Show Jumping, Dressage, and Eventing.

### Subtasks
- [ ] Define `GarmentMetadata` (style_code, season, discipline, garment_type, gender).
- [ ] Define `FabricSpec` (primary_fabric, lining, composition percentages, weight_gsm, weave_type, stretch_percentage, breathability_g_m2_24h, water_resistance_mm).
- [ ] Define `BOMComponent` (item_name, placement, supplier_code, material, color_code, unit_cost, quantity).
- [ ] Define `MeasurementSpec` & `MeasurementItem` (POM code, description, spec_cm, tolerance_plus_minus_cm, size_grading).
- [ ] Define `BrandingLogoSpec` (location, placement_type, width_cm, height_cm, calculated_area_cm2, description, colors).
- [ ] Define `AestheticDetails` (collar_type, collar_contrast_color, piping_width_mm, button_count, lapel_style, vent_style).
- [ ] Define `CostingSpec` (target_fob_usd, actual_fob_usd, fabric_cost, trim_cost, cmt_cost).
- [ ] Aggregate into master model `TechPackSpec`.

### AI Testing Plan
- Unit test schemas with full valid payloads, edge-case partial payloads, and invalid field types.
- Verify automatic validation and calculated fields (e.g. `calculated_area_cm2 = width_cm * height_cm`).

### Human Review Checklist
- [ ] Verify models cover all fields necessary for FEI regulation audits and brand SOP compliance.
- [ ] Review schema type annotations and docstrings.

### Work Log & Evidence
- Status: `[BACKLOG]`
