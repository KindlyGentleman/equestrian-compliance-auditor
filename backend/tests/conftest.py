"""Centralized pytest configuration and reusable test fixtures."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.api.sample_generator import create_sample_techpack_pdf
from backend.app.main import app
from backend.app.rag.vector_store import vector_store_manager


@pytest.fixture(scope="session", autouse=True)
def init_test_environment():
    """Ensure vector database collection is seeded with regulations for the test session."""
    vector_store_manager.index_all_regulations()


@pytest.fixture(scope="session")
def api_client() -> TestClient:
    """Provide a shared FastAPI TestClient instance."""
    return TestClient(app)


@pytest.fixture(scope="session")
def canonical_sample_pdf(tmp_path_factory) -> Path:
    """Generate a realistic 10-page show jacket tech pack PDF for testing."""
    temp_dir = tmp_path_factory.mktemp("shared_fixtures")
    pdf_path = temp_dir / "canonical_grand_prix_coat_10p.pdf"
    create_sample_techpack_pdf(pdf_path)
    return pdf_path
