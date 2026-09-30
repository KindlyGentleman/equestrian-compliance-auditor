"""High-speed PDF layout and text parser using PyMuPDF4LLM."""
import time
from pathlib import Path

import pymupdf
import pymupdf4llm
from pydantic import BaseModel, Field


class PageContent(BaseModel):
    """Extracted content for a single PDF page."""
    page_number: int = Field(ge=1, description="1-indexed page number")
    markdown: str = Field(description="Structured markdown text of the page")
    char_count: int = Field(default=0)
    has_tables: bool = Field(default=False)
    has_images: bool = Field(default=False)


class DocumentContent(BaseModel):
    """Complete extracted document payload with page-level mapping."""
    file_name: str
    total_pages: int
    full_markdown: str
    pages: list[PageContent]
    execution_time_seconds: float


class PDFParser:
    """SOTA CPU-native parser converting tech pack PDFs into structured Markdown."""

    def __init__(self, write_images: bool = False, image_dir: str | None = None, use_ocr: bool = False):
        self.write_images = write_images
        self.image_dir = image_dir
        self.use_ocr = use_ocr

    def parse(self, pdf_path: str | Path, use_ocr: bool | None = None) -> DocumentContent:
        """Parse multi-page tech pack PDF into page-mapped Markdown in a single optimized pass."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        start_time = time.time()
        doc = pymupdf.open(str(path))
        total_pages = len(doc)
        if total_pages == 0:
            doc.close()
            raise ValueError(f"PDF document is empty (0 pages): {path}")

        pages: list[PageContent] = []
        full_md_parts: list[str] = []
        should_use_ocr = self.use_ocr if use_ocr is None else use_ocr

        try:
            # Single-pass extraction using page_chunks=True for maximum throughput
            raw_chunks = pymupdf4llm.to_markdown(
                doc,
                page_chunks=True,
                write_images=self.write_images,
                image_path=self.image_dir,
                use_ocr=should_use_ocr,
            )

            for page_idx, chunk in enumerate(raw_chunks):
                page_num = page_idx + 1
                page_text = chunk.get("text", "").strip()

                # Check for images on page
                has_images = len(doc[page_idx].get_images()) > 0 if page_idx < total_pages else False
                has_tables = "|" in page_text and "-|-" in page_text

                page_content = PageContent(
                    page_number=page_num,
                    markdown=page_text,
                    char_count=len(page_text),
                    has_tables=has_tables,
                    has_images=has_images,
                )
                pages.append(page_content)
                full_md_parts.append(f"<!-- PAGE {page_num} START -->\n{page_text}\n<!-- PAGE {page_num} END -->")

            elapsed = time.time() - start_time
            full_markdown = "\n\n".join(full_md_parts)

            return DocumentContent(
                file_name=path.name,
                total_pages=total_pages,
                full_markdown=full_markdown,
                pages=pages,
                execution_time_seconds=round(elapsed, 4),
            )
        finally:
            doc.close()


pdf_parser = PDFParser()
