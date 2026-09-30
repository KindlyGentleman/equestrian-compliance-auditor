"""Tabular data extraction and markdown normalizer using pdfplumber."""
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import pdfplumber
from pydantic import BaseModel, Field


class ExtractedTable(BaseModel):
    """Normalized structured table representation."""
    page_number: int
    table_type: str = Field(description="BOM, MEASUREMENTS, GRADING, or GENERIC")
    headers: List[str]
    rows: List[Dict[str, Any]]
    markdown: str


class TableExtractionResult(BaseModel):
    """Aggregate result of table extraction across a PDF."""
    total_tables: int
    tables: List[ExtractedTable]


class TableExtractor:
    """Extracts, standardizes headers, and normalizes tables from tech packs."""

    HEADER_MAPPINGS = {
        # Measurement / POM synonyms
        "pom": "pom_code",
        "code": "pom_code",
        "pom code": "pom_code",
        "point of measure": "description",
        "description": "description",
        "spec": "spec_cm",
        "spec cm": "spec_cm",
        "tol": "tolerance_cm",
        "tol cm": "tolerance_cm",
        "tolerance": "tolerance_cm",
        "tolerance cm": "tolerance_cm",
        # BOM synonyms
        "item": "item_name",
        "item name": "item_name",
        "component": "item_name",
        "placement": "placement",
        "location": "placement",
        "material": "material",
        "fabric": "material",
        "color": "color_code",
        "unit cost": "unit_cost",
        "cost": "unit_cost",
        "supplier": "supplier_code",
    }

    def _normalize_header(self, raw_header: str) -> str:
        """Map raw header string to a standardized snake_case identifier."""
        cleaned = re.sub(r"[^\w\s]", "", str(raw_header or "").lower().strip())
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return self.HEADER_MAPPINGS.get(cleaned, cleaned.replace(" ", "_"))

    def _detect_table_type(self, headers: List[str]) -> str:
        """Infer table category based on standardized headers."""
        header_set = set(headers)
        if any(k in header_set for k in ["pom_code", "spec_cm", "tolerance_cm"]):
            return "MEASUREMENTS"
        if any(k in header_set for k in ["item_name", "material", "unit_cost", "placement"]):
            return "BOM"
        if any(k in header_set for k in ["size", "chest", "waist", "xs", "s", "m", "l", "34", "36", "38"]):
            return "GRADING"
        return "GENERIC"

    def _to_markdown_table(self, headers: List[str], data_rows: List[List[Any]]) -> str:
        """Convert headers and rows into clean GitHub-Flavored Markdown."""
        str_headers = [str(h) for h in headers]
        col_widths = [len(h) for h in str_headers]

        formatted_rows: List[List[str]] = []
        for row in data_rows:
            row_strs = [str(val if val is not None else "").strip() for val in row]
            # Ensure row length matches headers
            while len(row_strs) < len(headers):
                row_strs.append("")
            row_strs = row_strs[:len(headers)]
            for i, val in enumerate(row_strs):
                col_widths[i] = max(col_widths[i], len(val))
            formatted_rows.append(row_strs)

        header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(str_headers)) + " |"
        sep_line = "|-" + "-|-".join("-" * col_widths[i] for i in range(len(headers))) + "-|"
        
        row_lines = [
            "| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(r)) + " |"
            for r in formatted_rows
        ]
        return "\n".join([header_line, sep_line] + row_lines)

    def extract_tables(self, pdf_path: str | Path) -> TableExtractionResult:
        """Extract all tables from PDF, normalize headers, and format as markdown."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        extracted_tables: List[ExtractedTable] = []

        with pdfplumber.open(str(path)) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_num = page_idx + 1
                raw_tables = page.extract_tables()

                for table in raw_tables:
                    if not table or len(table) < 2:
                        continue  # Skip single-line or empty structures

                    raw_headers = [cell if cell is not None else f"col_{i}" for i, cell in enumerate(table[0])]
                    normalized_headers = [self._normalize_header(h) for h in raw_headers]
                    table_type = self._detect_table_type(normalized_headers)

                    data_rows: List[Dict[str, Any]] = []
                    raw_data_rows: List[List[Any]] = []

                    for row in table[1:]:
                        if not any(row):  # Skip all-None empty rows
                            continue
                        row_dict: Dict[str, Any] = {}
                        raw_data_rows.append(row)
                        for col_idx, norm_header in enumerate(normalized_headers):
                            val = row[col_idx] if col_idx < len(row) else None
                            row_dict[norm_header] = str(val).strip() if val is not None else ""
                        data_rows.append(row_dict)

                    if not data_rows:
                        continue

                    md_representation = self._to_markdown_table(raw_headers, raw_data_rows)

                    extracted_tables.append(
                        ExtractedTable(
                            page_number=page_num,
                            table_type=table_type,
                            headers=normalized_headers,
                            rows=data_rows,
                            markdown=md_representation,
                        )
                    )

        return TableExtractionResult(
            total_tables=len(extracted_tables),
            tables=extracted_tables,
        )


table_extractor = TableExtractor()
