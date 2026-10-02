"""Deep testing for RAG hybrid retriever: discipline isolation, query robustness, and vector store resilience."""
import pytest

from backend.app.models.tech_pack import Discipline
from backend.app.rag.retriever import HybridRetriever
from backend.app.rag.vector_store import VectorStoreManager


@pytest.fixture(scope="module")
def isolated_vector_store():
    """Create dedicated in-memory vector store for deep isolation and stress testing."""
    store = VectorStoreManager(in_memory=True, collection_name="test_deep_isolation_rules")
    count = store.index_all_regulations()
    assert count >= 6
    return store


def test_jumping_query_strict_discipline_isolation(isolated_vector_store: VectorStoreManager):
    """Ensure querying under JUMPING discipline never retrieves Dressage or Eventing specific articles."""
    retriever = HybridRetriever(vector_store=isolated_vector_store)
    results = retriever.retrieve_rules(
        query="collar logo maximum area",
        discipline=Discipline.JUMPING,
        top_k=10,
    )

    assert len(results) > 0
    for chunk in results:
        assert chunk.discipline in ("JUMPING", "ALL"), (
            f"Cross-discipline rule leak detected: {chunk.article_id} has discipline '{chunk.discipline}'"
        )
        # Ensure Dressage Article 427 or Eventing Article 538 are never returned for Jumping
        assert "427" not in chunk.article_id, f"Dressage rule leaked into Jumping query: {chunk.article_id}"
        assert "538" not in chunk.article_id, f"Eventing rule leaked into Jumping query: {chunk.article_id}"


def test_dressage_query_strict_discipline_isolation(isolated_vector_store: VectorStoreManager):
    """Ensure querying under DRESSAGE discipline never retrieves Jumping specific articles."""
    retriever = HybridRetriever(vector_store=isolated_vector_store)
    results = retriever.retrieve_rules(
        query="tailcoat collar velvet contrast color rules",
        discipline=Discipline.DRESSAGE,
        top_k=10,
    )

    assert len(results) > 0
    for chunk in results:
        assert chunk.discipline in ("DRESSAGE", "ALL"), (
            f"Cross-discipline rule leak detected: {chunk.article_id} has discipline '{chunk.discipline}'"
        )
        assert "256" not in chunk.article_id, f"Jumping rule leaked into Dressage query: {chunk.article_id}"


@pytest.mark.parametrize("query_variant", [
    "collar brand logo area",
    "jacket neck manufacturer emblem surface limit",
    "coat revers sponsor badge dimensions",
    "collar identification maximum square centimeters",
])
def test_synonym_and_vocabulary_invariance(isolated_vector_store: VectorStoreManager, query_variant: str):
    """Verify that varied natural vocabulary still surfaces the governing FEI logo constraint."""
    retriever = HybridRetriever(vector_store=isolated_vector_store)
    results = retriever.retrieve_rules(
        query=query_variant,
        discipline=Discipline.JUMPING,
        top_k=3,
    )

    assert len(results) > 0
    top = results[0]
    assert top.score is not None and top.score > 0.0
    # Must retrieve Jumping rule 256 or Brand logo specification
    assert "256" in top.article_id or "Logo" in top.title or "Commercial" in top.title


@pytest.mark.parametrize("adversarial_query", [
    "",
    "   \t\n   ",
    "SELECT * FROM regulations WHERE id = 1;",
    "' OR '1'='1' --",
    "<script>alert('xss')</script>",
    "A" * 5000,  # 5,000 character repetition query
])
def test_malicious_and_extreme_queries_fail_safely(isolated_vector_store: VectorStoreManager, adversarial_query: str):
    """Ensure malformed, empty, or malicious query strings execute safely without crashing."""
    retriever = HybridRetriever(vector_store=isolated_vector_store)
    results = retriever.retrieve_rules(
        query=adversarial_query,
        discipline=Discipline.JUMPING,
        top_k=3,
    )
    assert isinstance(results, list)


def test_reindexing_idempotency_does_not_duplicate_points():
    """Verify that repeated re-indexing calls overwrite existing IDs without point inflation."""
    store = VectorStoreManager(in_memory=True, collection_name="test_idempotency_check")
    count_1 = store.index_all_regulations()
    info_1 = store.client.get_collection(store.collection_name)

    # Re-index a second and third time
    count_2 = store.index_all_regulations()
    count_3 = store.index_all_regulations()
    info_final = store.client.get_collection(store.collection_name)

    assert count_1 == count_2 == count_3
    assert info_1.points_count == info_final.points_count, (
        f"Point count inflated from {info_1.points_count} to {info_final.points_count}"
    )
