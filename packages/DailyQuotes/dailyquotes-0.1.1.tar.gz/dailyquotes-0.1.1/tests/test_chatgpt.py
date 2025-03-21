import pytest
import openai
import logging
from quotes.chatgpt import chatgpt_generate

# Get logger
logger = logging.getLogger(__name__)

def test_api_connection_and_quote_generation(caplog):
    """Test if the API connects and generates a quote."""
    with caplog.at_level(logging.INFO):  # ✅ Ensures logging is captured
        try:
            quote = chatgpt_generate("Generate a unique inspirational quote.")
            logger.info(f"✅ Generated ChatGPT Quote: {quote}")  # ✅ Should log now!

            # Ensure the response is a non-empty string
            assert isinstance(quote, str)
            assert len(quote) > 0

        except openai.OpenAIError as e:
            logger.error(f"❌ OpenAI API connection failed: {e}")
            pytest.fail(f"OpenAI API connection failed: {e}")

    # ✅ Verify logs were actually captured in pytest
    assert "✅ Generated ChatGPT Quote" in caplog.text
