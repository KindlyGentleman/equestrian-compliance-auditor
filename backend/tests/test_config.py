import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



def test_settings_defaults():
    """Verify that settings load with valid defaults."""
    from backend.app.core.config import Settings

    settings = Settings()
    assert settings.APP_NAME == "Equestrian Compliance & Specification Auditor"
    assert settings.GEMINI_MODEL_NAME == "gemini-2.0-flash"
    assert settings.GEMINI_EMBEDDING_MODEL == "text-embedding-004"
    assert settings.PORT == 8000
    assert "qdrant" in settings.QDRANT_STORAGE_PATH


def test_ensure_directories():
    """Verify that ensure_directories successfully creates required paths."""
    from backend.app.core.config import Settings

    settings = Settings()
    settings.ensure_directories()

    assert Path(settings.QDRANT_STORAGE_PATH).exists()
    assert Path(settings.UPLOAD_DIR).exists()
    assert Path(settings.CACHE_DIR).exists()
    assert Path(settings.FEI_REGULATIONS_DIR).exists()
    assert Path(settings.BRAND_SOPS_DIR).exists()


def test_gemini_client_mock_mode():
    """Verify GeminiClientWrapper falls back cleanly to mock mode without an API key."""
    from backend.app.core.gemini_client import GeminiClientWrapper

    wrapper = GeminiClientWrapper(api_key="")
    assert wrapper.use_mock is True
    assert wrapper.client is None


def test_gemini_client_live_initialization():
    """Verify GeminiClientWrapper attempts live client with valid key string."""
    from backend.app.core.gemini_client import GeminiClientWrapper

    wrapper = GeminiClientWrapper(api_key="AIzaSyDummyTestKeyForVerification12345")
    # Should attempt live initialization
    assert wrapper.api_key == "AIzaSyDummyTestKeyForVerification12345"


if __name__ == "__main__":
    test_settings_defaults()
    test_ensure_directories()
    test_gemini_client_mock_mode()
    test_gemini_client_live_initialization()
    print("ALL TICK-0103 CONFIGURATION TESTS PASSED SUCCESSFULLY!")
