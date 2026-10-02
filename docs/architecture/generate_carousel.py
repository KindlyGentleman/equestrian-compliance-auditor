"""
Maison Équestre Atelier Pro - LinkedIn Carousel Generator (Option A)
Produces:
1. 6 High-Resolution 4:5 Slide Images (1080 x 1350 px) in docs/architecture/carousel_slides/
2. Multi-Page LinkedIn PDF Document in docs/architecture/linkedin_carousel.pdf
"""
import os
from PIL import Image, ImageDraw, ImageFont
import pymupdf

OUTPUT_DIR = r"d:\03_Proyek\RAG Testing\docs\architecture"
SLIDES_DIR = os.path.join(OUTPUT_DIR, "carousel_slides")
os.makedirs(SLIDES_DIR, exist_ok=True)

WIDTH, HEIGHT = 1080, 1350

# Fonts
FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 46)
FONT_SECTION = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 32)
FONT_H3 = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 25)
FONT_BODY = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
FONT_BODY_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
FONT_SMALL_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 16)
FONT_CODE = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 19)
FONT_CODE_BOLD = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 20)
FONT_METRIC_NUM = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 44)
FONT_METRIC_LABEL = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)

# Colors
C_BG = "#0C1812"
C_CARD_BG = "#13231B"
C_CARD_BORDER = "#253B2F"
C_CARD_DARK = "#09120D"
C_GOLD = "#C5A880"
C_GOLD_LIGHT = "#E2D2BC"
C_TEXT_WHITE = "#F5F6F3"
C_TEXT_MUTED = "#98A99E"
C_TEXT_FAINT = "#5B7063"

C_GREEN = "#10B981"
C_GREEN_BG = "#064E3B"
C_GREEN_BORDER = "#047857"

C_RED = "#EF4444"
C_RED_BG = "#450A0A"
C_RED_BORDER = "#991B1B"

C_AMBER = "#F59E0B"
C_AMBER_BG = "#451A03"
C_AMBER_BORDER = "#B45309"


def draw_rounded_card(draw, rect, fill, outline, radius=16, width=1):
    x, y, w, h = rect
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=outline, width=width)


