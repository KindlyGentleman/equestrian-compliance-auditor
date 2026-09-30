"""Smoke test for TICK-0102: Verifying core libraries installation and runtime compatibility."""
import sys
import time


def test_core_imports():
    """Verify that all core libraries can be imported without error."""
    start_time = time.time()
    
    import fastapi
    import pydantic
    import pydantic_settings
    import pymupdf
    import pymupdf4llm
    import pdfplumber
    import qdrant_client
    import google.genai
    import httpx
    
    elapsed = time.time() - start_time
    print(f"[OK] Core modules imported in {elapsed:.3f}s")
    assert elapsed < 15.0, f"Imports took too long: {elapsed}s"


def test_qdrant_in_memory():
    """Verify that Qdrant local embedded in-memory mode operates with zero external services."""
    from qdrant_client import QdrantClient
    from qdrant_client.models import VectorParams, Distance
    
    client = QdrantClient(":memory:")
    collection_name = "test_smoke"
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=4, distance=Distance.COSINE),
    )
    
    collections = client.get_collections().collections
    assert any(c.name == collection_name for c in collections), "Qdrant memory collection not found"
    print("[OK] Qdrant embedded in-memory client operational")


def test_rapidocr_onnx_runtime():
    """Verify RapidOCR can initialize its ONNX model on CPU."""
    from rapidocr_onnxruntime import RapidOCR
    
    # Initialize engine
    engine = RapidOCR()
    assert engine is not None
    print("[OK] RapidOCR ONNX CPU runtime initialized successfully")


if __name__ == "__main__":
    test_core_imports()
    test_qdrant_in_memory()
    test_rapidocr_onnx_runtime()
    print("ALL TICK-0102 CORE DEPENDENCY TESTS PASSED SUCCESSFULLY!")
