"""
System Architecture Diagram Generator for Maison Équestre Atelier Pro.
Produces both:
1. Native draw.io XML file (docs/architecture/system_architecture.drawio)
2. Interactive SVG with animated flow connectors matching DayuanJiang/next-ai-draw-io (docs/architecture/system_architecture.drawio.svg)
"""
import os
import xml.sax.saxutils as saxutils

OUTPUT_DIR = r"d:\03_Proyek\RAG Testing\docs\architecture"
PUBLIC_DIR = r"d:\03_Proyek\RAG Testing\frontend\public"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Native draw.io XML Generator
# -----------------------------------------------------------------------------
def build_drawio_xml():
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<mxfile host="app.diagrams.net" modified="2026-10-01T00:00:00.000Z" agent="Antigravity" version="24.7.17" type="device">',
        '  <diagram id="maison-equestre-arch" name="Maison Équestre System Architecture">',
        '    <mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1700" pageHeight="1150" math="0" shadow="0">',
        '      <root>',
        '        <mxCell id="0" />',
        '        <mxCell id="1" parent="0" />',
    ]

    # Helper to add cells
    def add_cell(cid, value, style, x, y, w, h, parent="1"):
        val_esc = saxutils.escape(value)
        style_esc = saxutils.escape(style)
        xml.append(f'        <mxCell id="{cid}" value="{val_esc}" style="{style_esc}" vertex="1" parent="{parent}">')
        xml.append(f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />')
        xml.append('        </mxCell>')

    def add_edge(eid, val, style, source, target, waypoints=None):
        val_esc = saxutils.escape(val)
        style_esc = saxutils.escape(style)
        xml.append(f'        <mxCell id="{eid}" value="{val_esc}" style="{style_esc}" edge="1" parent="1" source="{source}" target="{target}">')
        xml.append('          <mxGeometry relative="1" as="geometry">')
        if waypoints:
            xml.append('            <Array as="points">')
            for wx, wy in waypoints:
                xml.append(f'              <mxPoint x="{wx}" y="{wy}" />')
            xml.append('            </Array>')
        xml.append('          </mxGeometry>')
        xml.append('        </mxCell>')

    # Global Swimlane / Container styles
    c_swimlane = "swimlane;html=1;startSize=36;rounded=1;arcSize=8;fontFamily=Georgia;fontSize=14;fontStyle=1;strokeWidth=2;"
    c_box = "rounded=1;whiteSpace=wrap;html=1;arcSize=10;fontFamily=Helvetica;fontSize=11;strokeWidth=1.5;"
    c_edge = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#9E7E50;fontFamily=Helvetica;fontSize=10;fontColor=#4A5560;"

    # 1. Title Banner
    add_cell("title_banner", "MAISON ÉQUESTRE ATELIER PRO: HIGH-STAKES OLYMPIC EQUESTRIAN COMPLIANCE AUDITOR\nSystem Architecture & Multi-Modal Hybrid RAG Pipeline", "rounded=1;whiteSpace=wrap;html=1;fillColor=#0C1F16;strokeColor=#C5A880;strokeWidth=2;fontColor=#C5A880;fontFamily=Georgia;fontSize=16;fontStyle=1;align=center;", 40, 30, 1620, 65)

    # 2. Swimlane 1: Client & Presentation Tier (Next.js 14)
    add_cell("c_client", "PRESENTATION & CLIENT TIER (Next.js 14 App Router)", f"{c_swimlane}fillColor=#FBFBF9;strokeColor=#163828;fontColor=#163828;", 40, 120, 380, 960)
    add_cell("c1_user", "Senior Technical Designer\n(Apparel & Olympic Sourcing)", f"{c_box}fillColor=#FFFFFF;strokeColor=#163828;fontColor=#151C22;fontStyle=1;", 70, 175, 320, 60, "c_client")
    add_cell("c1_split", "Split-Screen Technical Flat Viewer\n- Synchronized BOM / Sketch Canvas\n- Bounding Box Inspection Zone", f"{c_box}fillColor=#FFFFFF;strokeColor=#C5A880;fontColor=#151C22;", 70, 260, 320, 75, "c_client")
    add_cell("c1_scorecard", "Luxury Compliance Audit Scorecard\n- 0.35s Execution Latency Metric\n- Category Score Progress Bars\n- Violation & Warning Badges", f"{c_box}fillColor=#FFFFFF;strokeColor=#C5A880;fontColor=#151C22;", 70, 360, 320, 85, "c_client")
    add_cell("c1_grounding", "Verbatim Citation & Gate Modal\n- FEI Official Rulebook Quotation\n- Delta Tolerance Math Display", f"{c_box}fillColor=#FFFFFF;strokeColor=#C5A880;fontColor=#151C22;", 70, 470, 320, 75, "c_client")
    add_cell("c1_rules", "Dynamic Rules Catalog Modal\n- Live Search & Filter Engine\n- '+ Add Rule' In-App Form\n- Delete Custom Brand Rules", f"{c_box}fillColor=#FFFFFF;strokeColor=#047857;fontColor=#151C22;fontStyle=1;", 70, 570, 320, 85, "c_client")
    add_cell("c1_vendor", "Supplier Action Plan & Export Modal\n- Official Letterhead PDF Export\n- Markdown Supplier Briefing\n- Direct Factory Email Draft", f"{c_box}fillColor=#FFFFFF;strokeColor=#C5A880;fontColor=#151C22;", 70, 680, 320, 85, "c_client")
    add_cell("c1_cert", "Digital Certificate of FEI Compliance\n- Official Landscape A4 Document\n- Olympic Regulatory Verification Seal\n- Double Gold Border Layout", f"{c_box}fillColor=#ECFDF5;strokeColor=#047857;fontColor=#065F46;fontStyle=1;", 70, 790, 320, 85, "c_client")
    add_cell("c1_api_client", "Centralized Typed API Client\n(frontend/src/lib/api.ts)", f"{c_box}fillColor=#0C1F16;strokeColor=#C5A880;fontColor=#C5A880;fontStyle=1;", 70, 900, 320, 50, "c_client")

    # 3. Swimlane 2: API & Gateway Tier (FastAPI)
    add_cell("c_api", "GATEWAY & ORCHESTRATION TIER (FastAPI / Python 3.12)", f"{c_swimlane}fillColor=#FBFBF9;strokeColor=#163828;fontColor=#163828;", 450, 120, 360, 960)
    add_cell("c2_audit_router", "POST /api/audit/upload\nPOST /api/audit/sample\nGET  /api/audit/{id}\nGET  /api/audit/{id}/certificate", f"{c_box}fillColor=#FFFFFF;strokeColor=#163828;fontColor=#151C22;fontFamily=Courier;", 480, 180, 300, 90, "c_api")
    add_cell("c2_rules_router", "GET    /api/rules\nPOST   /api/rules (Add Custom)\nPUT    /api/rules/{id}\nDELETE /api/rules/{id}\nPOST   /api/rules/search", f"{c_box}fillColor=#FFFFFF;strokeColor=#047857;fontColor=#151C22;fontFamily=Courier;fontStyle=1;", 480, 310, 300, 105, "c_api")
    add_cell("c2_vendor_router", "POST /api/vendor/action-plan\nGET  /api/vendor/export-notes\nPOST /api/vendor/export-notes", f"{c_box}fillColor=#FFFFFF;strokeColor=#163828;fontColor=#151C22;fontFamily=Courier;", 480, 455, 300, 80, "c_api")
    add_cell("c2_coordinator", "Audit Coordinator Engine\n(backend/app/engine/audit_coordinator.py)\n- End-to-End Audit Orchestration\n- Strict <30s SLA Enforcement\n- Audit Run History Serialization", f"{c_box}fillColor=#0C1F16;strokeColor=#C5A880;fontColor=#FFFFFF;fontStyle=1;", 480, 580, 300, 100, "c_api")
    add_cell("c2_cert_gen", "Official Certificate PDF Engine\n(backend/app/api/audit_router.py)\n- PyMuPDF Vector Drawing\n- Olympic Verification Seals\n- A4 Landscape Print Ready", f"{c_box}fillColor=#ECFDF5;strokeColor=#047857;fontColor=#065F46;fontStyle=1;", 480, 720, 300, 90, "c_api")
    add_cell("c2_vendor_gen", "Vendor Notes Generator\n(backend/app/api/vendor_router.py)\n- Letterhead PDF & Markdown Exporter", f"{c_box}fillColor=#FFFFFF;strokeColor=#C5A880;fontColor=#151C22;", 480, 850, 300, 75, "c_api")

    # 4. Swimlane 3: Multi-Modal Ingestion & Structuring Pipeline
    add_cell("c_ingest", "MULTI-MODAL INGESTION & STRUCTURING", f"{c_swimlane}fillColor=#FBFBF9;strokeColor=#163828;fontColor=#163828;", 840, 120, 420, 460)
    add_cell("c3_parser", "PyMuPDF4LLM Markdown Parser\n- Single-Pass Vector & Text Extraction\n- Page Boundary Markers & Typography", f"{c_box}fillColor=#FFFFFF;strokeColor=#163828;fontColor=#151C22;", 870, 180, 360, 65, "c_ingest")
    add_cell("c3_ocr", "RapidOCR ONNX Runtime Fallback\n- Density Gate: Activated Only on Scanned Pages\n- Zero Latency Overhead on Digital PDFs", f"{c_box}fillColor=#FFFFFF;strokeColor=#C5A880;fontColor=#151C22;", 870, 260, 360, 65, "c_ingest")
    add_cell("c3_table", "Deterministic Table Extractor\n(pdfplumber + Heuristic Layout Parser)\n- BOM Tables & Material Compositions\n- POM Point of Measure Dimensions", f"{c_box}fillColor=#FFFFFF;strokeColor=#163828;fontColor=#151C22;", 870, 340, 360, 75, "c_ingest")
    add_cell("c3_cropper", "Image & Figure Cropper (image_cropper.py)\n- Crops Technical Flat Sketches & Emblems\n- High-Res PNG Figures for Inspector UI", f"{c_box}fillColor=#FFFFFF;strokeColor=#163828;fontColor=#151C22;", 870, 430, 360, 65, "c_ingest")
    add_cell("c3_struct", "Gemini Extraction & Structuring Service\n- Google GenAI (Gemini 1.5/2.0 Flash) / Mock Engine\n- Pydantic TechPackSpec Schema Enforcement", f"{c_box}fillColor=#0C1F16;strokeColor=#C5A880;fontColor=#C5A880;fontStyle=1;", 870, 510, 360, 60, "c_ingest")

    # 5. Swimlane 4: Hybrid RAG & Knowledge Retrieval Tier
    add_cell("c_rag", "HYBRID KNOWLEDGE & RAG RETRIEVAL TIER", f"{c_swimlane}fillColor=#FBFBF9;strokeColor=#163828;fontColor=#163828;", 840, 610, 420, 470)
    add_cell("c4_catalog", "Codified Regulatory Catalog JSON\n(backend/app/knowledge/regulatory_catalog.json)\n- FEI Jumping Rules Art. 256\n- FEI Dressage Rules Art. 427\n- FEI Eventing Rules Art. 538\n- Maison Équestre Brand SOPs", f"{c_box}fillColor=#FFFFFF;strokeColor=#047857;fontColor=#151C22;fontStyle=1;", 870, 670, 360, 95, "c_rag")
    add_cell("c4_vector", "Qdrant Vector Database Engine\n- Local Persistent On-Disk / Memory Storage\n- HNSW Indexing for Dense Semantic Chunks", f"{c_box}fillColor=#FFFFFF;strokeColor=#163828;fontColor=#151C22;", 870, 785, 360, 70, "c_rag")
    add_cell("c4_embed", "Hybrid Embedder & Search Engine\n(backend/app/rag/retriever.py)\n- FastEmbed / Sentence-Transformers (384-dim)\n- BM25 Exact Keyword Match for Rule Articles\n- Reciprocal Rank Fusion (RRF) Reranking", f"{c_box}fillColor=#0C1F16;strokeColor=#C5A880;fontColor=#FFFFFF;fontStyle=1;", 870, 875, 360, 95, "c_rag")
    add_cell("c4_crud", "Live Rule CRUD & Syncer Service\n- In-Memory Update without Server Restart\n- Real-Time Validation & Conflict Prevention", f"{c_box}fillColor=#ECFDF5;strokeColor=#047857;fontColor=#065F46;fontStyle=1;", 870, 990, 360, 65, "c_rag")

    # 6. Swimlane 5: Deterministic Verifier & Audit Scoring Engine
    add_cell("c_verify", "DETERMINISTIC VERIFIER GATE & VERDICT ENGINE", f"{c_swimlane}fillColor=#FBFBF9;strokeColor=#163828;fontColor=#163828;", 1290, 120, 370, 960)
    add_cell("c5_spec_model", "Validated TechPackSpec Instance\n- Style, Discipline, Season Metadata\n- POM Dimensions (cm, mm, tolerances)\n- Embroidery Logos & Surface Areas\n- Bill of Materials & Cost Ceilings", f"{c_box}fillColor=#FFFFFF;strokeColor=#163828;fontColor=#151C22;fontFamily=Courier;", 1320, 180, 310, 100, "c_verify")
    add_cell("c5_engine", "Deterministic Rule Engine\n(backend/app/verifier/rule_engine.py)\n- Mathematical Operators (<=, >=, ==, in)\n- Unit Conversions (cm², %, EUR, mm)\n- Zero LLM Hallucinations in Math", f"{c_box}fillColor=#0C1F16;strokeColor=#C5A880;fontColor=#FFFFFF;fontStyle=1;", 1320, 310, 310, 95, "c_verify")
    add_cell("c5_ground", "Verbatim Citation Grounding Gate\n- Links Every Violation to Legal Text\n- 100% Traceability to FEI Rulebooks\n- Eliminates False Violations", f"{c_box}fillColor=#ECFDF5;strokeColor=#047857;fontColor=#065F46;fontStyle=1;", 1320, 435, 310, 95, "c_verify")
    add_cell("c5_score", "Audit Scorecard Aggregator\n- Overall Score Calculation (%)\n- Category Breakdown (Branding, Materials, POM)\n- Status Verdict: PASS | WARNING | VIOLATION", f"{c_box}fillColor=#FFFFFF;strokeColor=#C5A880;fontColor=#151C22;", 1320, 560, 310, 95, "c_verify")
    add_cell("c5_remedy", "Supplier Remediation Generator\n(backend/app/verifier/remediation.py)\n- Exact Delta Overage Calculations\n- Downscale Scaling Instructions\n- Commercial Variance Alerts", f"{c_box}fillColor=#FFFFFF;strokeColor=#163828;fontColor=#151C22;", 1320, 685, 310, 95, "c_verify")
    add_cell("c5_verified_payload", "Verified Findings Payload\n- VerifiedFinding Objects\n- Target Bounding Boxes for UI\n- Execution Timers & Memory Footprint", f"{c_box}fillColor=#0C1F16;strokeColor=#C5A880;fontColor=#C5A880;fontStyle=1;", 1320, 810, 310, 90, "c_verify")

    # 7. Connectors & Data Flow Edges
    # User -> Client UI
    add_edge("e_user_split", "Uploads PDF", c_edge, "c1_user", "c1_split")
    add_edge("e_split_api", "Invokes API", c_edge, "c1_split", "c1_api_client", [(230, 880)])

    # Client API Client -> FastAPI Audit Router
    add_edge("e_api_upload", "POST /api/audit/upload", c_edge, "c1_api_client", "c2_audit_router", [(410, 925), (410, 225)])

    # Client Rules Modal -> FastAPI Rules Router
    add_edge("e_rules_crud", "CRUD /api/rules", c_edge, "c1_rules", "c2_rules_router", [(420, 612), (420, 362)])

    # Audit Router -> Coordinator
    add_edge("e_router_coord", "Orchestrates", c_edge, "c2_audit_router", "c2_coordinator")

    # Coordinator -> Ingestion Pipeline
    add_edge("e_coord_ingest", "Extracts Document", c_edge, "c2_coordinator", "c3_parser", [(810, 630), (810, 212)])

    # Ingestion flow: Parser -> OCR fallback -> Table -> Cropper -> Structuring
    add_edge("e_parse_ocr", "Raster fallback", c_edge, "c3_parser", "c3_ocr")
    add_edge("e_ocr_table", "Normalized Text", c_edge, "c3_ocr", "c3_table")
    add_edge("e_table_crop", "BOM & POM Data", c_edge, "c3_table", "c3_cropper")
    add_edge("e_crop_struct", "Figures & Tables", c_edge, "c3_cropper", "c3_struct")

    # Structuring -> TechPackSpec Model
    add_edge("e_struct_model", "Extracts Spec", c_edge, "c3_struct", "c5_spec_model", [(1270, 540), (1270, 230)])

    # Structuring -> Hybrid RAG Search
    add_edge("e_struct_rag", "Queries Relevant Rules", c_edge, "c3_struct", "c4_embed", [(1050, 580), (1050, 875)])

    # Rules Router -> Catalog CRUD
    add_edge("e_router_crud", "Live Rule Updates", c_edge, "c2_rules_router", "c4_crud", [(820, 362), (820, 1022)])
    add_edge("e_crud_catalog", "Persists Catalog", c_edge, "c4_crud", "c4_catalog", [(850, 1022), (850, 717)])

    # Qdrant & Embedder -> Catalog
    add_edge("e_catalog_vector", "Indexes Rules", c_edge, "c4_catalog", "c4_vector")
    add_edge("e_vector_embed", "Retrieves Embeddings", c_edge, "c4_vector", "c4_embed")

    # Hybrid RAG & Spec -> Deterministic Verifier Engine
    add_edge("e_rag_verifier", "Candidate Rule Chunks", c_edge, "c4_embed", "c5_engine", [(1280, 922), (1280, 357)])
    add_edge("e_spec_verifier", "Normalized Measurements", c_edge, "c5_spec_model", "c5_engine")

    # Verifier Engine -> Grounding Gate -> Scoring -> Remediation -> Verified Payload
    add_edge("e_engine_ground", "Evaluates Delta", c_edge, "c5_engine", "c5_ground")
    add_edge("e_ground_score", "100% Verified Citations", c_edge, "c5_ground", "c5_score")
    add_edge("e_score_remedy", "Flags & Overages", c_edge, "c5_score", "c5_remedy")
    add_edge("e_remedy_payload", "Generates Action Plan", c_edge, "c5_remedy", "c5_verified_payload")

    # Verified Payload -> Coordinator
    add_edge("e_payload_coord", "Returns Scorecard", c_edge, "c5_verified_payload", "c2_coordinator", [(1270, 855), (1270, 640), (810, 640)])

    # Coordinator -> Certificate Generator & Vendor Generator
    add_edge("e_coord_cert", "Audit Passed / Verified", c_edge, "c2_coordinator", "c2_cert_gen")
    add_edge("e_coord_vendor", "Action Plan Data", c_edge, "c2_coordinator", "c2_vendor_gen")

    # Coordinator -> Client Scorecard UI
    add_edge("e_coord_ui", "0.35s Sub-Second Response", c_edge, "c2_coordinator", "c1_scorecard", [(440, 630), (440, 402)])

    # Certificate & Vendor -> UI Exporters
    add_edge("e_cert_ui", "Download A4 PDF", c_edge, "c2_cert_gen", "c1_cert")
    add_edge("e_vendor_ui", "Action Modal Export", c_edge, "c2_vendor_gen", "c1_vendor")

    xml.append('      </root>')
    xml.append('    </mxGraphModel>')
    xml.append('  </diagram>')
    xml.append('</mxfile>')
    return '\n'.join(xml)

# -----------------------------------------------------------------------------
# 2. Standalone SVG Generator matching DayuanJiang/next-ai-draw-io
# -----------------------------------------------------------------------------
def build_animated_svg():
    width = 1720
    height = 1120

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="{width}px" height="{height}px" viewBox="0 0 {width} {height}" style="background-color: #F8F9FA; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif;">',
        '  <defs>',
        '    <style>',
        '      @keyframes ge-flow-animation {',
        '        to {',
        '          stroke-dashoffset: -32;',
        '        }',
        '      }',
        '      .flow-path {',
        '        stroke-dasharray: 8 6;',
        '        animation: ge-flow-animation 1.2s linear infinite;',
        '      }',
        '      .gold-flow {',
        '        stroke: #9E7E50;',
        '        stroke-width: 2.5;',
        '        fill: none;',
        '      }',
        '      .green-flow {',
        '        stroke: #047857;',
        '        stroke-width: 2.5;',
        '        fill: none;',
        '      }',
        '      .node-card {',
        '        rx: 8px;',
        '        ry: 8px;',
        '        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.04));',
        '      }',
        '      .swimlane-title {',
        '        font-family: Georgia, serif;',
        '        font-size: 13px;',
        '        font-weight: bold;',
        '        letter-spacing: 0.5px;',
        '      }',
        '      .node-title {',
        '        font-size: 12px;',
        '        font-weight: bold;',
        '        fill: #151C22;',
        '      }',
        '      .node-desc {',
        '        font-size: 10.5px;',
        '        fill: #4A5560;',
        '        line-height: 1.3;',
        '      }',
        '      .code-font {',
        '        font-family: Consolas, monospace;',
        '        font-size: 10.5px;',
        '      }',
        '    </style>',
        '    <marker id="arrow-gold" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#9E7E50" />',
        '    </marker>',
        '    <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#047857" />',
        '    </marker>',
        '  </defs>',
    ]

    # Header Title Banner
    svg.append('  <!-- Header Title Banner -->')
    svg.append('  <rect x="40" y="25" width="1640" height="70" rx="10" fill="#0C1F16" stroke="#C5A880" stroke-width="2" />')
    svg.append('  <text x="860" y="54" fill="#C5A880" font-family="Georgia, serif" font-size="18" font-weight="bold" text-anchor="middle" letter-spacing="1">MAISON ÉQUESTRE ATELIER PRO : OLYMPIC EQUESTRIAN COMPLIANCE AUDITOR</text>')
    svg.append('  <text x="860" y="76" fill="#FBFBF9" font-size="11.5" text-anchor="middle" letter-spacing="0.5">High-Precision Multi-Modal Technical Specification Ingestion, Hybrid Qdrant RAG, and Sub-Second Deterministic Verifier Engine</text>')

    # Helper function for rendering swimlanes
    def render_swimlane(x, y, w, h, title, subtitle):
        t_esc = saxutils.escape(title)
        st_esc = saxutils.escape(subtitle)
        res = [
            f'  <!-- Swimlane: {t_esc} -->',
            f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#FBFBF9" stroke="#163828" stroke-width="2" />',
            f'  <path d="M {x} {y+40} L {x+w} {y+40}" stroke="#E2E4E1" stroke-width="1.5" />',
            f'  <text x="{x+18}" y="{y+25}" class="swimlane-title" fill="#163828">{t_esc}</text>',
            f'  <text x="{x+w-18}" y="{y+25}" font-size="11" fill="#9E7E50" text-anchor="end" font-weight="600">{st_esc}</text>',
        ]
        return '\n'.join(res)

    # 1. Swimlane 1: Client & Presentation
    svg.append(render_swimlane(40, 115, 380, 965, "PRESENTATION & CLIENT TIER", "Next.js 14 App Router"))
    
    # 2. Swimlane 2: API & Gateway
    svg.append(render_swimlane(440, 115, 360, 965, "API & ORCHESTRATION TIER", "FastAPI / Python 3.12"))

    # 3. Swimlane 3: Multi-Modal Ingestion
    svg.append(render_swimlane(820, 115, 420, 465, "MULTI-MODAL INGESTION ENGINE", "PyMuPDF4LLM + RapidOCR"))

    # 4. Swimlane 4: Hybrid RAG & Knowledge
    svg.append(render_swimlane(820, 600, 420, 480, "HYBRID KNOWLEDGE & RAG RETRIEVAL", "Qdrant DB & BM25"))

    # 5. Swimlane 5: Deterministic Verifier & Scorecard Engine
    svg.append(render_swimlane(1260, 115, 420, 965, "DETERMINISTIC VERIFIER GATE", "Zero False-Positive Engine"))

    # Render Node Cards
    def render_card(x, y, w, h, title, lines, fill="#FFFFFF", stroke="#C5A880", title_color="#151C22", is_code=False, badge=None):
        t_esc = saxutils.escape(title)
        res = [
            f'  <g transform="translate({x}, {y})">',
            f'    <rect width="{w}" height="{h}" class="node-card" fill="{fill}" stroke="{stroke}" stroke-width="1.5" />',
        ]
        if badge:
            bx, by, bw, bh, btext, bbg, btc = badge
            bt_esc = saxutils.escape(btext)
            res.append(f'    <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="4" fill="{bbg}" />')
            res.append(f'    <text x="{bx+bw/2}" y="{by+bh/2+3.5}" font-size="9" font-weight="bold" fill="{btc}" text-anchor="middle">{bt_esc}</text>')

        res.append(f'    <text x="16" y="24" class="node-title" fill="{title_color}">{t_esc}</text>')
        curr_y = 42
        for line in lines:
            font_cls = "code-font" if is_code else "node-desc"
            l_esc = saxutils.escape(line)
            res.append(f'    <text x="16" y="{curr_y}" class="{font_cls}">{l_esc}</text>')
            curr_y += 16
        res.append('  </g>')
        return '\n'.join(res)

    # Presentation Tier Cards
    svg.append(render_card(60, 175, 340, 65, "Senior Technical Designer", ["Olympic Equestrian Technical Wear Sourcing", "Direct Tech Pack PDF Ingestion"], fill="#FFFFFF", stroke="#163828"))
    svg.append(render_card(60, 260, 340, 75, "Split-Screen Technical Flat Viewer", ["Synchronized Technical Canvas & BOM Viewer", "Collar & Chest Highlighted Inspection Zones", "Page Jumping (POM, BOM, Branding)"], fill="#FFFFFF", stroke="#C5A880"))
    svg.append(render_card(60, 355, 340, 85, "Luxury Compliance Audit Scorecard", ["Overall Compliance Score KPI (71.4%)", "Sub-Second Response Badge: 0.35s SLA", "Category Progress Bars (Materials, POM, Logo)"], fill="#FFFFFF", stroke="#C5A880", badge=(245, 10, 80, 20, "0.35s SLA", "#ECFDF5", "#047857")))
    svg.append(render_card(60, 460, 340, 80, "Verbatim Citation & Gate Modal", ["FEI Official Rulebook Quotation Card", "Observed vs Allowed Tolerance Math", "Zero False-Positive Trust Seal Badge"], fill="#FFFFFF", stroke="#C5A880"))
    svg.append(render_card(60, 560, 340, 90, "Dynamic Regulatory Rules Modal", ["Live Rule Search & Multi-Discipline Tabs", "+ Add Custom Brand Rule Form Active", "Delete Deprecated SOPs in Real Time"], fill="#FFFFFF", stroke="#047857", title_color="#047857", badge=(240, 10, 85, 20, "CRUD ACTIVE", "#ECFDF5", "#047857")))
    svg.append(render_card(60, 670, 340, 85, "Supplier Action Plan & Export Modal", ["Official Supplier Letterhead PDF Download", "Executive Markdown Remediation Package", "Pre-formatted Factory Email Dispatch"], fill="#FFFFFF", stroke="#C5A880"))
    svg.append(render_card(60, 775, 340, 85, "Digital Certificate of FEI Compliance", ["Official A4 Landscape Certificate PDF", "Olympic Regulatory Verdict & Seal", "Double Gold Border Luxury Styling"], fill="#ECFDF5", stroke="#047857", title_color="#065F46", badge=(235, 10, 90, 20, "VERIFIED A4", "#D1FAE5", "#065F46")))
    svg.append(render_card(60, 880, 340, 50, "Centralized Typed API Client", ["frontend/src/lib/api.ts (Strict TypeScript)"], fill="#0C1F16", stroke="#C5A880", title_color="#C5A880"))

    # API Gateway Cards
    svg.append(render_card(460, 175, 320, 100, "Audit Router (POST /api/audit)", ["POST /api/audit/upload (PDF Parse)", "POST /api/audit/sample (Instant Mock)", "GET  /api/audit/{id} (State)", "GET  /api/audit/{id}/certificate (A4 PDF)"], fill="#FFFFFF", stroke="#163828", is_code=True))
    svg.append(render_card(460, 295, 320, 115, "Dynamic Rules Router (/api/rules)", ["GET    /api/rules (Catalog List)", "POST   /api/rules (Create Custom Rule)", "PUT    /api/rules/{id} (Update)", "DELETE /api/rules/{id} (Remove)", "POST   /api/rules/search (Hybrid Search)"], fill="#FFFFFF", stroke="#047857", is_code=True, title_color="#047857"))
    svg.append(render_card(460, 430, 320, 85, "Vendor Router (/api/vendor)", ["POST /api/vendor/action-plan", "GET  /api/vendor/export-notes (PDF)", "POST /api/vendor/export-notes"], fill="#FFFFFF", stroke="#163828", is_code=True))
    svg.append(render_card(460, 535, 320, 105, "Audit Coordinator Engine", ["backend/app/engine/audit_coordinator.py", "- Multi-Stage Execution Pipeline", "- Sub-30s Strict SLA Monitoring", "- Ingestion -> Structuring -> RAG -> Verifier"], fill="#0C1F16", stroke="#C5A880", title_color="#FFFFFF"))
    svg.append(render_card(460, 660, 320, 90, "Official Certificate Generator", ["backend/app/api/audit_router.py", "- PyMuPDF Vector Document Assembly", "- Double Gold Border & Olympic Seal", "- High-Res Print Export (<0.15s)"], fill="#ECFDF5", stroke="#047857", title_color="#065F46"))
    svg.append(render_card(460, 770, 320, 85, "Vendor Letterhead Generator", ["backend/app/api/vendor_router.py", "- Formatted Supplier Correction Notices", "- Exact Embroidery Reduction Specs"], fill="#FFFFFF", stroke="#C5A880"))

    # Ingestion Engine Cards
    svg.append(render_card(840, 175, 380, 65, "PyMuPDF4LLM Markdown Parser", ["Single-Pass Layout, Font & Structural Extraction", "Generates Page Boundary Anchors for UI Sync"], fill="#FFFFFF", stroke="#163828"))
    svg.append(render_card(840, 255, 380, 65, "RapidOCR ONNX Runtime Fallback", ["Activated selectively on rasterized/scanned pages", "Zero latency overhead on digital vector PDFs"], fill="#FFFFFF", stroke="#C5A880"))
    svg.append(render_card(840, 335, 380, 80, "Deterministic Table Extractor", ["pdfplumber + Heuristic Layout Table Parsing", "- Bill of Materials (BOM) & Material Blends", "- Points of Measure (POM) Dimension Tables"], fill="#FFFFFF", stroke="#163828"))
    svg.append(render_card(840, 430, 380, 65, "Image & Figure Cropper", ["Extracts technical flats and collar/chest emblems", "Persists PNG assets to backend/storage/figures/"], fill="#FFFFFF", stroke="#163828"))
    svg.append(render_card(840, 510, 380, 60, "Gemini Extraction & Structuring", ["Google GenAI (Gemini 2.0 Flash) / High-Speed Mock", "Pydantic TechPackSpec Schema Enforcement"], fill="#0C1F16", stroke="#C5A880", title_color="#C5A880"))

    # RAG Knowledge Cards
    svg.append(render_card(840, 660, 380, 95, "Codified Regulatory Rule Catalog", ["backend/app/knowledge/regulatory_catalog.json", "- FEI Jumping Art. 256 (Collar, Pocket, Surface)", "- FEI Dressage Art. 427 (Jacket Colors, Tailcoat)", "- FEI Eventing Art. 538 & Maison Brand SOPs"], fill="#FFFFFF", stroke="#047857", title_color="#047857"))
    svg.append(render_card(840, 775, 380, 75, "Qdrant Vector Database Engine", ["Local Persistent On-Disk Vector Storage", "HNSW Indexing for Dense Semantic Embeddings", "Filtered payload queries by discipline"], fill="#FFFFFF", stroke="#163828"))
    svg.append(render_card(840, 870, 380, 95, "Hybrid RAG Retriever (retriever.py)", ["FastEmbed / Sentence-Transformers (384-dim)", "+ BM25 Exact Keyword Match for Rule Articles", "+ Reciprocal Rank Fusion (RRF) Reranking", "= 100% Verbatim Precision, Zero Hallucinations"], fill="#0C1F16", stroke="#C5A880", title_color="#FFFFFF"))
    svg.append(render_card(840, 985, 380, 65, "Live Rule CRUD & Syncer Service", ["Immediate catalog sync without server restart", "Dynamic conflict checking & validation"], fill="#ECFDF5", stroke="#047857", title_color="#065F46"))

    # Verifier Engine Cards
    svg.append(render_card(1280, 175, 380, 95, "Validated TechPackSpec Instance", ["Structured Pydantic Model Data:", "- Style Code, Garment Type, Discipline", "- Measurements & Points of Measure (cm, tol)", "- Materials, Lining Silk %, Fabric Weight (GSM)", "- Embroidery Logo Dimensions (68cm² vs 60cm²)"], fill="#FFFFFF", stroke="#163828", is_code=True))
    svg.append(render_card(1280, 290, 380, 95, "Deterministic Rule Engine (rule_engine.py)", ["Pure Python Mathematical Verification (<=, >=, ==, in)", "Automated Unit Normalization (cm² to mm², EUR, %)", "Evaluates 100% of codified rules in <10ms", "Zero LLM Hallucinations in Mathematical Decisions"], fill="#0C1F16", stroke="#C5A880", title_color="#FFFFFF"))
    svg.append(render_card(1280, 405, 380, 95, "Verbatim Citation Grounding Gate", ["Cross-references every finding against legal rulebooks", "Enforces 100% verbatim quotes from FEI Articles", "Guarantees zero false-positive disqualifications", "Links exact source rulebook and article references"], fill="#ECFDF5", stroke="#047857", title_color="#065F46", badge=(260, 10, 105, 20, "ZERO FALSE +", "#D1FAE5", "#065F46")))
    svg.append(render_card(1280, 520, 380, 90, "Audit Scorecard Aggregator", ["Computes weighted category scores (0 - 100%)", "Evaluates final status: PASS | WARNING | VIOLATION", "Measures execution latency (sub-second SLA)", "Builds VerifiedFinding array with bounding boxes"], fill="#FFFFFF", stroke="#C5A880"))
    svg.append(render_card(1280, 630, 380, 95, "Supplier Remediation Generator", ["Calculates exact overage deltas (+8cm² / +13.3%)", "Generates downscale instructions for embroidery files", "Commercial tolerance & cost variance alerts", "Formulates actionable vendor notes"], fill="#FFFFFF", stroke="#163828"))
    svg.append(render_card(1280, 745, 380, 85, "Verified Findings Payload", ["AuditScorecard Response Object", "Embedded Findings, Verbatim Quotes & Remedies", "Persisted in-memory audit history run logs"], fill="#0C1F16", stroke="#C5A880", title_color="#C5A880"))

    # Flow Connectors (Animated SVG Paths with Markers)
    def render_flow(d, is_green=False, marker="arrow-gold"):
        cls = "green-flow" if is_green else "gold-flow"
        stroke = "#047857" if is_green else "#9E7E50"
        m_id = "arrow-green" if is_green else "arrow-gold"
        return f'  <path d="{d}" class="flow-path {cls}" fill="none" stroke="{stroke}" stroke-width="2.5" marker-end="url(#{m_id})" />'

    svg.append('  <!-- Animated Flow Connectors -->')
    # User -> Client Viewer
    svg.append(render_flow("M 230 240 L 230 260"))
    # Split Viewer -> API Client
    svg.append(render_flow("M 230 335 L 230 355"))
    svg.append(render_flow("M 230 860 L 230 880"))

    # Client -> Audit Router
    svg.append(render_flow("M 400 905 L 430 905 L 430 225 L 460 225"))

    # Client -> Rules Router (CRUD)
    svg.append(render_flow("M 400 605 L 430 605 L 430 350 L 460 350", is_green=True))

    # Audit Router -> Coordinator
    svg.append(render_flow("M 620 275 L 620 535"))

    # Coordinator -> Ingestion Pipeline
    svg.append(render_flow("M 780 575 L 810 575 L 810 205 L 840 205"))

    # Ingestion steps
    svg.append(render_flow("M 1030 240 L 1030 255"))
    svg.append(render_flow("M 1030 320 L 1030 335"))
    svg.append(render_flow("M 1030 415 L 1030 430"))
    svg.append(render_flow("M 1030 495 L 1030 510"))

    # Structuring -> Spec Instance
    svg.append(render_flow("M 1220 540 L 1250 540 L 1250 220 L 1280 220"))

    # Structuring -> Hybrid RAG Retrieval
    svg.append(render_flow("M 1030 570 L 1030 660"))

    # Rules Router -> Live Rule CRUD & Syncer
    svg.append(render_flow("M 780 370 L 810 370 L 810 1015 L 840 1015", is_green=True))
    svg.append(render_flow("M 1030 985 L 1030 965"))

    # Qdrant & Embedder -> Rules Catalog
    svg.append(render_flow("M 1030 755 L 1030 775"))
    svg.append(render_flow("M 1030 850 L 1030 870"))

    # RAG Retriever -> Deterministic Verifier Engine
    svg.append(render_flow("M 1220 915 L 1250 915 L 1250 335 L 1280 335"))

    # Spec Instance -> Verifier Engine
    svg.append(render_flow("M 1470 270 L 1470 290"))

    # Verifier Internal Pipeline
    svg.append(render_flow("M 1470 385 L 1470 405", is_green=True))
    svg.append(render_flow("M 1470 500 L 1470 520"))
    svg.append(render_flow("M 1470 610 L 1470 630"))
    svg.append(render_flow("M 1470 725 L 1470 745"))

    # Verified Payload -> Coordinator
    svg.append(render_flow("M 1280 785 L 1245 785 L 1245 615 L 780 615"))

    # Coordinator -> Certificate & Vendor Generator
    svg.append(render_flow("M 620 640 L 620 660", is_green=True))
    svg.append(render_flow("M 620 750 L 620 770"))

    # Coordinator -> Client Scorecard UI
    svg.append(render_flow("M 460 595 L 430 595 L 430 400 L 400 400"))

    # Certificate & Vendor Generator -> Client Modals
    svg.append(render_flow("M 460 705 L 430 705 L 430 815 L 400 815", is_green=True))
    svg.append(render_flow("M 460 810 L 420 810 L 420 710 L 400 710"))

    # Legend at bottom right
    svg.append('  <!-- Legend -->')
    svg.append('  <g transform="translate(1320, 875)">')
    svg.append('    <rect width="320" height="175" rx="8" fill="#FFFFFF" stroke="#E2E4E1" stroke-width="1.5" />')
    svg.append('    <text x="16" y="24" font-family="Georgia, serif" font-size="12" font-weight="bold" fill="#163828">SYSTEM PIPELINE LEGEND</text>')
    svg.append('    <line x1="16" y1="45" x2="55" y2="45" class="flow-path gold-flow" />')
    svg.append('    <text x="65" y="49" class="node-desc">Standard Data & Audit Pipeline Flow</text>')
    svg.append('    <line x1="16" y1="75" x2="55" y2="75" class="flow-path green-flow" />')
    svg.append('    <text x="65" y="79" class="node-desc">Dynamic Rules CRUD & Verbatim Verification</text>')
    svg.append('    <rect x="16" y="98" width="14" height="14" rx="3" fill="#0C1F16" stroke="#C5A880" />')
    svg.append('    <text x="40" y="110" class="node-desc">Core AI & Deterministic Engine Nodes</text>')
    svg.append('    <rect x="16" y="125" width="14" height="14" rx="3" fill="#ECFDF5" stroke="#047857" />')
    svg.append('    <text x="40" y="137" class="node-desc">Official FEI Verification & A4 Certificate</text>')
    svg.append('  </g>')

    svg.append('</svg>')
    return '\n'.join(svg)

def main():
    print("Generating native draw.io XML diagram...")
    xml_content = build_drawio_xml()
    drawio_path = os.path.join(OUTPUT_DIR, "system_architecture.drawio")
    with open(drawio_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"Saved: {drawio_path}")

    print("Generating animated SVG diagram matching next-ai-draw-io...")
    svg_content = build_animated_svg()
    svg_path = os.path.join(OUTPUT_DIR, "system_architecture.drawio.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Saved: {svg_path}")

    # Also save to frontend public for in-app viewing
    public_svg_path = os.path.join(PUBLIC_DIR, "system_architecture.svg")
    with open(public_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Saved: {public_svg_path}")

if __name__ == "__main__":
    main()
