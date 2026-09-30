# Ticket: TICK-0802
## Side-by-Side Interactive PDF Viewer Component

- **Ticket ID**: `TICK-0802`
- **Stage**: Stage 8: Next.js Luxury UI & Split-Screen Experience
- **Status**: `[BACKLOG]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0801`, `TICK-0703`

---

### Description
Implement the interactive PDF & flat sketch viewer component in `frontend/src/components/PDFViewer.tsx` using `react-pdf` / PDF.js. Supports page navigation, smooth zoom, and interactive bounding box overlays that jump directly to the specific page and highlight the relevant table or sketch when an audit issue is clicked on the right-hand scorecard.

### Subtasks
- [ ] Build drag-and-drop tech pack PDF uploader with progress feedback.
- [ ] Render PDF pages with fast canvas virtualization.
- [ ] Implement bounding box overlay layer: highlights POM measurement rows, BOM line items, or collar sketches.
- [ ] Support bi-directional linking: clicking an issue in the scorecard scrolls the PDF directly to that page and pulses the bounding box.

### AI Testing Plan
- Test PDF viewer rendering with synthetic tech pack.
- Verify jump-to-page event updates canvas view accurately.

### Human Review Checklist
- [ ] Test PDF upload interaction and page navigation smoothness.
- [ ] Confirm jump-to-highlight functionality works seamlessly from scorecard clicks.

### Work Log & Evidence
- Status: `[BACKLOG]`
