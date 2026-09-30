"""RapidOCR-ONNX fallback parser for scanned/rasterized tech pack pages."""
import time

import pymupdf
from pydantic import BaseModel
from rapidocr_onnxruntime import RapidOCR


class OCRLine(BaseModel):
    text: str
    confidence: float
    box: list[list[float]]


class OCRPageResult(BaseModel):
    page_number: int
    text: str
    markdown: str
    average_confidence: float
    line_count: int
    execution_time_seconds: float


class OCRFallback:
    """CPU-optimized ONNX fallback engine for pages with zero/low selectable text."""

    def __init__(self, char_threshold: int = 30):
        self.char_threshold = char_threshold
        self._engine: RapidOCR | None = None

    @property
    def engine(self) -> RapidOCR:
        """Lazily initialize RapidOCR ONNX model."""
        if self._engine is None:
            self._engine = RapidOCR()
        return self._engine

    def is_scanned_page(self, page_text: str) -> bool:
        """Determine if page has negligible digital text and needs OCR."""
        cleaned = "".join(page_text.split())
        return len(cleaned) < self.char_threshold

    def ocr_page(self, page: pymupdf.Page, page_number: int = 1, dpi: int = 150) -> OCRPageResult:
        """Render page to image pixmap and run RapidOCR."""
        start_time = time.time()
        pixmap = page.get_pixmap(dpi=dpi)
        img_bytes = pixmap.tobytes("png")

        results, _ = self.engine(img_bytes)

        if not results:
            elapsed = time.time() - start_time
            return OCRPageResult(
                page_number=page_number,
                text="",
                markdown="",
                average_confidence=0.0,
                line_count=0,
                execution_time_seconds=round(elapsed, 4),
            )

        lines: list[OCRLine] = []
        text_lines: list[str] = []
        confidences: list[float] = []

        for item in results:
            # item structure: [box, text, confidence]
            box = item[0]
            text = str(item[1]).strip()
            conf = float(item[2])

            lines.append(OCRLine(text=text, confidence=conf, box=box))
            text_lines.append(text)
            confidences.append(conf)

        avg_conf = sum(confidences) / max(len(confidences), 1)
        full_text = "\n".join(text_lines)
        markdown_text = "\n\n".join(text_lines)
        elapsed = time.time() - start_time

        return OCRPageResult(
            page_number=page_number,
            text=full_text,
            markdown=markdown_text,
            average_confidence=round(avg_conf, 4),
            line_count=len(text_lines),
            execution_time_seconds=round(elapsed, 4),
        )


ocr_fallback = OCRFallback()
