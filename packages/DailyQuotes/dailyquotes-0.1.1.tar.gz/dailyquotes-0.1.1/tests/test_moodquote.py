import pytest
import openai
from quotes.generator import generate_mood_quote

def test_generate_mood_quote_valid():
    """Test that a mood-based quote is generated correctly."""
    quote = generate_mood_quote("happy")
    assert isinstance(quote, str), "Output should be a string"
    assert len(quote) > 0, "Generated quote should not be empty"

def test_generate_mood_quote_invalid_empty():
    """Test that an empty string returns an error message."""
    quote = generate_mood_quote("")
    assert quote == "Error: Mood must be a valid string."

def test_generate_mood_quote_invalid_number():
    """Test that a number as mood returns an error message."""
    quote = generate_mood_quote(123)
    assert quote == "Error: Mood must be a valid string."
