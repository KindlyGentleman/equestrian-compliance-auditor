"""Document ingestion, layout OCR, and table extraction."""
from backend.app.ingestion.image_cropper import (
    ExtractedFigure,
    ImageCropper,
    ImageCropperResult,
    image_cropper,
)
from backend.app.ingestion.ocr_fallback import OCRFallback, OCRPageResult, ocr_fallback
from backend.app.ingestion.pdf_parser import DocumentContent, PageContent, PDFParser, pdf_parser
from backend.app.ingestion.pipeline import (
    IngestionPipeline,
    IngestionResult,
    IngestionStageTiming,
    ingestion_pipeline,
)
from backend.app.ingestion.table_extractor import (
    ExtractedTable,
    TableExtractionResult,
    TableExtractor,
    table_extractor,
)

__all__ = [
    "PDFParser",
    "PageContent",
    "DocumentContent",
    "pdf_parser",
    "TableExtractor",
    "ExtractedTable",
    "TableExtractionResult",
    "table_extractor",
    "ImageCropper",
    "ExtractedFigure",
    "ImageCropperResult",
    "image_cropper",
    "OCRFallback",
    "OCRPageResult",
    "ocr_fallback",
    "IngestionPipeline",
    "IngestionResult",
    "IngestionStageTiming",
    "ingestion_pipeline",
]
