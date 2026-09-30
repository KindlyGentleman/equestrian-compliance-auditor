"""Canonical sample tech pack PDF generator for instant client demonstrations."""
import io
from pathlib import Path
from PIL import Image
import pymupdf


def create_sample_techpack_pdf(output_path: Path) -> Path:
    """Create a realistic 10-page luxury equestrian show jacket tech pack PDF."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    sketch = Image.new("RGB", (300, 300), color=(245, 243, 238))
    sketch_bytes = io.BytesIO()
    sketch.save(sketch_bytes, format="PNG")

    doc = pymupdf.open()
    pages_data = [
        ("Cover Page", "STYLE CODE: ME-2026-SJ01\nSTYLE NAME: Grand Prix Show Coat\nDISCIPLINE: Show Jumping\nSEASON: Spring/Summer 2026\nGARMENT TYPE: Show Jacket\nGENDER: Women's\nDIVISION: Luxury Performance Equestrian"),
        ("Technical Flat Sketches", "FRONT AND BACK TECHNICAL SKETCHES WITH CONTOURED WAIST FIT\nNotched lapel with custom collar insert\nDual back vents with internal stay stitch\nFour-button front closure with concealed zip underlay"),
        ("Bill of Materials (BOM)", "BILL OF MATERIALS SPECIFICATION:\nMain Shell Fabric: 78% Polyamide 22% Elastane ($18.50/m)\nCollar Velvet: 100% Italian Cotton Velvet ($4.20/m)\nButtons: 4 Matte Horn Monogram Buttons ($3.80/set)\nThread: High-tenacity bonded nylon stretch thread ($1.20)"),
        ("Fabric Technical Data", "FABRIC TECHNICAL SPECIFICATION:\nPRIMARY COMPOSITION: 78% Polyamide, 22% Elastane\nFABRIC WEIGHT: 295 GSM\nBREATHABILITY: 14000 g/m²/24h\nWATER RESISTANCE: 5000 mm\nSTRETCH: 24% Weft, 18% Warp\nFINISH: Water-repellent and soil-resistant fluorocarbon-free DWR"),
        ("Points of Measure (POM)", "POM MEASUREMENTS (SIZE 38):\nPOM-01 Collar Stand Height: 4.5 cm (Tolerance: +/- 0.5 cm)\nPOM-02 Chest Width Across: 46.0 cm (Tolerance: +/- 0.75 cm)\nPOM-03 Waist Width: 39.5 cm (Tolerance: +/- 0.75 cm)\nPOM-04 Sleeve Length from Shoulder: 62.0 cm (Tolerance: +/- 1.0 cm)\nPOM-05 Center Back Length: 68.0 cm (Tolerance: +/- 1.0 cm)"),
        ("Branding & Emblem Placement", "BRANDING & EMBLEM SPECIFICATION:\nCollar Logo: Left Collar Stand, Dimensions: 6.0 cm x 8.0 cm (Area: 48.0 cm²)\nChest Emblem: Left Pocket, Dimensions: 10.0 cm x 12.0 cm (Area: 120.0 cm²)\nSleeve Monogram: Right Arm, Dimensions: 4.0 cm x 5.0 cm (Area: 20.0 cm²)\nFEI Compliance Verified: All logo areas comply with FEI Art. 256.3 limits"),
        ("Aesthetics & Trims", "AESTHETICS & TRIMS:\nCollar Type: Notched Lapel with Tonal Velvet Collar\nPiping: 3.0 mm Satin Piping along Lapel and Pocket Flaps\nButtons: 4 Front Monogram Buttons\nCuff: 3 Horn decorative sleeve buttons per cuff"),
        ("Construction Details", "SEAM SPECIFICATION & STITCHING:\n4-thread safety stitch with stretch thread\nReinforced taped lapel edges and clean internal bound seams\nVent tack bar reinforcement at upper vent stress points"),
        ("Labeling & Packaging", "CARE & PACKAGING SPECIFICATION:\nCARE LABEL: 30°C Gentle Machine Wash or Professional Dry Clean\nHanger: Branded Walnut Finish Hanger with Brass Hook\nGarment Bag: Breathable cotton twill travel garment bag"),
        ("Commercial Costing & Sign-Off", "COMMERCIAL COSTING BREAKDOWN:\nFABRIC COST: $28.50 USD\nTRIM & HARDWARE: $11.30 USD\nCMT (CUT, MAKE, TRIM): $14.00 USD\nTOTAL ACTUAL FOB: $53.80 USD\nTARGET FOB CEILING: $55.00 USD\nRECOMMENDED RETAIL PRICE: $480.00 USD\nSTATUS: Approved for SS26 Production Sample Run"),
    ]

    for title, text in pages_data:
        page = doc.new_page(width=595, height=842)
        # Header banner
        page.insert_text((50, 50), "MAISON ÉQUESTRE", fontsize=16, fontname="helv", color=(0.09, 0.22, 0.16))
        page.insert_text((50, 72), f"TECHNICAL SPECIFICATION PACKAGE - {title.upper()}", fontsize=11, fontname="helv", color=(0.4, 0.4, 0.4))
        page.draw_line((50, 85), (545, 85), color=(0.8, 0.75, 0.65), width=1)
        
        # Body text
        page.insert_text((50, 120), text, fontsize=10, fontname="helv", color=(0.15, 0.18, 0.22))
        
        # Sketch placeholder box
        page.insert_image(pymupdf.Rect(380, 110, 530, 260), stream=sketch_bytes.getvalue())
        page.draw_rect(pymupdf.Rect(380, 110, 530, 260), color=(0.85, 0.85, 0.85), width=0.5)
        
        # Footer
        page.draw_line((50, 800), (545, 800), color=(0.9, 0.9, 0.9), width=0.5)
        page.insert_text((50, 815), "CONFIDENTIAL - PROPERTY OF MAISON ÉQUESTRE ATELIER PRO", fontsize=8, fontname="helv", color=(0.6, 0.6, 0.6))
        page.insert_text((500, 815), f"Page {page.number + 1} of 10", fontsize=8, fontname="helv", color=(0.6, 0.6, 0.6))

    doc.save(str(output_path))
    doc.close()
    return output_path
