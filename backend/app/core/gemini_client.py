"""Google Gemini 2.0 Flash client wrapper with mock testing support."""
import logging
from typing import Any

from google import genai
from google.genai import types

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiClientWrapper:
    """Wrapper managing Google GenAI API client and mock fallback."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self._client: genai.Client | None = None
        self.use_mock = settings.USE_MOCK_LLM or not bool(self.api_key)

        if not self.use_mock:
            try:
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Initialized Google GenAI live client with model %s", settings.GEMINI_MODEL_NAME)
            except Exception as e:
                logger.warning("Failed to initialize live GenAI client (%s); falling back to mock mode", e)
                self.use_mock = True
        else:
            logger.info("Operating in Mock LLM mode (no GEMINI_API_KEY provided or USE_MOCK_LLM is True)")

    @property
    def client(self) -> genai.Client | None:
        """Return the underlying genai.Client instance."""
        return self._client

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Any,
        images: list | None = None,
        system_instruction: str | None = None,
    ) -> Any:
        """Generate structured Pydantic response from prompt."""
        if self.use_mock or self._client is None:
            logger.info("Mock generating structured response for schema: %s", getattr(response_schema, "__name__", "schema"))
            # In mock mode, construct empty or default instance
            if hasattr(response_schema, "model_validate"):
                # Try creating default or dummy dictionary
                return None
            return None

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            system_instruction=system_instruction,
            temperature=0.1,  # Low temperature for deterministic compliance extraction
        )

        contents = [prompt]
        if images:
            contents.extend(images)

        response = await self._client.aio.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=contents,
            config=config,
        )
        return response.parsed


# Singleton instance
gemini_wrapper = GeminiClientWrapper()
