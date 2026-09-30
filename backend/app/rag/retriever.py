"""Hybrid retrieval engine combining semantic vector search and discipline-filtered metadata."""
import re
from typing import List, Optional, Set
from qdrant_client.models import FieldCondition, Filter, MatchAny

from backend.app.models.tech_pack import Discipline, TechPackSpec
from backend.app.rag.vector_store import RuleChunk, VectorStoreManager, vector_store_manager


class HybridRetriever:
    """Retrieves relevant regulatory and brand SOP chunks with hybrid vector and lexical scoring."""

    def __init__(self, vector_store: Optional[VectorStoreManager] = None):
        self.store = vector_store or vector_store_manager

    def retrieve_rules(
        self,
        query: str,
        discipline: Optional[Discipline | str] = None,
        garment_type: Optional[str] = None,
        top_k: int = 5,
    ) -> List[RuleChunk]:
        """Query Qdrant collection with discipline pre-filtering and lexical re-ranking."""
        query_vector = self.store.generate_embedding(query)

        # Build discipline filter (matching specific discipline or ALL)
        query_filter: Optional[Filter] = None
        if discipline:
            disc_str = discipline.value if isinstance(discipline, Discipline) else str(discipline).upper()
            if disc_str in ["JUMPING", "DRESSAGE", "EVENTING"]:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="discipline",
                            match=MatchAny(any=[disc_str, "ALL"]),
                        )
                    ]
                )

        search_limit = max(top_k * 3, 10)
        search_results = self.store.client.query_points(
            collection_name=self.store.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=search_limit,
        ).points

        # Lexical boost words extracted from query
        query_tokens = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]

        scored_chunks: List[RuleChunk] = []
        for hit in search_results:
            payload = hit.payload or {}
            base_score = float(hit.score) if hasattr(hit, "score") and hit.score is not None else 0.5

            content_lower = str(payload.get("content", "")).lower()
            title_lower = str(payload.get("title", "")).lower()

            # Exact keyword match boost
            matches = sum(1 for t in query_tokens if t in content_lower or t in title_lower)
            lexical_boost = min(matches * 0.05, 0.25)
            final_score = round(base_score + lexical_boost, 4)

            scored_chunks.append(
                RuleChunk(
                    chunk_id=payload.get("chunk_id", ""),
                    source=payload.get("source", "FEI"),
                    rulebook=payload.get("rulebook", ""),
                    article_id=payload.get("article_id", ""),
                    discipline=payload.get("discipline", "ALL"),
                    category=payload.get("category", ""),
                    title=payload.get("title", ""),
                    content=payload.get("content", ""),
                    score=final_score,
                )
            )

        # Sort descending by final score and take top_k
        scored_chunks.sort(key=lambda c: c.score or 0.0, reverse=True)
        return scored_chunks[:top_k]

    def retrieve_rules_for_techpack(self, spec: TechPackSpec, top_k: int = 6) -> List[RuleChunk]:
        """Generate targeted compliance queries for a tech pack and retrieve consolidated rules."""
        queries = [
            f"{spec.metadata.discipline.value} collar logo chest emblem surface area limits",
            f"{spec.metadata.discipline.value} {spec.metadata.garment_type.value} collar lapel contrast velvet piping rules",
            f"Fabric breathability WVTR g/m2/24h and 4-way stretch standards",
            f"{spec.metadata.garment_type.value} maximum target FOB COGS ceiling",
        ]

        seen_chunk_ids: Set[str] = set()
        consolidated: List[RuleChunk] = []

        for q in queries:
            results = self.retrieve_rules(
                query=q,
                discipline=spec.metadata.discipline,
                garment_type=spec.metadata.garment_type.value,
                top_k=3,
            )
            for chunk in results:
                if chunk.chunk_id not in seen_chunk_ids:
                    seen_chunk_ids.add(chunk.chunk_id)
                    consolidated.append(chunk)

        consolidated.sort(key=lambda c: c.score or 0.0, reverse=True)
        return consolidated[:top_k]

    def format_context_for_prompt(self, chunks: List[RuleChunk]) -> str:
        """Format retrieved rule chunks into clean markdown blocks for LLM prompt context."""
        parts: List[str] = []
        for idx, chunk in enumerate(chunks, start=1):
            parts.append(
                f"### [Regulation Excerpt {idx}]: {chunk.rulebook} ({chunk.article_id})\n"
                f"- Category: {chunk.category} | Discipline: {chunk.discipline}\n"
                f"- Title: {chunk.title}\n"
                f"Official Rule Text:\n{chunk.content}\n"
            )
        return "\n".join(parts)


retriever = HybridRetriever()
