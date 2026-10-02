import logging
import re
from pathlib import Path

import pymupdf
from pydantic import BaseModel, Field

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class ExtractedFigure(BaseModel):
    """Metadata and cache path for an extracted technical illustration or logo."""
    figure_id: str
    page_number: int
    bounding_box: list[float] = Field(description="[x0, y0, x1, y1] on PDF canvas")
    width_px: int
    height_px: int
    file_path: str
    figure_type: str = Field(default="SKETCH", description="SKETCH, LOGO, SWATCH, or DIAGRAM")


class ImageCropperResult(BaseModel):
    """Aggregate result of figure extraction across a tech pack PDF."""
    total_figures: int
    figures: list[ExtractedFigure]


class ImageCropper:
    """Extracts, crops, and caches technical sketches and logos from PDF pages."""

    def __init__(self, output_dir: str | None = None, min_size: int = 80):
        self.output_dir = Path(output_dir or settings.FIGURE_EXPORT_DIR)
        self.min_size = min_size
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_figures(self, pdf_path: str | Path) -> ImageCropperResult:
        """Extract embedded figures and technical drawings with page coordinates."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        doc = pymupdf.open(str(path))
        extracted_figures: list[ExtractedFigure] = []

        max_figures = 50
        try:
            for page_idx in range(len(doc)):
                if len(extracted_figures) >= max_figures:
                    logger.warning("Reached maximum figure extraction limit (%d); halting extraction", max_figures)
                    break
                page = doc[page_idx]
                page_num = page_idx + 1
                image_list = page.get_images(full=True)

                for img_idx, img_info in enumerate(image_list):
                    if len(extracted_figures) >= max_figures:
                        break
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    width = base_image["width"]
                    height = base_image["height"]
                    ext = base_image["ext"]

                    # Filter out tiny icon artifacts
                    if width < self.min_size or height < self.min_size:
                        continue

                    # Get bounding box on page
                    rects = page.get_image_rects(xref)
                    bbox = [round(c, 2) for c in rects[0]] if rects else [0.0, 0.0, float(width), float(height)]

                    fig_id = f"fig_p{page_num}_{img_idx + 1}"
                    safe_stem = re.sub(r"[^\w\-]", "_", path.stem)
                    fig_filename = f"{safe_stem}_{fig_id}.{ext}"
                    fig_path = self.output_dir / fig_filename

                    with open(fig_path, "wb") as f:
                        f.write(image_bytes)

                    # Classify based on aspect ratio & size
                    aspect_ratio = width / max(height, 1)
                    if 0.7 <= aspect_ratio <= 1.4 and width > 200:
                        fig_type = "SKETCH"
                    elif aspect_ratio > 1.8 and width < 400:
                        fig_type = "LOGO"
                    else:
                        fig_type = "DIAGRAM"

                    extracted_figures.append(
                        ExtractedFigure(
                            figure_id=fig_id,
                            page_number=page_num,
                            bounding_box=bbox,
                            width_px=width,
                            height_px=height,
                            file_path=str(fig_path),
                            figure_type=fig_type,
                        )
                    )

            return ImageCropperResult(
                total_figures=len(extracted_figures),
                figures=extracted_figures,
            )
        finally:
            doc.close()


image_cropper = ImageCropper()
