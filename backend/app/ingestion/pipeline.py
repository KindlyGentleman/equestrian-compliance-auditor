"""Unified Document Ingestion Pipeline coordinating text parsing, OCR fallback, table extraction, and image cropping."""
import time
from pathlib import Path

import psutil
import pymupdf
from pydantic import BaseModel, Field

from backend.app.ingestion.image_cropper import ExtractedFigure, ImageCropper, image_cropper
from backend.app.ingestion.ocr_fallback import OCRFallback, ocr_fallback
from backend.app.ingestion.pdf_parser import DocumentContent, PageContent, PDFParser, pdf_parser
from backend.app.ingestion.table_extractor import ExtractedTable, TableExtractor, table_extractor


class IngestionStageTiming(BaseModel):
    """Execution timing breakdown across ingestion stages in seconds."""
    pdf_parse_seconds: float = 0.0
    ocr_seconds: float = 0.0
    table_extraction_seconds: float = 0.0
    figure_extraction_seconds: float = 0.0
    total_seconds: float = 0.0


class IngestionResult(BaseModel):
    """Comprehensive structured payload returned by the unified ingestion pipeline."""
    file_name: str
    total_pages: int
    full_markdown: str
    pages: list[PageContent]
    tables: list[ExtractedTable] = Field(default_factory=list)
    figures: list[ExtractedFigure] = Field(default_factory=list)
    ocr_pages_triggered: list[int] = Field(default_factory=list)
    timings: IngestionStageTiming
    peak_memory_mb: float = 0.0


class IngestionPipeline:
    """Master ingestion coordinator executing sub-3s extraction on technical tech packs."""

    def __init__(
        self,
        parser: PDFParser | None = None,
        table_ext: TableExtractor | None = None,
        cropper: ImageCropper | None = None,
        ocr: OCRFallback | None = None,
        char_threshold: int = 30,
    ):
        self.parser = parser or pdf_parser
        self.table_extractor = table_ext or table_extractor
        self.cropper = cropper or image_cropper
        self.ocr = ocr or ocr_fallback
        self.char_threshold = char_threshold

    def process(
        self,
        pdf_path: str | Path,
        extract_tables: bool = True,
        extract_figures: bool = True,
        force_ocr: bool = False,
    ) -> IngestionResult:
        """Run complete ingestion: single-pass text parse, selective OCR fallback, table normalization, and figure extraction."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        process = psutil.Process()
        mem_before = process.memory_info().rss / (1024 * 1024)
        overall_start = time.time()

        # Stage 1: Fast PyMuPDF4LLM Markdown parsing
        t0 = time.time()
        doc_content: DocumentContent = self.parser.parse(path, use_ocr=False)
        parse_elapsed = time.time() - t0

        # Stage 2: Selective OCR Fallback on blank/rasterized pages
        t0 = time.time()
        ocr_pages_triggered: list[int] = []
        pages_needing_ocr: list[int] = []
        for p in doc_content.pages:
            cleaned_text = "".join(p.markdown.split())
            if len(cleaned_text) < self.char_threshold or force_ocr:
                pages_needing_ocr.append(p.page_number)

        if pages_needing_ocr:
            doc = pymupdf.open(str(path))
            try:
                for page_num in pages_needing_ocr:
                    page_idx = page_num - 1
                    if page_idx < len(doc):
                        ocr_res = self.ocr.ocr_page(doc[page_idx], page_number=page_num)
                        if ocr_res.text.strip():
                            doc_content.pages[page_idx].markdown = ocr_res.markdown
                            doc_content.pages[page_idx].char_count = len(ocr_res.text)
                            ocr_pages_triggered.append(page_num)
            finally:
                doc.close()

            # Rebuild full markdown if any pages were updated by OCR
            if ocr_pages_triggered:
                full_md_parts = [
                    f"<!-- PAGE {p.page_number} START -->\n{p.markdown}\n<!-- PAGE {p.page_number} END -->"
                    for p in doc_content.pages
                ]
                doc_content.full_markdown = "\n\n".join(full_md_parts)

        ocr_elapsed = time.time() - t0

        # Stage 3: Structured Table Extraction & Normalization
        t0 = time.time()
        tables: list[ExtractedTable] = []
        if extract_tables:
            table_result = self.table_extractor.extract_tables(path)
            tables = table_result.tables
        table_elapsed = time.time() - t0

        # Stage 4: Figure and Artwork Cropping with Bounding Boxes
        t0 = time.time()
        figures: list[ExtractedFigure] = []
        if extract_figures:
            figure_result = self.cropper.extract_figures(path)
            figures = figure_result.figures
        figure_elapsed = time.time() - t0

        total_elapsed = time.time() - overall_start
        mem_after = process.memory_info().rss / (1024 * 1024)
        peak_memory = max(mem_before, mem_after)

        timings = IngestionStageTiming(
            pdf_parse_seconds=round(parse_elapsed, 4),
            ocr_seconds=round(ocr_elapsed, 4),
            table_extraction_seconds=round(table_elapsed, 4),
            figure_extraction_seconds=round(figure_elapsed, 4),
            total_seconds=round(total_elapsed, 4),
        )

        return IngestionResult(
            file_name=path.name,
            total_pages=doc_content.total_pages,
            full_markdown=doc_content.full_markdown,
            pages=doc_content.pages,
            tables=tables,
            figures=figures,
            ocr_pages_triggered=ocr_pages_triggered,
            timings=timings,
            peak_memory_mb=round(peak_memory, 2),
        )


ingestion_pipeline = IngestionPipeline()
