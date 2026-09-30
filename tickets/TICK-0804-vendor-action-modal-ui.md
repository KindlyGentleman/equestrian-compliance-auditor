# Ticket: TICK-0804
## Vendor Action Note Modal & One-Click Export UI

- **Ticket ID**: `TICK-0804`
- **Stage**: Stage 8: Next.js Luxury UI & Split-Screen Experience
- **Status**: `[TESTED_BY_AI]`
- **Assigned To**: Antigravity (AI Agent)
- **Reviewer**: User (Human)
- **Dependencies**: `TICK-0803`, `TICK-0704`

---

### Description
Implement the supplier communication interface in `frontend/src/components/VendorActionModal.tsx`. Provides a sleek slide-over or modal drawer displaying the AI-generated supplier revision notes. Enables the garment designer or sourcing lead to review, edit specific bullet points, and with one click: copy formatted email text to clipboard, download a formatted PDF revision sheet, or send via webhook.

### Subtasks
- [x] Build slide-over drawer triggered by "Generate Vendor Actions" button.
- [x] Implement rich-text editable preview of revision instructions grouped by recipient (Pattern Maker, Mill, Embroidery).
- [x] Add "Copy to Clipboard" with toast notification.
- [x] Add "Download PDF Revision Note" button wired to backend export endpoint.

### AI Testing Plan
- Test modal trigger and state management.
- Test clipboard copy API and PDF download trigger.

### Human Review Checklist
- [ ] Test editing notes directly inside the UI.
- [ ] Verify downloaded PDF is clean and supplier-ready.

### Work Log & Evidence
- Status: `[TESTED_BY_AI]`
- Implemented `frontend/src/components/VendorActionModal.tsx` supporting Action Items tab grouped by department, Email Draft tab, and raw Markdown report tab.
- Integrated one-click copy to clipboard with toast notification, and PDF download trigger wired to `/api/audit/{id}/export-vendor-notes?format=pdf`.
- Verified in `npm run build` and integration tests.