def draw_badge(draw, xy, text, bg_color, text_color, font=FONT_SMALL_BOLD, border_color=None, pad_x=14, pad_y=6):
    x, y = xy
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bw, bh = tw + pad_x * 2, th + pad_y * 2
    draw.rounded_rectangle([x, y, x + bw, y + bh], radius=bh // 2, fill=bg_color, outline=border_color or bg_color, width=1)
    draw.text((x + pad_x, y + pad_y - bbox[1]), text, fill=text_color, font=font)
    return bw, bh


def draw_wrapped_text(draw, xy, text, font, fill, max_width, line_spacing=6):
    x, y = xy
    words = text.split(" ")
    lines = []
    curr_line = []
    for word in words:
        test_line = " ".join(curr_line + [word])
        bbox = font.getbbox(test_line)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            curr_line.append(word)
        else:
            if curr_line:
                lines.append(" ".join(curr_line))
                curr_line = [word]
            else:
                lines.append(word)
                curr_line = []
    if curr_line:
        lines.append(" ".join(curr_line))

    curr_y = y
    for line in lines:
        bbox = font.getbbox(line)
        h = bbox[3] - bbox[1]
        draw.text((x, curr_y), line, fill=fill, font=font)
        curr_y += h + line_spacing
    return curr_y


def draw_header(draw, slide_idx, total_slides, tag_text):
    # Brand line
    draw.text((80, 70), "MAISON ÉQUESTRE ATELIER PRO", fill=C_GOLD, font=FONT_SMALL_BOLD)
    # Counter
    counter_str = f"0{slide_idx} / 0{total_slides}"
    c_bbox = FONT_CODE_BOLD.getbbox(counter_str)
    c_w = c_bbox[2] - c_bbox[0]
    draw.text((WIDTH - 80 - c_w, 68), counter_str, fill=C_GOLD_LIGHT, font=FONT_CODE_BOLD)
    # Divider line
    draw.line([(80, 105), (WIDTH - 80, 105)], fill=C_CARD_BORDER, width=1)
    # Category tag badge
    draw_badge(draw, (80, 130), tag_text.upper(), C_CARD_BG, C_GOLD, font=FONT_SMALL_BOLD, border_color=C_CARD_BORDER, pad_x=16, pad_y=6)


def draw_footer(draw, is_last=False):
    draw.line([(80, HEIGHT - 95), (WIDTH - 80, HEIGHT - 95)], fill=C_CARD_BORDER, width=1)
    draw.text((80, HEIGHT - 70), "High-Stakes Olympic Equestrian Compliance Auditor", fill=C_TEXT_FAINT, font=FONT_SMALL)
    if is_last:
        action_text = "GITHUB: KindlyGentleman/equestrian-compliance-auditor"
        a_bbox = FONT_SMALL_BOLD.getbbox(action_text)
        a_w = a_bbox[2] - a_bbox[0]
        draw.text((WIDTH - 80 - a_w, HEIGHT - 70), action_text, fill=C_GOLD, font=FONT_SMALL_BOLD)
    else:
        swipe_text = "SWIPE  -->"
        s_bbox = FONT_CODE_BOLD.getbbox(swipe_text)
        s_w = s_bbox[2] - s_bbox[0]
        draw.text((WIDTH - 80 - s_w, HEIGHT - 70), swipe_text, fill=C_GOLD_LIGHT, font=FONT_CODE_BOLD)


# -----------------------------------------------------------------------------
# SLIDE 1: The Hook & Olympic Disqualification Stakes
# -----------------------------------------------------------------------------
def build_slide_1():
    img = Image.new("RGB", (WIDTH, HEIGHT), color=C_BG)
    draw = ImageDraw.Draw(img)
    draw_header(draw, 1, 6, "01 / High-Stakes Compliance")

    draw.text((80, 185), "Why a 2mm piping error\ncan disqualify an Olympic rider", fill=C_TEXT_WHITE, font=FONT_TITLE, spacing=8)
    draw.text((80, 310), "In high-performance equestrian wear, garments are governed as regulated\nathletic equipment by the Fédération Équestre Internationale (FEI).", fill=C_TEXT_MUTED, font=FONT_BODY, spacing=6)

    # Main Card: Spec Breakdown with Violations
    draw_rounded_card(draw, (80, 395, 920, 680), C_CARD_BG, C_CARD_BORDER, radius=18)

    draw.text((120, 425), "GARMENT SPECIFICATION: Sovereign Grand Prix Coat", fill=C_GOLD, font=FONT_H3)
    draw.text((120, 465), "Discipline: Olympic Show Jumping  |  Material: 75% Polyamide, 25% Elastane", fill=C_TEXT_MUTED, font=FONT_SMALL)
    draw.line([(120, 500), (960, 500)], fill=C_CARD_BORDER, width=1)

    # Finding 1 (Violation)
    draw_rounded_card(draw, (120, 525, 840, 155), C_CARD_DARK, C_RED_BORDER, radius=12)
    draw_badge(draw, (145, 545), "DISQUALIFICATION RISK", C_RED_BG, C_RED, FONT_SMALL_BOLD, C_RED_BORDER)
    draw.text((380, 547), "FEI Jumping Rules, Art. 256.1.4", fill=C_TEXT_MUTED, font=FONT_SMALL)
    draw.text((145, 590), "Collar Sponsor Logo Area: 65.0 cm²", fill=C_TEXT_WHITE, font=FONT_H3)
    draw.text((145, 630), "Regulatory Ceiling: <= 60.0 cm²   |   Delta Overage: +5.0 cm² (+8.3%)", fill=C_RED, font=FONT_BODY_BOLD)

    # Finding 2 (Violation)
    draw_rounded_card(draw, (120, 705, 840, 155), C_CARD_DARK, C_RED_BORDER, radius=12)
    draw_badge(draw, (145, 725), "DISQUALIFICATION RISK", C_RED_BG, C_RED, FONT_SMALL_BOLD, C_RED_BORDER)
    draw.text((380, 727), "FEI Dressage Rules, Art. 427.1", fill=C_TEXT_MUTED, font=FONT_SMALL)
    draw.text((145, 770), "Collar Velvet Piping Width: 3.5 mm", fill=C_TEXT_WHITE, font=FONT_H3)
    draw.text((145, 810), "Regulatory Ceiling: <= 3.0 mm    |   Delta Overage: +0.5 mm (+16.7%)", fill=C_RED, font=FONT_BODY_BOLD)

    # Finding 3 (Passing)
    draw_rounded_card(draw, (120, 885, 840, 95), C_CARD_DARK, C_GREEN_BORDER, radius=12)
    draw_badge(draw, (145, 915), "PASS", C_GREEN_BG, C_GREEN, FONT_SMALL_BOLD, C_GREEN_BORDER)
    draw.text((230, 917), "Fabric Breathability: 12,000 g/m²/24h (SOP threshold: >= 10,000)", fill=C_TEXT_WHITE, font=FONT_BODY)
    draw.text((230, 945), "Hydrostatic Head: 4,000 mm (Water resistant athletic standard)", fill=C_TEXT_MUTED, font=FONT_SMALL)

    # Bottom Callout Banner
    draw_rounded_card(draw, (120, 1005, 840, 50), C_CARD_DARK, C_GOLD, radius=8)
    draw.text((140, 1018), "Manual Tech Pack Audit: 2 to 4 hours   ->   Atelier Pro: < 0.35 seconds", fill=C_GOLD_LIGHT, font=FONT_BODY_BOLD)

    draw_footer(draw)
    return img


# -----------------------------------------------------------------------------
# SLIDE 2: The Architectural Trap (Why Probabilistic LLMs Fail)
# -----------------------------------------------------------------------------
def build_slide_2():
    img = Image.new("RGB", (WIDTH, HEIGHT), color=C_BG)
    draw = ImageDraw.Draw(img)
    draw_header(draw, 2, 6, "02 / The AI Trap")

    draw.text((80, 185), "Why LLMs fail at\nhigh-stakes compliance math", fill=C_TEXT_WHITE, font=FONT_TITLE, spacing=8)
    draw.text((80, 310), "Probabilistic token predictors hallucinate mathematical bounds and invent fake\nrules. In athletic regulations, you cannot bet an Olympic career on probabilities.", fill=C_TEXT_MUTED, font=FONT_BODY, spacing=6)

    col_w = 445
    # Left Column: Pure LLM / AI Wrapper
    draw_rounded_card(draw, (80, 395, col_w, 680), "#181111", C_RED_BORDER, radius=18)
    draw_badge(draw, (110, 425), "GENERIC AI WRAPPER", C_RED_BG, C_RED, FONT_SMALL_BOLD, C_RED_BORDER)
    draw.text((110, 475), "Prompting an LLM Directly", fill=C_TEXT_WHITE, font=FONT_H3)

    items_wrapper = [
        ("Fuzzy Math", "Decides 65 cm² is 'close enough' to 60 cm² based on conversational training weights."),
        ("Article Hallucination", "Quotes nonexistent rules (e.g. 'FEI Art. 302.4') that sound authoritative but do not exist."),
        ("Non-Deterministic", "Running the exact same tech pack three times produces conflicting compliance verdicts."),
        ("High Latency & Cost", "Spends 15 to 30 seconds reading entire PDFs via expensive multi-shot prompt chaining.")
    ]

    curr_y = 525
    for title, desc in items_wrapper:
        draw.text((110, curr_y), "X", fill=C_RED, font=FONT_H3)
        draw.text((140, curr_y), title, fill=C_TEXT_WHITE, font=FONT_BODY_BOLD)
        draw_wrapped_text(draw, (140, curr_y + 30), desc, FONT_SMALL, C_TEXT_MUTED, max_width=355, line_spacing=4)
        curr_y += 125

    # Right Column: Atelier Pro Hybrid Engine
    draw_rounded_card(draw, (555, 395, col_w, 680), "#0F2017", C_GREEN_BORDER, radius=18)
    draw_badge(draw, (585, 425), "DETERMINISTIC VERIFIER", C_GREEN_BG, C_GREEN, FONT_SMALL_BOLD, C_GREEN_BORDER)
    draw.text((585, 475), "Our Dual-Layer Architecture", fill=C_TEXT_WHITE, font=FONT_H3)

    items_our = [
        ("Decoupled Perception", "Gemini 2.0 Flash is used solely for visual extraction into strict Pydantic schemas."),
        ("Pure Python Math", "A mathematical engine (< 10ms) executes exact <=, >=, and tolerance delta math."),
        ("Verbatim Citation Gate", "Every violation is anchored to verbatim rulebook text. Unanchored flags are downgraded."),
        ("Sub-Second Latency", "Completes ingestion, hybrid retrieval, and full audit verification in < 0.35 seconds.")
    ]

    curr_y = 525
    for title, desc in items_our:
        draw.text((585, curr_y), "/", fill=C_GREEN, font=FONT_H3)
        draw.text((615, curr_y), title, fill=C_TEXT_WHITE, font=FONT_BODY_BOLD)
        draw_wrapped_text(draw, (615, curr_y + 30), desc, FONT_SMALL, C_TEXT_MUTED, max_width=355, line_spacing=4)
        curr_y += 125

    draw_footer(draw)
    return img


# -----------------------------------------------------------------------------
# SLIDE 3: The 5-Stage System Architecture
# -----------------------------------------------------------------------------
def build_slide_3():
    img = Image.new("RGB", (WIDTH, HEIGHT), color=C_BG)
    draw = ImageDraw.Draw(img)
    draw_header(draw, 3, 6, "03 / System Blueprint")

    draw.text((80, 185), "The 5-stage hybrid\ncompliance pipeline", fill=C_TEXT_WHITE, font=FONT_TITLE, spacing=8)
    draw.text((80, 310), "Decoupling probabilistic extraction from deterministic verification\nguarantees zero false positives with sub-second execution.", fill=C_TEXT_MUTED, font=FONT_BODY, spacing=6)

    stages = [
        ("01", "MULTI-MODAL INGESTION", "PyMuPDF4LLM + RapidOCR ONNX", "Ingests 10 to 30 page tech pack PDFs. Extracts layout tables, dimensions, bill of materials (BOM), and crops technical flats.", C_GOLD),
        ("02", "SCHEMA STRUCTURING", "Gemini 2.0 Flash + Pydantic v2", "Normalizes unstructured garment data into strongly-typed TechPackSpec models with strict unit conversions (cm, mm, GSM, FOB).", C_GOLD),
        ("03", "REGULATORY KNOWLEDGE BASE", "Embedded Qdrant + BM25 Hybrid RAG", "Dense semantic embeddings (FastEmbed 384-dim) combined with exact article BM25 keyword matching and Reciprocal Rank Fusion.", C_GREEN),
        ("04", "DETERMINISTIC VERIFIER GATE", "Pure Python Verification Engine (< 10ms)", "Calculates mathematical differences against FEI limits. Validates verbatim legal citations to eliminate false-positive flags.", C_GREEN),
        ("05", "SCORECARD & VENDOR ACTIONS", "Next.js 14 Atelier Pro UI", "Instant split-screen inspection with highlighted garment flats, delta reduction specs, and exportable A4 compliance certificates.", C_GOLD)
    ]

    card_y = 390
    card_h = 130
    spacing = 14

    for num, tag, subtitle, desc, accent_color in stages:
        draw_rounded_card(draw, (80, card_y, 920, card_h), C_CARD_BG, C_CARD_BORDER, radius=14)
        
        # Left Accent Box & Number
        draw_rounded_card(draw, (95, card_y + 15, 60, card_h - 30), C_CARD_DARK, C_CARD_BORDER, radius=8)
        draw.text((108, card_y + 35), num, fill=accent_color, font=FONT_H3)

        # Title
        draw.text((175, card_y + 16), tag, fill=C_TEXT_WHITE, font=FONT_H3)
        # Tech Badge on the right
        draw_badge(draw, (WIDTH - 80 - 325, card_y + 14), subtitle, C_CARD_DARK, accent_color, font=FONT_SMALL_BOLD, border_color=C_CARD_BORDER, pad_x=12, pad_y=4)

        # Description wrapped
        draw_wrapped_text(draw, (175, card_y + 55), desc, FONT_SMALL, C_TEXT_MUTED, max_width=710, line_spacing=4)

        card_y += card_h + spacing

    draw_footer(draw)
    return img


# -----------------------------------------------------------------------------
# SLIDE 4: Real Case Study & Proof
# -----------------------------------------------------------------------------
def build_slide_4():
    img = Image.new("RGB", (WIDTH, HEIGHT), color=C_BG)
    draw = ImageDraw.Draw(img)
    draw_header(draw, 4, 6, "04 / Case Study & Proof")

    draw.text((80, 185), "Auditing a 15-page tech pack\nin 350 milliseconds", fill=C_TEXT_WHITE, font=FONT_TITLE, spacing=8)
    draw.text((80, 310), "Demonstrated on the Sovereign Grand Prix Competition Coat against\nofficial FEI Jumping and Dressage regulations.", fill=C_TEXT_MUTED, font=FONT_BODY, spacing=6)

    m_w = 290
    m_h = 135
    metrics = [
        ("0.35s", "EXECUTION LATENCY", "Sub-second turnaround SLA"),
        ("54 / 54", "AUTOMATED TESTS", "Unit, integration & benchmarks"),
        ("0.0%", "FALSE POSITIVE RATE", "Verbatim citation verified")
    ]

    for i, (val, label, sub) in enumerate(metrics):
        mx = 80 + i * (m_w + 25)
        draw_rounded_card(draw, (mx, 395, m_w, m_h), C_CARD_BG, C_CARD_BORDER, radius=14)
        draw.text((mx + 25, 415), val, fill=C_GOLD, font=FONT_METRIC_NUM)
        draw.text((mx + 25, 475), label, fill=C_TEXT_WHITE, font=FONT_SMALL_BOLD)
        draw.text((mx + 25, 497), sub, fill=C_TEXT_MUTED, font=FONT_SMALL)

    # Case Findings Box
    draw_rounded_card(draw, (80, 560, 920, 515), C_CARD_BG, C_CARD_BORDER, radius=18)
    draw.text((120, 585), "AUDIT FINDINGS & SUPPLIER REMEDIATION", fill=C_GOLD, font=FONT_H3)
    draw.line([(120, 625), (960, 625)], fill=C_CARD_BORDER, width=1)

    findings = [
        ("Collar Sponsor Logo Area", "65.0 cm²", "60.0 cm²", "Over by +5.0 cm²", "Downscale embroidery template by 7.7% before production run."),
        ("Lapel Contrast Velvet Piping", "3.5 mm", "3.0 mm", "Over by +0.5 mm", "Substitute with 2.5 mm gold satin piping trim code TP-2026."),
        ("Factory Quoted FOB Cost", "$62.00", "$55.00", "Variance +$7.00", "Commercial variance flag sent to Sourcing Lead for supplier negotiation.")
    ]

    fy = 645
    for name, observed, limit, delta, action in findings:
        draw_rounded_card(draw, (120, fy, 840, 118), C_CARD_DARK, C_CARD_BORDER, radius=12)
        draw.text((140, fy + 15), name, fill=C_TEXT_WHITE, font=FONT_BODY_BOLD)
        draw.text((140, fy + 45), f"Observed: {observed}   |   Regulatory Ceiling: {limit}", fill=C_TEXT_MUTED, font=FONT_SMALL)
        draw_badge(draw, (685, fy + 14), delta, C_RED_BG, C_RED, FONT_SMALL_BOLD, C_RED_BORDER)
        draw.text((140, fy + 78), f"Remediation: {action}", fill=C_GOLD_LIGHT, font=FONT_SMALL)
        fy += 132

    draw_footer(draw)
    return img


# -----------------------------------------------------------------------------
# SLIDE 5: The Enterprise Stack & Reliability
# -----------------------------------------------------------------------------
def build_slide_5():
    img = Image.new("RGB", (WIDTH, HEIGHT), color=C_BG)
    draw = ImageDraw.Draw(img)
    draw_header(draw, 5, 6, "05 / The Tech Stack")

    draw.text((80, 185), "Engineered for speed,\nprivacy, and determinism", fill=C_TEXT_WHITE, font=FONT_TITLE, spacing=8)
    draw.text((80, 310), "Built with modern Python and TypeScript without bloated external cloud dependencies.\nRuns 100% locally or inside hardened Docker containers.", fill=C_TEXT_MUTED, font=FONT_BODY, spacing=6)

    cw, ch = 445, 210
    techs = [
        ("FastAPI & Python 3.12", "BACKEND API LAYER", "High-throughput async execution, strict Pydantic v2 schemas, automated OpenAPI documentation, and < 10ms execution."),
        ("Next.js 14 App Router", "FRONTEND INTERFACE", "Luxury split-screen desktop experience, synchronized technical flats, SVG inspection bounding boxes, and Quiet Luxury UI tokens."),
        ("Qdrant Vector DB", "EMBEDDED HYBRID RAG", "Local persistent on-disk vector store with HNSW indexing and BM25 exact keyword matching for zero cloud dependency."),
        ("Gemini 2.0 Flash", "MULTI-MODAL EXTRACTION", "Fast multimodal parsing for complex technical flat drawings, structured JSON generation, and aesthetic evaluation."),
        ("PyMuPDF4LLM + ONNX", "INGESTION & OCR", "Sub-second extraction of layout tables and vector sketches with RapidOCR fallback strictly for scanned pages."),
        ("Pytest & Docker CI", "TESTING & DEVOPS", "54 automated unit, integration, and benchmark tests with multi-stage non-root containerization.")
    ]

    for i, (title, role, desc) in enumerate(techs):
        row = i // 2
        col = i % 2
        cx = 80 + col * (cw + 30)
        cy = 395 + row * (ch + 20)

        draw_rounded_card(draw, (cx, cy, cw, ch), C_CARD_BG, C_CARD_BORDER, radius=14)
        draw_badge(draw, (cx + 25, cy + 20), role, C_CARD_DARK, C_GOLD, FONT_SMALL_BOLD, C_CARD_BORDER)
        draw.text((cx + 25, cy + 58), title, fill=C_TEXT_WHITE, font=FONT_H3)
        draw_wrapped_text(draw, (cx + 25, cy + 98), desc, FONT_SMALL, C_TEXT_MUTED, max_width=395, line_spacing=4)

    draw_footer(draw)
    return img


# -----------------------------------------------------------------------------
# SLIDE 6: Production Blueprint & Takeaway
# -----------------------------------------------------------------------------
def build_slide_6():
    img = Image.new("RGB", (WIDTH, HEIGHT), color=C_BG)
    draw = ImageDraw.Draw(img)
    draw_header(draw, 6, 6, "06 / Production Blueprint")

    draw.text((80, 185), "3 core lessons for\nproduction AI engineering", fill=C_TEXT_WHITE, font=FONT_TITLE, spacing=8)
    draw.text((80, 310), "How to design AI applications when compliance failure is not an option.", fill=C_TEXT_MUTED, font=FONT_BODY, spacing=6)

    lessons = [
        ("01", "LLMs for Perception, Code for Governance", "Use neural networks where data is messy: PDF layouts, sketches, and natural language. Use deterministic code where logic is critical: legal thresholds, finances, and tolerances. Never let an LLM do arithmetic."),
        ("02", "Verifier Gates Beat Prompt Engineering", "Prompting an LLM to 'be accurate and strictly follow rules' is a brittle band-aid. Instead, structure model output with Pydantic and pass it through a hardcoded verification gate."),
        ("03", "Ground Every Decision with Verbatim Citations", "If a regulatory violation cannot be traced to exact verbatim text in the codified rulebook, downgrade it automatically to manual review. Eliminating false positives creates user trust.")
    ]

    ly = 395
    lh = 180
    for num, headline, explanation in lessons:
        draw_rounded_card(draw, (80, ly, 920, lh), C_CARD_BG, C_CARD_BORDER, radius=16)
        
        # Left Number
        draw_rounded_card(draw, (105, ly + 25, 55, lh - 50), C_CARD_DARK, C_CARD_BORDER, radius=8)
        draw.text((118, ly + 45), num, fill=C_GOLD, font=FONT_H3)

        draw.text((180, ly + 22), headline, fill=C_TEXT_WHITE, font=FONT_H3)
        draw_wrapped_text(draw, (180, ly + 62), explanation, FONT_BODY, C_TEXT_MUTED, max_width=700, line_spacing=5)
        ly += lh + 20

    # Bottom Open Source CTA Card
    draw_rounded_card(draw, (80, 990, 920, 95), C_CARD_DARK, C_GOLD, radius=12)
    draw.text((110, 1008), "Open-Source Implementation on GitHub:", fill=C_TEXT_MUTED, font=FONT_SMALL)
    draw.text((110, 1038), "github.com/KindlyGentleman/equestrian-compliance-auditor", fill=C_GOLD_LIGHT, font=FONT_BODY_BOLD)

    draw_footer(draw, is_last=True)
    return img


# -----------------------------------------------------------------------------
# Main Generator & PDF Assembler
# -----------------------------------------------------------------------------
def main():
    print("Generating LinkedIn Carousel slides (1080x1350)...")
    slides = [
        ("slide_1.png", build_slide_1()),
        ("slide_2.png", build_slide_2()),
        ("slide_3.png", build_slide_3()),
        ("slide_4.png", build_slide_4()),
        ("slide_5.png", build_slide_5()),
        ("slide_6.png", build_slide_6()),
    ]

    slide_paths = []
    for filename, img in slides:
        path = os.path.join(SLIDES_DIR, filename)
        img.save(path, quality=95)
        slide_paths.append(path)
        print(f"Saved: {path}")

    # Compile Multi-Page PDF for LinkedIn Document Carousel
    pdf_path = os.path.join(OUTPUT_DIR, "linkedin_carousel.pdf")
    doc = pymupdf.open()
    for sp in slide_paths:
        page = doc.new_page(width=WIDTH, height=HEIGHT)
        page.insert_image(page.rect, filename=sp)

    doc.save(pdf_path, deflate=True, garbage=4, clean=True)
    doc.close()
    print(f"\nSuccessfully created multi-page LinkedIn PDF Carousel:")
    print(f"PDF: {pdf_path} (Size: {os.path.getsize(pdf_path)} bytes)")
    print(f"Slides Directory: {SLIDES_DIR}")


if __name__ == "__main__":
    main()
