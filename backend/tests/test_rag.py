"""Automated test suite for Stage 4: Regulation corpus, rules catalog, Qdrant hybrid vector store, and retriever."""
import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from backend.app.core.config import settings
from backend.app.models.tech_pack import Discipline, GarmentMetadata, GarmentType, FabricSpec, CostingSpec, TechPackSpec
from backend.app.rag.vector_store import RuleChunk, VectorStoreManager
from backend.app.rag.retriever import HybridRetriever


@pytest.fixture(scope="module")
def in_memory_store():
    """Create in-memory Qdrant store indexed with FEI and Brand SOPs."""
    store = VectorStoreManager(in_memory=True, collection_name="test_equestrian_rules")
    count = store.index_all_regulations()
    assert count >= 6, f"Expected at least 6 regulation chunks, indexed {count}"
    return store


def test_markdown_chunking_parser():
    """Verify markdown regulation parser extracts chunks with complete metadata."""
    store = VectorStoreManager(in_memory=True, collection_name="test_chunking")
    jumping_file = Path(settings.FEI_REGULATIONS_DIR) / "fei_jumping_art256.md"
    assert jumping_file.exists(), f"File missing: {jumping_file}"

    chunks = store.parse_markdown_file(jumping_file)
    assert len(chunks) >= 2

    # Check Article 256.3 (Commercial Identification)
    logo_chunk = next((c for c in chunks if "256.3" in c.article_id or "Commercial" in c.title), None)
    assert logo_chunk is not None
    assert logo_chunk.source == "FEI"
    assert logo_chunk.discipline == "JUMPING"
    assert "60 cm²" in logo_chunk.content or "sixty square centimeters" in logo_chunk.content


def test_rules_catalog_json_schema():
    """Validate structure, uniqueness, and completeness of rules_catalog.json."""
    catalog_path = Path(settings.RULES_CATALOG_PATH)
    assert catalog_path.exists(), f"Catalog missing: {catalog_path}"

    with open(catalog_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "rules" in data
    rules = data["rules"]
    assert len(rules) >= 8

    rule_ids = set()
    for rule in rules:
        r_id = rule.get("rule_id")
        assert r_id is not None, "Missing rule_id"
        assert r_id not in rule_ids, f"Duplicate rule_id: {r_id}"
        rule_ids.add(r_id)

        assert rule.get("operator") in ["<=", ">=", "==", "in_range"]
        assert "threshold" in rule
        assert rule.get("severity_if_violated") in ["VIOLATION", "WARNING"]
        assert len(rule.get("verbatim_citation", "")) > 10


def test_vector_store_embedding_and_indexing(in_memory_store):
    """Verify vector generation and point indexing in Qdrant."""
    vec = in_memory_store.generate_embedding("Collar brand logo area constraint")
    assert len(vec) == 768

    info = in_memory_store.client.get_collection(in_memory_store.collection_name)
    assert info.points_count >= 6


def test_hybrid_retriever_query(in_memory_store):
    """Verify semantic retrieval returns relevant FEI Article 256 for jumping logo query."""
    retriever = HybridRetriever(vector_store=in_memory_store)
    results = retriever.retrieve_rules(
        query="collar logo maximum area",
        discipline=Discipline.JUMPING,
        top_k=3,
    )

    assert len(results) > 0
    top = results[0]
    assert isinstance(top, RuleChunk)
    assert top.score is not None and top.score > 0.0
    # Must retrieve Jumping or Logo rules
    assert "256" in top.article_id or "Logo" in top.title or "Commercial" in top.title


def test_hybrid_retriever_discipline_filter(in_memory_store):
    """Verify discipline filter excludes non-matching discipline rules."""
    retriever = HybridRetriever(vector_store=in_memory_store)
    results = retriever.retrieve_rules(
        query="tailcoat conservative dark colors and collar velvet lapel",
        discipline=Discipline.DRESSAGE,
        top_k=5,
    )

    for chunk in results:
        assert chunk.discipline in ["DRESSAGE", "ALL"], f"Found unexpected discipline {chunk.discipline}"


def test_retriever_techpack_context_generation(in_memory_store):
    """Verify automated tech pack query synthesis and LLM prompt context formatting."""
    retriever = HybridRetriever(vector_store=in_memory_store)
    spec = TechPackSpec(
        metadata=GarmentMetadata(
            style_code="ME-2026-SJ01",
            style_name="Grand Prix Show Coat",
            discipline=Discipline.JUMPING,
            garment_type=GarmentType.SHOW_JACKET,
        ),
        fabric=FabricSpec(
            primary_composition="78% Polyamide, 22% Elastane",
            weight_gsm=295.0,
        ),
        costing=CostingSpec(
            target_fob_usd=55.0,
            actual_fob_usd=58.5,
        ),
    )

    chunks = retriever.retrieve_rules_for_techpack(spec, top_k=4)
    assert len(chunks) >= 2

    context_str = retriever.format_context_for_prompt(chunks)
    assert "Regulation Excerpt" in context_str
    assert "Official Rule Text" in context_str
