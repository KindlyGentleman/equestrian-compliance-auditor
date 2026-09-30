"""Local embedded Qdrant vector store and regulatory chunking manager."""
import hashlib
import logging
import math
import re
from pathlib import Path

from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from backend.app.core.config import settings
from backend.app.core.gemini_client import gemini_wrapper

logger = logging.getLogger(__name__)


class RuleChunk(BaseModel):
    """Structured regulatory or standard operating procedure rule chunk."""
    chunk_id: str
    source: str = Field(description="FEI or Brand")
    rulebook: str = Field(description="FEI Jumping Rules, Brand SOP, etc.")
    article_id: str = Field(description="Article or section code e.g. Art. 256.3")
    discipline: str = Field(default="ALL", description="JUMPING, DRESSAGE, EVENTING, or ALL")
    category: str = Field(description="Dress & Identification, Fabric, Costing, etc.")
    title: str
    content: str
    score: float | None = None


class VectorStoreManager:
    """Manages embedded Qdrant storage, embedding generation, and regulation indexing."""

    VECTOR_SIZE = 768

    def __init__(
        self,
        storage_path: str | None = None,
        collection_name: str | None = None,
        in_memory: bool = False,
    ):
        self.collection_name = collection_name or settings.QDRANT_COLLECTION_NAME
        self.in_memory = in_memory

        if in_memory or (not storage_path and settings.APP_ENV == "testing"):
            self.client = QdrantClient(":memory:")
        else:
            resolved_path = Path(storage_path or settings.QDRANT_STORAGE_PATH)
            resolved_path.mkdir(parents=True, exist_ok=True)
            try:
                self.client = QdrantClient(path=str(resolved_path))
            except RuntimeError as exc:
                if "already accessed by another instance" in str(exc):
                    logger.warning(
                        "Local Qdrant directory is locked by another process (%s). Falling back to in-memory storage.",
                        exc,
                    )
                    self.client = QdrantClient(":memory:")
                else:
                    raise

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create Qdrant collection if not already initialized."""
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info("Created Qdrant collection '%s' with size=%d", self.collection_name, self.VECTOR_SIZE)

    def generate_embedding(self, text: str) -> list[float]:
        """Generate 768-dimensional normalized embedding via Gemini or deterministic hash fallback."""
        if not gemini_wrapper.use_mock and gemini_wrapper.client is not None:
            try:
                response = gemini_wrapper.client.models.embed_content(
                    model=settings.GEMINI_EMBEDDING_MODEL,
                    contents=text,
                )
                if hasattr(response, "embedding") and response.embedding.values:
                    return list(response.embedding.values)
                if hasattr(response, "embeddings") and response.embeddings:
                    return list(response.embeddings[0].values)
            except Exception as exc:
                logger.warning("Gemini live embedding call failed (%s); using deterministic projection", exc)

        # Deterministic 768-dim pseudo-semantic vector for offline/testing use
        vector = [0.0] * self.VECTOR_SIZE
        words = re.findall(r"\w+", text.lower())
        for idx, word in enumerate(words):
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            pos = h % self.VECTOR_SIZE
            val = ((h >> 8) % 1000) / 1000.0
            vector[pos] += val * (1.0 / (math.log(idx + 2)))

        # L2 Normalize
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        else:
            vector[0] = 1.0
        return vector

    def parse_markdown_file(self, file_path: Path) -> list[RuleChunk]:
        """Parse FEI or Brand SOP markdown file into granular rule chunks."""
        text = file_path.read_text(encoding="utf-8")
        chunks: list[RuleChunk] = []

        # Extract front metadata
        fed_match = re.search(r"-\s*\*\*Federation\*\*:\s*([^\n]+)", text)
        org_match = re.search(r"-\s*\*\*Organization\*\*:\s*([^\n]+)", text)
        source = "FEI" if fed_match else ("Brand" if org_match else "General")

        disc_match = re.search(r"-\s*\*\*Discipline\*\*:\s*([^\n]+)", text)
        discipline = "ALL"
        if disc_match:
            raw_d = disc_match.group(1).upper()
            if "JUMP" in raw_d:
                discipline = "JUMPING"
            elif "DRESS" in raw_d:
                discipline = "DRESSAGE"
            elif "EVENT" in raw_d:
                discipline = "EVENTING"

        rulebook_match = re.search(r"-\s*\*\*Rulebook\*\*:\s*([^\n]+)", text)
        standard_match = re.search(r"-\s*\*\*Standard\*\*:\s*([^\n]+)", text)
        rulebook = rulebook_match.group(1).strip() if rulebook_match else (
            standard_match.group(1).strip() if standard_match else file_path.stem
        )

        category_match = re.search(r"-\s*\*\*Category\*\*:\s*([^\n]+)", text)
        category = category_match.group(1).strip() if category_match else "Apparel Regulation"

        # Split on section headings '### '
        sections = re.split(r"\n###\s+", text)
        for s_idx, sec in enumerate(sections[1:], start=1):
            lines = sec.strip().split("\n")
            header = lines[0].strip()
            content = "\n".join(lines[1:]).strip()

            # Extract article ID from header (e.g. Article 256.3 or Section 2)
            art_match = re.search(r"(?:Article\s+([0-9\.]+)|Section\s+([0-9]+)|([A-Z0-9\-_]+))", header, re.I)
            article_id = f"Art. {art_match.group(1)}" if art_match and art_match.group(1) else (
                f"Sec. {art_match.group(2)}" if art_match and art_match.group(2) else f"Sec.{s_idx}"
            )

            # Categorize by section topic if applicable
            sec_category = category
            if "financial" in header.lower() or "cogs" in header.lower() or "cost" in header.lower():
                sec_category = "Costing & FOB"
            elif "fabric" in header.lower() or "material" in header.lower():
                sec_category = "Fabric & Performance"
            elif "logo" in header.lower() or "commercial" in header.lower() or "identification" in header.lower():
                sec_category = "Branding & Logos"
            elif "tailor" in header.lower() or "tolerance" in header.lower() or "stitch" in header.lower():
                sec_category = "Tailoring & Dimensions"

            chunk_id = f"{source.lower()}_{discipline.lower()}_{article_id.lower().replace(' ', '_').replace('.', '_')}"

            chunks.append(
                RuleChunk(
                    chunk_id=chunk_id,
                    source=source,
                    rulebook=rulebook,
                    article_id=article_id,
                    discipline=discipline,
                    category=sec_category,
                    title=header,
                    content=content,
                )
            )

        return chunks

    def index_all_regulations(
        self,
        fei_dir: str | None = None,
        brand_dir: str | None = None,
    ) -> int:
        """Scan regulation markdown directories, extract chunks, compute vectors, and upsert to Qdrant."""
        f_dir = Path(fei_dir or settings.FEI_REGULATIONS_DIR)
        b_dir = Path(brand_dir or settings.BRAND_SOPS_DIR)

        all_files = list(f_dir.glob("*.md")) + list(b_dir.glob("*.md"))
        all_chunks: list[RuleChunk] = []

        for p in all_files:
            if p.name.startswith("."):
                continue
            all_chunks.extend(self.parse_markdown_file(p))

        points: list[PointStruct] = []
        for idx, chunk in enumerate(all_chunks, start=1):
            text_to_embed = f"{chunk.rulebook} {chunk.title}\n{chunk.content}"
            vector = self.generate_embedding(text_to_embed)

            payload = {
                "chunk_id": chunk.chunk_id,
                "source": chunk.source,
                "rulebook": chunk.rulebook,
                "article_id": chunk.article_id,
                "discipline": chunk.discipline,
                "category": chunk.category,
                "title": chunk.title,
                "content": chunk.content,
            }

            points.append(PointStruct(id=idx, vector=vector, payload=payload))

        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)
            logger.info("Upserted %d regulation rule chunks into collection '%s'", len(points), self.collection_name)

        return len(points)


vector_store_manager = VectorStoreManager()
